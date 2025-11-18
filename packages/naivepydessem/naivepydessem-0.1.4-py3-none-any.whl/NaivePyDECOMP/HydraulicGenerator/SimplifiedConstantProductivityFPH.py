"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Simplified Constant Productivity FPH Function

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines a simplified hydropower production function (FPH) for short-term
operation models. The generation is assumed to be proportional to turbine
discharge, scaled by a constant productivity coefficient.

The FPH is expressed as:

    FPH(Q) = P * Q

where:
- Q : turbine discharge (hm^3)
- P : global productivity coefficient (dimensionless)

This formulation is particularly useful for approximate dispatch models,
sensitivity analyses, or didactic examples that do not require head-dependent
hydraulic modeling.

Notes
-----
- Unlike the more detailed constant-productivity model, this simplified
  function does not include the ``zeta`` scaling factor. If desired, the
  conversion constant can be absorbed directly into ``P`` to yield MW.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023 
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""

from NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH import simplified_constant_productivity_fph