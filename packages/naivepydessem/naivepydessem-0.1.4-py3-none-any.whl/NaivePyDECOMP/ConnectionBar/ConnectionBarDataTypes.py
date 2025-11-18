"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Connection Bar Data Structures

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines lightweight data classes for representing
connection bars (buses) in power system operation and expansion
models. Each connection bar encapsulates its electrical state,
demand profile, and configuration parameters. The aggregated
system-level data structure (`ConnectionBarData`) groups all
bars with the planning horizon and deficit penalty cost.

Classes
-------
ConnectionBarUnit
    Represents a single connection bar (bus) with demand profile,
    slack flag, and operational attributes.

ConnectionBarData
    Aggregates multiple connection bars with common parameters
    such as planning horizon, system-level demand reference, and
    deficit cost.

Notes
-----
- The demand profile of each bar is expressed as a deterministic
  time series aligned with the planning horizon.
- These structures serve as standardized inputs for Pyomo-based
  formulations of DECOMP, DESSEM, or the abstracted MDI model.
- Extend as needed to include locational data, voltage levels,
  or stochastic demand scenarios.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.ConnectionBar.ConnectionBarDataTypes import (
    ConnectionBarData,
    ConnectionBarUnit
)

