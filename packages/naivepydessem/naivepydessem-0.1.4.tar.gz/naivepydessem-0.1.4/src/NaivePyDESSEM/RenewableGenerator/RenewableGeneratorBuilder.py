"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Model Builder

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides high-level builders for renewable-only optimization
models in Pyomo. It assembles the complete model structure by combining
sets, parameters, variables, constraints, and optionally the objective
function for renewable generation systems.

Functions
---------
build_renewables(data, include_objective=True)
    Create a new ``ConcreteModel`` pre-populated with renewable unit
    commitment and dispatch components.
add_renewable_problem(m, data, include_objective=False)
    Add renewable-related sets, parameters, variables, constraints,
    and optionally the objective function to an existing Pyomo model.

Notes
-----
- Suitable for renewable-only systems (e.g., wind and solar). For hybrid
  hydrothermal-renewable systems, the balance constraint and objective
  must be adapted accordingly.
- The availability profiles are deterministic and exogenous, provided
  by the ``RenewableData`` structure.
- The optional objective minimizes deficit costs and enforces demand
  balance when ``include_objective=True``.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from .RenewableVars import renewable_add_sets_and_params, renewable_add_variables
from .RenewableConstraints import add_renewable_capacity_constraints, add_renewable_balance_constraint
from .RenewableObjectives import set_objective_renewable
from .RenewableDataTypes import RenewableData
from pyomo.environ import ConcreteModel


def build_renewables(data: RenewableData, 
                     include_objective: bool=True) -> ConcreteModel:
    """
    Construct a complete Pyomo model for renewable-only dispatch.

    This high-level builder creates a new ``ConcreteModel`` instance and
    populates it with sets, parameters, variables, constraints, and optionally
    the objective for renewable generation systems. It calls
    :func:`add_renewable_problem` internally.

    Parameters
    ----------
    data : RenewableData
        Input data structure with horizon, demand profile, deficit penalty,
        and renewable units with their availability profiles.
    include_objective : bool, optional
        If ``True``, add the renewable balance constraint and objective
        function (default is ``True``).

    Returns
    -------
    pyomo.environ.ConcreteModel
        A new Pyomo model fully configured for renewable-only dispatch.

    Notes
    -----
    - The model contains:
        * Sets: time periods, renewable units
        * Parameters: demand, availability (``gbar``), deficit penalty
        * Variables: renewable generation, deficit
        * Constraints: capacity limits, and optionally balance
        * Objective: deficit-penalizing minimization (if enabled)
    - For integration with hydro/thermal systems, use combined builders.
    """
    m = ConcreteModel()
    m = add_renewable_problem(m=m,
                              data=data,
                              include_objective=include_objective)
    return m


def add_renewable_problem(m: ConcreteModel, 
                          data: RenewableData,
                          include_objective: bool = False) -> ConcreteModel:
    """
    Add renewable dispatch problem structure to a Pyomo model.

    This routine attaches all renewable-related components to an existing
    ``ConcreteModel``. It initializes sets, parameters, variables, and the
    renewable capacity constraints. Optionally, it also includes the balance
    constraint and renewable objective.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which renewable problem components will be added.
    data : RenewableData
        Input data structure containing horizon, demand, units, and
        availability profiles.
    include_objective : bool, optional
        If ``True``, add the balance constraint and renewable objective
        function (default is ``False``).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with renewable sets, parameters, variables,
        constraints, and optionally the objective.

    Notes
    -----
    - Constraints added:
        * Renewable generation capacity limits
        * Renewable balance (if ``include_objective=True``)
    - The objective minimizes deficit cost and optionally penalizes
      renewable spill (depending on implementation of
      :func:`set_objective_renewable`).
    - This builder is intended for renewable-only systems. For mixed
      hydro/thermal/renewable dispatch, a combined balance formulation
      is required.
    """
    renewable_add_sets_and_params(m, data)
    renewable_add_variables(m)
    add_renewable_capacity_constraints(m)
    if include_objective:
        add_renewable_balance_constraint(m)
        set_objective_renewable(m)
    return m
