"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Provides initialization routines for adding storage-related sets, parameters,
and decision variables to Pyomo-based dispatch and unit commitment models.
This module ensures a consistent interface for modeling battery energy storage
systems (BESS) across different formulations.

Functions
---------
storage_add_sets_and_params(m, data)
    Initialize sets and Pyomo parameters for storage units, including
    state-of-charge bounds, initial conditions, power limits, efficiencies,
    and time-step duration.
storage_add_variables(m)
    Declare continuous decision variables for state-of-charge, charging
    power, and discharging power. If absent, also define a deficit variable
    for feasibility.

Notes
-----
- Parameters are namespaced with the prefix ``storage_`` for clarity and
  compatibility with other subsystems (hydro, thermal, renewable).
- The time-step duration (``delta_t``) converts power (MW) to energy (MWh)
  within the state-of-charge balance equation.
- The variables are declared as non-negative and continuous. Binary
  variables may be added in other modules if mutual exclusion between
  charge and discharge is required.
  
References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import (RangeSet, Set, Param, Var, NonNegativeReals, Binary)
from pyomo.environ import ConcreteModel
from .StorageDataTypes import StorageData


def storage_add_sets_and_params(m: ConcreteModel,
                                data: StorageData) -> ConcreteModel:
    """
    Initialize storage sets and parameters.

    Adds the storage unit set, state-of-charge bounds and initial values,
    power limits, (dis)charging efficiencies, and the time-step duration.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Target model to be updated.
    data : StorageData
        Input container with horizon, units, and ``delta_t``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with storage sets/parameters attached.

    Notes
    -----
    - If ``m.T`` already exists it is preserved; otherwise it is created
      as ``RangeSet(1, data.horizon)``.
    - Parameters are prefixed with ``storage_`` for namespacing.
    """
    T = data.horizon
    U = list(data.units.keys())

    if not hasattr(m, "T"):
        m.T = RangeSet(1, T)

    if not hasattr(m, "d"):
        m.d = Param(m.T, initialize=data.demand, within=NonNegativeReals)

    if not hasattr(m, "Cdef"):
        m.Cdef = data.Cdef

    m.SU = Set(initialize=U)

    # Scalar (hours)
    if not hasattr(m, "storage_delta_t"):
        m.storage_delta_t = Param(initialize=data.delta_t)

    # Per-unit parameters
    m.storage_Emin = {u: data.units[u].Emin for u in U}
    m.storage_Emax = {u: data.units[u].Emax for u in U}
    m.storage_Eini = {u: data.units[u].Eini for u in U}
    m.storage_Pch_max = {u: data.units[u].Pch_max for u in U}
    m.storage_Pdis_max = {u: data.units[u].Pdis_max for u in U}
    m.storage_eta_c = {u: data.units[u].eta_c for u in U}
    m.storage_eta_d = {u: data.units[u].eta_d for u in U}
    m.storage_M = {u: data.units[u].Emax for u in U}
    m.storage_bars = {u: data.units[u].bar for u in U}
    

    return m


def storage_add_variables(m: ConcreteModel) -> ConcreteModel:
    """
    Declare storage decision variables.

    Adds state-of-charge and charge/discharge power variables. If a deficit
    variable does not exist in the model, a non-negative ``D[t]`` is created.

    Variables
    ---------
    storage_E[s,t] : NonNegativeReals
        Energy stored at the end of period ``t`` (MWh).
    storage_ch[s,t] : NonNegativeReals
        Charging power (MW) in period ``t``.
    storage_dis[s,t] : NonNegativeReals
        Discharging power (MW) in period ``t``.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Target model (expects sets ``m.SU`` and ``m.T``).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with storage variables attached.
    """

    m.storage_E = Var(m.SU, m.T, within=NonNegativeReals)
    m.storage_ch = Var(m.SU, m.T, within=NonNegativeReals)
    m.storage_dis = Var(m.SU, m.T, within=NonNegativeReals)
    m.storage_mode = Var(m.SU, m.T, domain=Binary)
    return m
