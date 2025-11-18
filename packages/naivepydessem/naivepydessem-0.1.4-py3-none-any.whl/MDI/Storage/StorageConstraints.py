"""
Storage Constraints Module
==========================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines all **physical and operational constraints** for the
energy storage subsystem of the MDI optimization model.  
It ensures consistency between energy balance, power limits, state-of-charge
(SoC) boundaries, and investment linkage dynamics.

Description
-----------
Four main constraint groups are provided:

1. **Energy Balance Constraint**  
   Ensures conservation of stored energy over time, accounting for
   charging/discharging power and round-trip efficiency.

2. **SoC Bounds Constraint**  
   Enforces upper and lower limits on the energy stored as a function
   of installed capacity and operational state.

3. **Power Limits Constraint**  
   Restricts the charging and discharging power to their respective
   maximum values.

4. **Investment Link Constraint**  
   Links investment decisions with the operational availability of
   storage units across time.

Mathematical Formulation
------------------------
**Energy balance**
\[
E_{s,t} = E_{s,t-1} +
\eta_c P^{ch}_{s,t} \Delta t -
\frac{P^{dis}_{s,t}}{\eta_d} \Delta t
\]

**SoC bounds**
\[
E^{min}_s x_{s,t} \leq E_{s,t} \leq E^{max}_s x_{s,t}
\]

**Power limits**
\[
0 \leq P^{ch}_{s,t} \leq P^{ch,max}_s x_{s,t}
\quad\text{and}\quad
0 \leq P^{dis}_{s,t} \leq P^{dis,max}_s x_{s,t}
\]

**Investment linkage**
\[
x_{s,t} = x_{s,t-1} + y_{s,t}
\]

where:
- \(E_{s,t}\) — state of charge (MWh)  
- \(P^{ch}_{s,t}\), \(P^{dis}_{s,t}\) — charging/discharging power (MW)  
- \(\eta_c, \eta_d\) — charging/discharging efficiencies  
- \(x_{s,t}\) — operational existence of storage unit \(s\)  
- \(y_{s,t}\) — binary investment decision  
- \(\Delta t\) — duration of time step (hours)

Functions
---------
add_storage_energy_balance_constraint(m)
    Adds the intertemporal energy conservation constraint.

add_storage_soc_bounds_constraint(m)
    Adds the upper and lower bounds on the state of charge.

add_storage_power_limits_constraint(m)
    Adds the power limit constraints for charging and discharging.

add_storage_investment_link_constraint(m)
    Adds the investment linkage constraint ensuring logical consistency
    between existence and new builds.

Notes
-----
- The formulation assumes uniform time steps (\(\Delta t\)) across the horizon.  
- Charging and discharging are modeled as separate nonnegative variables.  
- Constraints are fully compatible with multi-level (patamar) formulations.

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,
    EELT7030/UFPR, 2023.

Module Dependencies
-------------------
- **External:** ``pyomo.environ.Constraint``
"""

from pyomo.environ import Constraint


def add_storage_energy_balance_constraint(m):
    """
    Add the state-of-charge (SoC) energy balance constraint.

    Defines the recursive relationship for the stored energy as a function
    of previous state, charging/discharging flows, efficiencies, and
    time-step duration.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing storage-related sets, variables,
        and parameters.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The model with the energy balance constraint added.
    """
    """ def _soc_rule(m, s, t, p):
        if t == 1:
            return m.storage_E[s, t, p] == m.storage_Eini[s] \
                   + m.storage_eta_c[s] * m.storage_ch[s, t, p] * m.storage_delta_t \
                   - (m.storage_dis[s, t, p] / m.storage_eta_d[s]) * m.storage_delta_t
        return m.storage_E[s, t, p] == m.storage_E[s, m.T.prev(t), p] \
               + m.storage_eta_c[s] * m.storage_ch[s, t, p] * m.storage_delta_t \
               - (m.storage_dis[s, t, p] / m.storage_eta_d[s]) * m.storage_delta_t """
    
    def _soc_rule(m, s, t, p):
        precedence = list(m.level_precedence)
        idx = precedence.index(p)

        if idx == 0:
            if t == 1:
                return m.storage_E[s, t, p] == m.storage_Eini[s] * m.storage_x[s, t]
            else:
                return m.storage_E[s, t, p] == (
                    m.storage_E[s, m.T.prev(t), precedence[-1]]
                    + m.storage_Eini[s] * m.storage_y[s, t]
                    + m.storage_eta_c[s] * m.storage_ch[s, t, p] * m.level_hours[p]
                    - (m.storage_dis[s, t, p] / m.storage_eta_d[s]) * m.level_hours[p]
                )

        p_prev = precedence[idx - 1]
        return m.storage_E[s, t, p] == (
            m.storage_E[s, t, p_prev]
            + m.storage_eta_c[s] * m.storage_ch[s, t, p] * m.level_hours[p]
            - (m.storage_dis[s, t, p] / m.storage_eta_d[s]) * m.level_hours[p]
        )


    m.storage_energy_balance_constraint = Constraint(m.SU, m.T, m.P, rule=_soc_rule)
    return m


def add_storage_soc_bounds_constraint(m):
    """
    Add upper and lower bounds on the state of charge (SoC).

    Enforces that the stored energy remains within defined physical
    limits as a function of the installed capacity and operational state.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing storage sets, variables, and parameters.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The model with SoC boundary constraints applied.
    """
    def _soc_max_rule(m, s, t, p):
        return m.storage_E[s, t, p] <= m.storage_Emax[s] * m.storage_x[s, t]

    def _soc_min_rule(m, s, t, p):
        return m.storage_E[s, t, p] >= m.storage_Emin[s] * m.storage_x[s, t]

    m.storage_soc_upper_constraint = Constraint(m.SU, m.T, m.P, rule=_soc_max_rule)
    m.storage_soc_lower_constraint = Constraint(m.SU, m.T, m.P, rule=_soc_min_rule)
    return m


def add_storage_power_limits_constraint(m):
    """
    Add charging and discharging power limit constraints.

    Ensures that the charging and discharging power of each storage
    unit does not exceed its respective rated capacity.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance with storage-related variables and parameters.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The model with charging and discharging power limits enforced.
    """
    def _ch_limit_rule(m, s, t, p):
        # power must be represented as MWh/h, not MWh/level
        return m.storage_ch[s, t, p] <= (m.storage_Pch_max[s, p] / m.level_hours[p]) * m.storage_x[s, t]
        # 

    def _dis_limit_rule(m, s, t, p):
        # power must be represented as MWh/h, not MWh/level
        return m.storage_dis[s, t, p] <= (m.storage_Pdis_max[s, p] / m.level_hours[p]) * m.storage_x[s, t]
    
    m.storage_charge_limit_constraint = Constraint(m.SU, m.T, m.P, rule=_ch_limit_rule)
    m.storage_discharge_limit_constraint = Constraint(m.SU, m.T, m.P, rule=_dis_limit_rule)
    return m

def add_storage_mutual_exclusion_constraint(m):
    """
    Prohibit simultaneous charge and discharge, considering construction state.

    Enforces:
        storage_ch[s,t,p]  <=  M[s] * storage_x[s,t]
        storage_dis[s,t,p] <=  M[s] * storage_x[s,t]
        storage_ch[s,t,p]  <=  M[s] * storage_mode[s,t,p]
        storage_dis[s,t,p] <=  M[s] * (1 - storage_mode[s,t,p])
    """
    def _no_simul_ch_rule(m, s, t, p):
        return m.storage_ch[s, t, p] <= m.storage_M[s] * m.storage_mode[s, t, p]

    def _no_simul_dis_rule(m, s, t, p):
        return m.storage_dis[s, t, p] <= m.storage_M[s] * (1 - m.storage_mode[s, t, p])

    def _no_ch_if_not_built(m, s, t, p):
        return m.storage_ch[s, t, p] <= m.storage_M[s] * m.storage_x[s, t]

    def _no_dis_if_not_built(m, s, t, p):
        return m.storage_dis[s, t, p] <= m.storage_M[s] * m.storage_x[s, t]

    m.storage_no_simul_charge_constraint = Constraint(m.SU, m.T, m.P, rule=_no_simul_ch_rule)
    m.storage_no_simul_discharge_constraint = Constraint(m.SU, m.T, m.P, rule=_no_simul_dis_rule)
    m.storage_no_ch_if_not_built_constraint = Constraint(m.SU, m.T, m.P, rule=_no_ch_if_not_built)
    m.storage_no_dis_if_not_built_constraint = Constraint(m.SU, m.T, m.P, rule=_no_dis_if_not_built)

    return m


def add_storage_investment_link_constraint(m):
    """
    Add the investment linkage constraint for storage units.

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
    
    def _inv_initial_value_rule(m, g, t):
        if t == 1:
            return m.storage_x[g, t] == m.storage_state[g]
        return Constraint.Skip

    def _inv_link_rule(m, s, t):
        if t == 1:
            return m.storage_x[s, t] == m.storage_y[s, t]
        return m.storage_x[s, t] == m.storage_x[s, m.T.prev(t)] + m.storage_y[s, t]

    m.storage_initial_state_constraint = Constraint(m.SU, m.T, rule=_inv_initial_value_rule)
    m.storage_investment_link_constraint = Constraint(m.SU, m.T, rule=_inv_link_rule)
    return m


