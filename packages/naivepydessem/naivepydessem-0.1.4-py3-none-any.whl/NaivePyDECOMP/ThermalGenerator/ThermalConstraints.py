"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Constraint builders for thermal unit commitment (UC) formulations in Pyomo.
Each function attaches a specific block of constraints to a
ConcreteModel, enabling modular construction of MILP/MIQP/MINLP UC
models. The naming convention uses the thermal_* prefix for variables,
parameters, and constraint blocks attached to the model.

Constraint Families
-------------------
1. Balance (system-wide):

   - sum_g thermal_p[g,t] + D[t] = d[t]

2. Capacity (per unit and period):

   - Lower bound: thermal_Pmin[g] * thermal_u[g,t] <= thermal_p[g,t]
   - Upper bound: thermal_p[g,t] <= thermal_Pmax[g] * thermal_u[g,t]

Usage
-----
Combine these builders with:

- set/parameter/variable definitions for thermal UC, and
- an appropriate objective (quadratic or piecewise linear).

By composing the blocks, one can construct MIQP (quadratic costs) or
MILP (piecewise linear costs) UC formulations, optionally with reserve constraints.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import Constraint, value


def thermal_add_balance_constraint(m):
    """
    Add the system-wide energy balance constraint.

    For each period t, the total thermal generation plus the deficit
    must match the demand:

        sum_g thermal_p[g,t] + D[t] == d[t]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model with thermal parameters and variables

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with constraint block
        m.thermal_balance_constraint.

    Examples
    --------
    >>> # Assume m has sets/vars/params defined; then:
    >>> _ = thermal_add_balance_constraint(m)
    >>> m.thermal_balance_constraint.pprint()  # doctest: +ELLIPSIS
    """

    def _rule(m, t):
        return sum(m.thermal_p[g, t] for g in m.TG) + m.D[t] == m.d[t]
    m.thermal_balance_constraint = Constraint(m.T, rule=_rule)
    return m


def thermal_add_capacity_constraint(m, include_reserve: bool = False):
    """
    Add generation capacity limits for all units and periods.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model containing thermal parameters and variables

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with constraint blocks
        m.thermal_cap_lower_constraint and
        m.thermal_cap_upper_constraint.

    Examples
    --------
    >>> _ = thermal_add_capacity_constraint(m)
    """
    def _lower(m, g, t):
        return m.thermal_p[g, t] >= m.thermal_Gmin[g]

    def _upper(m, g, t):
        return m.thermal_p[g, t] <= m.thermal_Gmax[g]

    m.thermal_cap_lower_constraint = Constraint(m.TG, m.T, rule=_lower)
    m.thermal_cap_upper_constraint = Constraint(m.TG, m.T, rule=_upper)
    return m

