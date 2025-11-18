"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines the physical and operational constraints for transmission
lines in DC power flow formulations. These constraints link line
flows to phase-angle differences through susceptance and limit
the flow magnitude according to each line’s capacity.

Functions
---------
add_transmission_line_flow_constraints(m)
    Enforce the DC flow definition:
    ``F_ij,t = b_ij (θ_i,t − θ_j,t)`` for all lines and time periods.
add_transmission_line_flow_limits_constraints(m)
    Apply the flow capacity limits:
    ``−pmax_ij ≤ F_ij,t ≤ pmax_ij`` for all lines and time periods.

Notes
-----
- Each line is characterized by:
  - ``b_ij`` : susceptance (1/x_ij)
  - ``pmax_ij`` : maximum active power flow (MW)
  - ``endpoints`` : list of two bars [i, j]
- These constraints are suitable for both static (operational)
  and mixed-integer (expansion) formulations.
- Phase angles ``θ_i,t`` and ``θ_j,t`` must exist in the model
  before these constraints are declared.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.TransmissionLine.TransmissionLineConstraints import (
    add_transmission_line_flow_constraints,
    add_transmission_line_flow_limits_constraints
)
