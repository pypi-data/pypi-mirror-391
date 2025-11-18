"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Energy Storage — Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines the operational constraints for battery energy storage
systems (BESS) within Pyomo-based dispatch and unit commitment models.
The formulation is consistent with the hydraulic and renewable modules,
ensuring interoperability in hybrid optimization frameworks.

Functions
---------
add_storage_energy_balance_constraint(m)
    Enforce intertemporal state-of-charge balance with charge/discharge
    efficiencies and time-step duration.
add_storage_soc_bounds_constraint(m)
    Impose minimum and maximum state-of-charge limits.
add_storage_power_limits_constraint(m)
    Impose per-period charging and discharging power limits.
add_storage_mutual_exclusion_constraint(m)
    (Optional) Prohibit simultaneous charging and discharging through a
    big-M formulation with binary mode variables.
add_storage_only_balance_constraint(m)
    Enforce system-wide balance for storage-only models, equating net
    injection plus deficit to the demand at each period.

Notes
-----
- The efficiencies (``eta_c``, ``eta_d``) can be specified per stage or
  derived from a round-trip value split by the user.
- For hybrid models (hydro, thermal, renewable, storage), the global
  balance should be implemented at a higher builder level.
- The formulation assumes a fixed period duration ``delta_t`` in hours,
  used to convert power (MW) to energy (MWh).

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""


from pyomo.environ import Constraint


def add_storage_energy_balance_constraint(m):
    """
    Add storage energy (SoC) balance constraints.

    Enforces conservation of energy per unit and period:

        E[s,1] = Eini[s] + eta_c[s] * ch[s,1] * Δt - (dis[s,1] / eta_d[s]) * Δt
        E[s,t] = E[s,t-1] + eta_c[s] * ch[s,t] * Δt - (dis[s,t] / eta_d[s]) * Δt,  t>1

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with sets ``m.SU``, ``m.T``; variables ``m.storage_E``,
        ``m.storage_ch``, ``m.storage_dis``; per-unit parameters
        ``m.storage_Eini``, ``m.storage_eta_c``, ``m.storage_eta_d``; and
        scalar ``m.storage_delta_t``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with constraint block
        ``m.storage_energy_balance_constraint``.
    """
    def _soc_rule(m, s, t):
        if t == 1:
            return m.storage_E[s, t] == m.storage_Eini[s] \
                   + m.storage_eta_c[s] * m.storage_ch[s, t] * m.storage_delta_t \
                   - (m.storage_dis[s, t] / m.storage_eta_d[s]) * m.storage_delta_t
        return m.storage_E[s, t] == m.storage_E[s, m.T.prev(t)] \
               + m.storage_eta_c[s] * m.storage_ch[s, t] * m.storage_delta_t \
               - (m.storage_dis[s, t] / m.storage_eta_d[s]) * m.storage_delta_t

    m.storage_energy_balance_constraint = Constraint(m.SU, m.T, rule=_soc_rule)
    return m


def add_storage_soc_bounds_constraint(m):
    """
    Add minimum/maximum SoC constraints.

        storage_Emin[s] <= storage_E[s,t] <= storage_Emax[s]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with sets ``m.SU``, ``m.T``; variable ``m.storage_E``; and
        parameters ``m.storage_Emin``, ``m.storage_Emax``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with upper and lower SoC bounds.
    """
    def _soc_max_rule(m, s, t):
        return m.storage_E[s, t] <= m.storage_Emax[s]

    def _soc_min_rule(m, s, t):
        return m.storage_E[s, t] >= m.storage_Emin[s]

    m.storage_soc_upper_constraint = Constraint(m.SU, m.T, rule=_soc_max_rule)
    m.storage_soc_lower_constraint = Constraint(m.SU, m.T, rule=_soc_min_rule)
    return m


def add_storage_power_limits_constraint(m):
    """
    Add charging and discharging power limits.

        0 <= storage_ch[s,t]  <= storage_Pch_max[s]
        0 <= storage_dis[s,t] <= storage_Pdis_max[s]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with sets ``m.SU``, ``m.T``; variables ``m.storage_ch``,
        ``m.storage_dis``; and parameters ``m.storage_Pch_max``,
        ``m.storage_Pdis_max``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with power limit constraints.
    """
    def _ch_limit_rule(m, s, t):
        return m.storage_ch[s, t] <= m.storage_Pch_max[s]

    def _dis_limit_rule(m, s, t):
        return m.storage_dis[s, t] <= m.storage_Pdis_max[s]

    m.storage_charge_limit_constraint = Constraint(m.SU, m.T, rule=_ch_limit_rule)
    m.storage_discharge_limit_constraint = Constraint(m.SU, m.T, rule=_dis_limit_rule)
    return m


def add_storage_mutual_exclusion_constraint(m):
    """
    (Optional) Prohibit simultaneous charge and discharge.

    Uses a big-M logic with a binary mode variable:

        storage_ch[s,t]  <=  M[s] * storage_mode[s,t]
        storage_dis[s,t] <=  M[s] * (1 - storage_mode[s,t])

    Assumes ``m.storage_mode[s,t]`` (binary) and ``m.storage_M[s]`` (big-M)
    exist in the model.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with sets ``m.SU``, ``m.T``; variables ``m.storage_ch``,
        ``m.storage_dis``, binary ``m.storage_mode``; and parameter
        ``m.storage_M``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with mutual exclusion constraints.
    """
    def _no_simul_ch_rule(m, s, t):
        return m.storage_ch[s, t] <= m.storage_M[s] * m.storage_mode[s, t]

    def _no_simul_dis_rule(m, s, t):
        return m.storage_dis[s, t] <= m.storage_M[s] * (1 - m.storage_mode[s, t])

    m.storage_no_simul_charge_constraint = Constraint(m.SU, m.T, rule=_no_simul_ch_rule)
    m.storage_no_simul_discharge_constraint = Constraint(m.SU, m.T, rule=_no_simul_dis_rule)
    return m


def add_storage_only_balance_constraint(m):
    """
    Add system-wide balance for storage-only models.

    Net injection from storage plus deficit must meet demand:

        Σ_s ( storage_dis[s,t] - storage_ch[s,t] )  +  D[t]  =  d[t]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with set ``m.T``; variables ``m.storage_ch``, ``m.storage_dis``,
        ``m.D``; and parameter ``m.d``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with ``m.storage_only_balance_constraint``.
    """
    def _bal_rule(m, t):
        return sum(m.storage_dis[s, t] - m.storage_ch[s, t] for s in m.SU) + m.D[t] == m.d[t]

    m.storage_only_balance_constraint = Constraint(m.T, rule=_bal_rule)
    return m
