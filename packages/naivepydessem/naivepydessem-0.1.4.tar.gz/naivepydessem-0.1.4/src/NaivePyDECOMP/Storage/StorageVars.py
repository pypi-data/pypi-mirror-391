"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Provides initialization routines for adding storage-related sets, parameters,
and decision variables to Pyomo-based dispatch and unit commitment models.
This module ensures a consistent interface for modeling battery energy storage
systems (BESS) across different formulations.

Functions
---------
storage_add_sets_and_params(m, data)
    Initialize sets and Pyomo parameters for storage units, including
    state-of-charge bounds, initial conditions, power limits, efficiencies,
    and time-step duration.
storage_add_variables(m)
    Declare continuous decision variables for state-of-charge, charging
    power, and discharging power. If absent, also define a deficit variable
    for feasibility.

Notes
-----
- Parameters are namespaced with the prefix ``storage_`` for clarity and
  compatibility with other subsystems (hydro, thermal, renewable).
- The time-step duration (``delta_t``) converts power (MW) to energy (MWh)
  within the state-of-charge balance equation.
- The variables are declared as non-negative and continuous. Binary
  variables may be added in other modules if mutual exclusion between
  charge and discharge is required.
  
References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.Storage.StorageVars import (
    storage_add_sets_and_params,
    storage_add_variables
)
