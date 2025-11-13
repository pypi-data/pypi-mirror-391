# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import logging
import os
from collections import OrderedDict
from copy import deepcopy

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from tankoh2 import log
from tankoh2.design.winding.contour import calculateWindability, getReducedCylinderLength, setReducedCylinder
from tankoh2.design.winding.material import getCompositeMuwind
from tankoh2.design.winding.optimize import calculateMinAngle, findValidWindingAngle, minimizeUtilization
from tankoh2.design.winding.solver import (
    getHelicalDesignFactors,
    getLinearResults,
    getMaxPuckLocalPuckMassIndexByShift,
    getPuckStrainDiff,
    getTargetFunctionValues,
    getThickShellScaling,
    getWeightedTargetFuncByAngle,
)
from tankoh2.design.winding.winding import getPolarOpeningNodesForAngle, windHoopLayer, windLayer
from tankoh2.design.winding.windingutils import (
    applyHoopShiftParameters,
    checkAnglesAndShifts,
    clusterHoopLayers,
    createHoopShiftsFromParameters,
    getAnglesFromVesselCylinder,
    getLayerAngles,
    getLayerThicknesses,
    getLinearResultsAsDataFrame,
    getMostCriticalElementIdxPuck,
    getStartOfHoopDropOff,
    getStartOfSortedLayers,
    isHoopLayer,
    moveHighAnglesOutwards,
    moveLastFittingLayerToStartOfSorted,
)
from tankoh2.geometry.dome import AbstractDome, flipContour
from tankoh2.mechanics.fatigue import getFatigueLifeFRPTankLevel
from tankoh2.service.exception import Tankoh2Error
from tankoh2.service.plot.generic import plotContour, plotDataFrame
from tankoh2.service.plot.muwind import plotPuckAndTargetFunc, plotStressEpsPuck, plotThicknesses
from tankoh2.service.utilities import indent, writeParametersToYAML
from tankoh2.settings import settings


def printLayer(layerNumber, postfix=""):
    sep = "\n" + "=" * 80
    verbose = log.level < logging.INFO
    log.info((sep if verbose else "") + f"\nLayer {layerNumber} {postfix}" + (sep if verbose else ""))


def getOptScalingFactors(targetFuncWeights, puck, strainDiff, optKwargs):
    r"""Adapt mass scaling since puck values are reduced over time and mass slightly increased.

    As result, the scaling between mass and puck must be adapted for each iteration to keep the proposed
    weights of targetFuncWeights.

    Perform the following operation:

    .. math::
        \lambda = \omega / \bar{y} \cdot y_{i, y_i \neq 0}

    Where :math:`\lambda` are the new scaling factors, :math:`\omega` are the initial weights and
    :math:`\bar{y}` is the vector of the target function constituents.

    :param targetFuncWeights: initial weights of the target functions constituents
    :param puck: puck values
    :param strainDiff: absolute difference of the strains (top, bot) for each element
    :param optKwargs: list of arguments. See tankoh2.design.winding.optimize.minimizeUtilization for a description
    :return: vector to scale the optimization values
        (used in tankoh2.design.winding.solver._getMaxPuckLocalPuckMass) for the next iteration.
        - scale puckMax
        - scale puck at last critical index
        - scale to sum(puck)
        - scale mass
        - scale max strain diff
        - scale max strain diff at last critical index
        - scale sum strain diff
        - scale windable contour function

    """
    vessel, layerNumberTotal = optKwargs["vessel"], optKwargs["layerNumber"]
    lastTargetFucValues = np.array(getTargetFunctionValues(optKwargs, (puck, strainDiff), False)[:-2])
    lastLayersMass = np.sum(
        [
            vessel.getVesselLayer(layerNumber).getVesselLayerPropertiesSolver().getWindingLayerResults().fiberMass
            for layerNumber in range(layerNumberTotal)
        ]
    )
    meanLayerMass = lastLayersMass / layerNumberTotal
    lastTargetFucValues[3] = meanLayerMass
    lastTargetFucValues[-1] = 1  # 0 gives problems for the windable contour function
    omega = targetFuncWeights
    scaling = [y for weight, y in zip(targetFuncWeights, lastTargetFucValues) if weight > 1e-8][0]
    targetFuncScaling = omega / abs(lastTargetFucValues) * scaling
    return targetFuncScaling


def windAnglesAndShifts(anglesShifts, vessel, compositeArgs):
    layerNumber = len(anglesShifts)
    angles = [a for a, _, _ in anglesShifts]
    composite = getCompositeMuwind(angles, *compositeArgs)
    log.debug(f"Layer {layerNumber}, already wound angles, shiftsside1, shiftsside2: {anglesShifts}")
    vessel.setComposite(composite)
    for layerNumber, (angle, shiftside1, shiftside2) in enumerate(anglesShifts):
        if isHoopLayer(angle):
            vessel.setHoopLayerShift(layerNumber, shiftside1, True)
            vessel.setHoopLayerShift(layerNumber, shiftside2, False)

    try:
        vessel.finishWinding()
    except (IndexError, RuntimeError):
        vessel.saveToFile("backup.vessel")
        log.error(f'Error while "vessel.finishWinding()" with these angles and shifts: \n' + indent(anglesShifts))
        raise
    return composite


def checkThickness(vessel, angle, bounds, symmetricContour):
    """When angle is close to fitting radius, sometimes the thickness of a layer is corrupt

    will be resolved by increasing the angle a little
    """
    thicknesses = getLayerThicknesses(vessel, symmetricContour)
    lastLayThick = thicknesses.loc[:, thicknesses.columns[-1]]
    if lastLayThick[::-1].idxmax() - lastLayThick.idxmax() > lastLayThick.shape[0] * 0.1:
        # adjust bounds
        if (
            not symmetricContour
            and lastLayThick.shape[0] - 1 - lastLayThick[::-1].idxmax() - lastLayThick.idxmax() == 0
        ):
            return True, bounds
        else:
            bounds = [angle + 0.1, bounds[1]]
            return False, bounds
    return True, bounds


def optimizeHelical(polarOpeningRadius, bandWidth, optKwArgs):
    """Optimize the angle of helical layers

    :param polarOpeningRadius: polar opening radius of tank
    :param bandWidth: width of the band
    :param optKwArgs: dict with optimization arguments. See tankoh2.design.winding.optimize.minimizeUtilization
         for a description
    :return:
    """
    log.debug("Optimize helical layer")
    vessel, layerNumber, newLayerPosition = optKwArgs["vessel"], optKwArgs["layerNumber"], optKwArgs["newLayerPosition"]
    anglePullToFitting = optKwArgs["anglePullToFitting"]
    symmetricContour = optKwArgs["symmetricContour"]
    bounds = [optKwArgs["lowerBound"], optKwArgs["upperBound"]]
    angles = getAnglesFromVesselCylinder(vessel)

    # When optimizing the angle for a new layer, move the last fitting layer above the newly added layer
    # This prevents bundles of layers that prevent future fitting layers because of too high bending loads
    if settings.preventHelicalBumps:
        for idx, angle in enumerate(reversed(angles[:newLayerPosition])):
            if angle < anglePullToFitting:
                lastFittingLayer = newLayerPosition - idx - 1
                optKwArgs["newLayerPosition"] = optKwArgs["newLayerPosition"] - 1
                for layer in range(lastFittingLayer, newLayerPosition):
                    windLayer(vessel, layer, angles[layer + 1])
                windLayer(vessel, newLayerPosition, angles[lastFittingLayer])
                if optKwArgs["helicalDesignFactors"]:
                    optKwArgs["helicalDesignFactors"].insert(
                        newLayerPosition - 1, optKwArgs["helicalDesignFactors"].pop(lastFittingLayer)
                    )
                if optKwArgs["thickShellScaling"]:
                    optKwArgs["thickShellScaling"].insert(
                        newLayerPosition - 1, optKwArgs["thickShellScaling"].pop(lastFittingLayer)
                    )
                break
        else:
            lastFittingLayer = newLayerPosition

    ### Move sorted (angle > sortAngle) layers above the newly added layer
    for layer in range(newLayerPosition + 1, layerNumber + 1):
        windLayer(vessel, layer, angles[layer - 1])
    if optKwArgs["helicalDesignFactors"]:
        optKwArgs["helicalDesignFactors"].insert(
            optKwArgs["newLayerPosition"], optKwArgs["helicalDesignFactors"].pop(-1)
        )
    if optKwArgs["thickShellScaling"]:
        optKwArgs["thickShellScaling"].insert(optKwArgs["newLayerPosition"], optKwArgs["thickShellScaling"].pop(-1))

    optKwArgs["anglesForOptimizer"] = getAnglesFromVesselCylinder(vessel)
    # the angle currently in the new layer's position is meaningless and should always be overwritten by something
    optKwArgs["anglesForOptimizer"][optKwArgs["newLayerPosition"]] = 0.0
    optimizationSucceeded = False
    while not optimizationSucceeded:
        angle, optimizedPolarOpeningRadius, funcVal, loopIt, tfPlotVals = minimizeUtilization(
            bounds,
            # getMaxPuckByAngle,
            getWeightedTargetFuncByAngle,
            optKwArgs,
            localOptimization="both",
        )
        if optKwArgs["sortLayersAboveAngle"] + 1 > angle > optKwArgs["sortLayersAboveAngle"] - 1:
            # optimization finished at start of sorted angles, lower the bounds and try again
            bounds = [optKwArgs["lowerBound"], optKwArgs["sortLayersAboveAngle"] - 1]

        elif optKwArgs["skipFEMForBadContour"] and not optKwArgs.get("usedFEMResults", True):
            # optimization didn't use FEM because all angles were unwindable, use FEM always and try again
            optKwArgs["skipFEMForBadContour"] = False
        else:
            optimizationSucceeded = True

    # After optimization, move layers back to the original positions
    if settings.preventHelicalBumps:
        for layer in range(lastFittingLayer, layerNumber):
            windLayer(vessel, layer, angles[layer])
    else:
        for layer in range(newLayerPosition, layerNumber):
            windLayer(vessel, layer, angles[layer])
    # calculate border indices of the new layer
    layerPolarOpeningRadius1 = windLayer(vessel, layerNumber, angle)
    radii1 = vessel.getVesselLayer(layerNumber).getOuterMandrel1().getRArray()
    if symmetricContour:
        newDesignIndexes = [np.argmin(np.abs(radii1 - layerPolarOpeningRadius1))]
    else:
        elemCount1 = len(radii1) - 1
        layerPolarOpeningRadius2 = vessel.getPolarOpeningR(layerNumber, False)
        radii2 = vessel.getVesselLayer(layerNumber).getOuterMandrel2().getRArray()
        newDesignIndexes = [
            elemCount1 - np.argmin(np.abs(radii1 - layerPolarOpeningRadius1)),
            elemCount1 + np.argmin(np.abs(radii2 - layerPolarOpeningRadius2)),
        ]
    log.debug(
        f"angle {angle}, puck value {funcVal}, loopIterations {loopIt}, "
        f"polar opening contour coord index {newDesignIndexes}"
    )

    return angle, optimizedPolarOpeningRadius, funcVal, loopIt, newDesignIndexes, tfPlotVals


def distributeHoop(
    maxHoopShift1,
    maxHoopShift2,
    anglesShifts,
    cylinderLength,
    compositeArgs,
    optArgs,
    hoopShiftRange=None,
    calculatePuck=True,
):
    """Distributes all existing hoop layers with a linear hoop shift

    Every #hoopShiftRange 90 deg layers will be distributed linearly in the interval [-maxHoopShift, maxHoopShift].
    This is an alternative option in contrast to optimizeHoop()

    :param maxHoopShift1: maximum hoop shift allowed for side1
    :param maxHoopShift2: maximum hoop shift allowed for side2
    :param anglesShifts: Existing angles and hoop shifts
    :param cylinderLength: length of the cylindrical section of the vessel
    :param compositeArgs: composite properties as required by tankoh2.design.winding.material.getComposite()
    :param optArgs: args to the optimizer callback function.
    :param hoopShiftRange: How many hoop layers to spread between the minimum and maximum hoop Shift, after which the pattern repeats. If None, spread all hoop layers between max and min
    :param calculatePuck: Flag whether to calculate and return Puck values
    :return: tuple:

     - hoop shift side 1,
     - hoop shift side 2,
     - funcVal,
     - loopIt,
     - newDesignIndexes,
     - tfPlotVals
    """
    hoopLayerCount = len([angle for angle, s1, s2 in anglesShifts if angle > 89])
    maxBoundside1 = np.min(
        [maxHoopShift1, settings.maxHoopShiftMuWind]
    )  # 250 is the maximum defined in µWind at the moment
    minHoopShift1 = -maxBoundside1 * settings.hoopShiftBalance
    bandWidthHoop = compositeArgs[4] * compositeArgs[7]
    minHoopShiftMuwind = -cylinderLength / 2 + 1.5 * bandWidthHoop
    minBoundside1 = np.max([minHoopShift1, minHoopShiftMuwind])
    vessel = optArgs["vessel"]
    hoopShiftsside1 = []
    if vessel.isSymmetric():
        if hoopShiftRange:
            existingRanges = hoopLayerCount // hoopShiftRange
            hoopShiftRangeMaxOffset = int(np.floor(hoopShiftRange * settings.hoopShiftMaxStagger))
            minBoundside1 = minBoundside1 - hoopShiftRangeMaxOffset / (hoopShiftRange - 1) * (
                maxBoundside1 - minBoundside1
            )
            linspaceValues = np.linspace(maxBoundside1, minBoundside1, hoopShiftRange + hoopShiftRangeMaxOffset)
            i = 0
            for hoopShiftRangeNumber in range(existingRanges + 1):
                thisRangeValues = linspaceValues[i : hoopShiftRange + i]
                i = (i + 1) % (hoopShiftRangeMaxOffset + 1)
                hoopShiftsside1.extend(thisRangeValues)
            hoopShiftsside1 = hoopShiftsside1[: hoopLayerCount + 1]
            windAnglesAndShifts(anglesShifts + [(90, hoopShiftsside1[-1], hoopShiftsside1[-1])], vessel, compositeArgs)
        else:
            if hoopLayerCount == 0:
                hoopShiftsside1 = [np.mean([minBoundside1, maxBoundside1])]
            else:
                hoopShiftsside1 = np.linspace(maxBoundside1, minBoundside1, hoopLayerCount + 1, endpoint=False)

            hoopShiftsIterside1 = iter(hoopShiftsside1)
            for (angle, _, _), index in zip(anglesShifts, range(len(anglesShifts))):
                if angle > 89:
                    hoopshift = next(hoopShiftsIterside1)
                    anglesShifts[index] = (angle, hoopshift, hoopshift)
            nextHoopIter = next(hoopShiftsIterside1)
            windAnglesAndShifts(anglesShifts + [(90, nextHoopIter, nextHoopIter)], vessel, compositeArgs)
        hoopShiftsside2 = hoopShiftsside1
    else:
        hoopShiftsside2 = []
        maxBoundside2 = np.min(
            [maxHoopShift2, settings.maxHoopShiftMuWind]
        )  # 250 is the maximum defined in µWind at the moment
        minHoopShift2 = -maxBoundside2 * settings.hoopShiftBalance
        minBoundside2 = np.max([minHoopShift2, minHoopShiftMuwind])

        if hoopShiftRange:
            existingRanges = hoopLayerCount // hoopShiftRange
            hoopShiftRangeMaxOffset = int(np.floor(hoopShiftRange * settings.hoopShiftMaxStagger))
            minBoundside1 = minBoundside1 - hoopShiftRangeMaxOffset / (hoopShiftRange - 1) * (
                maxBoundside1 - minBoundside1
            )
            minBoundside2 = minBoundside2 - hoopShiftRangeMaxOffset / (hoopShiftRange - 1) * (
                maxBoundside2 - minBoundside2
            )

            for hoopShifts, maxBound, minBound in [
                [hoopShiftsside1, maxBoundside1, minBoundside1],
                [hoopShiftsside2, maxBoundside2, minBoundside2],
            ]:
                linspaceValues = np.linspace(maxBound, minBound, hoopShiftRange + hoopShiftRangeMaxOffset)
                i = 0
                for hoopShiftRangeNumber in range(existingRanges + 1):
                    thisRangeValues = linspaceValues[i : hoopShiftRange + i]
                    i = (i + 1) % (hoopShiftRangeMaxOffset + 1)
                    hoopShifts.extend(thisRangeValues)
                del hoopShifts[hoopLayerCount + 1 :]
            windAnglesAndShifts(anglesShifts + [(90, hoopShiftsside1[-1], hoopShiftsside2[-1])], vessel, compositeArgs)

        else:
            if hoopLayerCount == 0:
                hoopShiftsside1 = [np.mean([minBoundside1, maxBoundside1])]
                hoopShiftsside2 = [np.mean([minBoundside2, maxBoundside2])]
            else:
                hoopShiftsside1 = np.linspace(maxBoundside1, minBoundside1, hoopLayerCount + 1, endpoint=False)
                hoopShiftsside2 = np.linspace(maxBoundside2, minBoundside2, hoopLayerCount + 1, endpoint=False)

            hoopShiftsIterside1 = iter(hoopShiftsside1)
            hoopShiftsIterside2 = iter(hoopShiftsside2)
            for (angle, _, _), index in zip(anglesShifts, range(len(anglesShifts))):
                if isHoopLayer(angle):
                    anglesShifts[index] = (angle, next(hoopShiftsIterside1), next(hoopShiftsIterside2))
            windAnglesAndShifts(
                anglesShifts + [(90, next(hoopShiftsIterside1), next(hoopShiftsIterside2))], vessel, compositeArgs
            )
    addedAngleShift = [(90, hoopShiftsside1[-1], hoopShiftsside2[-1])]
    checkAnglesAndShifts(anglesShifts + addedAngleShift, vessel)
    if calculatePuck:
        results = getMaxPuckLocalPuckMassIndexByShift(hoopShiftsside1[-1], hoopShiftsside2[-1], optArgs)
        tfValue = np.sum(results[:-2])
    else:
        tfValue = None
    return hoopShiftsside1[-1], hoopShiftsside2[-1], tfValue, 1, [], None


def optimizeHoopDistribution(
    maxHoopShift1, maxHoopShift2, anglesShifts, optArgs, hoopShiftRange, x0Mandrel1=None, x0Mandrel2=None
):
    """Distributes all existing hoop layers with a linear hoop shift, optimizes start and length of hoop distribution

    Every #hoopShiftRange 90 deg layers will be distributed linearly, with the start and length of the pattern being optimized

    :param maxHoopShift1: maximum hoop shift allowed for side1
    :param maxHoopShift2: maximum hoop shift allowed for side2
    :param anglesShifts: Existing angles and hoop shifts
    :param optArgs: args to the optimizer function.
    :param hoopShiftRange: How many hoop layers to spread between the minimum and maximum hoop Shift, after which the pattern repeats. If None, spread all hoop layers between max and min
    :param x0Mandrel1: initial x value to give to the genetic optimizer
    :param x0Mandrel2: initial x value to give to the genetic optimizer
    :return: tuple:

        - hoop shift side 1,
        - hoop shift side 2,
        - funcVal,
        - loopIt,
        - newDesignIndexes,
        - tfPlotVals
    """

    def targetFunction(hoopShiftParameters, *args):
        (isMandrel1,) = args
        vessel.resetWindingSimulation()
        hoopShiftIterator = createHoopShiftsFromParameters(
            hoopShiftParameters[0],
            hoopShiftParameters[1],
            hoopShiftParameters[2],
            hoopShiftRange,
            numberOfHoopShiftRanges,
        )
        for index, angle in enumerate(angles):
            if isHoopLayer(angle):
                shift = next(hoopShiftIterator)
                if isMandrel1:
                    vessel.setHoopLayerShift(index, shift, True)
                else:
                    vessel.setHoopLayerShift(index, shift, False)
                    # Don't change shift1
        try:
            vessel.finishWinding()
        except (IndexError, RuntimeError):
            vessel.saveToFile("backup.vessel")
            raise
        result = sum(getTargetFunctionValues(optArgs)[:-2])
        return result

    vessel = optArgs["vessel"]
    symmetricContour = optArgs["symmetricContour"]
    useIndices = optArgs["useIndices"].copy()
    helicalDesignFactorIndexes = optArgs["helicalDesignFactorIndexes"].copy()
    log.info("Optimizing Hoop Shifts")
    angles = getAnglesFromVesselCylinder(vessel)
    hoopLayerCount = sum(1 for angle in angles if isHoopLayer(angle))
    maxBoundSide1 = np.min([maxHoopShift1, settings.maxHoopShiftMuWind])
    if hoopShiftRange > 0:
        numberOfHoopShiftRanges = -(-hoopLayerCount // hoopShiftRange)
    else:
        numberOfHoopShiftRanges = 1
        hoopShiftRange = hoopLayerCount

    # Optimize Hoop Shifts side 1
    if not symmetricContour:
        optArgs["useIndices"] = [index for index in useIndices if index < vessel.getLiner().getMandrel1().numberOfNodes]
        optArgs["helicalDesignFactorIndexes"] = [
            index for index in helicalDesignFactorIndexes if index < vessel.getLiner().getMandrel1().numberOfNodes
        ]
    # 3 Variables are: max Hoop Shift of 1st Range, max Hoop Shift for Last Range (they are spread evenly in between), and Length of Ranges
    if numberOfHoopShiftRanges > 1:
        bounds = [(0, maxBoundSide1), (0, maxBoundSide1), (0, 3 * maxBoundSide1)]
    else:
        bounds = [(0, maxBoundSide1), (0, 0), (0, 3 * maxBoundSide1)]
    resultMandrel1 = differential_evolution(
        targetFunction,
        x0=x0Mandrel1,
        bounds=bounds,
        args=(True,),
        atol=settings.optimizerAtol,
        seed=settings.optimizerSeed,
        popsize=settings.optimizerPopsize,
        polish=False,
    )
    xMandrel1 = resultMandrel1.x
    finalTargetFunctionValue = resultMandrel1.fun

    # Optimize Hoop Shifts side 2 if not symmetric
    if not symmetricContour:
        optArgs["useIndices"] = [index for index in useIndices if index > vessel.getLiner().getMandrel1().numberOfNodes]
        optArgs["helicalDesignFactorIndexes"] = [
            index for index in helicalDesignFactorIndexes if index > vessel.getLiner().getMandrel1().numberOfNodes
        ]
        maxBoundSide2 = np.min([maxHoopShift2, settings.maxHoopShiftMuWind])
        if numberOfHoopShiftRanges > 1:
            bounds = [(0, maxBoundSide2), (0, maxBoundSide2), (0, 3 * maxBoundSide2)]
        else:
            bounds = [(0, maxBoundSide2), (0, 0), (0, 3 * maxBoundSide2)]
        resultMandrel2 = differential_evolution(
            targetFunction,
            x0=x0Mandrel2,
            bounds=bounds,
            args=(False,),
            atol=settings.optimizerAtol,
            seed=settings.optimizerSeed,
            popsize=settings.optimizerPopsize,
            polish=False,
        )
        xMandrel2 = resultMandrel2.x
        finalTargetFunctionValue = np.max([finalTargetFunctionValue, resultMandrel2.fun])
    else:
        xMandrel2 = None

    resultAnglesShifts = applyHoopShiftParameters(
        anglesShifts, hoopShiftRange, numberOfHoopShiftRanges, xMandrel1, xMandrel2
    )
    log.info("Optimized Hoop Shifts")
    return resultAnglesShifts, finalTargetFunctionValue, xMandrel1, xMandrel2


def _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd):
    """calculate borders and element regions for optimization

    :param vessel: µWind vessel instance
    :param symmetricContour: Flag if the contour is symmetric
    :param relRadiusHoopLayerEnd: relative radius (to cyl radius) where hoop layers end
    :return:
        - hoopStart: index where the hoop region starts (0 if symm contour, on mandrel1 of unsymm contour)
        - hoopEnd: index where the hoop region ends (mandrel1 if symm contour, on mandrel2 of unsymm contour)
        - maxHoopShift 1: maximal length of hoop shifts into dome section for side 1
        - maxHoopShift 2: maximal length of hoop shifts into dome section for side 2
        - useHoopIndices: list of element indicies that will be evaluated (stress, puck) in the hoop region
        - useHelicalIndices: list of element indicies that will be evaluated (stress, puck) in the dome region
    """
    liner = vessel.getLiner()
    mandrel1 = liner.getMandrel1()
    if symmetricContour:
        mandrels = [mandrel1]
    else:
        mandrels = [liner.getMandrel2() if not symmetricContour else None, mandrel1]
    startOfDropOffMandrel1, startOfDropOffMandrel2 = getStartOfHoopDropOff(vessel, symmetricContour)
    useHoopIndices, useHelicalIndices, useHelicalAndShoulderIndices = (
        np.array([], dtype=int),
        np.array([], dtype=int),
        np.array([], dtype=int),
    )
    maxHoopShifts = []
    for mandrel in mandrels:
        r = mandrel.getRArray()
        rCyl = r[0]
        mandrelElementCount = mandrel.numberOfNodes - 1
        hoopHelicalBorderIndex = np.argmin(np.abs(r - rCyl * relRadiusHoopLayerEnd))
        maxHoopShifts.append(mandrel.getLArray()[hoopHelicalBorderIndex] - liner.cylinderLength / 2)
        hoopIndexStart = 1
        hoopIndices = np.linspace(
            hoopIndexStart, hoopHelicalBorderIndex, hoopHelicalBorderIndex - hoopIndexStart + 1, dtype=int
        )
        if mandrel is mandrel1:
            hoopIndices = np.append([0], hoopIndices)
        helicalIndices = np.linspace(
            hoopHelicalBorderIndex, mandrelElementCount - 1, mandrelElementCount - hoopHelicalBorderIndex, dtype=int
        )
        if mandrel is mandrel1:
            helicalAndShoulderIndices = np.linspace(
                startOfDropOffMandrel1, mandrelElementCount - 1, mandrelElementCount - startOfDropOffMandrel1, dtype=int
            )
        else:
            helicalAndShoulderIndices = np.linspace(
                startOfDropOffMandrel2, mandrelElementCount - 1, mandrelElementCount - startOfDropOffMandrel2, dtype=int
            )
        if not symmetricContour and mandrel is mandrel1:
            # shift existing indices and include by mandrel 1 indices
            useHoopIndices += mandrelElementCount
            useHelicalIndices += mandrelElementCount
            useHelicalAndShoulderIndices += mandrelElementCount
            # twist indices
            hoopIndices = mandrelElementCount - hoopIndices[::-1]
            helicalIndices = mandrelElementCount - helicalIndices[::-1]
            helicalAndShoulderIndices = mandrelElementCount - helicalAndShoulderIndices[::-1]

        useHoopIndices = np.append(hoopIndices, useHoopIndices)
        useHelicalIndices = np.append(helicalIndices, useHelicalIndices)
        useHelicalAndShoulderIndices = np.append(helicalAndShoulderIndices, useHelicalAndShoulderIndices)

    hoopBounds = [np.min(useHoopIndices), np.max(useHoopIndices)]
    maxHoopShift1 = np.min(maxHoopShifts[-1])  # position 2 for unsymmetrical tank and position 1 for symmetrical
    if symmetricContour:
        maxHoopShift2 = maxHoopShift1
    else:
        maxHoopShift2 = np.min(maxHoopShifts[0])  # since it is at position 0 in mandrels and thus in maxHoopshifts

    return *hoopBounds, maxHoopShift1, maxHoopShift2, useHoopIndices, useHelicalIndices, useHelicalAndShoulderIndices


def designLayers(
    vessel,
    maxLayers,
    polarOpeningRadius,
    bandWidth,
    materialMuWind,
    burstPressure,
    pMinOperation,
    pMaxOperation,
    helicalDesignFactor,
    symmetricContour,
    runDir,
    compositeArgs,
    verbosePlot,
    useFibreFailure,
    relRadiusHoopLayerEnd,
    initialAnglesAndShifts,
    targetFuncWeights,
    materialName,
    sortLayers,
    sortLayersAboveAngle,
    hoopShiftRange,
    hoopLayerCluster,
    doHoopShiftOptimization,
    findValidWindingAngles,
    operationalCycles,
    zeroPressureCycles,
    simulatedTankLives,
    testPressureAfterFatigue,
    deltaT,
):
    """Perform design optimization layer by layer

    :param vessel: vessel instance of mywind
    :param maxLayers: maximum numbers of layers
    :param polarOpeningRadius: min polar opening where fitting is attached [mm]
    :param bandWidth: width of the band
    :param materialMuWind: material instance of mywind
    :param burstPressure: burst pressure [MPa]
    :param pMinOperation: minimal operational pressure [MPa]
    :param pMaxOperation: maximal operational pressure [MPa]
    :param helicalDesignFactor: additional design factor applied to helical layers in the dome region
    :param symmetricContour: Flag if the contour is symmetric
    :param runDir: directory where to store results
    :param compositeArgs: properties defining the composite:
        hoopLayerThickness, layerThkHelical, material, sectionAreaFibre, rovingWidthHoop, rovingWidthHelical,
        numberOfRovings, tex, designFilename, tankname
    :param verbosePlot: flag if more plots should be created
    :param useFibreFailure: flag, use fibre failure or inter fibre failure
    :param relRadiusHoopLayerEnd: relative radius (to cyl radius) where hoop layers end
    :param initialAnglesAndShifts: List with 3-tuples defining angles shift side 1 and
        shift side 2 (only relevant for asymmetric tanks) used before optimization starts
    :param targetFuncWeights: initial weights of the target functions constituents
    :param materialName: name of material json-file
    :param sortLayers: flag to sort helical layers by rising angle after each layer added
    :param sortLayersAboveAngle: Angle above which layers should be sorted and moved to the outside, when sortLayers is set to True.
    :param hoopShiftRange: number of hoop layers which are spread out between the maximum and minimum hoop Shift. After this number of layers, the pattern is repeated.
    :param hoopLayerCluster: number of hoop layers which are clustered together
    :param doHoopShiftOptimization: optimize the linear hoop shift distributions of the hoop layer patterns when trying to remove layers
    :param findValidWindingAngles: after optimization, choose winding angles that result in valid winding patterns
    :param operationalCycles: number of cycles from pMinOperation to pMaxOperation and back
    :param zeroPressureCycles: number of cycles from zero pressure to pMaxOperation and back
    :param simulatedTankLives: Number of simulated lifes (scatter)
    :param testPressureAfterFatigue: test Pressure to survive after the cycles have been reached [MPa]
    :param deltaT: temperature difference from initial conditions to operating condition

    :return: frpMass, volume, area, composite, iterations, anglesShifts

    Strategy:

    #. Start with helical layer:
        #. Maximize layer angle that still attaches to the fitting
        #. add layer with this angle

    #. If puck FF is used, add hoop layer
    #. Iteratively perform the following
        #. Get puck fibre failures
        #. Check if puck reserve factors are satisfied - if yes end iteration
        #. Reduce relevant locations to
            #. 1 element at cylindrical section and
            #. every element between polar opening radii of 0 and of 70° angle layers

        #. identify critical element
        #. if critical element is in cylindrical section
            #. add hoop layer
            #. next iteration step

        #. if most loaded element is in dome area:
            #. Define Optimization bounds [minAngle, 70°] and puck result bounds

        #. Minimize puck fibre failure:
            #. Set angle
            #. Use analytical linear solver
            #. return max puck fibre failure

        #. Apply optimal angle to actual layer
        #. next iteration step

    #. postprocessing: plot stresses, strains, puck, thickness

    """

    def getPuckAndStrainDiff():
        puck, strainDiff = getPuckStrainDiff(
            vessel,
            materialMuWind,
            burstPressure,
            symmetricContour=symmetricContour,
            useFibreFailure=useFibreFailure,
            useMeridianStrain=True,
            deltaT=deltaT,
        )

        if settings.useThickShellScaling:
            thickShellScaling = getThickShellScaling(vessel, burstPressure, composite)
            puck = puck.multiply(thickShellScaling, "columns")
        else:
            thickShellScaling = None
        if helicalDesignFactor > 1 + 1e-6:
            helicalDesignFactors = getHelicalDesignFactors(vessel, helicalDesignFactor)
            puck.iloc[useHelicalAndShoulderIndices] = puck.iloc[useHelicalAndShoulderIndices].multiply(
                helicalDesignFactors, "columns"
            )
        else:
            helicalDesignFactors = None
        for column in range(puck.shape[1]):
            puck.iloc[np.nonzero(puck.iloc[:, column])[0][-1], column] = 0
        return puck, strainDiff, thickShellScaling, helicalDesignFactors

    vessel.resetWindingSimulation()

    show = False
    save = True
    layerNumber = 0
    iterations = 0
    fatigueDamageLevel = 0
    frpMassStrengthOnly = None
    frpMassFatigueOnly = None
    if targetFuncWeights[-1] == 1:
        skipFEMForBadContour = True
    else:
        skipFEMForBadContour = False
    anglesShiftsFilename = os.path.join(runDir, "anglesAndShifts" + ".yaml")

    liner = vessel.getLiner()
    cylinderLength = liner.cylinderLength
    indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
    (
        hoopStart,
        hoopEnd,
        maxHoopShift1,
        maxHoopShift2,
        useHoopIndices,
        useHelicalIndices,
        useHelicalAndShoulderIndices,
    ) = indiciesAndShifts
    anglePullToFitting = calculateMinAngle(vessel, polarOpeningRadius, layerNumber, bandWidth * 2)
    sortLayersAboveAngle = max(sortLayersAboveAngle, anglePullToFitting)
    angleForContourSmoothingBorders = sortLayersAboveAngle if sortLayers else settings.maxHelicalAngle
    x, r = liner.getMandrel1().getXArray(), liner.getMandrel1().getRArray()
    if not symmetricContour:
        x, r = flipContour(x, r)
        x = np.append(x, liner.getMandrel2().getXArray()[1:] + np.max(x))
        r = np.append(r, liner.getMandrel2().getRArray()[1:])
        middleNode = liner.getMandrel1().numberOfNodes
    else:
        middleNode = 0
    plotContour(
        False, os.path.join(runDir, f"contour.png"), x, r, vlines=[hoopStart, hoopEnd], vlineColors=["black", "black"]
    )
    log.debug("Find minimal possible angle")

    if initialAnglesAndShifts is not None and len(initialAnglesAndShifts) > 0:
        # wind given angles
        composite = windAnglesAndShifts(initialAnglesAndShifts, vessel, compositeArgs)
        anglesShifts = initialAnglesAndShifts
        checkAnglesAndShifts(anglesShifts, vessel)
        layerNumber = len(anglesShifts) - 1
    else:
        # introduce layer up to the fitting. Optimize required angle
        windLayer(vessel, layerNumber, 90)
        minAngle = calculateMinAngle(vessel, polarOpeningRadius, layerNumber, bandWidth)
        printLayer(layerNumber, "- initial helical layer")
        windLayer(vessel, layerNumber, minAngle)
        anglesShifts = [(minAngle, 0, 0)]
        composite = windAnglesAndShifts(anglesShifts, vessel, compositeArgs)
        checkAnglesAndShifts(anglesShifts, vessel)
    vessel.saveToFile(os.path.join(runDir, "backup.vessel"))  # save vessel
    hoopLayerCount = sum(1 for angle, _, _ in anglesShifts if isHoopLayer(angle))
    # create other layers
    for layerNumber in range(layerNumber + 1, maxLayers):
        if sortLayers:
            moveHighAnglesOutwards(anglesShifts, sortLayersAboveAngle)
        if hoopLayerCluster > 1:
            clusterHoopLayers(
                anglesShifts,
                hoopLayerCluster,
                sortLayersAboveAngle,
                settings.putHoopLayersOnLiner,
                settings.putHoopLayersOnTop,
            )
        if sortLayers or hoopLayerCluster > 1:
            newLayerPosition = getStartOfSortedLayers(anglesShifts, sortLayersAboveAngle)
        else:
            newLayerPosition = layerNumber
        if settings.preventHelicalBumps:
            moveLastFittingLayerToStartOfSorted(anglesShifts, newLayerPosition, anglePullToFitting)
        composite = windAnglesAndShifts(anglesShifts, vessel, compositeArgs)
        # Find Windable Angles for existing layers
        if findValidWindingAngles:
            log.info("Finding closest valid winding angles")
            if targetFuncWeights[-1]:  # if using enforceWindableContour
                contourSmoothingBorders = getPolarOpeningNodesForAngle(
                    vessel, layerNumber - 1, angleForContourSmoothingBorders
                )
            else:
                contourSmoothingBorders = None
            for loopLayerNumber, (angle, shift1, shift2) in enumerate(anglesShifts):
                if not isHoopLayer(angle):
                    newAngle = findValidWindingAngle(
                        vessel,
                        loopLayerNumber,
                        angle,
                        polarOpeningRadius,
                        contourSmoothingBorders,
                        settings.useMoreCycles,
                    )
                    anglesShifts[loopLayerNumber] = (newAngle, shift1, shift2)
                    windLayer(vessel, loopLayerNumber, newAngle)

        # output angles and shifts after sort / reorder / valid angle search
        vessel.saveToFile(os.path.join(runDir, f"backup.vessel"))  # save vessel
        anglesShiftsOutput = [[round(float(y), 3) for y in list(x)] for x in zip(*anglesShifts)]
        writeParametersToYAML({"initialAnglesAndShifts": anglesShiftsOutput}, anglesShiftsFilename)

        composite = windAnglesAndShifts(anglesShifts, vessel, compositeArgs)
        indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
        (
            hoopStart,
            hoopEnd,
            maxHoopShift1,
            maxHoopShift2,
            useHoopIndices,
            useHelicalIndices,
            useHelicalAndShoulderIndices,
        ) = indiciesAndShifts
        puck, strainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()

        elemIdxPuckMax, layermax = getMostCriticalElementIdxPuck(puck)
        elemIdxBendMax = np.argmax(strainDiff)
        puckMax = puck.max().max()
        if operationalCycles > 0:
            fatigueDamageLevel = getFatigueLifeFRPTankLevel(
                materialName,
                pMaxOperation,
                pMinOperation,
                operationalCycles,
                zeroPressureCycles,
                simulatedTankLives,
                vessel,
                symmetricContour,
                useFibreFailure,
                thickShellScaling,
                testPressureAfterFatigue,
            )
            log.info(f"max fatigue damage Level: {fatigueDamageLevel}, puck max: {puckMax}")
            if puckMax < 1 and frpMassStrengthOnly is None:
                stats = vessel.calculateVesselStatistics()
                frpMassStrengthOnly = stats.overallFRPMass  # in [kg]
            if fatigueDamageLevel < 1 and frpMassFatigueOnly is None:
                stats = vessel.calculateVesselStatistics()
                frpMassFatigueOnly = stats.overallFRPMass  # in [kg]

        if puckMax < 1 and fatigueDamageLevel < 1 and layerNumber > 1:
            # stop criterion reached
            log.info(f"final max fatigue damage Level: {fatigueDamageLevel}, puck max: {puckMax}")
            log.debug("End Iteration")
            # stop criterion reached
            plotPuckAndTargetFunc(
                puck,
                anglesShifts,
                layerNumber,
                runDir,
                useFibreFailure,
                show,
                False,
            )
            layerNumber -= 1
            break

        if settings.reduceCylinder:
            reducedCylinderLength = getReducedCylinderLength(
                cylinderLength,
                symmetricContour,
                puck.max(1),
                x,
                middleNode,
                maxHoopShift1,
                maxHoopShift2,
            )
            if reducedCylinderLength < vessel.getLiner().cylinderLength:
                setReducedCylinder(
                    vessel, composite, reducedCylinderLength, symmetricContour, bandWidth, settings.nodesPerBand
                )
                indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
                (
                    hoopStart,
                    hoopEnd,
                    maxHoopShift1,
                    maxHoopShift2,
                    useHoopIndices,
                    useHelicalIndices,
                    useHelicalAndShoulderIndices,
                ) = indiciesAndShifts
                puck, strainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
                elemIdxPuckMax, layermax = getMostCriticalElementIdxPuck(puck)
                elemIdxBendMax = np.argmax(strainDiff)
                usingReducedCylinder = True
            else:
                usingReducedCylinder = False

        else:
            usingReducedCylinder = False

        # add one layer
        printLayer(layerNumber)
        log.info(f"Current puck max: {puckMax}")
        log.debug(f"Layer {layerNumber}, already wound angles, shifts: {anglesShifts}")
        if usingReducedCylinder:
            log.debug(f"Using Reduced cylinder length {reducedCylinderLength} for Optimization.")
        windAnglesAndShifts(anglesShifts + [(90, 0.0, 0.0)], vessel, compositeArgs)

        add90DegLay = layerNumber == 1 and useFibreFailure
        maxInHoopRegion = hoopStart <= elemIdxPuckMax <= hoopEnd
        if add90DegLay:
            optHoopRegion = True  # this layer should be a hoop layer
        elif useFibreFailure:
            # check if max puck value occurred in hoop or helical layer
            if isHoopLayer(anglesShifts[layermax][0]):
                # check for stress spike at the cylinder border
                if not symmetricContour:
                    middleOfCylinder = vessel.getLiner().getMandrel1().numberOfNodes
                else:
                    middleOfCylinder = 0
                if puck.iloc[middleOfCylinder, layermax] > 0.9 * puck.iloc[elemIdxPuckMax, layermax]:
                    optHoopRegion = True
                    add90DegLay = True
                else:
                    optHoopRegion = True
                    add90DegLay = False
            else:
                optHoopRegion = maxInHoopRegion
                log.info(f"{hoopStart} <= {elemIdxPuckMax} <= {hoopEnd}")
        else:
            optHoopRegion = maxInHoopRegion
            log.info(f"{hoopStart} <= {elemIdxPuckMax} <= {hoopEnd}")

        minAngle = calculateMinAngle(vessel, polarOpeningRadius, layerNumber, bandWidth)
        anglePullToFitting = calculateMinAngle(vessel, polarOpeningRadius, layerNumber, 2 * bandWidth)
        angleForContourSmoothingBorders = sortLayersAboveAngle if sortLayers else settings.maxHelicalAngle
        contourSmoothingBorders = getPolarOpeningNodesForAngle(vessel, layerNumber, angleForContourSmoothingBorders)
        useIndices = useHelicalAndShoulderIndices if useFibreFailure else useHelicalIndices
        windLayer(vessel, layerNumber, minAngle)
        if targetFuncWeights[-1] > 0:
            currentWindability = calculateWindability(
                vessel, layerNumber, settings.maxThicknessDerivative, None, contourSmoothingBorders
            )
            if currentWindability > 1:
                windabilityGoal = 0
            else:
                windabilityGoal = settings.maxThicknessDerivative
        else:
            windabilityGoal = settings.maxThicknessDerivative
        optKwargs = OrderedDict(
            [
                ("vessel", vessel),
                ("layerNumber", layerNumber),
                ("materialMuWind", materialMuWind),
                ("burstPressure", burstPressure),
                ("useIndices", useIndices),
                ("useFibreFailure", useFibreFailure),
                ("verbosePlot", verbosePlot),
                ("symmetricContour", symmetricContour),
                ("elemIdxPuckMax", elemIdxPuckMax),
                ("elemIdxBendMax", elemIdxBendMax),
                ("targetFuncScaling", None),
                ("thickShellScaling", thickShellScaling),
                ("helicalDesignFactors", helicalDesignFactors),
                ("helicalDesignFactorIndexes", useHelicalAndShoulderIndices),
                ("contourSmoothingBorders", contourSmoothingBorders),
                ("sortLayersAboveAngle", sortLayersAboveAngle if sortLayers else 90),
                ("windabilityGoal", windabilityGoal),
                ("newLayerPosition", newLayerPosition),
                ("anglePullToFitting", anglePullToFitting),
                ("upperBound", settings.maxHelicalAngle),
                ("lowerBound", minAngle),
                ("deltaT", deltaT),
                ("skipFEMForBadContour", skipFEMForBadContour),
            ]
        )
        targetFuncScaling = getOptScalingFactors(targetFuncWeights, puck, strainDiff, optKwargs)
        optKwargs["targetFuncScaling"] = targetFuncScaling

        if optHoopRegion:
            if useFibreFailure:
                optKwargs["useIndices"] = useHelicalAndShoulderIndices
            else:
                optKwargs["useIndices"] = useHoopIndices
            if helicalDesignFactors:
                optKwargs["helicalDesignFactors"] = helicalDesignFactors + [1.0]
            if thickShellScaling:
                optKwargs["thickShellScaling"] = thickShellScaling + [min(thickShellScaling)]
            resHoop = distributeHoop(
                maxHoopShift1,
                maxHoopShift2,
                anglesShifts,
                cylinderLength,
                compositeArgs,
                optKwargs,
                hoopShiftRange=hoopShiftRange,
            )
            if not add90DegLay:
                if helicalDesignFactors:
                    optKwargs["helicalDesignFactors"] = helicalDesignFactors + [helicalDesignFactor]
                if thickShellScaling:
                    optKwargs["thickShellScaling"] = thickShellScaling + [1.0]
                resHelical = optimizeHelical(polarOpeningRadius, bandWidth, optKwargs)
                log.info(
                    f"Max Puck in hoop region. Min targetFuc hoop {resHoop[2]}, "
                    f"min targetFuc helical {resHelical[2]}"
                )
                add90DegLay = resHoop[2] < resHelical[2]
            if add90DegLay:
                # add hoop layer
                shiftside1 = resHoop[0]
                shiftside2 = resHoop[1]
                if symmetricContour:
                    windHoopLayer(vessel, layerNumber, shiftside1)  # must be run since optimizeHelical ran last time
                    anglesShifts.append((90, shiftside1, shiftside1))
                else:
                    windHoopLayer(
                        vessel, layerNumber, shiftside1, shiftside2
                    )  # must be run since optimizeHelical ran last time
                    anglesShifts.append((90, shiftside1, shiftside2))
                checkAnglesAndShifts(anglesShifts, vessel)
                optResult = resHoop
                log.info(f"Added Hoop Layer")
                hoopLayerCount = hoopLayerCount + 1

            else:
                # add helical layer
                optResult = resHelical
                angle = optResult[0]
                if settings.pullLowHelicalsToFitting and angle < anglePullToFitting:
                    log.info(f"Angle {angle} in fitting Zone. Pulling to Fitting")
                    angle = minAngle
                windLayer(vessel, layerNumber, angle)
                anglesShifts.append((angle, 0, 0))
                checkAnglesAndShifts(anglesShifts, vessel)
                log.info(f"Added Helical Layer with Angle {angle}")
        else:
            if maxInHoopRegion:
                # case FF: if an helical angle in the hoop region has the maximum, check at hoop indices
                optKwargs["useIndices"] = None
            if helicalDesignFactors:
                optKwargs["helicalDesignFactors"] = helicalDesignFactors + [helicalDesignFactor]
            if thickShellScaling:
                optKwargs["thickShellScaling"] = thickShellScaling + [1.0]
            optResult = optimizeHelical(polarOpeningRadius, bandWidth, optKwargs)
            angle = optResult[0]
            if settings.pullLowHelicalsToFitting and angle < anglePullToFitting:
                log.info(f"Angle {angle} in fitting Zone. Pulling to Fitting")
                angle = minAngle
            windLayer(vessel, layerNumber, angle)
            anglesShifts.append((angle, 0, 0))
            checkAnglesAndShifts(anglesShifts, vessel)
            log.info(f"Added Helical Layer with Angle {angle}")
        composite = windAnglesAndShifts(anglesShifts, vessel, compositeArgs)
        _, _, _, loopIt, newDesignIndexes, tfValues = optResult
        iterations += loopIt
        plotPuckAndTargetFunc(
            puck,
            anglesShifts[:-1],
            layerNumber,
            runDir,
            useFibreFailure,
            show,
            verbosePlot,
            tfValues,
            anglesShifts[-1],
            elemIdxPuckMax,
            hoopStart,
            hoopEnd,
            newDesignIndexes,
            (targetFuncWeights, targetFuncScaling),
        )

        if usingReducedCylinder:  # reset to full cylinder
            vessel.setLiner(liner)
            vessel.setComposite(composite)
            vessel.finishWinding()
            indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
            (
                hoopStart,
                hoopEnd,
                maxHoopShift1,
                maxHoopShift2,
                useHoopIndices,
                useHelicalIndices,
                useHelicalAndShoulderIndices,
            ) = indiciesAndShifts

        vessel.saveToFile(os.path.join(runDir, f"backup.vessel"))  # save vessel
        if verbosePlot:
            vessel.saveToFile(os.path.join(runDir, "plots", f"backup{layerNumber}.vessel"))  # save vessel

        # output angles and shifts after each layer
        anglesShiftsOutput = [[round(float(y), 3) for y in list(x)] for x in zip(*anglesShifts)]
        writeParametersToYAML({"initialAnglesAndShifts": anglesShiftsOutput}, anglesShiftsFilename)

    else:
        indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
        (
            hoopStart,
            hoopEnd,
            maxHoopShift1,
            maxHoopShift2,
            useHoopIndices,
            useHelicalIndices,
            useHelicalAndShoulderIndices,
        ) = indiciesAndShifts
        puck, strainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
        puckMax = puck.max().max()
        plotPuckAndTargetFunc(
            puck,
            anglesShifts,
            layerNumber + 1,
            runDir,
            useFibreFailure,
            show,
            False,
        )
        log.warning(
            f"Reached max layers ({maxLayers}) but puck values are "
            f'still greater 1 ({puck.max().max()}). You need to specify more layers in "maxLayers" '
            f'or adjust the optimization weights in "targetFuncWeights".'
        )

    obsoleteLayers = settings.removeObsoleteLayers and puckMax < 1
    layersDeleted = 0

    if settings.reduceCylinder and obsoleteLayers:
        reducedCylinderLength = getReducedCylinderLength(
            vessel.getLiner().cylinderLength,
            symmetricContour,
            puck.max(1),
            x,
            middleNode,
            maxHoopShift1,
            maxHoopShift2,
        )
        if reducedCylinderLength < vessel.getLiner().cylinderLength:
            setReducedCylinder(
                vessel, composite, reducedCylinderLength, symmetricContour, bandWidth, settings.nodesPerBand
            )
            usingReducedCylinder = True
        else:
            usingReducedCylinder = False
    else:
        usingReducedCylinder = False

    # Try to delete obsolete hoop layers
    while obsoleteLayers:
        log.info("Trying to remove an obsolete hoop layer...")
        indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
        (
            hoopStart,
            hoopEnd,
            maxHoopShift1,
            maxHoopShift2,
            useHoopIndices,
            useHelicalIndices,
            useHelicalAndShoulderIndices,
        ) = indiciesAndShifts
        numberHoopLayers = len([angle for angle, _, _ in anglesShifts if isHoopLayer(angle)])
        if numberHoopLayers > 1:
            newAnglesShifts = deepcopy(anglesShifts)
            for i in range(len(newAnglesShifts) - 1, -1, -1):
                angle, shift1, shift2 = newAnglesShifts[i]
                if isHoopLayer(angle):
                    newAnglesShifts.pop(i)
                    break
            composite = windAnglesAndShifts(newAnglesShifts, vessel, compositeArgs)
            newPuck, newStrainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
            newPuckMax = newPuck.max().max()
            if newPuckMax < 1:
                log.info("Layer could be removed")
                layersDeleted += 1
                anglesShifts = newAnglesShifts
                puck, StrainDiff = newPuck, newStrainDiff
                puckMax = newPuckMax
                columns = ["lay{}_{:04.1f}".format(i, angle) for i, (angle, _, _) in enumerate(anglesShifts)]
                layerNumber -= 1
                plotPuckAndTargetFunc(
                    puck,
                    anglesShifts,
                    f"deleted_{layersDeleted}_hoop",
                    runDir,
                    useFibreFailure,
                    show,
                    False,
                )
            else:
                break
        else:
            break

    # Try to delete other obsolete Layers
    nrHoopLayers = len([angle for angle, _, _ in anglesShifts if isHoopLayer(angle)])
    x0Mandrel1, x0Mandrel2 = None, None
    while obsoleteLayers:
        log.info("Trying to remove an obsolete helical layer...")
        indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
        (
            hoopStart,
            hoopEnd,
            maxHoopShift1,
            maxHoopShift2,
            useHoopIndices,
            useHelicalIndices,
            useHelicalAndShoulderIndices,
        ) = indiciesAndShifts
        useOnlyHoopIndices = list(set(useHoopIndices) - set(useHelicalAndShoulderIndices))
        contourSmoothingBorders = getPolarOpeningNodesForAngle(vessel, 0, angleForContourSmoothingBorders)
        windAnglesAndShifts(anglesShifts, vessel, compositeArgs)
        previousWindability = [
            calculateWindability(
                vessel,
                layerToConsider,
                settings.maxThicknessDerivative,
                settings.minThicknessDerivativeSorted,
                contourSmoothingBorders,
            )
            for layerToConsider in range(0, layerNumber + 1)
        ]
        newPuckMaxList = np.ones(layerNumber + 1) * 10
        newPuckMaxListCylinder = np.ones(layerNumber + 1) * 1
        log.info("Choosing Layer to delete")
        for layerToDelete in range(layerNumber, -1, -1):
            if not isHoopLayer(anglesShifts[layerToDelete][0]):
                newAnglesShifts = deepcopy(anglesShifts)
                newAnglesShifts.pop(layerToDelete)
                composite = windAnglesAndShifts(newAnglesShifts, vessel, compositeArgs)
                if anglesShifts[layerToDelete][0] < angleForContourSmoothingBorders:
                    currentWindability = [
                        calculateWindability(
                            vessel,
                            layerToConsider,
                            settings.maxThicknessDerivative,
                            settings.minThicknessDerivativeSorted,
                            contourSmoothingBorders,
                        )
                        for layerToConsider in range(layerToDelete, layerNumber)
                    ]
                    if np.any([currentWindability > np.add(previousWindability[layerToDelete + 1 :], 0.5)]):
                        possibleToRemove = False
                    else:
                        possibleToRemove = True
                else:
                    possibleToRemove = True
                if possibleToRemove:
                    newPuck, newStrainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
                    newPuckMaxList[layerToDelete] = newPuck.iloc[useHelicalAndShoulderIndices].max().max()
                    newPuckMaxListCylinder[layerToDelete] = newPuck.iloc[useOnlyHoopIndices].max().max()

        # Sum of dome puck and cylinder puck for choice of layer to remove
        bestLayerChoiceList = np.sum([newPuckMaxList, newPuckMaxListCylinder], 0)
        # prefer options that are both < 1, then ones where cylinder puck is < 1, then ones where only dome puck is <1
        for i in range(0, layerNumber + 1):
            if newPuckMaxListCylinder[i] > 1:
                if newPuckMaxList[i] > 1:
                    bestLayerChoiceList[i] += 3
                else:
                    bestLayerChoiceList[i] += 2
            else:
                if newPuckMaxList[i] > 1:
                    bestLayerChoiceList[i] += 1

        bestLayer = np.argmin(bestLayerChoiceList)
        bestLayerAngle = anglesShifts[bestLayer][0]
        newPuckMax = newPuckMaxList[bestLayer]
        newPuckMaxCylinder = newPuckMaxListCylinder[bestLayer]
        log.info(
            f"Removing Layer {bestLayer} with angle {bestLayerAngle}, new PuckMax {newPuckMax} in Dome, {newPuckMaxCylinder} in Cylinder."
        )
        newAnglesShifts = deepcopy(anglesShifts)
        newAnglesShifts.pop(bestLayer)
        layersDeleted += 1
        layerNumber -= 1

        if newPuckMaxCylinder > 1:
            layerNumber += 1
            composite = windAnglesAndShifts(newAnglesShifts + [(90, 0.0, 0.0)], vessel, compositeArgs)
            resHoop = distributeHoop(
                maxHoopShift1,
                maxHoopShift2,
                newAnglesShifts,
                compositeArgs,
                {"vessel": vessel},
                hoopShiftRange=hoopShiftRange,
                calculatePuck=False,
            )
            newAnglesShifts.append((90, resHoop[0], resHoop[1]))
            if hoopLayerCluster > 1:
                clusterHoopLayers(
                    newAnglesShifts,
                    hoopLayerCluster,
                    sortLayersAboveAngle,
                    settings.putHoopLayersOnLiner,
                    settings.putHoopLayersOnTop,
                )
            log.info("Replaced layer with a 90 Degree Layer")
        composite = windAnglesAndShifts(newAnglesShifts, vessel, compositeArgs)
        puck, strainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
        puckMax = puck.max().max()
        if doHoopShiftOptimization and puckMax > 1:
            optKwargs = OrderedDict(
                [
                    ("vessel", vessel),
                    ("layerNumber", layerNumber),
                    ("newLayerPosition", layerNumber),
                    ("materialMuWind", materialMuWind),
                    ("burstPressure", burstPressure),
                    ("useIndices", useHelicalAndShoulderIndices),
                    ("useFibreFailure", useFibreFailure),
                    ("verbosePlot", verbosePlot),
                    ("symmetricContour", symmetricContour),
                    ("elemIdxPuckMax", 0),
                    ("elemIdxBendMax", 0),
                    ("targetFuncScaling", [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                    ("thickShellScaling", thickShellScaling),
                    ("helicalDesignFactors", helicalDesignFactors),
                    ("helicalDesignFactorIndexes", useHelicalAndShoulderIndices),
                    ("sortLayersAboveAngle", sortLayersAboveAngle if sortLayers else 90),
                    ("contourSmoothingBorders", [0, 0]),
                    ("anglePullToFitting", anglePullToFitting),
                    ("deltaT", deltaT),
                    ("windabilityGoal", settings.maxThicknessDerivative),
                    ("skipFEMForBadContour", False),
                ]
            )
            newAnglesShifts, newOptResult, x0Mandrel1, x0Mandrel2 = optimizeHoopDistribution(
                maxHoopShift1, maxHoopShift2, newAnglesShifts, optKwargs, hoopShiftRange, x0Mandrel1, x0Mandrel2
            )
            composite = windAnglesAndShifts(newAnglesShifts, vessel, compositeArgs)
            puck, strainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
            puckMax = puck.max().max()
        log.info(f"Max Puck: {puckMax}")
        if puckMax > 1:
            log.info("Reverting last change and finishing optimization")
            composite = windAnglesAndShifts(anglesShifts, vessel, compositeArgs)
            if usingReducedCylinder:  # reset to full cylinder
                vessel.setLiner(liner)
                vessel.setComposite(composite)
                vessel.finishWinding()
            # Find Windable Angles for existing layers
            if findValidWindingAngles:
                log.info("Finding closest valid winding angles")
                if targetFuncWeights[-1]:  # if using enforceWindableContour
                    contourSmoothingBorders = getPolarOpeningNodesForAngle(
                        vessel, layerNumber, angleForContourSmoothingBorders
                    )
                else:
                    contourSmoothingBorders = None
                for loopLayerNumber, (angle, shift1, shift2) in enumerate(anglesShifts):
                    if not isHoopLayer(angle):
                        newAngle = findValidWindingAngle(
                            vessel,
                            loopLayerNumber,
                            angle,
                            polarOpeningRadius,
                            contourSmoothingBorders,
                            settings.useMoreCycles,
                        )
                        anglesShifts[loopLayerNumber] = (newAngle, shift1, shift2)
                        windLayer(vessel, loopLayerNumber, newAngle)
                composite = windAnglesAndShifts(anglesShifts, vessel, compositeArgs)
            vessel.finishWinding()
            indiciesAndShifts = _getHoopAndHelicalIndices(vessel, symmetricContour, relRadiusHoopLayerEnd)
            (
                hoopStart,
                hoopEnd,
                maxHoopShift1,
                maxHoopShift2,
                useHoopIndices,
                useHelicalIndices,
                useHelicalAndShoulderIndices,
            ) = indiciesAndShifts
            puck, strainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
            puckMax = puck.max().max()
            vessel.saveToFile(os.path.join(runDir, "backup.vessel"))  # save vessel
            anglesShiftsOutput = [[round(float(y), 3) for y in list(x)] for x in zip(*anglesShifts)]
            writeParametersToYAML({"initialAnglesAndShifts": anglesShiftsOutput}, anglesShiftsFilename)
            plotPuckAndTargetFunc(
                puck,
                anglesShifts,
                f"final",
                runDir,
                useFibreFailure,
                show,
                False,
            )
            break
        else:
            anglesShifts = newAnglesShifts
            vessel.saveToFile(os.path.join(runDir, "backup.vessel"))  # save vessel
            anglesShiftsOutput = [[round(float(y), 3) for y in list(x)] for x in zip(*anglesShifts)]
            writeParametersToYAML({"initialAnglesAndShifts": anglesShiftsOutput}, anglesShiftsFilename)
            puck, strainDiff, thickShellScaling, helicalDesignFactors = getPuckAndStrainDiff()
            puckMax = puck.max().max()
            plotPuckAndTargetFunc(
                puck,
                anglesShifts,
                f"deleted_{layersDeleted}_helical",
                runDir,
                useFibreFailure,
                show,
                False,
            )

    vessel.finishWinding()
    if frpMassStrengthOnly is None:
        stats = vessel.calculateVesselStatistics()
        frpMassStrengthOnly = stats.overallFRPMass  # in [kg]
    if frpMassFatigueOnly is None:
        stats = vessel.calculateVesselStatistics()
        frpMassFatigueOnly = stats.overallFRPMass  # in [kg]

    # postprocessing
    # ##############################################################################
    results = getLinearResults(
        vessel,
        materialMuWind,
        burstPressure,
        symmetricContour=symmetricContour,
        useFibreFailure=useFibreFailure,
        deltaT=deltaT,
    )
    thicknesses = getLayerThicknesses(vessel, symmetricContour)
    angles = getLayerAngles(vessel, symmetricContour)
    if show or save:
        plotStressEpsPuck(show, os.path.join(runDir, f"sig_eps_puck.png") if save else "", *results)
        plotThicknesses(show, os.path.join(runDir, f"thicknesses.png"), thicknesses)

    thicknesses.columns = ["thk_lay{}".format(i) for i, (angle, _, _) in enumerate(anglesShifts)]
    angles.columns = ["ang_lay{}".format(i) for i, (angle, _, _) in enumerate(anglesShifts)]

    mechResults = getLinearResultsAsDataFrame(results)
    mandrel = liner.getMandrel1()
    lengthCoordinate = np.array([mandrel.getLArray()])
    elementLengths = lengthCoordinate[:, 1:] - lengthCoordinate[:, -1]
    elementLengths = pd.DataFrame(elementLengths.T, columns=["elementLength"])
    elementalResults = pd.concat([elementLengths, thicknesses, angles, mechResults], join="outer", axis=1)
    elementalResults.to_csv(os.path.join(runDir, "elementalResults.csv"), sep=";")

    if log.level == logging.DEBUG:
        # vessel.printSimulationStatus()
        composite.info()

    # get vessel results
    stats = vessel.calculateVesselStatistics()
    frpMass = stats.overallFRPMass  # in [kg]
    summedThicknesses = thicknesses.sum(1)
    cylinderThickness = summedThicknesses[middleNode]
    maxThickness = summedThicknesses.values.max()
    dome = liner.getDome1()
    areaDome = AbstractDome.getArea([dome.getXCoords(), dome.getRCoords()])
    area = 2 * np.pi * liner.cylinderRadius * liner.cylinderLength + 2 * areaDome  # [mm**2]
    area *= 1e-6  # [m**2]
    reserveFac = 1 / puckMax
    S11 = results[0]
    minCylinderStress = np.min(S11[middleNode, :])
    maxCylinderStress = np.max(S11[middleNode, :])
    stressRatio = minCylinderStress / maxCylinderStress
    return (
        frpMass,
        area,
        iterations,
        reserveFac,
        stressRatio,
        cylinderThickness,
        maxThickness,
        frpMassStrengthOnly,
        frpMassFatigueOnly,
        puckMax,
        *(np.array(anglesShifts).T),
    )
