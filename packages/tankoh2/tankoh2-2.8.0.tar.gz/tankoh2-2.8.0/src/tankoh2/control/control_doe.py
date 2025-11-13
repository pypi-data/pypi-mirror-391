# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""create DOEs and execute design workflow

Caution:
This module requires delismm as additional package!
"""
import csv
import os
from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime
from multiprocessing import cpu_count
from os.path import join

import numpy as np
from delismm.control.tank import getKrigings
from delismm.model.customsystemfunction import AbstractTargetFunction, BoundsHandler
from delismm.model.doe import AbstractDOE, DOEfromFile, FullFactorialDesign, LatinizedCentroidalVoronoiTesselation
from delismm.model.samplecalculator import getY
from patme.service.systemutils import getRunDir

import tankoh2
from tankoh2 import log, programDir
from tankoh2.arguments import resultKeyToUnitDict
from tankoh2.control.control_cryotank import createDesign as createDesignCryotank
from tankoh2.control.control_cryotank import updateKwargsForOuterVessel
from tankoh2.control.control_metal import createDesign as createDesignMetal
from tankoh2.control.control_winding import createDesign as createDesignWinding
from tankoh2.control.genericcontrol import parseConfigFile
from tankoh2.design.existingdesigns import DLightDOE, DLightDOE_T1100, vphDesign1_isotensoid
from tankoh2.service.exception import Tankoh2Error
from tankoh2.service.plot.doeplot import plotExact2GeometryRange, plotGeometryRange

useMetal = True
resultNames = [
    "shellMass",
    "linerMass",
    "insulationMass",
    "fairingMass",
    "totalMass",
    "volume",
    "h2Mass",
    "area",
    "lengthAxial",
    "numberOfLayers",
    "cylinderThickness",
    "maxThickness",
    "reserveFactor",
    "gravimetricIndex",
    "stressRatio",
    "hoopHelicalRatio",
    "iterations",
    "bucklingFactorMass",
    "bucklingFactorSkinThickness",
    "numberOfRings",
    "ringWebThickness",
    "ringMass",
]
if useMetal:
    resultNames = [
        "totalMass",
    ]

allowedDesignNames = {
    "dlight",
    "exact_cyl_isotensoid",
    "exact_conical_isotensoid",
    "vph2",
    "exact2",
    "exact2_large_designspace",
    "exact2_large_designspace_buck",
}
argParser = ArgumentParser()
argParser.add_argument(
    "--adaptExact2ParameterKey",
    help="parameter key to adapt in the design space",
    default="",
)
argParser.add_argument(
    "--designName",
    help=f"name of the design and bounds to return. Not case sensitive! Allowed names: {allowedDesignNames}",
    default="exact2",
)
argParser.add_argument(
    "--resumeFolder",
    help=f"path to a folder with sampleY results that should be resumed",
    default="",
)
argParser.add_argument("--doSensitivityStudy", action="store_true")
argParser.add_argument("--useBucklingCriterion", action="store_true")
parsedOptions = argParser.parse_args()
adaptExact2ParameterKey = parsedOptions.adaptExact2ParameterKey
if adaptExact2ParameterKey.lower() == "none":
    adaptExact2ParameterKey = ""
designName = parsedOptions.designName.lower()
resumeFolder = parsedOptions.resumeFolder
doSensitivityStudy = parsedOptions.doSensitivityStudy
useBucklingCriterion = parsedOptions.useBucklingCriterion


class AbstractCaller:

    def __init__(self, designKwargs):
        if "configFile" in designKwargs:
            configArgs = parseConfigFile(designKwargs["configFile"])
            configArgs["materialName"] = "CFRP_HyMod_cryo_no_thinply_half_insitu"
            configArgs.update(designKwargs)
            self.designKwargs = configArgs
        else:
            self.designKwargs = designKwargs
        self.allowFailedSample = True

    def _callMethod(self, inputDict):
        raise NotImplementedError("must be implemented by subclass")

    def _call(self, parameters):
        """call function for the model"""
        paramDict = OrderedDict(zip(self.parameterNames, parameters))
        inputDict = OrderedDict()
        inputDict.update(self.designKwargs)
        inputDict.update(paramDict)
        inputDict["minPressure"] = inputDict["pressure"] / 2

        if inputDict["useBucklingCriterion"] == True:
            updateKwargsForOuterVessel(inputDict)

        resultDict = self._callMethod(inputDict)
        result = [resultDict.get(key, None) for key in self.resultNames]
        return result


class TankWinder(AbstractCaller, AbstractTargetFunction):
    """"""

    name = "tank winder"
    resultNames = [
        "shellMass",
        "linerMass",
        "insulationMass",
        "fairingMass",
        "totalMass",
        "volume",
        "h2Mass",
        "area",
        "lengthAxial",
        "numberOfLayers",
        "cylinderThickness",
        "maxThickness",
        "reserveFactor",
        "gravimetricIndex",
        "stressRatio",
        "hoopHelicalRatio",
        "iterations",
        "ringMass",
        "numberOfRings",
        "bucklingFactorMass",
        "bucklingFactorSkinThickness",
    ]

    def __init__(self, lb, ub, runDir, designKwargs):
        """"""
        AbstractTargetFunction.__init__(self, lb, ub, resultNames=self.resultNames)
        AbstractCaller.__init__(self, designKwargs)
        if not designKwargs.get("useBucklingCriterion", False):
            self.resultNames = self.resultNames[:-4]
        if 0:
            self.doParallelization = []
        else:
            self.doParallelization = ["local"]
            import matplotlib

            # use Agg as backend instead of tkinter.
            # tkinter is not thread safe and causes problems with parallelization when creating plots
            # on the other hand Agg is non-interactive, and thus cannot be shown plt.show()
            matplotlib.use("Agg")

        self.runDir = runDir

        self.asyncMaxProcesses = int(np.ceil(cpu_count() * 2 / 3))

    def _callMethod(self, inputDict):
        """call function for the model"""
        runDir = getRunDir(basePath=join(self.runDir), useMilliSeconds=True)
        inputDict["runDir"] = runDir
        return createDesignWinding(**inputDict)

    def getNumberOfNewJobs(self):
        return self.asyncMaxProcesses


class TankMetal(AbstractCaller, AbstractTargetFunction):
    """"""

    name = "tank metal"
    resultNames = [
        "totalMass",
        "wallThickness",
        "fatigueFactor",
        "ringMass",
        "numberOfRings",
        "bucklingFactorMass",
        "bucklingFactorSkinThickness",
    ]

    def __init__(self, lb, ub, runDir, designKwargs):
        """"""
        AbstractTargetFunction.__init__(self, lb, ub, resultNames=self.resultNames)
        AbstractCaller.__init__(self, designKwargs)
        if not designKwargs.get("useBucklingCriterion", False):
            self.resultNames = self.resultNames[:-4]

    def _callMethod(self, inputDict):
        """call function for the model"""
        return createDesignMetal(**inputDict)


class CryoTankMetal(TankMetal):
    """for inner and outer vessel combined"""

    name = "cryo tank metal"
    resultNames = [
        "totalMass",
        "innerVessel_totalMass",
        "innerVessel_wallThickness",
        "innerVessel_fatigueFactor",
        "outerVessel_totalMass",
        "outerVessel_ringMass",
        "outerVessel_numberOfRings",
        "outerVessel_wallThickness",
        "outerVessel_fatigueFactor",
        "outerVessel_bucklingFactorMass",
        "outerVessel_bucklingFactorSkinThickness",
        "outerVessel_outerRadius",
    ]

    def _callMethod(self, inputDict):
        """call function for the model"""
        return createDesignCryotank(**inputDict)


def _getExtendedBounds(lb, ub, keys):
    """Extends bounds of all keys in keys"""
    for key in keys:
        lb[key], ub[key] = ub[key], ub[key] + (ub[key] - lb[key])
    return lb, ub


def getDesignAndBounds(name, innerAndOrOuterVessel, adaptExact2ParameterKey=None):
    """returns base design properties (like in existingdesigns) of a tank and upper/lower bounds for the doe

    :param name: name of the design and bounds to return. Not case sensitive!
    :param innerAndOrOuterVessel: [inner, outer, both]

    :return: designKwargs, lowerBoundDict, upperBoundDict, numberOfSamples
    """
    if name not in allowedDesignNames:
        raise Tankoh2Error(f"Parameter name={name} unknown. Allowed names: {allowedDesignNames}")
    tankRunnerClass = TankWinder
    name = name.lower()
    numberOfSamples = 101
    inputUnits = ["[mm]", "[mm]", "[MPa]"]
    doeClass = LatinizedCentroidalVoronoiTesselation
    if name == "dlight":
        lb = OrderedDict(
            [("dcyl", 200.0), ("lcyl", 800), ("pressure", 130), ("helicalDesignFactor", 1.0)]
        )  # [mm, mm , MPa]
        ub = OrderedDict([("dcyl", 800.0), ("lcyl", 6000), ("pressure", 190), ("helicalDesignFactor", 1.25)])
        inputUnits = ["[mm]", "[mm]", "[MPa]", "[-]"]
        designKwargs = DLightDOE_T1100
    if name in ["exact2", "exact2_large_designspace", "exact2_large_designspace_buck"]:
        lb = OrderedDict([("dcyl", 800.0), ("lcylByR", 0.1), ("pressure", 0.05)])
        ub = OrderedDict([("dcyl", 4800.0), ("lcylByR", 10.1), ("pressure", 0.65)])
        inputUnits = ["[mm]", "[-]", "[MPa]"]
        if name in ["exact2_large_designspace", "exact2_large_designspace_buck"]:
            ub = {key: value + (value - lb[key]) for key, value in ub.items()}
        if adaptExact2ParameterKey:
            # extend parameter space in one parameter direction
            lb, ub = _getExtendedBounds(lb, ub, [adaptExact2ParameterKey])
            numberOfSamples = 21
        if name == "exact2_large_designspace_buck":
            lb.pop("pressure")
            ub.pop("pressure")
            inputUnits = inputUnits[:2]
        metalStr = "_metal" if useMetal else ""
        designKwargs = OrderedDict([("configFile", f"hytazer_smr_iff_2.0bar_final{metalStr}.yaml")])
        designKwargs["windingOrMetal"] = "metal" if useMetal else "winding"
        if designKwargs["windingOrMetal"] == "metal":
            designKwargs["materialName"] = "alu6061T6"
    elif name == "exact_cyl_isotensoid":
        lb = OrderedDict([("dcyl", 1000.0), ("lcyl", 150), ("pressure", 0.1)])  # [mm, mm , MPa]
        ub = OrderedDict([("dcyl", 4000.0), ("lcyl", 3000), ("pressure", 1)])
        designKwargs = vphDesign1_isotensoid.copy()
        designKwargs["targetFuncWeights"] = [1.0, 0.2, 0.0, 0.0, 0, 0]
        designKwargs["verbosePlot"] = True
        designKwargs["numberOfRovings"] = 12
        designKwargs.pop("lcyl")
        designKwargs.pop("safetyFactor")
    elif name == "exact_conical_isotensoid":
        inputUnits = ["[mm]", "[mm]", "[MPa]", "[-]", "[-]"]
        lb = OrderedDict([("dcyl", 1000.0), ("lcyl", 150), ("pressure", 0.1), ("alpha", 0.2), ("beta", 0.5)])
        ub = OrderedDict([("dcyl", 4000.0), ("lcyl", 3000), ("pressure", 1), ("alpha", 0.8), ("beta", 2)])
        designKwargs = vphDesign1_isotensoid.copy()
        designKwargs.pop("safetyFactor")
        addArgs = OrderedDict(
            [
                ("targetFuncWeights", [1.0, 0.2, 1.0, 0.0, 0, 0]),
                ("verbosePlot", True),
                ("numberOfRovings", 12),
                ("gamma", 0.3),
                ("domeType", "conicalIsotensoid"),
                ("dome2Type", "isotensoid"),
                ("nodeNumber", 1000),
            ]
        )
        designKwargs.update(addArgs)
    elif name == "vph2":
        lb = OrderedDict([("minPressure", 0.0), ("safetyFactor", 1)])  # [MPa, -]
        ub = OrderedDict([("minPressure", 0.18), ("safetyFactor", 2.5)])
        designKwargs = {"configFile": "vph2_smr_iff_2bar_param_study"}
        doeClass = FullFactorialDesign
        sampleCount1d = 5
        numberOfSamples = sampleCount1d**2

    if designKwargs["windingOrMetal"] == "metal":
        tankRunnerClass = TankMetal
    if innerAndOrOuterVessel == "outer":
        designKwargs["useBucklingCriterion"] = True
    elif innerAndOrOuterVessel == "both":
        tankRunnerClass = CryoTankMetal

    if 0:  # for testing
        numberOfSamples = 5
        designKwargs["maxLayers"] = 3

    return designKwargs, lb, ub, numberOfSamples, doeClass, inputUnits, tankRunnerClass


def collectParallelYResultsFromSampleXYFiles(runDir, winder, names, lb, ub):
    """on parallel runs, collect the results that are already there"""
    finalSampleYFile = join(runDir, "sampleY.pickle")
    if os.path.exists(finalSampleYFile):
        raise FileExistsError(f"Target file already exists: {finalSampleYFile}")

    sampleX, sampleY = [], []
    for fileOrFolder in os.listdir(runDir):
        if os.path.isfile(fileOrFolder):
            continue

        parallelRunFolder = join(runDir, fileOrFolder)
        sampleXFile = join(parallelRunFolder, "sampleX_bounds.txt")
        sampleYFile = join(parallelRunFolder, "sampleY.pickle")
        if not os.path.exists(sampleXFile):
            continue

        log.info(f"add from folder: {fileOrFolder}")
        sampleXBoundsParallel = np.loadtxt(os.path.join(parallelRunFolder, "sampleX_bounds.txt"), encoding="utf8").T
        sampleYParallel = AbstractDOE.ysFromFile(os.path.join(parallelRunFolder, "sampleY.pickle"))
        if sampleYParallel is None:
            sampleYParallel = []

        sampleX.extend(sampleXBoundsParallel.T)
        sampleYParallel = list(sampleYParallel)
        sampleCountDiff = sampleXBoundsParallel.shape[1] - len(sampleYParallel)
        if sampleCountDiff > 0:
            sampleYParallel.extend([[None]] * (sampleCountDiff))
        sampleY.extend(sampleYParallel)

    sampleX = np.array(sampleX).T
    doe = AbstractDOE(*sampleX.shape[::-1])
    doe.sampleXNormalized = sampleX
    _storeSamples(doe, runDir, winder, sampleY, lb.keys(), lb, ub, scaleToBounds=False)


def collectYResultsFromAllResultsFile(runDir, tankRunner):
    """read results from /all_parameters_and_results.txt files in finalized runs"""

    results = list()
    results_path = runDir
    all_folders = [name for name in os.listdir(results_path) if os.path.isdir(join(results_path, name))]

    for count, filePath in enumerate(all_folders):
        worker_results_path = results_path + "/" + filePath
        all_sub_folders = [
            name for name in os.listdir(worker_results_path) if os.path.isdir(join(worker_results_path, name))
        ]
        for count, filePath in enumerate(all_sub_folders):

            with open(worker_results_path + "/" + filePath + "/all_parameters_and_results.txt", "r") as file:
                reader = csv.reader(file, delimiter="|")
                txt_reader = [x for x in reader]

            run_results = []
            for row in txt_reader:
                try:
                    entry = row[0].replace(" ", "")
                    if entry in tankRunner.resultNames:
                        run_results.append(float(row[2].replace(" ", "")))
                except (IndexError, ValueError):
                    continue

            results.append(run_results)
    return results


def createTankResults(
    name,
    innerAndOrOuterVessel,
    sampleXFile,
    designKwargs,
    lb,
    ub,
    numberOfSamples,
    doeClass,
    sampleYFolder="",
    basePath=None,
    runDirExtension="",
):
    """

    :param name: name of the design and bounds to return. Not case-sensitive!
    :param innerAndOrOuterVessel: [inner, outer, both]
    :param sampleXFile: path and filename to a list with sampleX values
    :param designKwargs:
    :param lb:
    :param ub:
    :param numberOfSamples:
    :param doeClass:
    :param sampleYFolder: path to a folder with sampleY results
    :param basePath: path to the base folder
    :param runDirExtension:
    :return:
    """
    startTime = datetime.now()

    designKwargs, lb, ub, numberOfSamples, doeClass, inputUnits, runnerClass = getDesignAndBounds(
        name, innerAndOrOuterVessel, adaptExact2ParameterKey
    )

    inputNames = list(lb.keys())
    if resumeFolder:
        runDir = resumeFolder
        resumeSamples = True
        if not sampleXFile:
            raise Tankoh2Error(
                "You're attempting to resume a doe without setting the previously used sampleXFile. This will lead to errors."
            )
    else:
        runDir = getRunDir(
            f"doe_{name}",
            basePath=basePath if basePath is not None else join(programDir, "tmp"),
            runDirExtension=runDirExtension,
        )
        resumeSamples = False

    runner = runnerClass(lb, ub, runDir, designKwargs)
    if sampleXFile:
        doe = DOEfromFile(sampleXFile)
    else:
        doe = doeClass(numberOfSamples, len(inputNames))

    sampleX = BoundsHandler.scaleToBoundsStatic(doe.sampleXNormalized, list(lb.values()), list(ub.values()))
    sampleXFile = join(runDir, "sampleX.txt")
    doe.xToFile(sampleXFile)
    doe.xToFileStatic(join(runDir, "sampleX_bounds.txt"), sampleX)
    if sampleYFolder:
        sampleY = collectYResultsFromAllResultsFile(sampleYFolder, runner)
    else:
        sampleY = getY(sampleX, runner, verbose=True, runDir=runDir, resumeSamples=resumeSamples, staggerStart=2)

    _storeSamples(doe, runDir, runner, sampleY, inputNames, lb, ub)

    duration = datetime.now() - startTime
    log.info(f"runtime {duration.seconds} seconds")
    return sampleXFile


def _storeSamples(doe, runDir, runner, sampleY, inputNames, lb, ub, scaleToBounds=True):

    # store samples
    filename = join(runDir, "sampleY.txt")
    if os.path.exists(filename):
        log.error(f"File already exists, not writing: {filename}")
    else:
        doe.yToFile(filename, runner, sampleY)

    filename = join(runDir, "full_doe.txt")
    if os.path.exists(filename):
        log.error(f"File already exists, not writing: {filename}")
    else:
        doe.xyToFile(
            filename,
            sampleY,
            headerNames=list(inputNames) + runner.resultNames,
            lb=lb,
            ub=ub,
            scaleToBounds=scaleToBounds,
        )


def main():
    import delismm.model.samplecalculator

    delismm.model.samplecalculator.manualMinParallelProcesses = int(np.ceil(cpu_count() / 2))

    innerAndOrOuterVessel = "outer"
    onlyCollectSamples = False
    createDoe = False
    plotDoe = False
    plotExact2Doe = False
    createSurrogate = True
    sampleXFile = ""
    if resumeFolder:
        runDir = None
    else:
        runDir = getRunDir(
            "tank_surrogates" + (f"_{adaptExact2ParameterKey}" if adaptExact2ParameterKey and createDoe else ""),
            basePath=join(tankoh2.programDir, "tmp"),
            runDirExtension=("_buck_localOpt" if useBucklingCriterion else ""),
        )
    if plotExact2Doe:
        if adaptExact2ParameterKey != "":
            raise Tankoh2Error("plotExact2Doe is not supported for adaptExact2ParameterKey")
    # mmRunDir = mmRunDir[:-7]
    resultNamesLog10 = [
        ("totalMass", True),
        # ("volume", True),
        # ("area", False),
        # ("lengthAxial", False),
        ("cylinderThickness", False),
        # ("ringMass", True),
        # ("ringWebThickness", False),
        # ("gravimetricIndex", False),
    ]

    designKwargs, lb, ub, numberOfSamples, doeClass, inputUnits, tankRunnerClass = getDesignAndBounds(
        designName, innerAndOrOuterVessel, adaptExact2ParameterKey
    )

    resultNamesIndexesLog10 = [
        (f"{resultName}[{resultKeyToUnitDict[resultName]}]", tankRunnerClass.resultNames.index(resultName), doLog10)
        for resultName, doLog10 in resultNamesLog10
        if resultName in tankRunnerClass.resultNames
    ]
    designKwargs, lb, ub, numberOfSamples, doeClass, units = getDesignAndBounds(designName, adaptExact2ParameterKey)

    if onlyCollectSamples:
        collectParallelYResultsFromSampleXYFiles(
            r"C:\Users\freu_se\Documents\pycharmProjects\tankoh2\tmp\tank_surrogates_20250915_081142_buck_globalOpt\doe_exact2_large_designspace_buck_20250915_081142",
            TankWinder(lb, ub, runDir, designKwargs),
            lb.keys(),
            lb,
            ub,
        )
        return

    if designName == "exact_cyl_isotensoid":
        sampleXFile = "" + r"C:\PycharmProjects\tankoh2\tmp\doe_exact_cyl_isotensoid_20230106_230150/sampleX.txt"
        surrogateDir = "" + r"C:\PycharmProjects\tankoh2\tmp\tank_surrogates_20230109_180336"
    elif designName == "exact_conical_isotensoid":
        sampleXFile = "" + r"C:\PycharmProjects\tankoh2\tmp\doe_exact_conical_isotensoid_20230111_180256/sampleX.txt"
        surrogateDir = ""  # + r'C:\PycharmProjects\tankoh2\tmp\tank_surrogates_20230109_180336'
    elif designName == "exact2_large_designspace":
        sampleXFile = r"C:\Users\freu_se\Documents\Projekte\EXACT2\05_Abwicklung\STM\Surrogate models\Model v1.1\Metal\sampleX.txt"
        sampleXFile = r"C:\Users\freu_se\Documents\pycharmProjects\tankoh2\tmp\sampleX.txt"
        sampleXFile = r"C:\Users\freu_se\Documents\surrogate V2 for exact2\tank_surrogates_20250912_084219_inner_vessel\doe_exact2_large_designspace_20250912_084219\sampleX.txt"
    elif designName == "exact2_large_designspace_buck":
        sampleXFile = r"C:\Users\freu_se\Documents\surrogate V2 for exact2\samples buck\sampleX.txt"
        sampleXFile = r"C:\Users\freu_se\Documents\pycharmProjects\tankoh2\tmp\tank_surrogates_20250915_081142_buck_globalOpt\doe_exact2_large_designspace_buck_20250915_081142\sampleX.txt"
    elif designName == "exact2":
        sampleXFile = r"C:\PycharmProjects\tankoh2\tmp\exact2_doe_complete_20250409\sampleX.txt"
        surrogateDir = ""
        if adaptExact2ParameterKey:
            sampleXFile = (
                r"C:\PycharmProjects\tankoh2\tmp\exact2_doe_" + adaptExact2ParameterKey + r"_20250409\doe\sampleX.txt"
            )
    elif designName == "dlight":
        sampleXFile = (
            r"C:\Users\jaco_li\Tools\tankoh2\tmp\tank_surrogates_20250801_175648\doe_dlight_20250801_175648\sampleX.txt"
        )
        pass
    else:
        raise Tankoh2Error(f"designName {designName} not supported. Supported are {allowedDesignNames}")
    if sampleXFile:
        log.info(f"Load sampleX file from {sampleXFile}")

    if createDoe:
        if not doSensitivityStudy:
            sampleXFile = createTankResults(
                designName,
                innerAndOrOuterVessel,
                sampleXFile,
                designKwargs,
                lb,
                ub,
                numberOfSamples,
                doeClass,
                basePath=runDir,
            )
        else:
            for parameterName in list(lb.keys())[1:2]:
                createTankResults(
                    designName,
                    innerAndOrOuterVessel,
                    None,
                    designKwargs,
                    {parameterName: lb[parameterName]},
                    {parameterName: ub[parameterName]},
                    11,
                    FullFactorialDesign,
                    basePath=runDir,
                    runDirExtension=f"_{parameterName}",
                )
            return
    if plotDoe:
        doe = DOEfromFile(sampleXFile)
        sampleX = BoundsHandler(lb, ub).scaleToBounds(doe.sampleXNormalized)
        plotGeometryRange(lb, ub, show=True, samples=sampleX, addBox=("exact" in designName), plotDir=runDir)
    if plotExact2Doe:
        sampleXFile = r"C:\Users\freu_se\Documents\Projekte\EXACT2\05_Abwicklung\STM\Surrogate models\Model v1.1\doe v 1.1 bis 2.0\exact2_doe_20250409\doe\sampleX.txt"
        plotExact2GeometryRange(lb, ub, runDir, sampleXFile, show=True)
        plotExact2GeometryRange(lb, ub, runDir, sampleXFile, useLogScale=False, show=False)
    if createSurrogate:
        parameterNames = lb.keys()
        parameterNames = [name + unit for name, unit in zip(parameterNames, inputUnits)]
        krigings = getKrigings(
            os.path.dirname(sampleXFile),
            os.path.dirname(sampleXFile),
            parameterNames,
            resultNamesIndexesLog10,
            nameAddition=("outerVessel_" if useBucklingCriterion else "innerVessel_"),
        )


def joinDoes():
    runMain = True
    if runMain:
        main()
    else:
        targetDoeDir_ = r"C:\PycharmProjects\tankoh2\tmp\exact2_doe_complete_20250409"
        baseDir = r"C:\PycharmProjects\tankoh2\tmp"
        _, lb, ub, _, _, _ = getDesignAndBounds("exact2")
        lb, ub = _getExtendedBounds(lb, ub, lb.keys())
        AbstractDOE.joinDoeResults(
            [
                join(baseDir, doeDir, "run")
                for doeDir in [
                    "exact2_doe_20250409",
                    "exact2_doe_dcyl_20250409",
                    "exact2_doe_lcylByR_20250409",
                    "exact2_doe_pressure_20250409",
                ]
            ],
            targetDoeDir_,
            TankWinder(lb, ub, targetDoeDir_, {}),
            list(lb.keys()),
        )


if __name__ == "__main__":

    main()
