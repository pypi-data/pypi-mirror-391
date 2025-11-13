"""
See tankoh2/doc for a description
"""

from copy import copy

import numpy as np
import patme
from patme.service.stringutils import indent
from scipy.optimize import NonlinearConstraint, differential_evolution, minimize

from tankoh2 import log
from tankoh2.masses.massestimation import getVesselMass
from tankoh2.service.exception import Tankoh2Error

optLogger = log.info  # whether optimization steps should be logged as debug or info
minRingPitch = 150
min_gap_between_rings = 20


def getRingParameterDict(paramKwArgs):
    ringKeys = [
        "ringCrossSectionType",
        "ringInertiaTransform",
        "ringInertiaTransformRatio",
        "ringHeight",
        "ringFootWidth",
        "ringLayerThickness",
        "numberOfRings",
        "ringLayup",
        "ringMaterial",
    ]
    return {key: paramKwArgs.get(key, None) for key in ringKeys}


def checkStability(
    burst_pressure,
    liner,
    minimal_cylinder_thickness,
    layupCylinder,
    material,
    ringParameterDict,
    use_bk_hydrostatic,
    use_bk_safety_factor,
):
    """
    :param burst_pressure: burst pressure in bar
    :param liner: tankoh2 liner object
    :param minimal_cylinder_thickness: minimal thickness of cylinder from strength&fatigue calculation in mm
    :param layupCylinder:
    :param material: material definition of type tankoh2.mechanics.material.MaterialDefinition
    :param ringParameterDict: dict with ring parameters:
        ["ringCrossSectionType","ringInertiaTransform","ringInertiaTransformRatio","ringHeight",
        "ringFootWidth","ringLayerThickness","numberOfRings",]
    :param use_bk_hydrostatic: If true, in-plane axial load will be applied to the cylinder edges to represent
        the pressure applied to the domes
    :param use_bk_safety_factor: additional safety factor by 0.75, recommended in nasa SP8007.
        Can be omitted if a safety factor is already applied to burst_pressure
    :return:
    """
    results = stabilityOpt(
        liner,
        minimal_cylinder_thickness,
        material,
        ringParameterDict,
        burst_pressure,
        layupCylinder,
        use_bk_hydrostatic,
        use_bk_safety_factor,
    )

    resultKeys = "cylinderLayerThickness", "ringLayerThickness", "numberOfRings", "mass"
    resultDict = {key: value for key, value in zip(resultKeys, results)}
    return resultDict


def stabilityOpt(
    liner,
    layer_thickness_cylinder,
    material,
    ringParameterDict,
    burstPressure,
    layup_cylinder,
    hydrostatic_flag=False,
    safety_flag=False,
    useLocalOptimizer=True,
):
    ringKeys = [
        "ringCrossSectionType",
        "ringInertiaTransform",
        "ringInertiaTransformRatio",
        "ringHeight",
        "ringFootWidth",
        "ringLayerThickness",
        "numberOfRings",
        "ringLayup",
    ]
    (
        ring_cross_section_type,
        inertia_transform,
        ringInertiaTransformRatio,
        ringHeight,
        ringFootWidth,
        ringLayerThickness,
        numberOfRings,
        ringLayup,
    ) = [ringParameterDict[key] for key in ringKeys]

    isCfrpRun = len(layup_cylinder) > 1
    if isCfrpRun:
        minLayerThicknessRingStatic = 0.125
        maxLayerThicknessRingStatic = 0.5
    else:
        minLayerThicknessRingStatic = 1
        maxLayerThicknessRingStatic = 4

    # bounds
    min_rings, max_rings = calculate_minimum_nrings(liner.lcyl, ringFootWidth)
    bounds = np.array(
        [
            (layer_thickness_cylinder, layer_thickness_cylinder * 5),
            (
                np.min([minLayerThicknessRingStatic, layer_thickness_cylinder]),
                np.max([layer_thickness_cylinder * 5, maxLayerThicknessRingStatic]),
            ),  # web half thickness
            (min_rings, max_rings),
        ]
    )
    # opt values: cylinder thickness, ring web half thickness, number of rings
    x0 = [layer_thickness_cylinder, layer_thickness_cylinder, 5]  # at lower bounds
    x0 = bounds.mean(axis=1)  # at mean bounds
    x0 = bounds[:, 1]  # at upper bounds
    optLogger("X0 and bounds:\n" + indent([["skinThk", "halfWebThk", "nRings"]] + [x0] + list(np.array(bounds).T)))

    # constraints
    localBuckConstraintFunction = BucklingConstraintFunction(
        liner, material, layup_cylinder, hydrostatic_flag, safety_flag
    )
    localBuckConstraintFunction.usedConstraintFunction = localBuckConstraintFunction.getCritPressureLocalBuck
    localBuckConstraint = NonlinearConstraint(localBuckConstraintFunction, burstPressure, np.inf)
    globalBuckConstraintFunction = BucklingConstraintFunction(
        liner, material, layup_cylinder, ringParameterDict, hydrostatic_flag, safety_flag
    )
    globalBuckConstraintFunction.usedConstraintFunction = globalBuckConstraintFunction.getCritPressureGlobalBuck
    globalBuckConstraint = NonlinearConstraint(globalBuckConstraintFunction, burstPressure, np.inf)
    constraints = [localBuckConstraint, globalBuckConstraint]

    # arguments to opt function
    args = [liner, material, layup_cylinder, ring_cross_section_type, ringLayup, ringHeight, ringFootWidth]

    if useLocalOptimizer:
        res = minimize(
            optTargetFunctionVesselMass,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            args=args,
            options={"ftol": 1e-2},
        )
    else:
        res = differential_evolution(
            optTargetFunctionVesselMass,
            bounds=bounds,
            constraints=constraints,
            args=[args],
            tol=0.5,
        )

    if not res.success:
        raise Tankoh2Error(
            f"Optimization did not terminated successully! Last x, result: {res.x, res.fun}, Message: {res.message}"
        )
    optLogger(f"x, fun, comment: {res.x, res.fun, res.message}")
    x = copy(res.x)
    x[2] = int(np.ceil(x[2]))
    resMass = optTargetFunctionVesselMass(x, args)

    return *x, resMass


def optTargetFunctionVesselMass(x, args):
    layer_thickness_cylinder, layer_thickness_ring, nRings = x
    liner, material, layup_cylinder, ring_cross_section_type, ring_stacking, ringHeight, ringFootWidth = args
    pitch = getPitch(liner.lcyl, nRings)

    cross_section = getCrossSection(
        ring_cross_section_type, layer_thickness_ring, ring_stacking, ringHeight, ringFootWidth
    )
    ringMassPerArea = cross_section.getAreaMass(material, pitch)
    thickness_cylinder = layer_thickness_cylinder * len(layup_cylinder)
    mass = getVesselMass(liner, thickness_cylinder, material.rho, ringMassPerArea)

    optLogger(f"Mass x: {x} mass: {mass}")
    return mass


def getCritPressureLocalBuck(
    radius, axial_length, layer_thickness, layup_cylinder, material_cylinder, hydrostatic_flag=False, safety_flag=False
):
    """Calculates the critical pressure for all half waves"""
    # TODO: the local buckling criterion must be revised for short cylinders, as it may produce too conservative results
    #  for short cylinders.
    _, cylinderAbdMatrix, _ = calculate_SP8007_stiffness(layup_cylinder, layer_thickness, material_cylinder)

    n_range = range(2, 201)  # circumferential half waves
    m_range = range(1, 21) if hydrostatic_flag else range(1, 2)  # axial half waves
    m_cr = min(m_range)
    n_cr = min(n_range)
    lowestCriticalPressure = float("inf")
    for m in m_range:
        for n in n_range:
            pressure = getCritPressureFixedHalfWaves(
                radius, axial_length, m, n, None, None, hydrostatic_flag, True, safety_flag, cylinderAbdMatrix
            )
            if pressure < lowestCriticalPressure:
                lowestCriticalPressure = pressure
                m_cr = m
                n_cr = n
    optLogger(f"Local Buckling m,n: {m_cr, n_cr}")
    return lowestCriticalPressure


def getCritPressureGlobalBuck(
    radius,
    axial_length,
    layer_thickness_cylinder,
    layup_cylinder,
    material,
    ringParameterDict,
    hydrostatic_flag=False,
    safety_flag=False,
):
    """Calculates the critical pressure for all half waves"""
    _, cylinderAbdMatrix, cylinder_laminate_thickness = calculate_SP8007_stiffness(
        layup_cylinder, layer_thickness_cylinder, material
    )

    n_range = range(2, 51)  # circumferential half waves
    m_range = range(1, 21) if hydrostatic_flag else range(1, 2)  # axial half waves
    ringKeys = [
        "ringCrossSectionType",
        "ringInertiaTransform",
        "ringInertiaTransformRatio",
        "ringHeight",
        "ringFootWidth",
        "ringLayerThickness",
        "numberOfRings",
        "ringLayup",
        "ringMaterial",
    ]
    (
        ring_cross_section_type,
        inertia_transform,
        ringInertiaTransformRatio,
        ringHeight,
        ringFootWidth,
        ringLayerThickness,
        numberOfRings,
        ringLayup,
        ringMaterial,
    ) = [ringParameterDict[key] for key in ringKeys]
    if ringMaterial is None:
        ringMaterial = material

    pitch = getPitch(axial_length, numberOfRings)
    (
        extensional_stiffness,
        bending_stiffness,
        twisting_stiffness,
        coupling_stiffness,
        ring_stacking,
    ) = calculateCrossSectionConstant(
        ring_cross_section_type,
        pitch,
        ringLayup,
        ringLayerThickness,
        ringMaterial,
        inertia_transform,
        ringInertiaTransformRatio,
        cylinder_laminate_thickness,
        ringHeight,
        ringFootWidth,
    )

    check_ring, constraint = check_ring_stiffness(
        cylinderAbdMatrix, extensional_stiffness, bending_stiffness, twisting_stiffness
    )
    if not check_ring:
        log.info(
            "The rings provide an additional stiffness that likely will be associate with non-conservative "
            f"results with following constraints: {constraint}"
        )

    lowestCriticalPressure = float("inf")
    m_global = min(m_range)
    n_global = min(n_range)
    ring_stiffness = [extensional_stiffness, bending_stiffness, twisting_stiffness, coupling_stiffness]
    for m in m_range:
        for n in n_range:
            pressure_global = getCritPressureFixedHalfWaves(
                radius,
                axial_length,
                m,
                n,
                ring_stiffness,
                None,
                hydrostatic_flag,
                False,
                safety_flag,
                cylinderAbdMatrix,
            )
            log.debug(f"{pressure_global, m,n}")
            if pressure_global < lowestCriticalPressure:
                lowestCriticalPressure = pressure_global
                m_global = m
                n_global = n

    optLogger(f"global buckling m, n: {m_global, n_global}")
    return lowestCriticalPressure


def get_lamina_stiffness_matrix(material):
    e1, e2, nu12, g12, g13, g23 = (
        material.moduli["e11"],
        material.moduli["e22"],
        material.moduli["nu12"],
        material.moduli["g12"],
        material.moduli["g13"],
        material.moduli["g23"],
    )

    if e2 in (None, 0, 0.0):
        e2 = e1
        g12 = e1 / (2.0 * (1.0 + nu12))

    nu21 = nu12 * e2 / e1
    aux_var = 1.0 - nu12 * nu21

    return np.array(
        [[e1 / aux_var, nu12 * e2 / aux_var, 0.0], [nu12 * e2 / aux_var, e2 / aux_var, 0.0], [0.0, 0.0, g12]]
    )


def calculate_transform_matrix(angle):

    m = np.cos(np.deg2rad(angle))
    n = np.sin(np.deg2rad(angle))

    t_inv_t = np.array(
        [[m**2.0, n**2.0, m * n], [n**2.0, m**2.0, -m * n], [-2.0 * m * n, 2.0 * m * n, m**2.0 - n**2.0]]
    )
    t_inv = np.array([[m**2.0, n**2.0, -2.0 * m * n], [n**2.0, m**2.0, 2.0 * m * n], [m * n, -m * n, m**2.0 - n**2.0]])

    return t_inv_t, t_inv


def calculate_SP8007_stiffness(layup, ply_thickness, materialCylinder):

    n_plies = len(layup)
    laminate_thickness = ply_thickness * n_plies

    a_matrix, b_matrix, d_matrix = np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))
    for count, angle in enumerate(layup):
        q_matrix = get_lamina_stiffness_matrix(materialCylinder)
        t_inv_t, t_inv = calculate_transform_matrix(angle)
        q_bar = np.dot(np.dot(t_inv, q_matrix), t_inv_t)

        zbar = -(laminate_thickness + ply_thickness) / 2 + (count + 1) * ply_thickness
        a_matrix += q_bar * ply_thickness
        b_matrix += q_bar * ply_thickness * zbar
        d_matrix += q_bar * ply_thickness * (zbar**2 + ply_thickness**2 / 12)

    abd_matrix = np.block([[a_matrix, b_matrix], [b_matrix, d_matrix]])
    abd_matrix[np.abs(abd_matrix) < patme.epsilon] = 0

    abd_inv = np.linalg.inv(abd_matrix)

    axx, ayy, ass = abd_inv[0, 0], abd_inv[1, 1], abd_inv[2, 2]
    ayx, axy, axs, asx, asy, ays = (
        abd_inv[1, 0],
        abd_inv[0, 1],
        abd_inv[0, 2],
        abd_inv[2, 0],
        abd_inv[2, 1],
        abd_inv[1, 2],
    )

    laminate_properties = dict(
        Exbar=1 / (laminate_thickness * axx),
        Eybar=1 / (laminate_thickness * ayy),
        Gxybar=1 / (laminate_thickness * ass),
        nuxybar=-ayx / axx,
        nuyxbar=-axy / ayy,
        etasxbar=axs / ass,
        etaxsbar=asx / axx,
        etaysbar=asy / ayy,
        etasybar=ays / ass,
    )

    return laminate_properties, abd_matrix, laminate_thickness


def retrieve_abd_matrix(param_dict, material_dict, lam_thickness):

    q_matrix = get_lamina_stiffness_matrix(material_dict)

    ue = (3.0 * q_matrix[0, 0] + 3.0 * q_matrix[1, 1] + 2.0 * q_matrix[0, 1] + 4.0 * q_matrix[2, 2]) / 8.0
    ug = (q_matrix[0, 0] + q_matrix[1, 1] - 2.0 * q_matrix[0, 1] + 4.0 * q_matrix[2, 2]) / 8.0
    udc = (q_matrix[0, 0] - q_matrix[1, 1]) / 2.0
    unuc = (q_matrix[0, 0] + q_matrix[1, 1] - 2.0 * q_matrix[0, 1] - 4.0 * q_matrix[2, 2]) / 8.0

    ie = np.array([[1, 1, 0], [1, 1, 0], [0, 0, 0]])
    ig = np.array([[0, -2, 0], [-2, 0, 0], [0, 0, 1]])
    i1 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]])
    i2 = np.array([[0, 0, 0.5], [0, 0, 0.5], [0.5, 0.5, 0]])
    i3 = np.array([[1, -1, 0], [-1, 1, 0], [0, 0, -1]])
    i4 = np.array([[0, 0, 1], [0, 0, -1], [1, -1, 0]])

    xsi_a_vec, xsi_b_vec, xsi_d_vec = param_dict.values()

    a_matrix = (
        ue * ie
        + ug * ig
        + xsi_a_vec[0] * udc * i1
        + xsi_a_vec[1] * udc * i2
        + xsi_a_vec[2] * unuc * i3
        + xsi_a_vec[3] * unuc * i4
    ) * lam_thickness
    b_matrix = (
        (
            ue * ie
            + ug * ig
            + xsi_b_vec[0] * udc * i1
            + xsi_b_vec[1] * udc * i2
            + xsi_b_vec[2] * unuc * i3
            + xsi_b_vec[3] * unuc * i4
        )
        * lam_thickness**2
        / 4
    )
    d_matrix = (
        (
            ue * ie
            + ug * ig
            + xsi_d_vec[0] * udc * i1
            + xsi_d_vec[1] * udc * i2
            + xsi_d_vec[2] * unuc * i3
            + xsi_d_vec[3] * unuc * i4
        )
        * lam_thickness**3
        / 12
    )

    abd_matrix = np.block([[a_matrix, b_matrix], [b_matrix, d_matrix]])
    abd_inv = np.linalg.inv(abd_matrix)

    axx, ayy, ass = abd_inv[0, 0], abd_inv[1, 1], abd_inv[2, 2]
    ayx, axy, axs, asx, asy, ays = (
        abd_inv[1, 0],
        abd_inv[0, 1],
        abd_inv[0, 2],
        abd_inv[2, 0],
        abd_inv[2, 1],
        abd_inv[1, 2],
    )

    laminate_properties = dict(
        Exbar=1 / (lam_thickness * axx),
        Eybar=1 / (lam_thickness * ayy),
        Gxybar=1 / (lam_thickness * ass),
        nuxybar=-ayx / axx,
        nuyxbar=-axy / ayy,
        etasxbar=axs / ass,
        etaxsbar=asx / axx,
        etaysbar=asy / ayy,
        etasybar=ays / ass,
    )

    return laminate_properties, abd_matrix


def calculate_lamination_parameters(lamination_angles, ply_thickness, material_dict, abd_flag):

    n_plies = len(lamination_angles)
    lam_thickness = ply_thickness * n_plies

    xsi_a_vec, xsi_b_vec, xsi_d_vec = np.zeros((4, 1)), np.zeros((4, 1)), np.zeros((4, 1))

    for count, angle in enumerate(lamination_angles):
        theta = np.deg2rad(angle)

        aux_vec = np.array([[np.cos(2 * theta)], [np.sin(2 * theta)], [np.cos(4 * theta)], [np.sin(4 * theta)]])
        zbar = -(lam_thickness + ply_thickness) / 2 + (count + 1) * ply_thickness
        xsi_a_vec += aux_vec
        xsi_b_vec += aux_vec * zbar
        xsi_d_vec += aux_vec * ply_thickness * (12 * zbar**2 + ply_thickness**2)

    xsi_a_vec = xsi_a_vec / n_plies
    xsi_b_vec = 4 * xsi_b_vec / (n_plies * lam_thickness)
    xsi_d_vec = xsi_d_vec / lam_thickness**3

    lamination_parameters = dict(xsi_a_vec=xsi_a_vec, xsi_b_vec=xsi_b_vec, xsi_d_vec=xsi_d_vec)

    if abd_flag:
        laminate_properties, abd_matrix = retrieve_abd_matrix(lamination_parameters, material_dict, lam_thickness)
        return laminate_properties, abd_matrix, lamination_parameters, lam_thickness

    else:
        return lamination_parameters, lam_thickness


def check_lamination_parameters(lamination_parameters):

    # TODO: In case of an optimization strategy based on lamination parameters, this function must be defined for
    #  checking the design space

    xsi_a_vec, xsi_b_vec, xsi_d_vec = lamination_parameters.values()
    xsi_vec = xsi_a_vec + xsi_d_vec
    constraint = [
        2 * xsi_vec[0] ** 2 * (1 - xsi_vec[2])
        + 2 * xsi_vec[1] ** 2 * (1 + xsi_vec[2])
        + xsi_vec[2] ** 2
        + xsi_vec[3] ** 2
        - 4 * xsi_vec[0] * xsi_vec[1] * xsi_vec[3]
        <= 1,
        xsi_vec[0] ** 2 + xsi_vec[1] ** 2 <= 1,
        2 * xsi_vec[4] ** 2 * (1 - xsi_vec[6])
        + 2 * xsi_vec[5] ** 2 * (1 + xsi_vec[6])
        + xsi_vec[6] ** 2
        + xsi_vec[7] ** 2
        - 4 * xsi_vec[4] * xsi_vec[5] * xsi_vec[7]
        <= 1,
        xsi_vec[4] ** 2 + xsi_vec[5] ** 2 <= 1,
        0.25 * xsi_vec[0] ** 3 + 0.75 * xsi_vec[0] ** 2 + 0.75 * xsi_vec[0] - xsi_vec[4] <= 0.75,
        -0.25 * xsi_vec[0] ** 3 + 0.75 * xsi_vec[0] ** 2 - 0.75 * xsi_vec[0] + xsi_vec[4] <= 0.75,
        0.25 * xsi_vec[2] ** 3 + 0.75 * xsi_vec[2] ** 2 + 0.75 * xsi_vec[2] - xsi_vec[6] <= 0.75,
        -0.25 * xsi_vec[2] ** 3 + 0.75 * xsi_vec[2] ** 2 - 0.75 * xsi_vec[2] + xsi_vec[6] <= 0.75,
        1.75 * xsi_vec[0] ** 4 + 0.19 * xsi_vec[0] ** 2 - xsi_vec[6] <= 1,
        1.31 * xsi_vec[4] ** 6 - 1.2 * xsi_vec[4] ** 4 + 1.38 * xsi_vec[4] ** 2 - xsi_vec[2] <= 1,
    ]

    if not all(constraint):
        return False

    if not all(-1 <= x <= 1 for x in xsi_vec):
        return False

    return True


def calculate_buckling_determinant(
    stiffness_matrix,
    radius,
    axial_length,
    axial_halfwaves,
    circumferential_waves,
    ring_stiffness=None,
    stringer_stiffness=None,
):

    mm = axial_halfwaves * np.pi / axial_length
    mm2 = mm * mm
    nn = circumferential_waves / radius
    nn2 = nn * nn

    _ex_bar, _ey_bar, _exy_bar, _gxy_bar = [
        stiffness_matrix[0, 0],
        stiffness_matrix[1, 1],
        stiffness_matrix[0, 1],
        stiffness_matrix[2, 2],
    ]
    _dx_bar, _dy_bar, _dxy_bar = [stiffness_matrix[3, 3], stiffness_matrix[4, 4], stiffness_matrix[3, 4]]
    _cx_bar, _cy_bar, _cxy_bar, _kxy_bar = [
        stiffness_matrix[0, 3],
        stiffness_matrix[1, 4],
        stiffness_matrix[0, 4],
        stiffness_matrix[2, 5],
    ]

    if ring_stiffness is not None:
        _ey_bar += ring_stiffness[0]
        _dy_bar += ring_stiffness[1]
        _dxy_bar += ring_stiffness[2]
        _cy_bar += ring_stiffness[3]

    if stringer_stiffness is not None:
        _ex_bar += stringer_stiffness[0]
        _dx_bar += stringer_stiffness[1]
        _dxy_bar += stringer_stiffness[2]
        _cx_bar += stringer_stiffness[3]

    a11 = _ex_bar * mm2 + _gxy_bar * nn2
    a12 = (_exy_bar + _gxy_bar) * mm * nn
    a13 = (_exy_bar / radius) * mm + _cx_bar * mm**3 + (_cxy_bar + 2 * _kxy_bar) * mm * nn2
    a22 = _gxy_bar * mm2 + _ey_bar * nn2
    a23 = (_cxy_bar + 2 * _kxy_bar) * mm2 * nn + (_ey_bar / radius) * nn + _cy_bar * nn**3
    a33 = (
        _dx_bar * mm2**2
        + _dxy_bar * mm2 * nn2
        + _dy_bar * nn2**2
        + _ey_bar / (radius**2)
        + (2 * _cy_bar / radius) * nn2
        + (2 * _cxy_bar / radius) * mm2
    )

    det3_over_det2 = a33 + (a23 * (a13 * a12 - a11 * a23) + a13 * (a12 * a23 - a13 * a22)) / (a11 * a22 - a12**2)

    return det3_over_det2


def check_ring_stiffness(stiffness_matrix, extensional_stiffness, bending_stiffness, twisting_stiffness, tol=5000):

    ey_bar = stiffness_matrix[1, 1]
    dy_bar, dxy_bar = stiffness_matrix[4, 4], stiffness_matrix[3, 4]

    ey_bar_ring = extensional_stiffness
    dy_bar_ring = bending_stiffness
    dxy_bar_ring = twisting_stiffness

    constraints = [
        ey_bar_ring / ey_bar < tol,
        dy_bar_ring / dy_bar < tol * 100,
        dxy_bar_ring / dxy_bar < tol,
    ]
    return all(constraints), [ey_bar_ring / ey_bar, dy_bar_ring / dy_bar, dxy_bar_ring / dxy_bar]


def balanced_symmetric(layup_sequence):
    """Transforms winding angles to balanced symmetric angles

    e.g. [a1, a2] → [+a1,-a1,+a2,-a2,-a2,+a2,-a1,+a1]
    """

    layup_complete = []
    for item in layup_sequence:
        layup_complete.extend([item, -item])
    layup_complete = [abs(item) if item in (-0, -90) else item for item in layup_complete]
    layup_complete = layup_complete + layup_complete[::-1]

    return layup_complete


def calculate_minimum_nrings(axial_length, ringFootWidth, max_pitch_factor=5):
    """
    Suggests a maximum distance between rings, so the ring stiffnesses can be properly smeared in the cylinder
    thickness.
    """

    # TODO: Maybe include here a rule that depends on the smeared stiffness, not on the geometry. This "If L/R is
    #  equal or smaller than 2, the maximum distance is a fraction of the radius, otherwise the axial length is used
    #  as a reference." was tested and it does not solve for small tanks.
    #  TODO: Once it is finished, remove the radius as input.

    max_pitch = axial_length / max_pitch_factor
    num_rings_min = axial_length / max_pitch
    min_rings = int(np.ceil(num_rings_min))

    min_pitch = np.max([ringFootWidth + min_gap_between_rings, minRingPitch])
    num_rings_max = axial_length / min_pitch
    max_rings = int(num_rings_max)

    if min_rings > max_rings:
        min_rings = max_rings

    return min_rings, max_rings


def getCritPressureFixedHalfWaves(
    radius,
    axial_length,
    m,
    n,
    ring_stiffness,
    stringer_stiffness,
    hydrostatic_flag,
    isLocalBuckling,
    safety_flag,
    cylinderAbdMatrix,
):
    """
    It is common for metallic tanks sized by ASME code 2 part section 3 to consider 30% of the dome height as part
    of the cylindrical length. Here it is assumed that the dome is torispherical and follows r1ToD0=0.8 and
    r2ToD0=0.154, resulting in h_dome = 0.66 * radius
    """
    h_dome = 0.66 * radius  # Calculated based on torispherical geometry
    length_factor = 0.3
    sf_factor = 0.75

    axial_length = axial_length if isLocalBuckling else axial_length + (2 * length_factor * h_dome)
    det3_over_det2 = calculate_buckling_determinant(
        cylinderAbdMatrix, radius, axial_length, m, n, ring_stiffness, stringer_stiffness
    )
    aux_var = n**2.0 + 0.5 * (m * np.pi * radius / axial_length) ** 2.0 if hydrostatic_flag else n**2.0
    p_cr = (radius / aux_var) * det3_over_det2
    if safety_flag:
        p_cr *= sf_factor
    return p_cr


def getPitch(axial_length, numberOfRings):
    return axial_length / (numberOfRings + 1)


def calculateCrossSectionConstant(
    ring_cross_section_type,
    pitch,
    ring_stacking,
    ply_thickness,
    material,
    inertia_transform,
    ringInertiaTransformRatio,
    cylinder_thickness,
    ringHeight=None,
    footWidth=None,
):

    laminate_properties_web, _, _ = calculate_SP8007_stiffness(
        ring_stacking + ring_stacking[::-1], ply_thickness, material
    )
    laminate_properties_base, _, _ = calculate_SP8007_stiffness(ring_stacking, ply_thickness, material)
    e_bar_web, g_bar_web = laminate_properties_web["Exbar"], laminate_properties_web["Gxybar"]
    e_bar_base, g_bar_base = laminate_properties_base["Exbar"], laminate_properties_base["Gxybar"]

    cross_section = getCrossSection(ring_cross_section_type, ply_thickness, ring_stacking, ringHeight, footWidth)

    area_web = cross_section.area_web
    area_base = cross_section.area_base
    centroid_y_web = cross_section.centroid_y_web
    centroid_y_base = cross_section.centroid_y_base

    zy_web, zy_base = 0.0, 0.0
    if inertia_transform == "mid-surface":
        zy_web = cylinder_thickness / 2.0 + centroid_y_web
        zy_base = cylinder_thickness / 2.0 + centroid_y_base
    elif inertia_transform == "top-surface":
        zy_web = centroid_y_web
        zy_base = centroid_y_base
    elif inertia_transform == "percent":
        zy_web = (cylinder_thickness / 2.0 + centroid_y_web) * ringInertiaTransformRatio
        zy_base = (cylinder_thickness / 2.0 + centroid_y_base) * ringInertiaTransformRatio

    moment_of_inertia_web = cross_section.moment_of_inertia_x_web
    moment_of_inertia_base = cross_section.moment_of_inertia_x_base
    torsional_constant_web = cross_section.torsional_constant_web
    torsional_constant_base = cross_section.torsional_constant_base

    extensional = (e_bar_web * area_web + e_bar_base * area_base) / pitch
    bending = (
        (moment_of_inertia_web + area_web * zy_web**2.0) * e_bar_web
        + (moment_of_inertia_base + area_base * zy_base**2.0) * e_bar_base
    ) / pitch
    twisting = (g_bar_web * torsional_constant_web + g_bar_base * torsional_constant_base) / pitch
    coupling = (zy_web * e_bar_web * area_web + zy_base * e_bar_base * area_base) / pitch
    return [extensional, bending, twisting, coupling, ring_stacking]


def getCrossSection(ring_cross_section_type, ply_thickness, ring_stacking, ringHeight, footWidth):

    if ring_cross_section_type.lower() == "t":
        cross_section = TCrossSection(ply_thickness, ring_stacking, ringHeight, footWidth)
    elif ring_cross_section_type.lower() == "rectangle":
        cross_section = RecCrossSection(ply_thickness, ring_stacking)
    else:
        raise NotImplementedError(f'Cross section "{ring_cross_section_type}" is not implemented yet')
    return cross_section


class CrossSection:
    def getAreaMass(self, material, pitch):
        massPerMeter = self.area / 100 / 100 / 100 * material.rho
        massPerArea = massPerMeter / (pitch / 1000)
        return massPerArea


class TCrossSection(CrossSection):
    def __init__(self, h_ply, stack_list, total_height=None, foot_width=None):
        """
        :param h_ply: thickness of a ply
        :param stack_list: stacking as list in [°]. Full stacking for the foot, half stacking of the web
        :param total_height: height of the cross section
        :param foot_width: width of the foot
        """
        h_ply = h_ply if isinstance(h_ply, list) else [h_ply] * len(stack_list)
        h_laminate = float(sum(h_ply))

        """foot stacking thickness"""
        self.foot_thickness = float(h_laminate)

        """web stacking thickness"""
        self.web_thickness = float(2 * self.foot_thickness)

        """web height"""
        self.web_height = float(10 * self.web_thickness) if total_height is None else total_height - self.foot_thickness

        """footwidth"""
        self.foot_width = 50  # float(10 * self.web_thickness) if foot_width is None else foot_width

        """total height"""
        self.total_height = float(self.foot_thickness + self.web_height)

    @property
    def area_web(self):
        return self.web_height * self.web_thickness

    @property
    def area_base(self):
        return self.foot_width * self.foot_thickness

    @property
    def area(self):
        return self.area_base + self.area_web

    @property
    def centroid_y_web(self):
        return self.foot_thickness + self.web_height / 2.0

    @property
    def centroid_y_base(self):
        return self.foot_thickness / 2.0

    @property
    def centroid_x(self):
        return 0.0

    @property
    def centroid_y(self):
        return (self.area_base * self.centroid_y_base + self.area_web * self.centroid_y_web) / (
            self.area_base + self.area_web
        )

    @property
    def moment_of_inertia_x_web(self):
        return (
            self.area_web * self.web_height**2.0 / 12.0 + self.area_web * (self.centroid_y_web - self.centroid_y) ** 2.0
        )

    @property
    def moment_of_inertia_x_base(self):
        return (
            self.area_base * self.foot_thickness**2.0 / 12.0
            + self.area_base * (self.centroid_y_base - self.centroid_y) ** 2.0
        )

    @property
    def moment_of_inertia_y_web(self):
        return self.area_web * self.web_thickness**2.0 / 12.0

    @property
    def moment_of_inertia_y_base(self):
        return self.area_base * self.foot_width**2.0 / 12.0

    @property
    def torsional_constant_web(self):
        # (self._a * self._t ** 3.0 * (0.3333 - 0.105 * self._t / self._a * (1.0 - self._t ** 4.0 / (192.0 * self._a ** 4.0))))
        return 0.3333 * (self.total_height - self.foot_thickness / 2) * self.web_thickness**3

    @property
    def torsional_constant_base(self):
        # (self._b * self._s ** 3.0 * (0.3333 - 0.21 * self._s / self._s * (1.0 - self._s ** 4.0 / (12.0 * self._b ** 4.0))))
        return 0.3333 * self.foot_width * self.foot_thickness**3

    @property
    def display_info(self):
        return f"Cross-section: {self.__class__.__name__}\nA: {self.area_web} + {self.area_base}\nIx: {self.moment_of_inertia_x_web} + {self.moment_of_inertia_x_base}\nJ: {self.torsional_constant_web} + {self.torsional_constant_base}"


class RecCrossSection(CrossSection):
    def __init__(self, h_ply, stack_list, height=None):
        h_ply = h_ply if isinstance(h_ply, list) else [h_ply] * len(stack_list)
        h_laminate = float(sum(h_ply))
        if height:
            self._a = height
        else:
            self._a = float(10 * 2 * h_laminate)
        self._b = float(h_laminate)

    @property
    def area_web(self):
        return self._a * self._b

    @property
    def area_base(self):
        return 0.0

    @property
    def area(self):
        return self.area_web

    def centroid_y_web(self):
        return self._a / 2

    @property
    def centroid_y_base(self):
        return 0.0

    @property
    def centroid_x(self):
        return self._b / 2

    @property
    def centroid_y(self):
        return self._a / 2

    @property
    def moment_of_inertia_x_web(self):
        return self._b * self._a**3 / 12

    @property
    def moment_of_inertia_x_base(self):
        return 0.0

    @property
    def moment_of_inertia_y_web(self):
        return self._b**3 * self._a / 12

    @property
    def moment_of_inertia_y_base(self):
        return 0.0

    @property
    def torsional_constant_web(self):
        return self._a**3 * self._b * (0.3333 - 0.21 * self._a / self._b * (1 - self._a**4 / (12 * self._b**4)))

    @property
    def torsional_constant_base(self):
        return 0.0

    @property
    def display_info(self):
        return f"Cross-section: {self.__class__.__name__}\nA: {self.area_web}\nIx: {self.moment_of_inertia_x_web}\nIy: {self.moment_of_inertia_y_web}\nJ: {self.torsional_constant_web}"


class BucklingConstraintFunction:

    def __init__(self, *args):
        self.usedConstraintFunction = None
        self.args = args  # constants to the problem in usedConstraintFunction

    def __call__(self, x):
        """fun to be called in scipy.optimize.NonlinearConstraint"""
        return self.usedConstraintFunction(x)

    def getCritPressureLocalBuck(self, x):
        liner, material_cylinder, layup_cylinder, hydrostatic_flag, safety_flag = self.args
        layer_thickness_cylinder, _, nRings = x
        pitch = getPitch(liner.lcyl, nRings)
        critBuckPressure = getCritPressureLocalBuck(
            liner.rCyl,
            pitch,
            layer_thickness_cylinder,
            layup_cylinder,
            material_cylinder,
            hydrostatic_flag,
            safety_flag,
        )
        self.logData(x, critBuckPressure, "Local")
        return critBuckPressure

    def getCritPressureGlobalBuck(self, x):
        liner, material_cylinder, layup_cylinder, ringParameterDict, hydrostatic_flag, safety_flag = self.args
        layer_thickness_cylinder, ringLayerThickness, nRings = x
        ringParameterDict["ringLayerThickness"] = ringLayerThickness
        ringParameterDict["numberOfRings"] = nRings
        critBuckPressure = getCritPressureGlobalBuck(
            liner.rCyl,
            liner.lcyl,
            layer_thickness_cylinder,
            layup_cylinder,
            material_cylinder,
            ringParameterDict,
            hydrostatic_flag,
            safety_flag,
        )
        self.logData(x, critBuckPressure, "Global")
        return critBuckPressure

    def logData(self, x, pressure, localOrGlobal):
        optLogger(f"{localOrGlobal} x: {x} buck: {pressure}")
