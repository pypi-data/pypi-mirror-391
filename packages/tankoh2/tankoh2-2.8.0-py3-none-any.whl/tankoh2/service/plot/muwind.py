# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""plot functions for µWind specific values"""
import itertools
import os
from copy import deepcopy

import numpy as np
from matplotlib import colormaps, colors
from matplotlib import pylab as plt
from matplotlib import rcParams

from tankoh2.design.winding.solver import targetFuncNames
from tankoh2.design.winding.windingutils import isHoopLayer
from tankoh2.service.plot.generic import plotDataFrame, saveShowClose
from tankoh2.settings import settings


def plotPuckAndTargetFunc(
    puck,
    anglesShifts,
    plotName,
    runDir,
    useFibreFailure,
    show,
    verbosePlot,
    tfValues=None,
    newAngleShift=None,
    elemIdxmax=None,
    hoopStart=None,
    hoopEnd=None,
    newDesignIndexes=None,
    targetFuncScaling=None,
    symTank=True,
    colorLayersBy="default",
):
    """"""
    puckForPlot = deepcopy(puck)
    puckForPlot.index = puckForPlot.index + 0.5
    puckLabelName = "max puck fibre failure" if useFibreFailure else "max puck inter fibre failure"
    useTwoPlots = verbosePlot and tfValues is not None
    fig, axs = plt.subplots(1, 2 if useTwoPlots else 1, figsize=(16 if useTwoPlots else 10, 7))
    if useTwoPlots:
        plotTargetFunc(
            axs[1], tfValues, newAngleShift, puckLabelName, targetFuncScaling, None, None, False, symTank=symTank
        )
        ax = axs[0]
    else:
        ax = axs  # if only one subplot is used, axs is no iterable
    # Plot Data Frame
    # Use these lines to plot imported plots saved through muwind gui
    # AbqAxSolid_FF = pandas.read_csv("AbqAxSolid_FF.csv",delimiter=";").iloc[:, 4:]/1000
    # AbqAxSolid_FF[AbqAxSolid_FF < 0.55] = np.nan

    angles = [angleShift[0] for angleShift in anglesShifts]
    hoopLayerIndexes = np.argwhere([isHoopLayer(angle) for angle in angles])
    puckForPlot.columns = ["lay{}_{:04.1f}".format(i, angle) for i, angle in enumerate(angles)]
    vlines = []
    vlineColors = []
    for idx in hoopStart, hoopEnd:
        if idx is not None:
            vlines.append(idx)
            vlineColors.append("black")
    if elemIdxmax is not None:
        vlines.append(elemIdxmax)
        vlineColors.append("red")
    if newDesignIndexes is not None:
        vlines.extend(newDesignIndexes)
        vlineColors.extend(["green"] * len(newDesignIndexes))
    # rcParams["font.size"] = 22 #better for presentations
    plotDataFrame(
        False,
        "",
        puckForPlot.replace(0, np.nan),
        ax,
        vlines=vlines,
        vlineColors=vlineColors,
        yLabel=puckLabelName,
        xLabel="Contour index",
        plotKwArgs={"legendKwargs": {"loc": "center left", "bbox_to_anchor": (1.03, 0.5)}, "linewidth": 1.0},
    )
    if colorLayersBy == "angle":
        ax.legend().remove()
        norm = colors.Normalize(min(angles), 90)
        colorMap = colormaps["viridis"].reversed()
        for i in range(0, len(puckForPlot.columns)):
            colorValue = angles[i]
            color = colorMap(norm(colorValue))
            ax.lines[i].set_color(color)
        sm = plt.cm.ScalarMappable(cmap=colorMap, norm=norm)
        sm.set_array([])
        plt.colorbar(sm, label="Angle", ax=ax)
    elif colorLayersBy == "layerNumber":
        ax.legend().remove()
        norm = colors.Normalize(0, len(angles) - 1)
        colorMap = colormaps["viridis"].reversed()
        for i in range(0, len(puckForPlot.columns)):
            colorValue = i
            color = colorMap(norm(colorValue))
            ax.lines[i].set_color(color)
        sm = plt.cm.ScalarMappable(cmap=colorMap, norm=norm)
        sm.set_array([])
        plt.colorbar(sm, label="Layer Number", ax=ax)
    else:
        layersToColor = set()
        if hoopLayerIndexes.size:
            firstHoopLayerIdx = hoopLayerIndexes[0][0]
            lastHoopLayerIdx = hoopLayerIndexes[-1][0]
            layersToColor.update({firstHoopLayerIdx, lastHoopLayerIdx})
        fittingLayerIndexes = np.argwhere(puckForPlot.iloc[min(-2 - settings.ignoreLastElements, -3), :])
        firstFittingLayerIdx = fittingLayerIndexes[0][0]
        lastFittingLayerIdx = fittingLayerIndexes[-1][0]
        layersToColor.update({firstFittingLayerIdx, lastFittingLayerIdx})
        angleBoxes = np.linspace(angles[firstFittingLayerIdx], settings.maxHelicalAngle, 7)
        maxPerLayer = puckForPlot.max(axis=0)
        for i in range(angleBoxes.size - 1):
            lowerBoxBound = angleBoxes[i]
            upperBoxBound = angleBoxes[i + 1]
            layerIndexesInBox = np.argwhere([lowerBoxBound < angle <= upperBoxBound for angle in angles])
            if layerIndexesInBox.size:
                maxLayerInBoxIdx = layerIndexesInBox[np.argmax([maxPerLayer.iloc[idx[0]] for idx in layerIndexesInBox])]
                layersToColor.add(maxLayerInBoxIdx[0])
        colorCycle = itertools.cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        for i in range(0, len(puckForPlot.columns)):
            if i in layersToColor:
                color = next(colorCycle)
                ax.lines[i].set_color(color)
                ax.get_legend().legend_handles[i].set_color(color)
            else:
                ax.lines[i].set_color("black")
                ax.lines[i].set_label("_")
        ax.legend(loc="center left", bbox_to_anchor=(1.03, 0.5))
    fig.tight_layout()
    saveShowClose(
        os.path.join(runDir, f"puck_{plotName}.png") if runDir else "", show=show, fig=fig, verbosePlot=verbosePlot
    )


def plotTargetFunc(
    ax, tfValues, newAngleShift, puckLabelName, targetFuncScaling, runDir, layerNumber, show, symTank=True
):
    ishelical = not isHoopLayer(newAngleShift[0])
    # create target function plot
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 7))
    else:
        fig = None
    xLabel = "angle" if ishelical else "hoop shift"
    if ishelical:
        # plot angle
        angleOrHoopShift = [newAngleShift[0]]
    else:
        # plot hoop
        if symTank:
            # one Hoop Shift
            angleOrHoopShift = [newAngleShift[0]]
        else:
            # Hoop Shift 1, Hoop Shift 2
            angleOrHoopShift = [newAngleShift[1], newAngleShift[2]]
    tfX = tfValues[0]
    tfMaxPuckIndexes = tfValues[-2]
    tfMaxStrainIndexes = tfValues[-1]
    tfValues = tfValues[1:-2]
    weights, scaling = targetFuncScaling
    labelNames = targetFuncNames
    labelNames = [
        f"{labelName}, weight: {round(weight, 4)}, scaleFac: {round(scale, 4)}"
        for labelName, weight, scale in zip(labelNames, weights, scaling)
    ]
    puckIndex, bendIndex, linesIndex = None, None, 0  # index of puck line and bending line
    for values, labelName, index in zip(tfValues, labelNames, range(len(labelNames))):
        if np.all(abs(values) < 1e-8):
            continue
        if index == 0:
            puckIndex = linesIndex
        if index == 4:
            bendIndex = linesIndex
        linesIndex += 1
        ax.plot(tfX, values, label=labelName)
    if tfValues.shape[0] > 1:  # plot weighted sum
        ax.plot(tfX, tfValues.sum(axis=0), label="target function: weighted sum")

    # plot optimal angle or shift as vertical line
    ax.plot(
        [angleOrHoopShift[0]] * 2,
        [0, 1.1 * np.max(tfValues.sum(axis=0))],
        linestyle="dashed",
        color="green",
        label=f"new design {xLabel}",
    )
    if not symTank and not ishelical:
        # plot also hoop side 2
        ax.plot(
            [angleOrHoopShift[1]] * 2,
            [0, 1.1 * np.max(tfValues.sum(axis=0))],
            linestyle="dashed",
            color="green",
            label=f"new design {xLabel}",
        )
    ax.set_ylabel("Target function")
    ax.set_xlabel(xLabel)
    ax2 = ax.twinx()  # plot on secondary axes
    ax2.set_ylabel("Contour index of highest Puck value")
    lines, labels = ax.get_legend_handles_labels()
    if puckIndex is not None:
        ax2.scatter(
            tfX, tfMaxPuckIndexes, label="Contour index of highest Puck value", s=3, color=lines[puckIndex].get_color()
        )
    if bendIndex is not None:
        ax2.scatter(
            tfX,
            tfMaxStrainIndexes,
            label="Contour index of highest strain value",
            s=3,
            color=lines[bendIndex].get_color(),
        )
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    if fig:
        fig.tight_layout()
    saveShowClose(os.path.join(runDir, f"tf_{layerNumber}.png") if runDir else "", show=show, fig=fig)


def plotStressEpsPuck(show, filename, S11, S22, S12, epsAxialBot, epsAxialTop, epsCircBot, epsCircTop, puckFF, puckIFF):
    fig, axs = plt.subplots(3, 3, figsize=(18, 10))
    axs = iter(axs.T.flatten())
    singleLegend = True

    ax = next(axs)
    ax.set_title("eps axial")
    ax.plot(epsAxialBot, label="epsAxialBot")
    ax.plot(epsAxialTop, label="epsAxialTop")
    if not singleLegend:
        ax.legend()

    ax = next(axs)
    ax.set_title("eps circ")
    ax.plot(epsCircBot, label="epsCircBot")
    ax.plot(epsCircTop, label="epsCircTop")
    if singleLegend:
        ax.legend(loc="upper left", bbox_to_anchor=(0.05, -0.2))
    else:
        ax.legend()

    ax = next(axs)
    ax.remove()

    ax = next(axs)
    ax.set_title("S11")
    for layerIndex, stressLayer11 in enumerate(S11.T):
        ax.plot(stressLayer11, label=f"layer {layerIndex}")
    if not singleLegend:
        ax.legend()

    ax = next(axs)
    ax.set_title("S22")
    for layerIndex, stressLayer22 in enumerate(S22.T):
        ax.plot(stressLayer22, label=f"layer {layerIndex}")
    if not singleLegend:
        ax.legend()

    ax = next(axs)
    ax.set_title("S12")
    for layerIndex, stressLayer22 in enumerate(S12.T):
        ax.plot(stressLayer22, label=f"layer {layerIndex}")
    if singleLegend:
        ax.legend(loc="upper left", bbox_to_anchor=(1.1, 0.99))
    else:
        ax.legend()

    ax = next(axs)
    ax.set_title("puck fibre failure")
    puckFF.plot(ax=ax, legend=False)
    if not singleLegend:
        ax.legend()

    ax = next(axs)
    ax.set_title("puck inter fibre failure")
    puckIFF.plot(ax=ax, legend=False)
    if not singleLegend:
        ax.legend()

    ax = next(axs)
    ax.remove()

    if filename:
        plt.savefig(filename)
    if show:
        plt.show()
    plt.close(fig)


def plotThicknesses(show, filename, thicknesses):
    # thicknesses = thicknesses.iloc[::-1,:].reset_index(drop=True)
    fig, axs = plt.subplots(1, 2, figsize=(17, 5))
    plotDataFrame(
        show, None, thicknesses, ax=axs[0], title="Layer thicknesses", yLabel="thickness [mm]", xLabel="Contour index"
    )
    plotDataFrame(
        show,
        None,
        thicknesses,
        ax=axs[1],
        title="Cumulated layer thickness",
        yLabel="thickness [mm]",
        xLabel="Contour index",
        plotKwArgs={"stacked": True},
    )

    if filename:
        plt.savefig(filename)
    if show:
        plt.show()
    plt.close(fig)
