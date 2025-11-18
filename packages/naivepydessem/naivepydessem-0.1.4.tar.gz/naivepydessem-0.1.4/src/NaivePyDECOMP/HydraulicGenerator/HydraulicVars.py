"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Hydropower Model Initialization: Sets, Parameters, and Variables

Description
-----------
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
- Turbined/Spill discharges (Q, S): hm^3.
- Storage volume (V): hm^3.
- Demand and power (d, G): MWh.

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

from NaivePyDESSEM.HydraulicGenerator.HydraulicVars import (
    hydralic_add_variables_g
)


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
      (e.g., ``m.d``) are Pyomo ``Param`` objects.
    - The attribute ``m.horizon`` stores the number of periods for quick access.
    """
    T = data.horizon
    H = list(data.units.keys())

    m.HG = Set(initialize=H)

    if not hasattr(m, "T"):
        m.T = RangeSet(1, T)

    m.horizon = T

    m.hydro_Qmin = {h: data.units[h].Qmin for h in H}
    m.hydro_Qmax = {h: data.units[h].Qmax for h in H}
    m.hydro_Vmin = {h: data.units[h].Vmin for h in H}
    m.hydro_Vmax = {h: data.units[h].Vmax for h in H}
    m.hydro_Vini = {h: data.units[h].Vini for h in H}
    m.hydro_afluencia = {h: data.units[h].afluencia for h in H}
    m.hydro_upstreams = {h: data.units[h].upstreams for h in H}
    m.hydro_compute_total_inflow = {h: data.units[h].compute_total_inflow for h in H}
    m.hydro_bars = {h: data.units[h].bar for h in H}
    return m
