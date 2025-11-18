"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines the operational constraints for renewable generation
within Pyomo-based unit commitment and dispatch models. It enforces both
the per-unit generation availability limits and the system-wide energy
balance when only renewable units and deficit are considered.

Functions
---------
add_renewable_capacity_constraints(m)
    Enforce that renewable generation for each unit and period does not
    exceed the exogenous availability profile ``gbar``.
add_renewable_balance_constraint(m)
    Enforce the energy balance by equating total renewable generation
    plus deficit to the system demand at each time period.

Notes
-----
- The capacity constraints guarantee that ``renewable_gen[r,t]`` is bounded
  above by ``renewable_gbar[r,t]``, which typically comes from forecasts.
- The balance constraint is suitable for renewable-only models. In hybrid
  models (thermal + hydro + renewables), a combined balance formulation
  must be applied instead.
- The deficit variable ``D[t]`` provides feasibility when renewable
  generation cannot meet demand.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.RenewableGenerator.RenewableConstraints import (
    add_renewable_capacity_constraints,
    add_renewable_balance_constraint
)

