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
    m.hydro_Q[h,t] : turbined discharge (hm^3)
    m.hydro_S[h,t] : spill discharge (m^3/s)
    m.hydro_G[h,t] : hydropower generation (MW)
    m.D[t]         : deficit (MW), if used
Parameters
    m.hydro_Vini[h]  : initial storage (hm^3)
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

from NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints import (
    add_hydro_balance_constraint,
    add_hydro_generation_constraint,
    add_hydro_qmin_constraint,
    add_hydro_qmax_constraint,
    add_hydro_volume_max_constraint,
    add_hydro_volume_mim_constraint,
    hydro_total_inflow_expr
)


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
            return m.hydro_V[h, t] == m.hydro_Vini[h] + \
                (hydro_total_inflow_expr(m, h, t) -
                 m.hydro_Q[h, t] - m.hydro_S[h, t])
        return m.hydro_V[h, t] == m.hydro_V[h, t-1] + \
            (hydro_total_inflow_expr(m, h, t) -
             m.hydro_Q[h, t] - m.hydro_S[h, t])
    
    def _min_s_rule(m, h, t):
        return m.hydro_S[h, t] >= 0.0

    m.hydro_volume_balance_constraint = Constraint(m.HG, m.T, rule=_vol_rule)
    # m.hydro_spillage_constraint = Constraint(m.HG, m.T, rule=_min_s_rule)
    return m