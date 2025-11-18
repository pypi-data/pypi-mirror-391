"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Connection Bar — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines initialization routines for connection bars (nodes)
within power system operation and expansion models in Pyomo. It provides
the sets, parameters, and decision variables associated with network
buses, including demand, deficit, and phase angles for DC power flow
formulations.

Functions
---------
connection_bar_add_sets_and_params(m, data)
    Initialize sets and parameters for connection bars, including
    demand profiles and bar-specific attributes (state, slack status, etc.).

connection_bar_add_variables(m)
    Declare bar-level decision variables: deficit (unserved demand) and
    phase angle (for DC models).

Notes
-----
- Designed for integration with hydrothermal and renewable subsystems.
- The time set ``m.T`` is assumed global and will only be created if
  not already defined.
- Each bar (bus) has a time-varying demand ``demand[b,t]`` and, optionally,
  a deficit variable ``D[b,t]`` penalized by ``m.Cdef`` in the objective.
- The slack bar is identified by ``bar.slack = True`` and its phase angle
  is fixed at zero.

References
----------
[1] CEPEL, DECOMP / DESSEM Methodology Manuals, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.ConnectionBar.ConnectionBarVars import (
    connection_bar_add_sets_and_params,
    connection_bar_add_variables
)
