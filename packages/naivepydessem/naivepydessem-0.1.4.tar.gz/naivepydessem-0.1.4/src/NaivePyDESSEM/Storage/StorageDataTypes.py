"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage Bank — Data Structures

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Lightweight data classes for battery energy storage systems (BESS). These
structures provide standardized inputs for Pyomo-based unit commitment and
dispatch models.

Classes
-------
StorageUnit
    Parameters of a single storage unit (SoC bounds, power limits,
    efficiencies, initial state).
StorageData
    System-level container that aggregates storage units and common
    parameters such as time-step duration.

Notes
-----
- The efficiencies can be specified per stage (charge/discharge) or derived
  from a round-trip value split across both stages by the user before
  instantiation.
- The time-step duration ``delta_t`` (hours) converts power (MW) to energy
  (MWh) in the state-of-charge balance.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class StorageUnit:
    """
    Data container for a battery energy storage unit.

    Parameters
    ----------
    name : str
        Unique identifier of the storage unit.
    bar: str
        Connection Bar of the Unit (defaults to BAR_1)
    Emin : float
        Minimum energy content (MWh).
    Emax : float
        Maximum energy content (MWh).
    Eini : float
        Initial energy content at the beginning of the horizon (MWh).
    Pch_max : float
        Maximum charging power (MW).
    Pdis_max : float
        Maximum discharging power (MW).
    eta_c : float
        Charging efficiency in ``[0, 1]``.
    eta_d : float
        Discharging efficiency in ``[0, 1]``.

    Notes
    -----
    - Ensure ``Emin <= Eini <= Emax`` for feasibility at the first period.
    - If a round-trip efficiency is provided externally, split it into
      ``eta_c`` and ``eta_d`` before creating the instance.
    """
    name: str
    bar: str
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
    System-wide data container for storage modeling.

    Parameters
    ----------
    horizon : int
        Number of time periods in the planning horizon.    
    units : Dict[str, StorageUnit]
        Mapping from unit identifier to :class:`StorageUnit`.
    delta_t : float
        Time-step duration (hours), used to convert MW to MWh.

    Notes
    -----
    - Typical values for ``delta_t`` are 1.0 (hourly) or 0.5 (30 minutes).
    """
    horizon: int
    units: Dict[str, StorageUnit]
    delta_t: float
