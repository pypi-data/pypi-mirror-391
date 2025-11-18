"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Connection Bar — Balance Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines the nodal (per-bar) power balance constraints for
Pyomo-based operation and expansion models. It enforces Kirchhoff’s
Current Law (1st Law) at each connection bar and time period, ensuring
that total injections (generation, inflows) and withdrawals (demand,
outflows, and storage) are balanced.

Functions
---------
add_connection_bar_balance_constraint(m)
    Assemble and add the nodal power balance constraints for all bars
    and time periods using the component expressions provided by
    :mod:`ConnectionBarEquations`.

Notes
-----
- The routine calls modular expression builders such as
  :func:`add_hydraulic_balance_expression`,
  :func:`add_thermal_balance_expression`,
  :func:`add_renewable_balance_expression`,
  :func:`add_storage_balance_expression`, and
  :func:`add_transmission_line_balance_expression`.
- Each time period ``t`` generates a set of symbolic expressions by bar,
  which are then converted into Pyomo constraints and appended to
  ``m.Balance`` (a :class:`pyomo.core.base.constraint.ConstraintList`).
- This formulation supports hybrid systems (hydro, thermal, renewable,
  storage) with multiple connection bars.
- The deficit variable ``m.D[bar,t]`` ensures model feasibility whenever
  the available generation and imports cannot fully meet local demand.
- For single-bus systems, the resulting formulation is equivalent to the
  traditional system-wide balance equation.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConstraintList, Constraint, ConcreteModel
from .ConnectionBarEquations import add_connection_bar_balance_expression
import numpy as np


def add_connection_bar_balance_constraints(m: ConcreteModel) -> ConcreteModel:
    """
    Add nodal power balance constraints for all connection bars and time periods.

    For each period ``t`` in the planning horizon, this function assembles
    the power balance expressions by connection bar (node) using
    :func:`add_connection_bar_balance_expression`, and converts them into
    Pyomo constraints stored in ``m.Balance``.

    Mathematically, for each bar ``b`` and period ``t``:

    .. math::

        \\sum_{s \\in S_b} P^{\\text{gen}}_{s,t}
        + \\sum_{i:(i,b)\\in\\mathcal{L}} F_{i b,t}
        - \\sum_{j:(b,j)\\in\\mathcal{L}} F_{b j,t}
        + D_{b,t} = d_{b,t}

    where:
        - ``P^{gen}`` represents generation injections (hydro, thermal, renewable, storage),
        - ``F_{ij,t}`` are line flows between bars ``i`` and ``j``,
        - ``D_{b,t}`` is the local deficit variable,
        - ``d_{b,t}`` is the active demand at bar ``b``.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing:
        - Sets: ``m.BAR`` (connection bars), ``m.T`` (time periods)
        - Variables: ``m.D[bar,t]`` (deficit), generation and flow variables
        - Parameters: ``m.d[bar,t]`` (demand per bar and time)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with all bar-level power balance constraints
        added to ``m.Balance``.

    Notes
    -----
    - The component ``m.Balance`` is created as a :class:`ConstraintList`
      if not already present.
    - Each call to this function appends constraints dynamically;
      it does not overwrite existing entries.
    - The structure is compatible with both operation (short-term)
      and expansion (long-term) formulations.
    """
    if not hasattr(m, "Balance"):
        m.Balance = ConstraintList()

    for t in m.T:
        balance_exprs = {}
        add_connection_bar_balance_expression(m, t, balance_exprs)

        for b, expr in balance_exprs.items():
            m.Balance.add(expr == m.d[b, t])
    return m

def add_connection_bar_angle_limits_constraints(m: ConcreteModel) -> ConcreteModel:
    """
    Add angular bounds for non-slack connection bars.

    Enforces -π ≤ θ_b ≤ π for all bars that are not marked as slack.
    This constraint bounds the nodal phase angles in DC power flow
    formulations, preventing unrealistic or numerically unstable
    solutions.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing:
        - ``m.BAR`` : set of all bars
        - ``m.SB`` : set of slack bars
        - ``m.theta[b]`` : voltage phase angle variable (radians)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with constraint block ``m.AngleLimits``.

    Notes
    -----
    - The bounds are symbolic (±π radians) and apply only to non-slack bars.
    - The restriction helps numerical stability when solving large MILP
      or MINLP systems involving binary investment variables.
    - This function complements :func:`add_connection_bar_slack_constraints`.

    References
    ----------
    [1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
    [2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
        Lecture Notes, EELT7030/UFPR, 2023.
    """
    def _angle_sup_rule(m, b, t):
        return m.theta[b, t] <= np.pi
    
    def _angle_inf_rule(m, b, t):
        return m.theta[b, t] >= -np.pi
    
    non_slack = [b for b in m.CB if not getattr(m, "SB", set()).__contains__(b)]
    if not m.unique_bar:
        if non_slack:
            m.AngleLimitsSupConstraint = Constraint(non_slack, m.T, rule=_angle_sup_rule)
            m.AngleLimitsInfConstraint = Constraint(non_slack, m.T, rule=_angle_inf_rule)

    return m

def add_connection_bar_slack_constraints(m: ConcreteModel) -> ConcreteModel:
    """
    Add the slack-bar reference constraints to fix phase angles.

    Enforces θ_b = 0 for all bars marked as slack in the system data,
    establishing the angular reference for the DC power flow model.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing:
        - ``m.theta[b]`` : voltage phase angle variable (radians)
        - ``m.SB`` : set of bars designated as reference

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with constraint block ``m.SlackConstraint``.

    Notes
    -----
    - The DC power flow equations determine only angle differences,
      so a reference (slack) bar must be fixed to zero to avoid
      singularity in the system Jacobian.
    - In multi-slack configurations (rare but possible), all selected
      bars are fixed to θ = 0.
    - This constraint should be added **after** variable declaration
      and set initialization (i.e., after :mod:`ConnectionBarVariables`).

    """
    def _slack_rule(m, b, t):
        return m.theta[b, t] == 0.0
    
    if not m.unique_bar:
        if hasattr(m, "SB") and hasattr(m, "theta"):
            m.SlackConstraint = Constraint(m.SB, m.T, rule=_slack_rule)
    return m
