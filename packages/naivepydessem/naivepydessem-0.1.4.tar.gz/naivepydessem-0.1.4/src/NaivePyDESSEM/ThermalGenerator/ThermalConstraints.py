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
   - Upper bound (no reserve): thermal_p[g,t] <= thermal_Pmax[g] * thermal_u[g,t]
   - Upper bound (with reserve): thermal_p[g,t] + thermal_r[g,t] <= thermal_Pmax[g] * thermal_u[g,t]

3. Spinning reserve:
   sum_g thermal_r[g,t] >= thermal_Rreq[t]

4. Commitment logic:

   - Mutual exclusivity: thermal_y[g,t] + thermal_w[g,t] <= 1
   - State transition:

     - t=1: thermal_u[g,1] - thermal_u0[g] = thermal_y[g,1] - thermal_w[g,1]
     - t>1: thermal_u[g,t] - thermal_u[g,t-1] = thermal_y[g,t] - thermal_w[g,t]

5. Ramping (with start/shut effects):
   
   - Up: thermal_p[g,t] - thermal_p[g,t-1] <= thermal_RU[g] + thermal_Pmax[g] * thermal_y[g,t]
   - Down: thermal_p[g,t-1] - thermal_p[g,t] <= thermal_RD[g] + thermal_Pmax[g] * thermal_w[g,t]
     At t=1, use thermal_p0[g] in place of the previous-period power.)

6. Minimum up/down time:
   
   - Up: \SUM_{t=t-Tu+1}^{t} thermal_y[g,t] <= thermal_u[g,t]
   - Down: \SUM_{t=t-Td+1}^{t} thermal_w[g,t] <= 1 - thermal_u[g,t]

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

    Enforces unit-wise lower and upper bounds linked to the on/off status.
    When include_reserve is True, the upper bound also accounts for
    spinning reserve provision.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model containing thermal parameters and variables
    include_reserve : bool, optional
        If True, apply thermal_p + thermal_r <= Pmax * u as the upper
        bound. Default is False.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with constraint blocks
        m.thermal_cap_lower_constraint and
        m.thermal_cap_upper_constraint.

    Examples
    --------
    >>> # Upper bound includes reserve if requested:
    >>> _ = thermal_add_capacity_constraint(m, include_reserve=True)
    """
    def _lower(m, g, t):
        return m.thermal_Pmin[g] * m.thermal_u[g, t] <= m.thermal_p[g, t]

    def _upper(m, g, t):
        if include_reserve:
            return (m.thermal_p[g, t] + m.thermal_r[g, t]
                    <= m.thermal_Pmax[g] * m.thermal_u[g, t])
        return m.thermal_p[g, t] <= m.thermal_Pmax[g] * m.thermal_u[g, t]
    m.thermal_cap_lower_constraint = Constraint(m.TG, m.T, rule=_lower)
    m.thermal_cap_upper_constraint = Constraint(m.TG, m.T, rule=_upper)
    return m


def thermal_add_reserve_constraint(m):
    """
    Add spinning reserve requirement constraints.

    For each period t, total spinning reserve must satisfy:

        sum_g thermal_r[g,t] >= thermal_Rreq[t].

    Notes
    -----
    This constraint assumes that reserve variables and requirements are
    present, and that capacity limits were added with
    include_reserve=True.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with thermal parameters and variables

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with constraint block
        m.thermal_reserve_req_constraint.

    Examples
    --------
    >>> _ = thermal_add_reserve_constraint(m)
    >>> m.thermal_reserve_req_constraint.pprint()  # doctest: +ELLIPSIS
    """
    assert hasattr(m, 'r'), "thermal_add_reserve requires reserve variables."

    def _req(m, t):
        return sum(m.thermal_r[g, t] for g in m.TG) >= m.thermal_Rreq[t]
    m.thermal_reserve_req_constraint = Constraint(m.T, rule=_req)
    return m


def thermal_add_startup_shutdown_logic_constraint(m):
    """
    Add startup/shutdown logical consistency constraints.

    Imposes:

    - Mutual exclusivity of start and shut in the same period:
      thermal_y[g,t] + thermal_w[g,t] <= 1.
    - State transition linking on/off status to start/shut variables:
    
      - t=1: thermal_u[g,1] - thermal_u0[g] = thermal_y[g,1] - thermal_w[g,1]
      - t>1: thermal_u[g,t] - thermal_u[g,t-1] = thermal_y[g,t] - thermal_w[g,t]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with thermal paraeters and variables

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with constraint blocks
        m.thermal_f_ss_constraint and m.thermal_logic_constraint.

    Examples
    --------
    >>> _ = thermal_add_startup_shutdown_logic_constraint(m)
    """
    
    def _f_shut_start_same_time(m, g, t):
        return m.thermal_y[g, t] + m.thermal_w[g, t] <= 1

    def _logic(m, g, t):
        if t == 1:
            return (m.thermal_u[g, 1] - m.thermal_u0[g]
                    == m.thermal_y[g, 1] - m.thermal_w[g, 1])
        return (m.thermal_u[g, t] - m.thermal_u[g, t-1]
                == m.thermal_y[g, t] - m.thermal_w[g, t])
    m.thermal_f_ss_constraint = Constraint(
        m.TG, m.T, rule=_f_shut_start_same_time)
    m.thermal_logic_constraint = Constraint(m.TG, m.T, rule=_logic)
    return m


def thermal_add_ramps_constraint(m):
    """
    Add ramp-up and ramp-down constraints.

    Limits the change in generation between consecutive periods according
    to thermal_RU[g] and thermal_RD[g], with allowances when a unit
    starts up or shuts down. At t=1, the previous-period generation is
    given by thermal_p0[g].

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with thermal paraeters and variables

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with constraint blocks
        m.thermal_ramp_up_constraint and m.thermal_ramp_dn_constraint.

    Examples
    --------
    >>> _ = thermal_add_ramps_constraint(m)
    """
    def _up(m, g, t):
        if t == 1:
            """if m.has_history:
                return (m.thermal_p[g, 1] - m.thermal_p0[g]
                    <= m.thermal_RU[g] + m.thermal_Pmax[g]*m.thermal_y[g, 1])"""
            return Constraint.Skip
        return (m.thermal_p[g, t] - m.thermal_p[g, t-1]
                <= m.thermal_RU[g] + m.thermal_Pmax[g]*m.thermal_y[g, t])

    def _down(m, g, t):
        if t == 1:
            """if m.has_history:
                return (m.thermal_p0[g] - m.thermal_p[g, 1]
                        <= m.thermal_RD[g] + m.thermal_Pmax[g]*m.thermal_w[g, 1])"""
            return Constraint.Skip
        return (m.thermal_p[g, t-1] - m.thermal_p[g, t]
                <= m.thermal_RD[g] + m.thermal_Pmax[g]*m.thermal_w[g, t])

    m.thermal_ramp_up_constraint = Constraint(m.TG, m.T, rule=_up)
    m.thermal_ramp_dn_constraint = Constraint(m.TG, m.T, rule=_down)
    return m


from pyomo.environ import Constraint, value

def thermal_add_min_up_down_constraint(m):
    """
    Add minimum up-time and down-time constraints with initial state consideration.

    These constraints ensure logical consistency of operating sequences:
    
    - **Minimum up-time**: if a unit is started, it must remain ON for at least
      thermal_t_up[g] periods. If the unit has already been ON before the
      optimization window (according to thermal_init_status[g] > 0),
      the remaining required ON time is reduced accordingly.

    - **Minimum down-time**: if a unit is shut down, it must remain OFF for at least
      thermal_t_dn[g] periods. If the unit has already been OFF before the
      optimization window (according to thermal_init_status[g] < 0),
      the remaining required OFF time is reduced accordingly.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with thermal paraeters and variables

    Returns
    -------
    pyomo.environ.ConcreteModel
        Model with added constraint blocks:
        - m.thermal_min_up_constraint
        - m.thermal_min_dn_constraint

    Examples
    --------
    >>> _ = thermal_add_min_up_down_constraint(m)
    """
    def _min_up(m, g, t):
        Tu = int(value(m.thermal_t_up[g]))
        if Tu <= 1:
            return Constraint.Skip

        initial_status = int(value(m.thermal_init_status[g]))
        if initial_status > 0:
            if t <= Tu - initial_status:
                return Constraint.Skip

        start = max(1, t - Tu + 1)
        return sum(m.thermal_y[g, tau] for tau in range(start, t+1)) <= m.thermal_u[g, t]

    def _min_dn(m, g, t):
        Td = int(value(m.thermal_t_dn[g]))
        if Td <= 1:
            return Constraint.Skip

        initial_status = int(value(m.thermal_init_status[g]))
        if initial_status < 0:
            if t <= Td + initial_status:
                return Constraint.Skip

        start = max(1, t - Td + 1)
        
        return sum(m.thermal_w[g, tau] for tau in range(start, t+1)) <= 1 - m.thermal_u[g, t]

    m.thermal_min_up_constraint = Constraint(m.TG, m.T, rule=_min_up)
    m.thermal_min_dn_constraint = Constraint(m.TG, m.T, rule=_min_dn)
    return m

