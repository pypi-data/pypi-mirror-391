"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Hydropower Dispatch Model Builder

Description
-----------
This module defines the construction logic for assembling a **hydropower-only**
optimization model in Pyomo. It integrates the full sequence of:

- Set and parameter initialization,
- Decision variable declaration,
- Piecewise or analytical hydropower production modeling (FPH),
- Operational constraints,
- Objective function (optional).

Supported generation modes (per unit)
-------------------------------------
- Constant productivity
- Specific productivity with fixed head
- Exact head-dependent generation with nonlinear losses
- Simplified constant productivity (didactic)

Functions
---------
build_FPHs(m, data)
    Initialize the hydropower production function (FPH) callable for each unit.

build_hydro_dispatch(data, include_objective=True)
    Assemble a complete Pyomo model for hydropower dispatch optimization.

Modeling Conventions and Units
------------------------------
- Time periods are indexed as integers t = 1, …, horizon.
- Turbined and spill discharges (Q, S): hm^3.
- Storage volume (V): hm^3.
- Power (G) and demand (d): MWh.

Notes
-----
- This builder targets **pure hydropower** systems. To include thermal units,
  couple with a combined system balance elsewhere.
- The callable stored in m.hydro_FPH[h] must accept the signature
  FPH(Q, V, S) → MW and be consistent with model units.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023 
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""
import copy
from pyomo.environ import ConcreteModel, Param, value
from .HydraulicVars import hydraulyc_add_sets_and_params, hydralic_add_variables_g
from .HydraulicConstraints import (
    add_hydro_balance_constraint,
    add_hydro_generation_constraint,
    add_hydro_qmin_constraint,
    add_hydro_qmax_constraint,
    add_hydro_volume_continuity_constraint,
    add_hydro_volume_max_constraint,
    add_hydro_volume_mim_constraint
)
from .HydraulicDataTypes import HydraulicData
from .HydraulicObjectives import set_objective_hydro
from .SimplifiedConstantProductivityFPH import simplified_constant_productivity_fph

from typing import Dict


def build_FPHs(m: ConcreteModel,
               data: HydraulicData):
    """
    Initialize hydropower production functions (FPH) for all units.

    For each hydro unit h, this function selects and constructs a callable
    FPH according to the unit's declared mode (constant, simplified,
    specific, or exact) and assigns it to m.hydro_FPH[h] with
    the signature FPH(Q, V, S) => MW.

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Pyomo model into which the FPH callables will be attached.
    data : HydraulicData
        Configuration object containing unit maps and modes

    Returns
    -------
    None
        The model m is modified in place. A dictionary m.hydro_FPH is
        created, indexed by unit name, each entry being a callable of the form
        FPH(Q, V, S).
    """
    H = list(data.units.keys())
    m.hydro_FPH = dict()
    for h in H:
        unit = data.units[h]
        m.hydro_FPH[h] = simplified_constant_productivity_fph(unit.p)


def build_hydro_dispatch(
    data: HydraulicData,
    include_objective: bool = True
):
    """
    Assemble a complete Pyomo model for hydropower dispatch.

    The resulting model includes:

    - Set and parameter definitions (via hydraulyc_add_sets_and_params)
    - Continuous decision variables (via hydralic_add_variables_g)
    - Per-unit FPH callables (via build_FPHs)
    - Operational constraints: generation equation, reservoir mass balance,
      Qmin/Qmax, volume bounds, terminal storage target
    - Optional system-wide demand balance and cost-minimization objective

    Parameters
    ----------
    data : HydraulicData
        Input data with horizon, demand, unit map, and conversion constants.
    include_objective : bool, optional
        If True, add the hydropower balance constraint and define the
        objective function. Default is True.

    Returns
    -------
    pyomo.core.base.PyomoModel.ConcreteModel
        A Pyomo ConcreteModel ready to be passed to a solver.

    Notes
    -----
    - Designed for hydropower-only settings. For mixed hydro-thermal
      systems, use an extended builder with a combined balance equation.
    - The order of operations ensures FPH callables are available before
      generation constraints are added.
    """
    m = ConcreteModel()

    m = add_hydro_problem(m,
                          data,
                          include_objective)

    return m


def add_hydro_problem(m: ConcreteModel,
                      data: HydraulicData,
                      include_objective: bool = False) -> ConcreteModel:
    """
    Assemble a hydropower dispatch problem in Pyomo.

    This builder configures a Pyomo model for reservoir-based hydropower
    optimization. It attaches sets, parameters, decision variables, the
    hydropower production functions (FPHs), and all relevant operational
    constraints. Optionally, it includes the demand balance and the
    cost-minimization objective.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which the hydropower problem will be added.
    data : HydraulicData
        Input data object containing planning horizon, demand mapping,
        unit definitions, inflows, storage bounds, and productivity
        coefficients.
    include_objective : bool, optional
        If True, add the system-wide demand balance and deficit-penalizing
        objective function (default is False).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated Pyomo model with hydropower sets, parameters, variables,
        constraints, and optionally the objective.
    """
    build_FPHs(m, data)

    hydraulyc_add_sets_and_params(m, data)
    hydralic_add_variables_g(m)

    add_hydro_generation_constraint(m)
    add_hydro_qmin_constraint(m)
    add_hydro_qmax_constraint(m)
    add_hydro_volume_continuity_constraint(m)
    add_hydro_volume_max_constraint(m)
    add_hydro_volume_mim_constraint(m)

    if include_objective:
        add_hydro_balance_constraint(m)
        set_objective_hydro(m)

    return m


def add_hydro_subproblem(m: ConcreteModel,
                         data: HydraulicData,
                         stage: int) -> ConcreteModel:
    """
    Assemble a hydropower dispatch problem in Pyomo.

    This builder configures a Pyomo model for reservoir-based hydropower
    optimization. It attaches sets, parameters, decision variables, the
    hydropower production functions (FPHs), and all relevant operational
    constraints. Optionally, it includes the demand balance and the
    cost-minimization objective.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which the hydropower problem will be added.
    data : HydraulicData
        Input data object containing planning horizon, demand mapping,
        unit definitions, inflows, storage bounds, and productivity
        coefficients.
    include_objective : bool, optional
        If True, add the system-wide demand balance and deficit-penalizing
        objective function (default is False).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated Pyomo model with hydropower sets, parameters, variables,
        constraints, and optionally the objective.

    """
    # data copy
    subproblem_data = copy.deepcopy(data)
    subproblem_data.horizon = 1
    for name in subproblem_data.units.keys():
        subproblem_data.units[name].afluencia = [
            data.units[name].afluencia[stage]]

    build_FPHs(m, subproblem_data)

    hydraulyc_add_sets_and_params(m, subproblem_data)
    hydralic_add_variables_g(m)

    add_hydro_generation_constraint(m)
    add_hydro_qmin_constraint(m)
    add_hydro_qmax_constraint(m)
    add_hydro_volume_continuity_constraint(m)
    add_hydro_volume_max_constraint(m)
    add_hydro_volume_mim_constraint(m)

    return m
