"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Objective Function

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines the objective function for renewable-only dispatch models in Pyomo.
The objective minimizes the total cost of unmet demand (deficit) over the
planning horizon. It uses the deficit penalty parameter ``Cdef`` to quantify
the economic impact of unserved energy.

Functions
---------
set_objective_renewable(m)
    Attach a minimization objective to the model, penalizing unmet demand.

Notes
-----
- This objective is designed for renewable-only systems, where generation
  is fully determined by availability and no explicit fuel costs exist.
- The deficit variable ``D[t]`` ensures feasibility when renewable
  generation cannot meet the demand ``d[t]``.
- The penalty coefficient ``Cdef`` should be chosen high enough to
  discourage deficits under normal conditions.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.RenewableGenerator.RenewableObjectives import set_objective_renewable
