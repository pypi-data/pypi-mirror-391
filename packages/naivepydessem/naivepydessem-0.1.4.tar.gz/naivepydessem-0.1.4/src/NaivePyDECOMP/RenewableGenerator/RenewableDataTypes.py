"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Generation Data Structures

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines lightweight data classes for representing renewable
generation units (e.g., wind and solar) and their aggregated system-level
data. These structures serve as standardized inputs for optimization
models of unit commitment and dispatch in Pyomo.

Classes
-------
RenewableUnit
    Encapsulates the characteristics of a single renewable unit, including
    identifier and time-varying availability profile.
RenewableData
    Aggregates renewable units with system-wide parameters such as horizon,
    demand profile, and deficit penalty cost.

Notes
-----
- The exogenous availability profiles are represented as deterministic
  time series (MW) and aligned with the planning horizon.
- The classes are designed for seamless integration into Pyomo-based
  optimization formulations, ensuring consistency with similar structures
  for thermal and hydro subsystems.
- Extend these classes as needed to incorporate stochastic scenarios or
  uncertainty modeling for renewable availability.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.RenewableGenerator.RenewableDataTypes import (
    RenewableUnit, 
    RenewableData
)
