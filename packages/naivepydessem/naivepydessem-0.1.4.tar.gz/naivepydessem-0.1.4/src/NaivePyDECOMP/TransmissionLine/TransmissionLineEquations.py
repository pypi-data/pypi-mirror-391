"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Symbolic Equations

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines symbolic expressions for the active power flow on transmission
lines under the DC power flow approximation. These expressions are
used as intermediate components for nodal balance equations and other
network-level constraints.

Functions
---------
add_transmission_line_flow_expression(m, t, flow_dict)
    Construct symbolic expressions for each line’s power flow at period ``t``
    and append them to the supplied dictionary.
add_transmission_line_balance_expression(m, t, balance_dict)
    Aggregate inflow and outflow terms for each bar at time ``t`` to be used
    in connection-bar power balance constraints.

Notes
-----
- The DC power flow model assumes:
    ``F_ij,t = b_ij (θ_i,t − θ_j,t)``
  where:
    - ``F_ij,t`` : active power flow (MW)
    - ``b_ij`` : susceptance (1/x_ij)
    - ``θ_i,t`` : voltage phase angle at bar i (radians)
- Line flows are positive from the first to the second endpoint in the
  ``endpoints`` list, and negative in the opposite direction.
- This module produces expressions only; the corresponding constraints
  are enforced in :mod:`TransmissionLineConstraints`.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.TransmissionLine.TransmissionLineEquations import (
    add_transmission_line_cost_expression,
    add_transmission_line_balance_expression
)
