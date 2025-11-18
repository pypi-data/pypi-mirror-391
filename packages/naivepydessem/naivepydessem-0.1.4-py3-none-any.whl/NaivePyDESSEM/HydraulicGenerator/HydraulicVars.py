"""
Hydropower Model Initialization: Sets, Parameters, and Variables
================================================================

This module provides initialization routines for setting up the basic
sets, parameters, and continuous variables required by hydropower
optimization models in Pyomo. It accommodates multiple hydropower
generation modes, natural-inflow handling, and head-dependent power
relationships supplied elsewhere in the modeling stack.

Functions
---------
hydraulyc_add_sets_and_params(m, data)
    Initialize sets and model-level parameters/containers for hydropower units
    and system-wide demand.

hydralic_add_variables_g(m)
    Declare continuous decision variables for hydropower dispatch modeling.

Modeling Conventions and Units
------------------------------
- Time periods are indexed as integers ``t = 1, …, horizon``.
- Turbined/Spill discharges (Q, S): m^3/s.
- Storage volume (V): hm^3.
- Demand and power (d, G): MW.
- Typical period conversion for volume: ``zeta_vol = 3600/1e6`` (hourly steps).
- Typical head–flow–power conversion: ``zeta = 9.81/1000`` (when used inside FPH).

Notes
-----
- The argument ``data`` is expected to be an instance of ``HydraulicData``,
  where each unit is a ``HydraulicUnit``.
- Some attributes attached to the model are plain Python containers
  (e.g., dictionaries) rather than Pyomo ``Param`` objects, by design.
- This module targets short-term planning models and is suitable for
  integration into MILP/MIQP hydropower (or hydrothermal) formulations.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023 
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""

from pyomo.environ import (RangeSet, Set, Param, Var,
                           NonNegativeReals)


def hydraulyc_add_sets_and_params(m, data):
    """
    Initialize hydropower sets and model-level parameters/containers.

    Configures the Pyomo model ``m`` with time and hydropower unit sets,
    system-level demand, and per-unit attributes such as flow limits,
    storage bounds, initial/terminal storages, natural inflows, cascade
    topology, and flags used by inflow aggregation. Values are sourced
    from the ``HydraulicData``/``HydraulicUnit`` objects.

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Target Pyomo model to be populated with sets and parameters.
    data : HydraulicData
        Input data object with planning horizon, demand mapping, and the
        dictionary of hydropower units.

    Returns
    -------
    pyomo.core.base.PyomoModel.ConcreteModel
        The same model ``m`` with initialized sets and parameters/containers.

    Notes
    -----
    - All plant-specific containers are indexed by the hydropower unit set
      ``m.HG``.
    - Time-varying arrays (e.g., ``afluencia``) are assumed to be external,
      0-based Python lists that are accessed as ``[t-1]`` inside constraints.
    - Some attributes (e.g., ``m.hydro_Qmin``, ``m.hydro_Vmax``) are plain
      Python dictionaries attached to the model for convenience; others
      (e.g., ``m.d``, ``m.hydro_zeta``) are Pyomo ``Param`` objects.
    - The attribute ``m.horizon`` stores the number of periods for quick access.
    """
    T = data.horizon
    H = list(data.units.keys())

    m.HG = Set(initialize=H)

    if not hasattr(m, "T"):
        m.T = RangeSet(1, T)

    if not hasattr(m, "d"):
        m.d = Param(m.T, initialize=data.demand, within=NonNegativeReals)
    
    if not hasattr(m, "Cdef"):
        m.Cdef = data.Cdef

    m.hydro_zeta = Param(initialize=data.zeta)
    m.hydro_zeta_vol = data.zeta_vol
    m.horizon = T

    m.hydro_Qmin = {h: data.units[h].Qmin for h in H}
    m.hydro_Qmax = {h: data.units[h].Qmax for h in H}
    m.hydro_Vmin = {h: data.units[h].Vmin for h in H}
    m.hydro_Vmax = {h: data.units[h].Vmax for h in H}
    m.hydro_Vmeta = {h: data.units[h].Vmeta for h in H}
    m.hydro_Vini = {h: data.units[h].Vini for h in H}
    m.hydro_afluencia = {h: data.units[h].afluencia for h in H}
    m.hydro_upstreams = {h: data.units[h].upstreams for h in H}
    m.hydro_compute_total_inflow = {h: data.units[h].compute_total_inflow for h in H}
    m.hydro_bars = {h: data.units[h].bar for h in H}
    return m


def hydralic_add_variables_g(m):
    """
    Declare continuous decision variables for hydropower dispatch.

    The following Pyomo variables are added to model ``m``:
    - ``hydro_Q[h,t]`` : turbined discharge (m^3/s)
    - ``hydro_V[h,t]`` : storage volume (hm^3)
    - ``hydro_S[h,t]`` : spill discharge (m^3/s)
    - ``hydro_G[h,t]`` : hydropower generation (MW)
    - ``D[t]``         : system deficit (MW)

    All variables are nonnegative and defined over the hydropower units and
    the planning horizon.

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Pyomo model to which the decision variables will be attached.

    Returns
    -------
    pyomo.core.base.PyomoModel.ConcreteModel
        The same model ``m`` with variables declared.

    Notes
    -----
    - Assumes that sets ``m.HG`` and ``m.T`` have been initialized previously.
    - Both ``D`` and ``hydro_D`` are provided to ease integration with
      different objective/balance formulations; keep only the one you use.
    """
    # Variáveis contínuas 
    
    m.hydro_Q = Var(m.HG, m.T, within=NonNegativeReals)
    m.hydro_V = Var(m.HG, m.T, within=NonNegativeReals)
    m.hydro_S = Var(m.HG, m.T, within=NonNegativeReals)
    m.hydro_G = Var(m.HG, m.T, within=NonNegativeReals)
    return m
