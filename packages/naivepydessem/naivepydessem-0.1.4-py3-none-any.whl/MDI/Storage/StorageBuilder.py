"""
Storage Builder Module
======================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines the construction logic of the **energy storage subsystem**
within the MDI optimization framework. It provides high-level builder functions
that assemble the complete storage model — including sets, parameters,
variables, constraints, and the objective function — from structured input data.

Description
-----------
Two functions are defined in this module:

1. **`build_storage(data, include_objective=True)`**  
   Creates and initializes a standalone Pyomo model for the storage subsystem,
   suitable for testing or modular integration.

2. **`add_storage_problem(m, data, include_objective=False)`**  
   Extends an existing Pyomo model with the complete storage problem definition,
   including constraints and (optionally) the objective function.

The builder integrates all necessary symbolic components:
sets and parameters, decision variables, constraints on power,
energy balance, state-of-charge (SoC), and investment logic.

Mathematical Overview
---------------------
The storage subsystem typically includes the following formulations:

**Energy balance**
\[
E_{t} = E_{t-1} + \eta_c P^{ch}_{t} - \frac{1}{\eta_d} P^{dis}_{t}
\]

**Power limits**
\[
0 \leq P^{ch}_{t}, P^{dis}_{t} \leq P^{max} \, x_{t}
\]

**State of charge bounds**
\[
E^{min} \leq E_{t} \leq E^{max}
\]

**Investment linkage**
\[
x_{t} = x_{t-1} + y_{t}
\]

where:
- \(E_t\): energy stored at period *t*  
- \(P^{ch}_t, P^{dis}_t\): charging/discharging power  
- \(\eta_c, \eta_d\): charging/discharging efficiencies  
- \(x_t, y_t\): operational and investment binary decisions  

Functions
---------
build_storage(data, include_objective=True)
    Creates and returns a complete Pyomo model for the storage subsystem.

add_storage_problem(m, data, include_objective=False)
    Adds the storage problem definition to an existing model.

Notes
-----
- The `include_objective` flag controls whether the subsystem-level
  objective (minimization of total storage cost) is included.
- The modular structure mirrors that of the generator subsystem
  to ensure composability within hybrid systems (hydrothermal or
  generation-storage models).
- All internal components (sets, variables, constraints) are
  imported from specialized modules to maintain separation of concerns.

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,
    EELT7030/UFPR, 2023.

Module Dependencies
-------------------
- **Internal:**  
  - ``StorageDataTypes``  
  - ``StorageObjective``  
  - ``StorageVars``  
  - ``StorageConstraints``  

- **External:**  
  - ``pyomo.environ`` (ConcreteModel, Objective, minimize)
"""

from pyomo.environ import ConcreteModel, Objective, minimize
from .StorageDataTypes import StorageData
from .StorageObjective import set_objective_storage
from .StorageVars import storage_add_sets_and_params, storage_add_variables
from .StorageConstraints import (
    add_storage_energy_balance_constraint,
    add_storage_investment_link_constraint,
    add_storage_power_limits_constraint,
    add_storage_soc_bounds_constraint,
    add_storage_mutual_exclusion_constraint
)


def build_storage(data: StorageData, include_objective: bool = True) -> ConcreteModel:
    """
    Build a standalone Pyomo model for the storage subsystem.

    This function creates a new ConcreteModel instance and populates it
    with all the sets, parameters, variables, and constraints required to
    represent an energy storage unit within the optimization framework.

    Parameters
    ----------
    data : StorageData
        Structured input data describing storage characteristics and parameters.
    include_objective : bool, optional
        If True, includes the subsystem objective function. Default is True.

    Returns
    -------
    pyomo.environ.ConcreteModel
        A fully defined storage model ready for integration or standalone analysis.
    """
    m = ConcreteModel()
    m = add_storage_problem(m=m, data=data, include_objective=include_objective)
    return m


def add_storage_problem(m: ConcreteModel,
                        data: StorageData,
                        include_objective: bool = False) -> ConcreteModel:
    """
    Add the complete storage problem definition to a given model.

    Extends an existing Pyomo model with the full symbolic formulation of
    the energy storage subsystem, including all relevant constraints and,
    optionally, the objective function.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which the storage subsystem will be appended.
    data : StorageData
        Structured data object defining all storage parameters and time horizon.
    include_objective : bool, optional
        If True, includes the storage cost minimization objective. Default is False.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model instance extended with storage sets, variables,
        constraints, and (optionally) the objective function.

    Notes
    -----
    The following constraints are added to the model:
    - Power limits (charging/discharging capacity)
    - Energy balance (state-of-charge dynamics)
    - Investment linkage (capacity expansion logic)
    - SoC bounds (minimum and maximum limits)
    """
    # Sets and parameters
    storage_add_sets_and_params(m, data)
    # Variables
    storage_add_variables(m)
    # Constraints
    add_storage_power_limits_constraint(m)
    add_storage_energy_balance_constraint(m)
    add_storage_investment_link_constraint(m)
    add_storage_soc_bounds_constraint(m)
    add_storage_mutual_exclusion_constraint(m)

    # Objective (optional)
    if include_objective:
        set_objective_storage(m)

    return m
