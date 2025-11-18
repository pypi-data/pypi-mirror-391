"""
Hydropower Constraints Module for Multi-Mode Generation Modeling
================================================================

This module implements hydropower-related constraints for Unit Commitment
and Dispatch models in Pyomo. It supports multiple representations of the
hydraulic production function (FPH), including constant productivity,
specific productivity (fixed head), simplified polynomial approximations,
and exact head-dependent formulations.

The functions herein enforce:
- Generation computation using plant-specific FPH callables;
- Reservoir mass balance via continuity constraints;
- Upstream water aggregation for cascaded systems (no travel time);
- Final storage requirements;
- System-wide demand balance for hydropower-only settings.

Each hydropower mode (constant, specific, exact, simplified) must be
associated with a callable set in the model attribute m.hydro_FPH[h].
The upstream connectivity and inflows must be available as
m.hydro_upstreams[h] and m.hydro_afluencia[h][t-1], respectively.
This module assumes **no routing delay** between cascaded plants.

This interface is compatible with Pyomo-based MILP/MIQP dispatch models
and is intended to interoperate cleanly with thermal subsystems when a
combined balance is used elsewhere.

Imported Dependencies
---------------------
- pyomo.environ.Constraint

Functions
---------
- add_hydro_generation_constraint(m)
- hydro_total_inflow_expr(m, h, t)
- add_hydro_qmin_constraint(m)
- add_hydro_qmax_constraint(m)
- add_hydro_volume_continuity_constraint(m)
- add_hydro_volume_meta_constraint(m)
- add_hydro_volume_max_constraint(m)
- add_hydro_volume_mim_constraint(m)
- add_hydro_balance_constraint(m)

Model Requirements
------------------
Sets
    m.HG : hydropower units
    m.T  : time periods
Variables
    m.hydro_V[h,t] : storage volume (hm^3)
    m.hydro_Q[h,t] : turbined discharge (m^3/s)
    m.hydro_S[h,t] : spill discharge (m^3/s)
    m.hydro_G[h,t] : hydropower generation (MW)
    m.D[t]         : deficit (MW), if used
Parameters
    m.hydro_zeta_vol : flow-to-volume converter per period (e.g., 3600/1e6)
    m.hydro_Vini[h]  : initial storage (hm^3)
    m.hydro_Vmeta[h] : terminal storage target (hm^3)
    m.hydro_Vmin[h]  : minimum storage (hm^3)
    m.hydro_Vmax[h]  : maximum storage (hm^3)
    m.hydro_afluencia[h][t-1] : natural inflow (m^3/s), 0-based external array
    m.hydro_upstreams[h]      : collection of upstream units for h
    m.hydro_FPH[h]            : callable FPH(Q,V,S) => MW
    m.hydro_compute_total_inflow[h] : bool flag to aggregate upstream releases
    m.horizon : last period index, if used for terminal constraints
    m.d[t]    : demand (MW), if hydropower-only balance is applied

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import Constraint


def add_hydro_generation_constraint(m):
    """
    Add hydropower generation constraints using plant-specific FPH callables.

    For each hydropower unit and time period, this constraint enforces

    m.hydro_G[h, t] == m.hydro_FPH[h](m.hydro_Q[h, t], m.hydro_V[h, t], m.hydro_S[h, t])

    The callable m.hydro_FPH[h] may represent:

    - Constant productivity
    - Specific productivity with fixed head
    - Exact head-dependent model (possibly nonlinear)
    - Simplified approximations

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Pyomo model containing hydraulic variables and callables
        
    Returns
    -------
    pyomo.core.base.PyomoModel.ConcreteModel
        The updated model with constraint block m.hydro_generation_constraint.

    Notes
    -----
    Ensure unit consistency across the callable and model variables so that
    the right-hand side yields MW.
    """

    def _gen_rule(m, h, t):
        return m.hydro_G[h, t] == m.hydro_FPH[h](m.hydro_Q[h, t],
                                                 m.hydro_V[h, t],
                                                 m.hydro_S[h, t])

    m.hydro_generation_constraint = Constraint(m.HG, m.T, rule=_gen_rule)
    return m


def hydro_total_inflow_expr(m, h, t):
    """
    Compute instantaneous total inflow without travel time.

    The returned expression equals the sum of:

    (a) natural inflow to plant h at period t, plus
    (b) releases (turbined flow + spill) from all immediate upstream plants
        during the **same** period t (no routing delay).

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Pyomo model providing variables m.hydro_Q, m.hydro_S and
        parameters/containers m.hydro_afluencia, m.hydro_upstreams,
        and the boolean flag m.hydro_compute_total_inflow[h].
    h : hashable
        Plant identifier (element of m.HG).
    t : int
        Time period (element of m.T). External arrays are 0-based,
        hence access via t-1.

    Returns
    -------
    pyomo.core.expr.numeric_expr.ExpressionBase
        Pyomo expression for the total inflow to plant h at time t.

    Notes
    -----
    This function assumes **no travel time** between cascaded plants. If
    routing is relevant, replace this expression with a routed inflow model.
    """
    nat = m.hydro_afluencia[h][t-1]
    if m.hydro_compute_total_inflow[h]:
        if len(m.hydro_upstreams[h]) == 0:
            return nat
        return nat + sum(m.hydro_Q[hu, t] + m.hydro_S[hu, t]
                         for hu in m.hydro_upstreams[h])
    return nat


def add_hydro_qmin_constraint(m):
    """
    Add minimum turbined flow constraint.

    Ensures that, for each hydro unit and period,
    m.hydro_Q[h,t] >= m.hydro_Qmin[h].

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with variables/parameters:
        m.hydro_Q[h,t], m.hydro_Qmin[h]; sets m.HG, m.T.

    Returns
    -------
    pyomo.environ.ConcreteModel
        Model with constraint block m.hydro_qmin_constraint.
    """
    def _qmin_rule(m, h, t):
        return m.hydro_Q[h, t] >= m.hydro_Qmin[h]
    m.hydro_qmin_constraint = Constraint(m.HG, m.T, rule=_qmin_rule)
    return m


def add_hydro_qmax_constraint(m):
    """
    Add maximum turbined flow constraint.

    Ensures that, for each hydro unit and period,
    m.hydro_Q[h,t] <= m.hydro_Qmax[h].

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with variables/parameters:
        m.hydro_Q[h,t], m.hydro_Qmax[h]; sets m.HG, m.T.

    Returns
    -------
    pyomo.environ.ConcreteModel
        Model with constraint block m.hydro_qmax_constraint.
    """
    def _qmax_rule(m, h, t):
        return m.hydro_Q[h, t] <= m.hydro_Qmax[h]
    m.hydro_qmax_constraint = Constraint(m.HG, m.T, rule=_qmax_rule)
    return m


def add_hydro_volume_continuity_constraint(m):
    """
    Add reservoir mass balance (water continuity) constraints.

    Updates stored volume using natural + upstream inflows (no delay),
    turbined discharge, and spill. Uses the initial storage at the first
    period.

    For each (h, t):
        if t == 1:
            m.hydro_V[h,1] == m.hydro_Vini[h]
                + m.hydro_zeta_vol * (Inflow(h,1) - Q[h,1] - S[h,1])
        else:
            m.hydro_V[h,t] == m.hydro_V[h,t-1]
                + m.hydro_zeta_vol * (Inflow(h,t) - Q[h,t] - S[h,t])

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Model with variables m.hydro_V, m.hydro_Q, m.hydro_S,
        sets m.HG, m.T, and parameters
        m.hydro_zeta_vol, m.hydro_Vini. Inflow is given by
        :func:`hydro_total_inflow_expr`.

    Returns
    -------
    pyomo.core.expr.relational.EqualityExpression
        Constraint block m.hydro_volume_balance_constraint added to the model.

    Notes
    -----
    m.hydro_zeta_vol converts flow (m^3/s) into volume (hm^3) over one period
    (e.g., 3600 / 1e6 for hourly steps).
    """
    def _vol_rule(m, h, t):
        if t == 1:
            return m.hydro_V[h, t] == m.hydro_Vini[h] + m.hydro_zeta_vol * \
                (hydro_total_inflow_expr(m, h, t) -
                 m.hydro_Q[h, t] - m.hydro_S[h, t])
        return m.hydro_V[h, t] == m.hydro_V[h, t-1] + m.hydro_zeta_vol * \
            (hydro_total_inflow_expr(m, h, t) -
             m.hydro_Q[h, t] - m.hydro_S[h, t])

    m.hydro_volume_balance_constraint = Constraint(m.HG, m.T, rule=_vol_rule)
    return m


def add_hydro_volume_meta_constraint(m):
    """
    Add terminal storage target constraints.

    Enforces a minimum end-of-horizon storage for each plant:
        m.hydro_V[h, m.horizon] >= m.hydro_Vmeta[h].

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Model with variable m.hydro_V, parameter m.hydro_Vmeta,
        and an integer m.horizon indicating the last period.

    Returns
    -------
    pyomo.core.expr.relational.InequalityExpression
        Constraint block m.hydro_volume_meta_constraint added to the model.
    """
    def _vol_meta_rule(m, h):
        return m.hydro_V[h, m.horizon] >= m.hydro_Vmeta[h]

    m.hydro_volume_meta_constraint = Constraint(m.HG, rule=_vol_meta_rule)
    return m


def add_hydro_volume_max_constraint(m):
    """
    Add maximum storage constraints.

    For all (h, t):
        m.hydro_V[h,t] <= m.hydro_Vmax[h].

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Model with variable m.hydro_V and parameter m.hydro_Vmax.

    Returns
    -------
    pyomo.core.expr.relational.InequalityExpression
        Constraint block m.hydro_volume_maximal_constraint added to the model.
    """
    def _vol_max_rule(m, h, t):
        return m.hydro_V[h, t] <= m.hydro_Vmax[h]

    m.hydro_volume_maximal_constraint = Constraint(m.HG, m.T, rule=_vol_max_rule)
    return m


def add_hydro_volume_mim_constraint(m):
    """
    Add minimum storage constraints.

    For all (h, t):
        m.hydro_V[h,t] >= m.hydro_Vmin[h].

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Model with variable m.hydro_V and parameter m.hydro_Vmin.

    Returns
    -------
    pyomo.core.expr.relational.InequalityExpression
        Constraint block m.hydro_volume_minimal_constraint added to the model.

    Notes
    -----
    The function name includes mim for historical reasons; the constraint
    enforces a **minimum** volume at each time period.
    """
    def _vol_min_rule(m, h, t):
        return m.hydro_V[h, t] >= m.hydro_Vmin[h]

    m.hydro_volume_minimal_constraint = Constraint(m.HG, m.T, rule=_vol_min_rule)
    return m


def add_hydro_balance_constraint(m):
    """
    Add hydropower-only system balance constraints.

    For each time period t:
        sum_h m.hydro_G[h,t] + m.D[t] == m.d[t].

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Model with variables m.hydro_G[h,t], m.D[t] and parameter m.d[t],
        and sets m.HG, m.T.

    Returns
    -------
    pyomo.core.base.constraint.Constraint
        Constraint block m.hydro_balance_constraint enforcing balance per period.

    Notes
    -----
    This is intended for pure hydropower settings. If thermal generation is present,
    a combined (hydro + thermal) balance should be used instead.
    """
    def _hydro_balance_rule(m, t):
        return sum(m.hydro_G[h, t] for h in m.HG) + m.D[t] == m.d[t]
    m.hydro_balance_constraint = Constraint(m.T, rule=_hydro_balance_rule)
