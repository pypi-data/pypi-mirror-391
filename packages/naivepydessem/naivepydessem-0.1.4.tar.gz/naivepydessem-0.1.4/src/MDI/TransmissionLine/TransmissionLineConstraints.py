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
    Add DC flow definition constraints to the model with MILP-compatible linearization.

    Enforces, for each line ``l``, time ``t``, and load level ``p``:
        F[l,t,p] = b[l] * (θ[i,t,p] − θ[j,t,p]) * x[l,t]

    To preserve MILP linearity, this relation is linearized using a Big-M formulation:

        -M * (1 - x[l,t]) <= F[l,t,p] - b[l]*(θ[i,t,p] - θ[j,t,p]) <= M * (1 - x[l,t])

    where:
        M = lines_Fmax[l]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model containing:
        - ``m.LT`` : set of transmission lines
        - ``m.T`` : set of time periods
        - ``m.P`` : set of load levels
        - ``m.lines_flow[l,t,p]`` : power flow variable (MW)
        - ``m.lines_b[l]`` : line susceptance (1/x)
        - ``m.lines_Fmax[l]`` : flow capacity (MW)
        - ``m.lines_endpoints[l]`` : tuple/list [i, j]
        - ``m.theta[b,t,p]`` : phase angle (radians)
        - ``m.lines_x[l,t]`` : binary operational state (1 if built)

    Returns
    -------
    pyomo.environ.ConcreteModel
        Model with constraint block ``m.FlowDefinitionConstraint`` added.

    Notes
    -----
    - The formulation ensures linearity by relaxing the DC flow equation
      when the line is not built (x = 0).
    - Flow limits (±Fmax) should already be enforced elsewhere.
    - ``m.p_base`` (power base) is optional and defaults to 1 if not present.
    """

    def _flow_rule_pos(m, l, t, p):
        """Upper inequality: F - b*(θ_i - θ_j) ≤ M*(1 - x)"""
        i, j = m.lines_endpoints[l]
        if m.lines_transmission_model[l] == "dc":
            M = m.lines_pmax[l]
            return (
                m.lines_flow[l, t, p]
                - m.p_base * m.lines_b[l] * (m.theta[i, t, p] - m.theta[j, t, p])
                <= M * (1 - m.lines_x[l, t])
            )
        return Constraint.Skip

    def _flow_rule_neg(m, l, t, p):
        """Lower inequality: F - b*(θ_i - θ_j) ≥ -M*(1 - x)"""
        i, j = m.lines_endpoints[l]
        if m.lines_transmission_model[l] == "dc":
            M = m.lines_pmax[l]
            return (
                m.lines_flow[l, t, p]
                - m.p_base * m.lines_b[l] * (m.theta[i, t, p] - m.theta[j, t, p])
                >= -M * (1 - m.lines_x[l, t])
            )
        return Constraint.Skip

    # Add constraints to model
    m.FlowDefinitionConstraint_pos = Constraint(m.LT, m.T, m.P, rule=_flow_rule_pos)
    m.FlowDefinitionConstraint_neg = Constraint(m.LT, m.T, m.P, rule=_flow_rule_neg)

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
    def _flow_max_rule(m, l, t, p):
        return m.lines_flow[l, t, p] <= m.lines_pmax[l] * m.lines_x[l, t]
    
    def _flow_min_rule(m, l, t, p):
        return m.lines_flow[l, t, p] >= -m.lines_pmax[l] * m.lines_x[l, t]
    
    m.LinesFlowMaxLimitConstraint = Constraint(m.LT, m.T, m.P, rule=_flow_max_rule)
    m.LinesFlowMinLimitConstraint = Constraint(m.LT, m.T, m.P, rule=_flow_min_rule)
    return m



def add_transmission_line_investment_link_constraints(m):
    """
    Add the investment linkage constraint for transmission line units.

    Defines the relationship between construction decisions and
    operational availability across time periods.  
    Ensures that the existence variable accumulates investments
    over the planning horizon.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing the investment and operational variables.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The model with investment linkage and initial-state constraints applied.
    """
    
    def _inv_initial_value_rule(m, l, t):
        if t == 1:
            return m.lines_x[l, t] == m.lines_state[l]
        return Constraint.Skip

    def _inv_link_rule(m, l, t):
        if t == 1:
            return m.lines_x[l, t] == m.lines_y[l, t]
        return m.lines_x[l, t] == m.lines_x[l, m.T.prev(t)] + m.lines_y[l, t]

    m.lines_initial_state_constraint = Constraint(m.LT, m.T, rule=_inv_initial_value_rule)
    m.lines_investment_link_constraint = Constraint(m.LT, m.T, rule=_inv_link_rule)
    return m


