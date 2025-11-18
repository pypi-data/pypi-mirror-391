"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Data Structures and Problem Skeleton

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines the canonical data structures for short-term thermal
unit commitment (UC) and economic dispatch problems. It is designed to be
paired with Pyomo model builders that assemble:

- Mixed-Integer Quadratic Programs (MIQP) with quadratic variable cost
  a * u + b * p + c * p² and start-up cost SC * y.
- Mixed-Integer Linear Programs (MILP) using piecewise-linear (PWL) cost
  curves via SOS2/convex-combination.
- Optional spinning reserve coupling and global emissions/fuel caps.

Notation (per unit g and time t)
--------------------------------
Decision variables (model side):

    u_{g,t} \in {0,1}   : on/off state
    y_{g,t}, w_{g,t}  : start-up / shut-down flags (binary)
    p_{g,t} >= 0       : electrical output (MW)
    r_{g,t} >= 0       : spinning reserve (MW, optional)
    D_t >= 0           : demand deficit (MW, optional)

Core parameters (this module):

    Pmin_g, Pmax_g    : power bounds (MW)
    RU_g, RD_g        : ramp-up / ramp-down limits (MW/Δt)
    a_g, b_g, c_g     : cost coefficients for a * u + b * p + c * p²
    SC_g              : hot start cost
    t_up_g, t_down_g  : minimum up/down times (periods)
    u0_g, p0_g        : initial state and output
    pw_breaks, pw_costs : PWL points for variable cost C(p)
    γ_g               : emissions factor (tCO₂/MWh), optional

Typical objective (MIQP form)
-----------------------------
Minimize over t,g:

    sum ( a_g u_{g,t} + b_g p_{g,t} + c_g p_{g,t}^2 + SC_g y_{g,t} ) + C_def sum(D_t)

subject to balance, capacity, ramping, min up/down, and (optionally)
reserve and emissions constraints.

Usage
-----
- *ThermalUnit*: describes a single thermal unit, including technical
  limits, cost curve, start-up, ramping, and optional PWL and emissions.
- *ThermalData*: wraps the system horizon, hourly demand, the unit map,
  and optional reserve/emissions settings to feed a Pyomo builder.

Intended pairing
----------------
This module is agnostic to the specific Pyomo modeling choices. It is
compatible with builders that: (i) set MIQP objectives directly from
(a,b,c); or (ii) construct MILP PWL costs from (pw_breaks, pw_costs),
keeping a * u and SC * y in the linear objective.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ThermalUnit:
    """
    Data container for a thermal generating unit with unit commitment attributes.

    Parameters
    ----------
    name : str
        Unique identifier of the thermal unit.
    bar: str
        Connection Bar of the Unit (defaults to BAR_1)
    Pmin : float
        Minimum operating power output (MW).
    Pmax : float
        Maximum operating power output (MW).
    RU : float
        Ramp-up limit (MW per period).
    RD : float
        Ramp-down limit (MW per period).
    a : float, optional
        Fixed cost coefficient ($/h), default is 0.0.
    b : float, optional
        Linear generation cost coefficient ($/MWh), default is 0.0.
    c : float, optional
        Quadratic generation cost coefficient ($/MWh²), default is 0.0.
    SC : float, optional
        Hot start-up cost ($), default is 0.0.
    t_up : int, optional
        Minimum up-time (hours/periods), default is 1.
    t_down : int, optional
        Minimum down-time (hours/periods), default is 1.
    init_status_h: int, optional
        Value to compute initial t_min_up/t_min_down
    u0 : int, optional
        Initial commitment status at t=0 (1=ON, 0=OFF), default is 0.
    p0 : float, optional
        Initial generation level at t=0 (MW), default is 0.0.
    pw_breaks : List[float], optional
        Breakpoints for piecewise-linear cost approximation.
    pw_costs : List[float], optional
        Cost values corresponding to the piecewise breakpoints.
    gamma : float, optional
        Emission factor or auxiliary cost coefficient (unit-dependent),
        default is 0.0.

    Notes
    -----
    - The quadratic cost curve is typically defined as:
      ``C(p) = a * u + b * p + c * p² + SC * y``,
      where ``u`` is the commitment status and ``y`` the startup indicator.
    - Piecewise approximations use ``pw_breaks`` and ``pw_costs`` for MILP models.
    """
    name: str
    bar: str
    Pmin: float
    Pmax: float
    RU: float
    RD: float
    a: float = 0.0
    b: float = 0.0
    c: float = 0.0
    SC: float = 0.0
    t_up: int = 1
    t_down: int = 1
    init_status_h: int = -1
    u0: int = 0
    p0: float = 0.0
    pw_breaks: Optional[List[float]] = None
    pw_costs: Optional[List[float]] = None
    gamma: float = 0.0


@dataclass
class ThermalData:
    """
    System-wide data container for thermal unit commitment problems.

    Parameters
    ----------
    horizon : int
        Number of time periods in the planning horizon.
    units : Dict[str, ThermalUnit]
        Dictionary mapping unit identifiers to their ``ThermalUnit`` objects.
    Rreq : Dict[int, float], optional
        Mapping of each period ``t`` to spinning reserve requirement (MW).
        Defaults to ``None``.
    has_history: bool, optional
        Consider previous states or not. Default is false
    Notes
    -----
    - This class serves as a structured input for Pyomo-based UC models.
    - ``Rreq`` is optional; if not provided, reserve constraints must be disabled.
    """
    horizon: int
    units: Dict[str, ThermalUnit]
    Rreq: Optional[Dict[int, float]] = None
    has_history: bool = False 
