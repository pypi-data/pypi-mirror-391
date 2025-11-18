"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Energy Storage — Constraints

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines the operational constraints for battery energy storage
systems (BESS) within Pyomo-based dispatch and unit commitment models.
The formulation is consistent with the hydraulic and renewable modules,
ensuring interoperability in hybrid optimization frameworks.

Functions
---------
add_storage_energy_balance_constraint(m)
    Enforce intertemporal state-of-charge balance with charge/discharge
    efficiencies and time-step duration.
add_storage_soc_bounds_constraint(m)
    Impose minimum and maximum state-of-charge limits.
add_storage_power_limits_constraint(m)
    Impose per-period charging and discharging power limits.
add_storage_mutual_exclusion_constraint(m)
    (Optional) Prohibit simultaneous charging and discharging through a
    big-M formulation with binary mode variables.
add_storage_only_balance_constraint(m)
    Enforce system-wide balance for storage-only models, equating net
    injection plus deficit to the demand at each period.

Notes
-----
- The efficiencies (``eta_c``, ``eta_d``) can be specified per stage or
  derived from a round-trip value split by the user.
- For hybrid models (hydro, thermal, renewable, storage), the global
  balance should be implemented at a higher builder level.
- The formulation assumes a fixed period duration ``delta_t`` in hours,
  used to convert power (MW) to energy (MWh).

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.Storage.StorageConstraints import (
    add_storage_energy_balance_constraint,
    add_storage_only_balance_constraint,
    add_storage_power_limits_constraint,
    add_storage_soc_bounds_constraint,
    add_storage_mutual_exclusion_constraint
)
