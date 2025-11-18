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

from NaivePyDESSEM.Storage.StorageDataTypes import (
    StorageUnit,
    StorageData
)
