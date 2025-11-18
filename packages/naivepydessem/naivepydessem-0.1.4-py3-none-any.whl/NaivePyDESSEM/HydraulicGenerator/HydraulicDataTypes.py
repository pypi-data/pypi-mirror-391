"""
Hydraulic System Data Classes for Reservoir Optimization
========================================================

This module defines data classes for modeling structural and operational
characteristics of hydroelectric systems in short-term dispatch and
unit-commitment studies. The classes are designed to serve as a clean
interface between problem data and Pyomo-based optimization models.

Overview
--------
Two classes are provided:

- ``HydraulicUnit``: describes a single hydro plant, including storage bounds,
  turbined-flow limits, initial/terminal volumes, natural inflows, cascade
  topology, and optional coefficients for alternative FPH (hydropower
  production function) modes.

- ``HydraulicData``: encapsulates system-wide information such as planning
  horizon, hourly demand, plant map, and conversion/penalty constants.

Conventions and Units
---------------------
- Time is discretized in periods ``t = 1, …, horizon`` (integers).
- Discharges (Q, S) are in m^3/s.
- Storage volumes (V) are in hm^3.
- Demand is in MW.
- ``zeta`` typically equals 9.81/1000 to convert head * flow to MW.
- ``zeta_vol`` converts flow (m^3/s) into volume (hm^3) over one period
  (e.g., 3600/1e6 for hourly steps).

Notes
-----
- Cascade routing: this data layer assumes **no travel time**. If routing
  delays are relevant, they should be handled in the modeling layer.
- The field ``mode`` is a selector for FPH modeling choices (e.g., constant,
  specific, exact, simplified). The interpretation belongs to the modeling
  code that consumes these data.
- Optional vectors (``a``, ``b``, ``rho``, ``losses``) can parameterize
  alternative FPH formulations; their semantics depend on the chosen mode.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class HydraulicUnit:
    """
    Hydropower plant data container.

    Parameters
    ----------
    name : str
        Unique identifier of the hydro plant.
    bar: str
        Connection Bar/bus of the unit (defaults to BAR_1)
    Qmin : float
        Minimum allowed turbined flow (m^3/s).
    Qmax : float
        Maximum allowed turbined flow (m^3/s).
    Vmin : float
        Minimum storage volume (hm^3).
    Vmax : float
        Maximum storage volume (hm^3).
    Vmeta : float
        Terminal target storage at the end of the horizon (hm^3).
    Vini : float
        Initial storage volume at the beginning of the horizon (hm^3).
    afluencia : List[float]
        Natural inflow time series (m^3/s); external, 0-based list aligned
        with model periods (accessed as ``afluencia[t-1]``).
    upstreams : List[str], optional
        List of immediate upstream plant names that feed this unit.
        Defaults to ``None`` (treated as no upstreams).
    a : List[float], optional
        Optional coefficient vector associated with an FPH/head submodel
        (semantics defined by the chosen ``mode``).
    b : List[float], optional
        Optional coefficient vector associated with an FPH/head submodel
        (semantics defined by the chosen ``mode``).
    rho : List[float], optional
        Optional weights/coefficients for specific productivity surfaces
        (e.g., colina-type fits), depending on the ``mode``.
    losses : List[float], optional
        Optional coefficients for hydraulic-loss approximations.
    pe : float, optional
        Specific productivity coefficient (dimensionless multiplier used in
        simplified models).
    p : float, optional
        Global productivity coefficient (used in constant/simplified models;
        unit interpretation depends on how head is handled in the FPH).
    mode : str, optional
        Generation-mode selector. Valid options include
        {"constant", "specific", "exact", "simplified"}.
        Default is "constant".
    compute_total_inflow : bool, optional
        If ``True``, total inflow will include upstream releases in addition
        to exogenous natural inflow in expressions that support it.
        Default is ``True``.

    Notes
    -----
    - The presence and interpretation of the optional vectors (``a``, ``b``,
      ``rho``, ``losses``) are **model-dependent** and only take effect if
      the consuming code uses them for the selected ``mode``.
    """
    name: str
    bar: str
    Qmin: float
    Qmax: float
    Vmin: float
    Vmax: float
    Vmeta: float
    Vini: float
    afluencia: List[float]
    upstreams: List[str] = None
    a: Optional[List[float]] = None
    b: Optional[List[float]] = None
    rho: Optional[List[float]] = None
    losses: Optional[List[float]] = None
    pe: Optional[float] = None
    p: Optional[float] = None
    mode: str = "constant"
    compute_total_inflow: bool = True


@dataclass
class HydraulicData:
    """
    System-wide hydropower data for planning and dispatch.

    Parameters
    ----------
    horizon : int
        Number of time periods in the planning horizon.
    units : Dict[str, HydraulicUnit]
        Map from plant name to its ``HydraulicUnit`` data structure.
    zeta : float, optional
        Conversion constant for head–flow to power (typ. 9.81/1000). Default
        is ``9.81/1000``; ensure consistency with the FPH used.
    zeta_vol : float, optional
        Flow-to-volume conversion over one period (hm^3 per (m^3/s)).
        Default is ``3600/1e6`` for hourly steps.
    Cdef : float, optional
        Penalty cost for unmet demand (R$/MWh), to be used by objectives in
        optimization models. Default is ``1000.0``.

    Notes
    -----
    - The dictionary ``demand`` is assumed to be 1-based (``t = 1..horizon``).
      If your data are 0-based, map them accordingly before constructing this
      object.
    - The interpretation of ``zeta`` depends on where power conversion is
      performed (inside the FPH callable or in the model).
    """
    horizon: int
    units: Dict[str, HydraulicUnit]
    zeta: float = 9.81 / 1000
    zeta_vol: float = 3600 / 1e6
