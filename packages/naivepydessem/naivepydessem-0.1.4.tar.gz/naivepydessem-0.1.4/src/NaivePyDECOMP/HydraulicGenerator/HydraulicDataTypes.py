"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Hydraulic System Data Classes for Reservoir Optimization

Description
-----------
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
- Discharges (Q, S) are in hm^3.
- Storage volumes (V) are in hm^3.

Notes
-----
- Cascade routing: this data layer assumes **no travel time**. If routing
  delays are relevant, they should be handled in the modeling layer.

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
        Connection Bar of the Unit (defaults to BAR_1)
    Qmin : float
        Minimum allowed turbined flow (hm^3).
    Qmax : float
        Maximum allowed turbined flow (hm^3).
    Vmin : float
        Minimum storage volume (hm^3).
    Vmax : float
        Maximum storage volume (hm^3).
    Vini : float
        Initial storage volume at the beginning of the horizon (hm^3).
    afluencia : List[float]
        Natural inflow time series (hm^3); external, 0-based list aligned
        with model periods (accessed as ``afluencia[t-1]``).
    upstreams : List[str], optional
        List of immediate upstream plant names that feed this unit.
        Defaults to ``None`` (treated as no upstreams).
    p : List[float]
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
    """
    name: str
    bar: str
    Qmin: float
    Qmax: float
    Vmin: float
    Vmax: float
    Vini: float
    afluencia: List[float]
    upstreams: List[str] = None
    p: List[float] = None
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
