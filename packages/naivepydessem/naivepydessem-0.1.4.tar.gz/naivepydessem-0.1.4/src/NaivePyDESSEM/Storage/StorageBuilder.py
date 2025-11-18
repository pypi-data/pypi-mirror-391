"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage — Model Builder

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
High-level builders for storage-only optimization models in Pyomo. This
module assembles the complete model structure by combining storage sets,
parameters, variables, constraints, and an optional objective function.

Functions
---------
build_storage(data, include_objective=True)
    Create a new ``ConcreteModel`` with storage components and, optionally,
    the balance constraint and objective.
add_storage_problem(m, data, include_objective=False)
    Add storage components (sets/params/vars/constraints) to an existing
    model and, optionally, attach the balance constraint and objective.

Notes
-----
- The default objective minimizes deficit cost (no explicit storage
  operating costs). If you have cycling costs or degradation penalties,
  replace the objective accordingly.
- For hybrid systems (hydro/thermal/renewables + storage), prefer a
  combined system balance and a joint objective in a higher-level builder.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConcreteModel, Objective, minimize

from .StorageDataTypes import StorageData
from .StorageObjective import set_objective_storage
from .StorageVars import storage_add_sets_and_params, storage_add_variables
from .StorageConstraints import (
    add_storage_energy_balance_constraint,
    add_storage_soc_bounds_constraint,
    add_storage_power_limits_constraint,
    add_storage_only_balance_constraint,
    add_storage_mutual_exclusion_constraint
)

def build_storage(data: StorageData, include_objective: bool = True) -> ConcreteModel:
    """
    Construct a complete Pyomo model for storage-only dispatch.

    Parameters
    ----------
    data : StorageData
        Input container with horizon, storage units, and time-step duration.
    include_objective : bool, optional
        If ``True``, add the storage-only balance constraint and attach the
        deficit objective (default is ``True``).

    Returns
    -------
    pyomo.environ.ConcreteModel
        A new model configured with storage sets/params/vars/constraints and,
        optionally, the balance constraint and objective.

    Notes
    -----
    - The model contains:
        * Sets: time periods (``m.T``), storage units (``m.SU``)
        * Parameters: SoC bounds/initial, power limits, efficiencies, Δt
        * Variables: SoC, charge, discharge, and (if missing) deficit
        * Constraints: SoC balance, SoC bounds, power limits
        * Optional: system balance and deficit objective
    """
    m = ConcreteModel()
    m = add_storage_problem(m=m, data=data, include_objective=include_objective)
    return m


def add_storage_problem(m: ConcreteModel,
                        data: StorageData,
                        include_objective: bool = False) -> ConcreteModel:
    """
    Add storage dispatch problem structure to an existing model.

    This routine initializes storage sets and parameters, declares decision
    variables, and attaches operational constraints. Optionally, it enforces
    a storage-only system balance and adds a deficit-penalizing objective.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Target model to be updated.
    data : StorageData
        Input container with horizon, units, and time-step duration.
    include_objective : bool, optional
        If ``True``, add the storage-only balance constraint and attach the
        deficit objective (default is ``False``).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with storage components and, optionally, the
        balance constraint and objective.

    Notes
    -----
    - Constraints added (always):
        * Energy (SoC) balance
        * SoC bounds (min/max)
        * Charge/discharge power limits
    - If ``include_objective=True``:
        * Add storage-only balance: Σ(dis − ch) + D = d
        * Attach deficit objective
    """
    # sets & params
    storage_add_sets_and_params(m, data)
    # variables
    storage_add_variables(m)
    # constraints
    add_storage_energy_balance_constraint(m)
    add_storage_soc_bounds_constraint(m)
    add_storage_power_limits_constraint(m)
    add_storage_mutual_exclusion_constraint(m)  # descomente se usar binária

    if include_objective:
        add_storage_only_balance_constraint(m)
        set_objective_storage(m)

    return m
