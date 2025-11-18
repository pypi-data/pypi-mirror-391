"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines the operational constraints for renewable generation
within Pyomo-based unit commitment and dispatch models. It enforces both
the per-unit generation availability limits and the system-wide energy
balance when only renewable units and deficit are considered.

Functions
---------
add_renewable_capacity_constraints(m)
    Enforce that renewable generation for each unit and period does not
    exceed the exogenous availability profile ``gbar``.
add_renewable_balance_constraint(m)
    Enforce the energy balance by equating total renewable generation
    plus deficit to the system demand at each time period.

Notes
-----
- The capacity constraints guarantee that ``renewable_gen[r,t]`` is bounded
  above by ``renewable_gbar[r,t]``, which typically comes from forecasts.
- The balance constraint is suitable for renewable-only models. In hybrid
  models (thermal + hydro + renewables), a combined balance formulation
  must be applied instead.
- The deficit variable ``D[t]`` provides feasibility when renewable
  generation cannot meet demand.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""


from pyomo.core import Constraint


def add_renewable_capacity_constraints(m):
    """
    Add renewable capacity (availability) constraints.

    For each renewable unit ``r`` and time period ``t``, the dispatched
    renewable generation cannot exceed its available potential
    (exogenous profile ``gbar``):

        renewable_gen[r,t] <= renewable_gbar[r,t]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model containing:
        - Sets: ``m.RU`` (renewable units), ``m.T`` (time periods)
        - Variables: ``m.renewable_gen[r,t]`` (MW)
        - Parameters: ``m.renewable_gbar[r,t]`` (MW, availability profile)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with constraint block
        ``m.renewable_cap_constraint``.

    Notes
    -----
    - Ensures that renewable generation respects exogenous availability.
    - The availability parameter ``m.renewable_gbar`` is typically
      initialized from forecast profiles or scenario data.
    """
    def _cap_rule(m, r, t):
        return m.renewable_gen[r, t] <= m.renewable_gbar[r, t]
    m.renewable_cap_constraint = Constraint(m.RU, m.T, rule=_cap_rule)
    return m


def add_renewable_balance_constraint(m):
    """
    Add the system-wide energy balance constraint for renewable-only models.

    Enforces, for each period ``t``, that the total renewable generation
    plus the deficit variable equals the system demand:

        sum_r renewable_gen[r,t] + D[t] == d[t]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model containing:
        - Sets: ``m.RU`` (renewable units), ``m.T`` (time periods)
        - Variables: ``m.renewable_gen[r,t]`` (MW), ``m.D[t]`` (MW, deficit)
        - Parameters: ``m.d[t]`` (MW, demand)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with constraint block
        ``m.renewable_balance_constraint``.

    Notes
    -----
    - This balance assumes a system composed solely of renewable units
      and deficit. For hybrid systems (hydro, thermal, renewables),
      a combined balance constraint should be implemented.
    - The deficit variable ``m.D[t]`` allows feasibility in case
      renewable generation is insufficient to meet demand.
    """
    def _energy_balance_rule(m, t):
        return sum(m.renewable_gen[r, t] for r in m.RU) + m.D[t] == m.d[t]
    m.renewable_balance_constraint = Constraint(m.T, rule=_energy_balance_rule)
    return m
