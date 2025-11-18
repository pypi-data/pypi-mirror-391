"""
Storage Data Types Module
=========================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines the fundamental **data structures** that describe
the technical, economic, and operational attributes of **energy storage units**.
It serves as the foundation for building symbolic Pyomo models used in
optimization formulations for system operation and expansion.

Description
-----------
Two main dataclasses are defined:

1. **`StorageUnit`**  
   Represents a single energy storage unit, including its operational
   parameters, efficiency characteristics, and economic coefficients.

2. **`StorageData`**  
   Aggregates all input data required to formulate a storage optimization
   problem, including horizon definition, demand, level duration,
   and a collection of `StorageUnit` instances.

Both classes provide a lightweight, strongly typed data interface for
Python–Pyomo integration, facilitating modular problem definition
and reproducible experiment design.

Mathematical Interpretation
---------------------------
Each storage unit *s* is characterized by:

- \( E_{min}, E_{max}, E_{ini} \): Minimum, maximum, and initial energy levels.  
- \( P^{ch}_{max}, P^{dis}_{max} \): Maximum charging and discharging powers.  
- \( \eta_c, \eta_d \): Charging and discharging efficiencies.  
- \( c_{op}, c_{inv} \): Operating and investment costs.  
- \( state \): Binary indicator of existing capacity (0 or 1).

The `StorageData` structure encapsulates:

- Temporal horizon \( T \)
- Demand curves by patamar and time
- Duration of load levels (in hours)
- Dictionary of `StorageUnit` definitions.

Usage
-----
Instances of `StorageData` are typically created from preprocessed
input datasets and passed directly to model-construction functions such as:

>>> from .StorageBuilder import build_storage
>>> model = build_storage(data=storage_data)

Classes
-------
StorageUnit
    Defines the parameters of a single storage unit.
StorageData
    Encapsulates all data required for the formulation of the storage problem.

Notes
-----
- This data structure is **independent of Pyomo** and can be serialized
  or deserialized to JSON for reproducibility.
- Units follow the SI convention: MWh for energy, MW for power, and
  monetary units for costs.

References
----------
[1] CEPEL, *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C., *Introdução aos Sistemas de Energia Elétrica*,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from dataclasses import dataclass
from typing import Dict, Union, List


@dataclass
class StorageUnit:
    """
    Defines the parameters of a single storage unit.

    Attributes
    ----------
    name : str
        Identifier of the storage unit.
    bar: str
        Connection Bar of the Unit (defaults to BAR_1)
    state : int
        Initial state (0 = not installed, 1 = existing).
    c_op : float
        Operational cost (per MWh of discharge or equivalent).
    c_inv : float
        Investment cost (annualized).
    Emin : float
        Minimum stored energy capacity (MWh).
    Emax : float
        Maximum stored energy capacity (MWh).
    Eini : float
        Initial stored energy at the beginning of the horizon (MWh).
    Pch_max : float
        Maximum charging power (MW).
    Pdis_max : float
        Maximum discharging power (MW).
    eta_c : float
        Charging efficiency (fraction between 0 and 1).
    eta_d : float
        Discharging efficiency (fraction between 0 and 1).
    """
    name: str
    bar: str
    state: int
    c_op: float
    c_inv: float
    Emin: float
    Emax: float
    Eini: float
    Pch_max: float
    Pdis_max: float
    eta_c: float
    eta_d: float


@dataclass
class StorageData:
    """
    Aggregates all data required for the storage optimization problem.

    Attributes
    ----------
    horizon : int
        Number of discrete time periods in the planning horizon.
    demand : Dict[str, List[float]]
        Dictionary of demand profiles, organized by
        patamar and time index.
    level_hours : Dict[str, float]
        Duration (in hours) associated with each demand level.
    delta_t : float
        Time step (years) used in the energy balance equations.
    units : Dict[str, StorageUnit]
        Dictionary of storage units indexed by their identifiers.
    """
    horizon: int
    delta_t: float
    units: Dict[str, StorageUnit]

