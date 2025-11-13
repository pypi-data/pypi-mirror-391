# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""control a tank optimization"""

import os
from datetime import datetime

import numpy as np
import pandas as pd

from tankoh2 import log, programDir, pychain
from tankoh2.control.genericcontrol import (
    _parameterNotSet,
    getBurstPressure,
    parseDesignArgs,
    performStabilityAnalysis,
    saveLayerBook,
    saveParametersAndResults,
)
from tankoh2.design.designutils import getMassByVolume
from tankoh2.design.metal.material import getMaterial as getMaterialMetal
from tankoh2.design.winding.contour import buildFitting, getDomeMuWind, getLinerMuWind, saveLiner
from tankoh2.design.winding.designopt import designLayers
from tankoh2.design.winding.material import checkFibreVolumeContent, getCompositeMuwind, getMaterialPyChain
from tankoh2.design.winding.windingutils import (
    copyAsJson,
    getLayerNodalCoordinates,
    getMandrelNodalCoordinates,
    updateName,
)
from tankoh2.geometry.liner import Liner
from tankoh2.masses.massestimation import (
    getAuxMaterials,
    getFairingMass,
    getFittingMass,
    getInsulationMass,
    getLinerMass,
)
from tankoh2.mechanics.material import MaterialDefinition
from tankoh2.mechanics.pbucklcritcyl_SP8007 import balanced_symmetric
from tankoh2.service.utilities import writeParametersToYAML


def createDesign(**kwargs):
    """Create a winding design

    For a list of possible parameters, please refer to tankoh2.design.existingdesigns.allDesignKeywords
    """
    startTime = datetime.now()
    # #########################################################################################
    # SET Parameters of vessel
    # #########################################################################################
    kwargs["windingOrMetal"] = "winding"
    designArgs, nonDefaultArgs, domeObjects = parseDesignArgs(kwargs)
    saveParametersAndResults(designArgs["runDir"], nonDefaultArgs, designArgs)
    domeContourFilename = os.path.join(designArgs["runDir"], f"domeContour" + ".yaml")
    writeParametersToYAML(
        {
            f"{domeName}Contour": domeObjects[f"{domeName}Contour"]
            for domeName in ["dome2", "dome"]
            if domeName in domeObjects and domeObjects[domeName] is not None
        },
        domeContourFilename,
    )
    # General
    tankname = designArgs["tankname"]
    nodeNumber = designArgs["nodeNumber"]  # number of nodes of full model.
    runDir = designArgs["runDir"]
    verbosePlot = designArgs["verbosePlot"]
    if designArgs["initialAnglesAndShifts"] is None:
        initialAnglesAndShifts = None
    else:
        initialAnglesAndShifts = list(zip(*designArgs.get("initialAnglesAndShifts", None)))
        if len(initialAnglesAndShifts[0]) == 2:  # convert to 3-Tuple if given as a 2-Tuple
            initialAnglesAndShifts = [(angle, shift, shift) for (angle, shift) in initialAnglesAndShifts]
    # Transpose

    # Optimization
    layersToWind = designArgs["maxLayers"]
    relRadiusHoopLayerEnd = designArgs["relRadiusHoopLayerEnd"]
    targetFuncWeights = designArgs["targetFuncWeights"]
    if designArgs["enforceWindableContour"]:
        targetFuncWeights.append(1.0)
    else:
        targetFuncWeights.append(0.0)
    sortLayers = designArgs["sortLayers"]
    sortLayersAboveAngle = designArgs["sortLayersAboveAngle"]
    findValidWindingAngles = designArgs["findValidWindingAngles"]
    doHoopShiftOptimization = designArgs["optimizeHoopShifts"]
    hoopShiftRange = designArgs["hoopShiftRange"]
    hoopLayerCluster = designArgs["hoopLayerCluster"]

    # Geometry - generic
    polarOpeningRadius = designArgs["polarOpeningRadius"]  # mm
    dcyl = designArgs["dcyl"]  # mm
    lcylinder = designArgs["lcyl"]  # mm

    # Design Args
    pMinOperation = designArgs["minPressure"]
    pMaxOperation = designArgs["fatigueCyclePressure"] if designArgs["fatigueCyclePressure"] else designArgs["pressure"]
    burstPressure = getBurstPressure(designArgs, designArgs["tankLength"])
    helicalDesignFactor = designArgs["helicalDesignFactor"]
    failureMode = designArgs["failureMode"]
    useFibreFailure = failureMode.lower() == "fibrefailure"
    deltaT = 0 if designArgs["temperature"] is None else 273 - designArgs["temperature"]

    # Material
    materialName = designArgs["materialName"]
    materialName = materialName if materialName.endswith(".json") else materialName + ".json"
    materialFilename = materialName
    if not os.path.exists(materialName):
        materialFilename = os.path.join(programDir, "data", materialName)

    # fatigue
    operationalCycles = designArgs["operationalCycles"]
    zeroPressureCycles = designArgs["zeroPressureCycles"]
    simulatedTankLives = designArgs["simulatedTankLives"]
    testPressureAfterFatigue = designArgs["testPressureAfterFatigue"]

    # Fiber roving parameter
    layerThkHoop = designArgs["layerThkHoop"]
    layerThkHelical = designArgs["layerThkHelical"]
    rovingWidthHoop = designArgs["rovingWidthHoop"]
    rovingWidthHelical = designArgs["rovingWidthHelical"]
    numberOfRovings = designArgs["numberOfRovings"]
    bandWidth = rovingWidthHoop * numberOfRovings
    tex = designArgs["tex"]  # g / km
    rho = designArgs["fibreDensity"]  # g / cm^3
    sectionAreaFibre = tex / (1000.0 * rho)
    checkFibreVolumeContent(layerThkHoop, layerThkHelical, sectionAreaFibre, rovingWidthHoop, rovingWidthHelical)

    # output files
    linerFilename = os.path.join(runDir, tankname + ".liner")
    designFilename = os.path.join(runDir, tankname + ".design")
    vesselFilename = os.path.join(runDir, tankname + ".vessel")
    windingResultFilename = os.path.join(runDir, tankname + ".wresults")

    # #########################################################################################
    # Create Liner
    # #########################################################################################
    # Geometry - domes
    dome = getDomeMuWind(dcyl / 2.0, polarOpeningRadius, designArgs["domeType"], *domeObjects["domeContour"])
    dome2 = (
        None
        if designArgs["dome2Type"] is None
        else getDomeMuWind(dcyl / 2.0, polarOpeningRadius, designArgs["dome2Type"], *domeObjects["dome2Contour"])
    )

    linerMuWind = getLinerMuWind(dome, lcylinder, dome2=dome2, nodeNumber=nodeNumber)
    fittingMaterial = getMaterialMetal(designArgs["fittingMaterial"])
    buildFitting(
        linerMuWind,
        designArgs["fittingType"],
        designArgs["r0"],
        designArgs["r1"],
        designArgs["r3"],
        designArgs["rD"],
        designArgs["dX1"],
        designArgs["dXB"],
        designArgs["dX2"],
        designArgs["lV"],
        designArgs["alphaP"],
        designArgs["rP"],
        designArgs["customBossName"],
    )
    saveLiner(
        linerMuWind,
        linerFilename,
        "liner_" + tankname,
    )
    # ###########################################
    # Create material
    # ###########################################
    materialMuWind = getMaterialPyChain(materialFilename)
    linerMat, insMat, fairMat = getAuxMaterials(
        designArgs["linerMaterial"], designArgs["insulationMaterial"], designArgs["fairingMaterial"]
    )

    compositeArgs = [
        layerThkHoop,
        layerThkHelical,
        materialMuWind,
        sectionAreaFibre,
        rovingWidthHoop,
        rovingWidthHelical,
        numberOfRovings,
        numberOfRovings,
        tex,
        designFilename,
        tankname,
    ]
    composite = getCompositeMuwind([90.0], *compositeArgs)
    # create vessel and set liner and composite
    vessel = pychain.winding.Vessel()
    vessel.setLiner(linerMuWind)
    mandrel = linerMuWind.getMandrel1()
    df = pd.DataFrame(
        np.array([mandrel.getXArray(), mandrel.getRArray(), mandrel.getLArray()]).T, columns=["x", "r", "l"]
    )
    df.to_csv(os.path.join(runDir, "nodalResults.csv"), sep=";")

    vessel.setComposite(composite)

    fittingMass = 0
    if designArgs["includeFitting"]:
        fittingMass = getFittingMass(
            vessel, designArgs["fittingType"], fittingMaterial, True, designArgs["customBossName"]
        )
        if designArgs["dome2Type"] is None:
            fittingMass *= 2
        else:
            fittingMass += getFittingMass(
                vessel, designArgs["fittingType"], fittingMaterial, False, designArgs["customBossName"]
            )
    # #############################################################################
    # run winding simulation
    # #############################################################################
    vessel.saveToFile(vesselFilename)  # save vessel
    copyAsJson(vesselFilename, "vessel")
    results = designLayers(
        vessel,
        layersToWind,
        polarOpeningRadius,
        bandWidth,
        materialMuWind,
        burstPressure,
        pMinOperation,
        pMaxOperation,
        helicalDesignFactor,
        dome2 is None,
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
    )

    (
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
        angles,
        hoopLayerShiftsSide1,
        hoopLayerShiftsSide2,
    ) = results
    angles = np.around(angles, decimals=3)
    hoopByHelicalFrac = len([a for a in angles if a > 89]) / len([a for a in angles if a < 89])
    hoopLayerShiftsSide1 = np.around(hoopLayerShiftsSide1, decimals=3)
    hoopLayerShiftsSide2 = np.around(hoopLayerShiftsSide2, decimals=3)

    # #############################################################################
    # stability analysis for outer vessels
    # #############################################################################

    material = MaterialDefinition()
    material.getMaterialFromMuWindJsonFile(materialFilename)
    buckAngles = balanced_symmetric(angles)

    linerTankoh = Liner(domeObjects["dome"], lcylinder, domeObjects["dome2"])
    (
        buckResultDict,
        bucklingFactorMass,
        bucklingFactorSkinThickness,
        massWithBuckling,
        ringMass,
        cylinderLayerThickness,
    ) = performStabilityAnalysis(
        burstPressure,
        designArgs,
        linerTankoh,
        material,
        layerThkHoop
        / 2,  # due to buckAngles = balanced_symmetric(angles) which uses 4 times plys. On the other hand layerThkHoop is for one ply not BAP as used in muWind
        buckAngles,
    )
    if designArgs["useBucklingCriterion"]:
        frpMass *= bucklingFactorMass
        cylinderThickness *= bucklingFactorSkinThickness
        maxThickness *= bucklingFactorSkinThickness

    duration = datetime.now() - startTime

    # #############################################################################
    # postprocessing
    # #############################################################################

    linerThk, insThk, fairThk = (
        designArgs["linerThickness"],
        designArgs["insulationThickness"],
        designArgs["fairingThickness"],
    )
    if designArgs["temperature"] is None:  # liquid, cryo vessel
        auxMasses = [
            getLinerMass(linerTankoh, linerMatName=linerMat, linerThickness=linerThk),
            getInsulationMass(linerTankoh, insulationMatName=insMat, insulationThickness=insThk),
            getFairingMass(linerTankoh, fairingMatName=fairMat, fairingThickness=fairThk),
        ]
    else:
        if designArgs["temperature"] > 33.145:  # compressed gas vessel
            auxMasses = [
                getLinerMass(linerTankoh, linerMatName=linerMat, linerThickness=linerThk),
                0.0,
                0.0,
            ]
        else:  # liquid, cryo vessel
            auxMasses = [
                getLinerMass(linerTankoh, linerMatName=linerMat, linerThickness=linerThk),
                getInsulationMass(linerTankoh, insulationMatName=insMat, insulationThickness=insThk),
                getFairingMass(linerTankoh, fairingMatName=fairMat, fairingThickness=fairThk),
            ]
    totalMass = np.sum([frpMass] + auxMasses + [fittingMass])
    linerInnerTankoh = linerTankoh.getLinerResizedByThickness(-1 * linerThk)
    volume = linerInnerTankoh.volume / 1e6  # Volume considering liner
    if not _parameterNotSet(designArgs, "h2Mass"):
        h2Mass = designArgs["h2Mass"]
    else:
        h2Mass = getMassByVolume(
            volume / 1e3, designArgs["pressure"], designArgs["maxFill"], temperature=designArgs["temperature"]
        )
    gravimetricIndex = h2Mass / (totalMass + h2Mass)

    results = {
        "shellMass": frpMass,
        "linerMass": auxMasses[0],
        "insulationMass": auxMasses[1],
        "fairingMass": auxMasses[2],
        "fittingMass": fittingMass,
        "totalMass": totalMass,
        "volume": volume,
        "h2Mass": h2Mass,
        "area": area,
        "lengthAxial": linerMuWind.linerLength,
        "numberOfLayers": vessel.getNumberOfLayers(),
        "cylinderThickness": cylinderThickness,
        "maxThickness": maxThickness,
        "reserveFactor": reserveFac,
        "gravimetricIndex": gravimetricIndex,
        "stressRatio": stressRatio,
        "hoopHelicalRatio": hoopByHelicalFrac,
        "iterations": iterations,
        "duration": duration,
        "frpMassStrengthOnly": frpMassStrengthOnly,
        "frpMassFatigueOnly": frpMassFatigueOnly,
        "puckMax": puckMax,
        "fatigueFactor": frpMassFatigueOnly / frpMassStrengthOnly,
        "angles": angles,
        "hoopLayerShifts1": hoopLayerShiftsSide1,
        "hoopLayerShifts2": hoopLayerShiftsSide2,
    }
    if designArgs["useBucklingCriterion"]:
        results.update(
            {
                "bucklingFactorMass": bucklingFactorMass,
                "bucklingFactorSkinThickness": bucklingFactorSkinThickness,
                "numberOfRings": buckResultDict["numberOfRings"],
                "ringWebThickness": buckResultDict["ringLayerThickness"]
                * len(buckResultDict["ringLayup"])
                * 2,  # *2 due to doulbe layup of web, and single layup of foot
                "ringMass": ringMass,
                "h2Mass": 0,
                "gravimetricIndex": 0,
            }
        )

    saveParametersAndResults(designArgs["runDir"], results=results)
    anglesShiftsFilename = os.path.join(designArgs["runDir"], "anglesAndShifts" + ".yaml")
    writeParametersToYAML(
        {"initialAnglesAndShifts": [angles, hoopLayerShiftsSide1, hoopLayerShiftsSide2]}, anglesShiftsFilename
    )
    vessel.securityFactor = designArgs["safetyFactor"] * designArgs["valveReleaseFactor"]
    vessel.burstPressure = burstPressure * 10
    vessel.calculateVesselStatistics()
    vessel.saveToFile(vesselFilename)  # save vessel
    updateName(vesselFilename, tankname, ["vessel"])
    copyAsJson(vesselFilename, "vessel")

    # save winding results
    windingResults = pychain.winding.VesselWindingResults()
    windingResults.buildFromVessel(vessel)
    windingResults.saveToFile(windingResultFilename)
    copyAsJson(windingResultFilename, "wresults")

    # write nodal layer results dataframe to csv
    mandrelCoordinatesDataframe = getMandrelNodalCoordinates(linerMuWind, dome2 is None)
    layerCoordinatesDataframe = getLayerNodalCoordinates(windingResults, dome2 is None)
    nodalResultsDataframe = pd.concat([mandrelCoordinatesDataframe, layerCoordinatesDataframe], join="outer", axis=1)
    nodalResultsDataframe.to_csv(os.path.join(runDir, "nodalResults.csv"), sep=";")

    saveLayerBook(runDir, tankname)

    log.info(f"iterations {iterations}, runtime {duration.seconds} seconds")
    log.info("FINISHED")

    return results


if __name__ == "__main__":
    if 1:
        params = {"configFile": "hytazer_smr_iff_outer_tank.yaml"}
        params = {"configFile": "exact2_D250.yaml"}
        params["CPACSConfigFile"] = r"C:\PycharmProjects\tankoh2\cpacs\defaultParametricCryoTank.xml"
        params["tankuID"] = "CryoFuelTank"
    elif 1:
        # params = parameters.defaultUnsymmetricDesign.copy()
        params = {"configFile": "dLight_reference_opt.yaml"}
        createDesign(**params)
