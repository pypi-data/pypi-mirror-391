"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides initialization routines for renewable generation
within unit-commitment and dispatch models in Pyomo. It defines the sets,
parameters, and decision variables required to incorporate renewable
units (e.g., wind or solar) into short-term planning formulations.

Functions
---------
renewable_add_sets_and_params(m, data)
    Initialize sets and parameters for renewable units, including the
    renewable unit set and availability profiles ``gbar``.
renewable_add_variables(m)
    Declare renewable generation decision variables and, if not present,
    the deficit variable.

Notes
-----
- Availability profiles ``gbar`` are assumed to be exogenous, deterministic,
  and aligned with the planning horizon.
- The module is designed for integration with hydro and thermal
  subsystems, ensuring that common components such as time set ``m.T``,
  demand ``m.d``, and deficit penalty ``m.Cdef`` are not redefined if
  already present.
- Renewable generation is always bounded above by its availability; the
  actual capacity constraint should be added separately.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.RenewableGenerator.RenewableVars import (
    renewable_add_sets_and_params, 
    renewable_add_variables
)
