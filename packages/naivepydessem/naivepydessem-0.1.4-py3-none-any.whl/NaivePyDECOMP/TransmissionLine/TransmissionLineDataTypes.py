"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Data Structures

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines lightweight data classes for representing transmission lines
in DC power flow formulations. Each line connects two connection bars
(endpoints), has a specified susceptance and maximum power limit.

These structures serve as standardized inputs for Pyomo-based
optimization models, supporting both operational (DCOPF) and
expansion (MDI) formulations.

Classes
-------
TransmissionLineUnit
    Encapsulates the physical andproperties of a single
    transmission line or circuit, including endpoints and flow limits.

TransmissionLineData
    Aggregates multiple line units along with global configuration
    parameters such as planning horizon and reference data.

Notes
-----
- The line susceptance ``b`` is defined as the inverse of the series
  reactance ``x_ij`` in per-unit.
- The endpoints are represented as a list ``[bar_i, bar_j]``.
- The ``state`` attribute allows distinguishing between existing (1)
  and candidate (0) lines for expansion studies.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""
from NaivePyDESSEM.TransmissionLine.TransmissionLineDataTypes import (
    TransmissionLineUnit,
    TransmissionLineData
)
