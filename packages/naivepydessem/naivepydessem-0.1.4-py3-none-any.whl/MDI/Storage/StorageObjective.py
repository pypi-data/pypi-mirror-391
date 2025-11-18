
"""
Storage Objective Function Module
=================================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines the **objective function** for the energy storage subsystem,
used in the Mixed-Integer Linear Programming (MILP) formulation of the
operation and expansion planning problem.

Description
-----------
The objective function represents the **total system cost** associated
with the operation and investment of storage units.  
It aggregates two main cost components:

1. **Operational Cost (c_op)** — proportional to the total amount of energy moved
   (charging and discharging), weighted by the duration of each load level.
2. **Investment Cost (c_inv)** — proportional to the existence of installed
   capacity throughout the planning horizon.

Both cost components are expressed as additive terms in a global minimization
objective, consistent with standard formulations in expansion planning models.

Mathematical Formulation
------------------------
The objective function is defined as:

\[
\min \; Z = 
\sum_{s \in SU} \sum_{t \in T} \sum_{p \in P}
  h_p \, c^{op}_s \, (P^{ch}_{s,t,p} + P^{dis}_{s,t,p})
+ \sum_{s \in SU} \sum_{t \in T}
  c^{inv}_s \, x_{s,t}
\]

where:

| Symbol | Description |
|:--------|:------------|
| \(h_p\) | Duration of load level \(p\) (hours) |
| \(c^{op}_s\) | Operational cost of unit \(s\) (per MWh) |
| \(c^{inv}_s\) | Investment cost of unit \(s\) |
| \(P^{ch}_{s,t,p}\) | Charging power (MW) |
| \(P^{dis}_{s,t,p}\) | Discharging power (MW) |
| \(x_{s,t}\) | Binary existence variable |
| \(SU, T, P\) | Sets of storage units, time steps, and load levels |

Functions
---------
set_objective_storage(m)
    Adds the objective function to the Pyomo model, minimizing total storage costs.

Notes
-----
- The function assumes that all sets, parameters, and variables
  have already been defined (typically via `storage_add_sets_and_params`
  and `storage_add_variables`).
- Units are consistent with the rest of the framework:  
  MW for power, MWh for energy, and monetary units for costs.
- The resulting objective is fully compatible with mixed-integer solvers
  such as CBC, GLPK, or commercial solvers (Gurobi, CPLEX).

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes, UFPR, 2023.
"""

from pyomo.environ import ConcreteModel, Objective, minimize


def set_objective_storage(m: ConcreteModel) -> ConcreteModel:
    """
    Define the total cost minimization objective for the storage subsystem.

    This function constructs a Pyomo `Objective` expression that
    aggregates operational and investment costs for all storage units
    across time steps and load levels.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing all sets, parameters, and variables
        related to the storage subsystem.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model instance, now with an attached objective function
        named `OBJ`.

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> # (Assume sets and parameters already defined)
    >>> set_objective_storage(m)
    >>> print(m.OBJ.sense)
    minimize
    """
    def _obj_rule(m):
        expr = sum(
            # Operational cost: proportional to charging and discharging energy
            m.level_hours[p] * m.storage_c_op[s] * (
                m.storage_ch[s, t, p] + m.storage_dis[s, t, p]
            )
            for s in m.SU for t in m.T for p in m.P
        ) + sum(
            # Investment cost: proportional to installed capacity
            m.storage_c_inv[s] * m.storage_x[s, t]
            for s in m.SU for t in m.T
        )
        return expr

    # Define objective: minimize total storage cost
    m.OBJ = Objective(rule=_obj_rule, sense=minimize)
    return m
