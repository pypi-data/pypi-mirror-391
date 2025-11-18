"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines the physical and operational constraints for transmission
lines in DC power flow formulations. These constraints link line
flows to phase-angle differences through susceptance and limit
the flow magnitude according to each line’s capacity.

Functions
---------
add_transmission_line_flow_constraints(m)
    Enforce the DC flow definition:
    ``F_ij,t = b_ij (θ_i,t − θ_j,t)`` for all lines and time periods.
add_transmission_line_flow_limits_constraints(m)
    Apply the flow capacity limits:
    ``−pmax_ij ≤ F_ij,t ≤ pmax_ij`` for all lines and time periods.

Notes
-----
- Each line is characterized by:
  - ``b_ij`` : susceptance (1/x_ij)
  - ``pmax_ij`` : maximum active power flow (MW)
  - ``endpoints`` : list of two bars [i, j]
- These constraints are suitable for both static (operational)
  and mixed-integer (expansion) formulations.
- Phase angles ``θ_i,t`` and ``θ_j,t`` must exist in the model
  before these constraints are declared.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import Constraint, ConcreteModel


def add_transmission_line_flow_constraints(m: ConcreteModel) -> ConcreteModel:
    """
    Add DC flow definition constraints to the model.

    Enforces, for each line ``l`` and time period ``t``:
    ``F_ij,t = b_ij (θ_i,t − θ_j,t)``

    For the transport model, F_ij,t is unrestricted by Second Kirchoff law

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing:
        - ``m.LT`` : set of transmission lines
        - ``m.T`` : set of time periods
        - ``m.lines_flow[l,t]`` : power flow variable (MW)
        - ``m.lines_b[l]`` : line susceptance (1/x)
        - ``m.lines_endpoints[l]`` : list of bar identifiers [i, j]
        - ``m.theta[b,t]`` : phase angle variable (radians)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with constraint block ``m.FlowDefinitionConstraint``.

    Notes
    -----
    - Flow sign convention: positive from the first to the second
      bar in the ``endpoints`` list.
    - This constraint establishes the physical relationship between
      electrical angles and transmitted power in the DC approximation.
    """
    def _flow_rule(m, l, t):
        i, j = m.lines_endpoints[l]
        if m.lines_transmission_model[l] == "dc":
            # trick to get Power Flow in MW => multiply by p_base
            return m.lines_flow[l, t] == m.p_base * m.lines_b[l] * (m.theta[i, t] - m.theta[j, t])
        return Constraint.Skip
    
    m.FlowDefinitionConstraint = Constraint(m.LT, m.T, rule=_flow_rule)
    return m

def add_transmission_line_flow_limits_constraints(m: ConcreteModel) -> ConcreteModel:
    """
    Add flow capacity limit constraints to the model.

    For each line ``l`` and time period ``t``:
    ``−pmax_ij ≤ F_ij,t ≤ pmax_ij``

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing:
        - ``m.LT`` : set of transmission lines
        - ``m.T`` : set of time periods
        - ``m.lines_flow[l,t]`` : power flow variable (MW)
        - ``m.lines_pmax[l]`` : maximum capacity (MW)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with constraint block ``m.LinesFlowMaxLimitConstraint`` and 
        ``m.LinesFlowMinLimitConstraint``.

    Notes
    -----
    - The limit is symmetric (±pmax) and applies to both flow directions.
    - These constraints should be added after
      :func:`add_transmission_line_flow_constraints`.
    """
    def _flow_max_rule(m, l, t):
        return m.lines_flow[l, t] <= m.lines_pmax[l]
    
    def _flow_min_rule(m, l, t):
        return m.lines_flow[l, t] >= - m.lines_pmax[l]
    
    m.LinesFlowMaxLimitConstraint = Constraint(m.LT, m.T, rule=_flow_max_rule)
    m.LinesFlowMinLimitConstraint = Constraint(m.LT, m.T, rule=_flow_min_rule)
    return m