"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines initialization routines for transmission lines
within DC power flow formulations in Pyomo. It provides the sets,
parameters, and decision variables associated with transmission
circuits, including susceptance, flow limits, and endpoint
connectivity between connection bars.

Functions
---------
transmission_line_add_sets_and_params(m, data)
    Initialize sets and parameters for transmission lines, including
    susceptance, flow capacity, and bar-to-bar connectivity.
transmission_line_add_variables(m)
    Declare line-level decision variables representing active power
    flows for each line and time period.

Notes
-----
- Designed for integration with connection-bar models and other
  subsystems (hydro, thermal, renewable, storage).
- The time set ``m.T`` is assumed global and will only be created if
  not already defined.
- Each line connects two bars defined by its ``endpoints`` attribute.
- The parameters ``b``, ``pmax`` and ``endpoints`` are initialized
  directly from the data structure :class:`TransmissionLineData`.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.TransmissionLine.TransmissionLineVars import (
    transmission_line_add_sets_and_params,
    transmission_line_add_variables
)
