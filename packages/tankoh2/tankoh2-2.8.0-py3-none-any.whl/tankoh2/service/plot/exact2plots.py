# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""Create plots for vph project - will be removed/reintegrated elsewhere in the future"""
import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm, ticker

from tankoh2.control.genericcontrol import parseConfigFile, parseDesignArgs
from tankoh2.design.metal.material import getMaterialDefinitionMetal
from tankoh2.geometry.dome import getDome
from tankoh2.geometry.liner import Liner
from tankoh2.mechanics.pbucklcritcyl_SP8007 import (
    BucklingConstraintFunction,
    getCritPressureGlobalBuck,
    getCritPressureLocalBuck,
    getRingParameterDict,
    optTargetFunctionVesselMass,
    stabilityOpt,
)
from tankoh2.sensitivityAnalysis.parameterSets import parameterSet


def plotTankMassesWithSurrogate():

    dcyl = np.array([3296, 3462])
    lcyl = np.array([3693, 3859])
    params = pd.DataFrame({"dcyl": dcyl, "lcyl": lcyl, "lcylByR": lcyl * 2 / dcyl}, index=["inner", "outer"])
    print(params)

    iv = [823, 825, 249, 260]
    ov = [966, 1035, 552, 529]
    index = ["Alu 6061", "Alu 6061\nsurrogate", "CFRP", "CFRP\nsurrogate"]
    df = pd.DataFrame(
        {
            "outer vessel": ov,
            "inner vessel": iv,
        },
        index=index,
    )
    print(df)
    ax = df.plot.bar(stacked=True, color=("#009BD1", "#FFEB72"), width=0.7)
    ax.set_ylabel("Mass [kg]")
    ax.set_title("Mass comparison")
    plt.xticks(rotation=0)

    plt.show()


def plotTankMassBreakdown():

    mInnerFatigue = np.array([823, 249.0])
    mInnerStrength = mInnerFatigue / np.array([1.7085, 1])
    mOuterStabRing = np.array([192, 84.0])
    mOuterStabSkin = np.array([966, 552.0]) - mOuterStabRing
    mOuterFatigue = mOuterStabSkin / np.array([1.27, 2.55])
    mOuterStrength = mOuterFatigue / np.array([2.817, 1])
    df = pd.DataFrame(
        [mOuterStrength, mOuterFatigue, mOuterStabSkin, mOuterStabRing, mInnerFatigue, mInnerStrength],
        index=[
            "mOuterStrength",
            "mOuterFatigue",
            "mOuterStabSkin",
            "mOuterStabRing",
            "mInnerFatigue",
            "mInnerStrength",
        ],
        columns=["Alu 6061", "CFRP"],
    )
    print(df)

    mInnerFatigue -= mInnerStrength
    mOuterStabSkin -= mOuterFatigue
    mOuterFatigue -= mOuterStrength

    df = pd.DataFrame(
        [mOuterStrength, mOuterFatigue, mOuterStabSkin, mOuterStabRing, mInnerFatigue, mInnerStrength],
        index=[
            "mOuterStrength",
            "mOuterFatigue",
            "mOuterStabSkin",
            "mOuterStabRing",
            "mInnerFatigue",
            "mInnerStrength",
        ],
        columns=["Alu 6061", "CFRP"],
    )
    print(df)
    indexes = np.arange(len(mInnerStrength))
    width = 0.4
    p1 = plt.bar(indexes, mOuterStrength, width, color="#00668D")
    p2 = plt.bar(indexes, mOuterFatigue, width, color="#009BD1", bottom=mOuterStrength)
    p3 = plt.bar(indexes, mOuterStabSkin, width, color="#1DBADF", bottom=mOuterStrength + mOuterFatigue)
    p4 = plt.bar(
        indexes, mOuterStabRing, width, color="#94D4EE", bottom=mOuterStrength + mOuterFatigue + mOuterStabSkin
    )
    p5 = plt.bar(
        indexes,
        mInnerStrength,
        width,
        color="#E0B02E",
        bottom=mOuterStrength + mOuterFatigue + mOuterStabSkin + mOuterStabRing,
    )
    p6 = plt.bar(
        indexes,
        mInnerFatigue,
        width,
        color="#FFEB72",
        bottom=mOuterStrength + mOuterFatigue + mOuterStabSkin + mOuterStabRing + mInnerStrength,
    )

    plt.ylabel("Mass [kg]")
    # plt.ylim(0,1700)
    plt.title("Mass breakdown of inner and outer vessel")
    plt.xticks(indexes, ("Aluminium 6061", "CFRP"))
    plt.legend(
        (p1[0], p2[0], p3[0], p4[0], p5[0], p6[0]),
        (
            "OV mass strength",
            "OV mass addition fatigue",
            "OV mass addition stability",
            "OV mass addition ring",
            "IV mass strength",
            "IV mass addition fatigue",
        ),
        loc=(0.33, 0.5),
    )

    plt.show()


def plotTransverseTension():

    strengths = np.array([44, 84, 183, 115, 99.5, 43.5])
    # strengths = np.array([44, 84,0,0,0,0])
    # strengths = np.array([44, 84,183,115,0,0])
    index = [
        "293K",
        "77K",
        "in-situ strength\ninner ply",
        "in-situ strength\nouter ply",
        "knockdown: use\nhalf insitu change",
        "thermomechanical\nstress",
    ]
    df = pd.DataFrame({"strengths": strengths}, index=index)
    print(df)
    fig = plt.figure(figsize=(8, 4.5))

    indexes = np.arange(len(strengths))
    plt.bar(indexes, strengths, width=0.5, color="#009BD1")
    ax = fig.get_axes()[0]
    plt.xticks(indexes, index)
    plt.subplots_adjust(left=None, bottom=0.36, right=None, top=None, wspace=None, hspace=None)

    plt.ylim(0, 190)
    ax.set_ylabel("Transverse tension strength [MPa]")
    ax.set_title("Strength definition")
    plt.xticks(rotation=45)

    plt.show()


def getLiner(r=1200, lcyl=1000, domeType="isotensoid"):
    dome = getDome(r, 10, domeType)
    liner = Liner(dome, lcyl)
    return liner


def getVesselInputs(configFileName, windingOrMetal):
    paramKwArgs = parseConfigFile(configFileName)
    paramKwArgs, _, _ = parseDesignArgs(paramKwArgs, windingOrMetal)
    liner = getLiner(paramKwArgs["dcyl"] / 2, paramKwArgs["dcyl"] / 2 * paramKwArgs["lcylByR"], paramKwArgs["domeType"])
    ringParameterDict = getRingParameterDict(paramKwArgs)
    return liner, ringParameterDict, paramKwArgs


def getVesselInputsMetal():
    liner, ringParameterDict, paramKwArgs = getVesselInputs("hytazer_smr_iff_2.0bar_final_metal", "metal")
    material = getMaterialDefinitionMetal(paramKwArgs["materialName"])
    layer_thickness_cylinder = 4
    layup_cylinder = [0]
    ringParameterDict["ringLayup"] = layup_cylinder
    ringParameterDict["ringLayerThickness"] = 2
    return liner, layer_thickness_cylinder, layup_cylinder, material, ringParameterDict


def plotBuckOptProblem(xIndex=0, yIndex=2, fixedParamIndex=1, show=True, save=False):
    liner, layer_thickness_cylinder, layup_cylinder, material, ringParameterDict = getVesselInputsMetal()
    args = [
        liner,
        material,
        [0],
        ringParameterDict["ringCrossSectionType"],
        [0],
        ringParameterDict["ringHeight"],
        ringParameterDict["ringFootWidth"],
    ]

    paramNames = ["cylinder skin thickness", "ring thickness", "number of rings"]
    paramUnits = [" [mm]", " [mm]", ""]
    params_result = [3.99800402, 1.0, 25.0]
    bounds = np.array([[2, 1.0, 5.0], [16, 16, 25.0]])

    N = 21
    x = np.linspace(bounds[0, xIndex], bounds[1, xIndex], N)
    y = np.linspace(bounds[0, yIndex], bounds[1, yIndex], N)
    X, Y = np.meshgrid(x, y)

    localBuckConstraintFunction = BucklingConstraintFunction(liner, material, layup_cylinder, True, False)
    localBuckConstraintFunction.getCritPressureLocalBuck
    globalBuckConstraintFunction = BucklingConstraintFunction(
        liner, material, layup_cylinder, ringParameterDict, True, False
    )
    globalBuckConstraintFunction.getCritPressureGlobalBuck

    mass, localStabResults, globalStabResults = [], [], []
    params = [0, 0, 0]
    for XLine, YLine in zip(X, Y):
        massLine, locLine, globLine = [], [], []
        for Xitem, Yitem in zip(XLine, YLine):
            params[xIndex] = Xitem
            params[yIndex] = Yitem
            params[fixedParamIndex] = params_result[fixedParamIndex]
            massLine.append(optTargetFunctionVesselMass(params, args))
            locLine.append(localBuckConstraintFunction.getCritPressureLocalBuck(params))
            globLine.append(globalBuckConstraintFunction.getCritPressureGlobalBuck(params))
        mass.append(massLine)
        localStabResults.append(locLine)
        globalStabResults.append(globLine)

    fig, ax = plt.subplots()
    cs = ax.contourf(
        X,
        Y,
        mass,
    )
    cbar = fig.colorbar(cs, label=f"Vessel mass [kg]")

    stabLineLevels = [0.1, 0.2, 0.4, 0.8]
    CS = ax.contour(X, Y, localStabResults, stabLineLevels, colors="k")
    ax.clabel(CS, fontsize=10)
    CS = ax.contour(X, Y, globalStabResults, stabLineLevels, colors="w")
    ax.clabel(CS, fontsize=10)
    sc = ax.scatter([params_result[xIndex]], [params_result[yIndex]], s=50, color="orange", label="Design point")
    ax.set_xlabel(paramNames[xIndex])
    ax.set_ylabel(paramNames[yIndex])
    ax.set_title(f"Cylinder stability with fixed {paramNames[fixedParamIndex]}", pad=18)

    plt.legend()
    if save:
        folder = r"C:\Users\freu_se\Documents\Projekte\EXACT2\08_Aussendarstellung\03_Konferenzen\DLRK 2025\presentation\buck plots"
        plt.savefig(os.path.join(folder, f"{paramNames[xIndex]}_{paramNames[yIndex]}.png"))
    if show:
        plt.show()


if __name__ == "__main__":
    plt.rcParams.update({"font.size": 14})
    if 0:
        plotBuckOptProblem()
    else:
        for x, y, fixed in [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]:
            plotBuckOptProblem(x, y, fixed, False, True)
