# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""optimizers for various target functions

- optimize frition to achieve a target polar opening
- optimize shift for hoop layers
- optimize layup
"""
import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import differential_evolution, minimize, minimize_scalar

from tankoh2 import log
from tankoh2.design.winding.contour import calculateWindability
from tankoh2.design.winding.solver import (
    getMaxPuckByAngle,
    getMaxPuckByShift,
    getMaxPuckLocalPuckMassIndexByAngle,
    getMaxPuckLocalPuckMassIndexByShift,
    getWeightedTargetFuncByAngle,
)
from tankoh2.design.winding.winding import (
    getCorrectedProgress,
    getNegAngleAndPolarOpeningDiffByAngle,
    getPolarOpeningDiffByAngle,
    getPolarOpeningDiffByAngleBandMid,
    getPolarOpeningDiffHelical,
    getPolarOpeningDiffHelicalUsingLogFriction,
    getPolarOpeningDiffHelicalUsingNegativeLogFriction,
    getPolarOpeningDiffHoop,
    getPolarOpeningXDiffHoop,
    getWindingPatternInfo,
    isFittingLayer,
    windHoopLayer,
    windLayer,
)
from tankoh2.geometry.geoutils import getRadiusByShiftOnContour
from tankoh2.service.exception import Tankoh2Error
from tankoh2.settings import settings

_lastMinAngle = None


def calculateMinAngle(vessel, targetPolarOpening, layerNumber, bandWidth):
    if settings.useClairaultAngle:
        return clairaultAngle(vessel, targetPolarOpening, layerNumber, bandWidth)
    else:
        angle, funVal, iterations = optimizeAngle(
            vessel, targetPolarOpening, layerNumber, bandWidth, getPolarOpeningDiffByAngleBandMid
        )
        return angle


def optimizeAngle(vessel, targetPolarOpening, layerNumber, bandWidth, targetFunction=getPolarOpeningDiffByAngle):
    """optimizes the angle of the actual layer to realize the desired polar opening

    :param vessel: vessel object
    :param targetPolarOpening: polar opening radius that should be realized
    :param layerNumber: number of the actual layer
    :param bandWidth: total width of the band (only used for tf getPolarOpeningDiffByAngleBandMid)
    :param targetFunction: target function to be minimized
    :return: 3-tuple (resultAngle, polar opening, number of runs)
    """

    global _lastMinAngle
    angleBounds = (1.0, settings.maxHelicalAngle) if _lastMinAngle is None else (_lastMinAngle - 1, _lastMinAngle)
    tol = 1e-2
    if targetFunction is getPolarOpeningDiffByAngleBandMid:
        args = [vessel, layerNumber, targetPolarOpening, bandWidth]
    else:
        args = [vessel, layerNumber, targetPolarOpening]
    while angleBounds[0] < 30:
        try:
            popt = minimize_scalar(
                targetFunction,
                method="bounded",
                bounds=angleBounds,
                args=args,
                options={"maxiter": 1000, "disp": 1, "xatol": tol},
            )
            break
        except RuntimeError as e:
            # if minBound too small, µWind may raise an error "Polar Opening too small - Thickness Error!"
            if str(e) == "Polar Opening too small - Thickness Error!":
                angleBounds = angleBounds[0] + 0.1, angleBounds[1] + 1
                log.info("Min angle bound of optimization was too low - increased by one deg.")
            else:
                raise
    if not popt.success:
        raise Tankoh2Error("Could not find optimal solution")
    plotTargetFun = False
    if plotTargetFun:
        angles = np.linspace(angleBounds[0], 10, 200)
        tfValues = [targetFunction(angle, args) for angle in angles]
        fig, ax = plt.subplots()
        ax.plot(angles, tfValues, linewidth=2.0)
        plt.show()
    angle, funVal, iterations = popt.x, popt.fun, popt.nfev
    if popt.fun > 1 and targetFunction is getPolarOpeningDiffByAngle:
        # desired polar opening not met. This happens, when polar opening is near fitting.
        # There is a discontinuity at this point. Switch target function to search from the fitting side.
        angle, funVal, iterations = optimizeAngle(
            vessel, targetPolarOpening, layerNumber, getNegAngleAndPolarOpeningDiffByAngle
        )
    else:
        windLayer(vessel, layerNumber, angle)
    log.debug(f"Min angle {angle} at funcVal {funVal}")
    _lastMinAngle = angle
    return angle, funVal, iterations


def clairaultAngle(vessel, targetPolarOpening, layerNumber, bandWidth):
    """finds the angle of a layer to realize the desired polar opening using the clairault relation

    :param vessel: vessel object
    :param targetPolarOpening: polar opening radius that should be realized
    :param layerNumber: number of the actual layer
    :param bandWidth: total width of the band (only used for tf getPolarOpeningDiffByAngleBandMid)
    :return: angle: cylinder angle that leads to target polar opening according to clairault relation
    """

    windLayer(vessel, layerNumber, 90)
    r = vessel.getVesselLayer(layerNumber).getInnerMandrel1().getRArray()[0]
    bandMidPolarOpening = getRadiusByShiftOnContour(
        vessel.getVesselLayer(layerNumber).getInnerMandrel1().getRArray(),
        vessel.getVesselLayer(layerNumber).getInnerMandrel1().getLArray(),
        targetPolarOpening,
        -bandWidth / 2,
    )
    angle = np.rad2deg(np.arcsin(bandMidPolarOpening / r))
    while True:
        if windLayer(vessel, layerNumber, angle) < np.inf:
            break
        else:
            angle += 0.01

    return angle


def minimizeUtilization(bounds, targetFunction, optKwArgs, localOptimization=False):
    """Minimizes puck (inter) fibre failure criterion in defined bounds (angles or hoop shifts)

    This method calls the optimization routines. There is a distinction between local and global
    optimization.

    :param bounds: iterable with 2 items: lower and upper bound
    :param targetFunction: function to be used as target function
    :param optKwArgs: dict with these items:
        - vessel: µWind vessel instance
        - layerNumber: actual layer (zero based counting)
        - materialMuWind: µWind material instance
        - burstPressure: burst pressure in MPa
        - useIndices: list of element indicies that will be used for stress and puck evaluation
        - useFibreFailure: flag if fibrefailure or interfibrefailure is used
        - verbosePlot: flag if additional plot output values should be created
        - symmetricContour: flag if the conour is symmetric or unsymmetric
        - elemIdxPuckMax: index of the most critical element (puck) before adding the actual layer
        - elemIdxBendMax: index of the most critical element (strain diff) before adding the actual layer
        - targetFuncScaling: scaling of the target function constituents for the weighted sum
    :param localOptimization: can be (True, False, 'both'). Performs a local or global optimization. If 'both'
        is selected, both optimizations are performed and the result with the lowest function value is used.
    :return: 4-tuple
        - x optimization result
        - funVal: target function value at x
        - iterations: number of iterations used
        - tfPlotVals: plot values of the target function if verbosePlot==True else None

    """

    helicalTargetFunctions = [getWeightedTargetFuncByAngle, getMaxPuckByAngle]
    verbosePlot = optKwArgs["verbosePlot"]
    if verbosePlot:
        tfX = np.linspace(*bounds, 50)
        targetFunctionPlot = (
            getMaxPuckLocalPuckMassIndexByAngle
            if targetFunction in helicalTargetFunctions
            else getMaxPuckLocalPuckMassIndexByShift
        )
        tfPlotVals = [targetFunctionPlot(angleParam, optKwArgs) for angleParam in tfX]
        isInfArray = [val[0] == np.inf for val in tfPlotVals]
        tfX = np.array([x for x, isInf in zip(tfX, isInfArray) if not isInf])
        tfPlotVals = np.array([val for val, isInf in zip(tfPlotVals, isInfArray) if not isInf]).T
        if targetFunction in [getMaxPuckByAngle, getMaxPuckByShift]:
            tfPlotVals = np.append(tfPlotVals[:1], tfPlotVals[-1:], axis=0)
        tfPlotVals = np.append([tfX], tfPlotVals, axis=0)
    else:
        tfPlotVals = None

    if localOptimization not in [True, False, "both"]:
        raise Tankoh2Error("no proper value for localOptimization")
    localOptimization = "both"
    if localOptimization is True or localOptimization == "both":
        if (
            localOptimization == "both"
            and settings.pullLowHelicalsToFitting
            and bounds[0] < optKwArgs["anglePullToFitting"]
        ):
            localBounds = [bounds[0], bounds[0]]
            # if using global optimizer and pullLowHelicalsToFitting, don't perform local optimization, just take the fitting clairault angle
        else:
            localBounds = bounds
        localTol = 1e-3
        popt_loc = minimize(
            targetFunction,
            localBounds[:1],
            bounds=[localBounds],  # bounds of the angle or hoop shift
            args=optKwArgs,
            tol=localTol,
        )
        if localOptimization is True:
            popt = popt_loc
    if localOptimization is False or localOptimization == "both":
        globalBounds = bounds
        popt_glob = differential_evolution(
            targetFunction,
            bounds=(globalBounds,),
            args=[optKwArgs],
            atol=settings.optimizerAtol,
            seed=settings.optimizerSeed,
            popsize=settings.optimizerPopsize,
            polish=False,
        )
        if localOptimization is False:
            popt = popt_glob
    if localOptimization == "both":
        popt = popt_loc if popt_loc.fun < popt_glob.fun else popt_glob
        popt.nfev = popt_loc.nfev + popt_glob.nfev
        if not popt.success:
            popt = popt_loc if popt_loc.fun > popt_glob.fun else popt_glob
    if not popt.success:
        from tankoh2.service.plot.muwind import plotTargetFunc

        errMsg = "Could not find optimal solution"
        log.error(errMsg)
        plotTargetFunc(
            None, tfPlotVals, (popt.x, 0, 0), "label Name", ([0] * 4, optKwArgs["targetFuncScaling"]), None, None, True
        )
        raise Tankoh2Error(errMsg)
    x, funVal, iterations = popt.x, popt.fun, popt.nfev
    if hasattr(x, "__iter__"):
        x = x[0]
    vessel, layerNumber = optKwArgs["vessel"], optKwArgs["newLayerPosition"]
    if targetFunction in helicalTargetFunctions:
        polarOpeningRadius = windLayer(vessel, layerNumber, x)
    else:
        polarOpeningRadius = windHoopLayer(vessel, layerNumber, x)

    return x, polarOpeningRadius, funVal, iterations, tfPlotVals


def optimizeFriction(vessel, wendekreisradius, layerindex):
    # popt, pcov = curve_fit(getPolarOpeningDiff, layerindex, wk_goal, bounds=([0.], [1.]))
    #
    # popt  = minimize(getPolarOpeningDiff, x0 = (1.), method = 'BFGS', args=[vessel, wendekreisradius],
    #                   options={'gtol': 1e-6, 'disp': True})
    tol = 1e-7
    popt = minimize_scalar(
        getPolarOpeningDiffHelical,
        method="bounded",
        bounds=[0.0, 1e-5],
        args=[vessel, wendekreisradius, layerindex],
        options={"maxiter": 1000, "disp": 1, "xatol": tol},
    )
    friction = popt.x
    return friction, popt.fun, popt.nfev


def optimizeHoopShift(vessel, krempenradius, layerindex):
    popt = minimize_scalar(
        getPolarOpeningDiffHoop, method="brent", options={"xtol": 1e-2}, args=[vessel, krempenradius, layerindex]
    )
    shift = popt.x
    return shift, popt.fun, popt.nit


def optimizeHoopShiftForPolarOpeningX(vessel, polarOpeningX, layerindex):
    popt = minimize_scalar(
        getPolarOpeningXDiffHoop, method="brent", options={"xtol": 1e-2}, args=[vessel, polarOpeningX, layerindex]
    )
    shift = popt.x
    return shift, popt.fun, popt.nit


# write new optimasation with scipy.optimize.differential_evolution


def optimizeFrictionGlobal_differential_evolution(vessel, wendekreisradius, layerindex):
    """
    optimize friction value for given polarOpening
    using global optimizer scipy.optimize.differential_evolution
    """
    tol = 1e-15
    args = (vessel, wendekreisradius, layerindex)
    popt = differential_evolution(
        getPolarOpeningDiffHelicalUsingLogFriction,
        bounds=[(-10, -4)],
        args=[args],
        strategy="best1bin",
        mutation=1.9,
        recombination=0.9,
        seed=settings.optimizerSeed,
        tol=tol,
        atol=tol,
    )
    friction = popt.x
    return 10**friction, popt.fun, popt.nfev


def optimizeNegativeFrictionGlobal_differential_evolution(vessel, wendekreisradius, layerindex):
    """
    optimize friction value for given polarOpening
    using global optimizer scipy.optimize.differential_evolution
    """
    tol = 1e-15
    args = (vessel, wendekreisradius, layerindex)
    popt = differential_evolution(
        getPolarOpeningDiffHelicalUsingNegativeLogFriction,
        bounds=[(-10, -3.6)],
        args=[args],
        strategy="best1bin",
        mutation=1.9,
        recombination=0.9,
        seed=settings.optimizerSeed,
        tol=tol,
        atol=tol,
    )
    friction = popt.x
    return -1.0 * abs(10**friction), popt.fun, popt.nfev


def findAllValidWindingAngles(vessel, layerNumber, minimumPolarOpeningRadius, useMoreCycles=0):
    """
    Find all possible angles which lead to a valid winding pattern.

    :param vessel: The µWind vessel instance.
    :param layerNumber: The index of the vessel's layer to wind.
    :param minimumPolarOpeningRadius: Minimum polar opening radius required
    :param useMoreCycles: Number of additional cycles to use (allows more valid angles with higher overlap)

    :return: A list of valid angles.
    """

    def targetFunction(angle):
        return abs(getCorrectedProgress(angle, attemptCycles, vessel, layerNumber) - attemptProgress)

    # Get initial layer information
    layer = vessel.getVesselLayer(layerNumber)
    initialLayerResults = layer.getVesselLayerPropertiesSolver().getWindingLayerResults()
    bandWidth = initialLayerResults.cylinderBandWidth
    radius = layer.getInnerMandrel1().getRArray()[0]
    minAngle = calculateMinAngle(vessel, minimumPolarOpeningRadius, layerNumber, 0.5 * bandWidth)

    # get bounds for possible cycle numbers
    windLayer(vessel, layerNumber, minAngle)
    _, upperCycleBound, _ = getWindingPatternInfo(vessel, layerNumber)
    windLayer(vessel, layerNumber, settings.maxHelicalAngle)
    _, lowerCycleBound, _ = getWindingPatternInfo(vessel, layerNumber)

    # get bounds for the winding angles to separate the search spaces with constant cycle numbers
    bounds = []
    for baseCycles in range(lowerCycleBound, upperCycleBound + 2):
        angleBound = min(
            max(np.rad2deg(np.arccos(min((baseCycles - 1) * bandWidth / (radius * 2 * np.pi), 1))), minAngle),
            settings.maxHelicalAngle,
        )
        windLayer(vessel, layerNumber, angleBound)
        progressBound, progressBoundCycles, _ = getWindingPatternInfo(vessel, layerNumber)
        bounds.append([angleBound, progressBound, progressBoundCycles])

    # within each search space, try to find any valid angles (those with integer progress values)
    validAngles = []
    for i, baseCycles in enumerate(range(lowerCycleBound, upperCycleBound + 1)):
        lowerAngleBound = bounds[i + 1][0]
        upperAngleBound = bounds[i][0]
        for attemptCycles in range(baseCycles, baseCycles + useMoreCycles + 1):
            # bounds for possible integer progress values
            progressBound1 = bounds[i][1] * attemptCycles / bounds[i][2]
            progressBound2 = bounds[i + 1][1] * attemptCycles / bounds[i + 1][2]
            lowerProgressBound, upperProgressBound = sorted([progressBound1, progressBound2])
            for attemptProgress in range(math.floor(lowerProgressBound) + 1, math.floor(upperProgressBound) + 1):
                # check if this combination of integer progress and cycle number would result in a valid pattern
                if np.gcd(attemptProgress % attemptCycles, attemptCycles) == 1:
                    # check if there is a minimum within the search area
                    if upperProgressBound >= attemptProgress >= lowerProgressBound:
                        # find the angle which reaches the integer progress value
                        res = minimize_scalar(
                            targetFunction, bounds=(lowerAngleBound, upperAngleBound), method="bounded"
                        )
                        if res.fun < 0.05:
                            validAngles.append([res.x])
    log.info(f" found {len(validAngles)} valid angles")
    log.info(validAngles)
    return validAngles


def findValidWindingAngle(
    vessel, layerNumber, angle, minimumPolarOpeningRadius, contourSmoothingBorders, useMoreCycles=0
):
    """
    Find the closest angle which results in a valid winding pattern to the given angle

    :param vessel: The µWind vessel instance.
    :param layerNumber: The index of the vessel's layer to wind.
    :param angle: the current angle on which to base the valid angle search
    :param minimumPolarOpeningRadius: Minimum polar opening radius required
    :param contourSmoothingBorders: borders for consideration of contour windability, if supplied
    :param useMoreCycles: Number of additional cycles to use (allows more valid angles with higher overlap)

    :return: closest valid angle or original angle if none could be found.
    """

    def targetFunction(currentAngle):
        return abs(getCorrectedProgress(currentAngle, attemptCycles, vessel, layerNumber) - attemptProgress)

    # Get initial layer information
    layer = vessel.getVesselLayer(layerNumber)
    initialLayerResults = layer.getVesselLayerPropertiesSolver().getWindingLayerResults()
    bandWidth = initialLayerResults.cylinderBandWidth
    radius = layer.getInnerMandrel1().getRArray()[0]
    minAngle = calculateMinAngle(vessel, minimumPolarOpeningRadius, layerNumber, 0.5 * bandWidth)

    windLayer(vessel, layerNumber, angle)
    fittingLayer = isFittingLayer(vessel, layerNumber)
    startProgress, startCycles, _ = getWindingPatternInfo(vessel, layerNumber)

    # Check if current angle is already valid
    for cycles in range(startCycles, startCycles + useMoreCycles + 1):
        progress = startProgress * cycles / startCycles
        closestIntProgress = round(progress)
        if np.gcd(closestIntProgress % cycles, cycles) == 1:
            if abs(progress - closestIntProgress) < 0.05:
                extraCycles = cycles - startCycles
                log.debug(f"Angle was {angle}, which is already a valid pattern with extra cycles {extraCycles}")
                return angle

    # Initialize Bounds and steps for the loop
    baseCycles = startCycles
    lowerAngleBound = min(
        max(np.rad2deg(np.arccos(min(baseCycles * bandWidth / (radius * 2 * np.pi), 1))), minAngle),
        settings.maxHelicalAngle,
    )
    upperAngleBound = min(
        max(np.rad2deg(np.arccos(min((baseCycles - 1) * bandWidth / (radius * 2 * np.pi), 1))), minAngle),
        settings.maxHelicalAngle,
    )
    if angle > (lowerAngleBound + upperAngleBound) / 2:
        cycleStep = -1
    else:
        cycleStep = 1

    patternFound = False
    breakEarly = False
    validAngles = []

    # Search for valid angles in the cycle search space around the current angle, as well as 2 above and 2 below
    for i in range(3):
        for attemptCycles in range(baseCycles, baseCycles + useMoreCycles + 1):
            # Set bounds for possible integer progress values
            progressBound1 = getCorrectedProgress(lowerAngleBound, attemptCycles, vessel, layerNumber)
            progressBound2 = getCorrectedProgress(upperAngleBound, attemptCycles, vessel, layerNumber)
            lowerProgressBound, upperProgressBound = sorted([progressBound1, progressBound2])
            for attemptProgress in range(math.floor(lowerProgressBound) + 1, math.floor(upperProgressBound) + 1):
                # check if this combination of integer progress and cycle number would result in a valid pattern
                if np.gcd(attemptProgress % attemptCycles, attemptCycles) == 1:
                    # check if there is a minimum within the search area
                    if upperProgressBound >= attemptProgress >= lowerProgressBound:
                        res = minimize_scalar(
                            targetFunction, bounds=(lowerAngleBound, upperAngleBound), method="bounded"
                        )
                        # find the angle which reaches the integer progress value
                        if res.fun < 0.05:
                            if fittingLayer:
                                # check that this angle doesn't pull a fitting layer away from the fitting
                                if isFittingLayer(vessel, layerNumber):
                                    validAngles.append([res.x, 0, attemptCycles - baseCycles])
                                    patternFound = True
                                    breakEarly = True
                            elif contourSmoothingBorders:
                                windability = calculateWindability(
                                    vessel,
                                    layerNumber,
                                    settings.maxThicknessDerivative,
                                    settings.minThicknessDerivativeSorted,
                                    contourSmoothingBorders,
                                )
                                validAngles.append([res.x, windability, attemptCycles - baseCycles])
                                patternFound = True
                            else:
                                validAngles.append([res.x, 0, attemptCycles - baseCycles])
                                patternFound = True
                                breakEarly = True
        if breakEarly:  # Found a good solution
            break
        # update search bounds and cycles
        baseCycles = baseCycles + cycleStep
        if cycleStep < 0:
            cycleStep = -cycleStep + 1
        else:
            cycleStep = -cycleStep - 1
        lowerAngleBound = min(
            max(np.rad2deg(np.arccos(min(baseCycles * bandWidth / (radius * 2 * np.pi), 1))), minAngle),
            settings.maxHelicalAngle,
        )
        upperAngleBound = min(
            max(np.rad2deg(np.arccos(min((baseCycles - 1) * bandWidth / (radius * 2 * np.pi), 1))), minAngle),
            settings.maxHelicalAngle,
        )

    # reset layer angle
    windLayer(vessel, layerNumber, angle)

    if patternFound:
        validAngles = np.array(validAngles)
        # choose the closest valid angle
        if contourSmoothingBorders:
            # add windability penalty (prefer windable angles)
            diffToBaseAngle = np.abs(validAngles[:, 0] - angle) + validAngles[:, 1] * 10
        else:
            diffToBaseAngle = np.abs(validAngles[:, 0] - angle)
        bestValidAngleIndex = np.argmin(diffToBaseAngle)
        bestValidAngle = validAngles[bestValidAngleIndex, 0]
        neededExtraCycles = validAngles[bestValidAngleIndex, 2]
        log.debug(f"Found valid angle {bestValidAngle}, {neededExtraCycles}")
        return bestValidAngle
    else:
        log.debug(f"Couldn't find valid angle, returning {angle}")
        return angle
