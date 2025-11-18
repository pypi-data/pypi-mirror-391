"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Objective Function for Pure Hydropower Dispatch - deprecated

Description
-----------
This module defines the objective for reservoir-based **hydropower-only**
optimization models. The objective minimizes (i) the total cost of unmet
energy (deficit) and (ii) a small penalty on water spillage to discourage
gratuitous releases, thereby promoting more efficient water usage.

Functions
---------
set_objective_hydro(m)
    Attach a minimization objective to a Pyomo model that penalizes
    deficit and spillage over the planning horizon.

Modeling Conventions and Units
------------------------------
- Time periods: integers ``t = 1, …, horizon``.
- Deficit ``D[t]``: MW (interpreted per-period, consistent with objective scaling).
- Spill ``hydro_S[h,t]``: m^3/s.
- ``Cdef``: $/MWh (ensure consistency with how deficit is modeled and aggregated).

Notes
-----
- Designed for **pure hydropower** systems (no thermal generation).
- The spillage penalty uses a fixed coefficient (0.3). Adjust as needed
  to break degeneracy or steer solutions away from unnecessary spill.
- Compatible with NaivePyDECOMP hydropower data and constraints.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023 
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""

from pyomo.environ import Objective, minimize
from NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives import set_objective_hydro
