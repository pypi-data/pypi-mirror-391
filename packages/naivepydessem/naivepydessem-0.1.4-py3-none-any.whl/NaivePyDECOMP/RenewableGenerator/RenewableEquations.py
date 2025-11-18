"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Renewable Model Expression Utilities for Pyomo Optimization

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides helper functions to construct symbolic expressions
related to renewable energy generation in Pyomo-based optimization models.
The expressions generated here can be used to assemble power balance
constraints and, when applicable, cost functions that include renewable
generation impacts such as curtailment penalties or contractual delivery.

The functions are designed to operate modularly, enabling integration
into hybrid models that combine thermal, hydro, storage, and renewable
sources in a unified dispatch or expansion framework.

Each function verifies the availability of required model components
before contributing expressions, allowing for flexible integration
without error propagation in partially defined models.

Intended Use
------------
- To support the incremental construction of power balance constraints
  by including generation terms from renewable units.
- To optionally incorporate renewable-related cost components, including
  penalties or market mechanisms.

Examples
--------
>>> cost_terms = []
>>> add_renewable_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)

>>> balance_terms = []
>>> add_renewable_balance_expression(model, t=5, balance_array=balance_terms)
>>> model.PowerBalance.add(balance_terms[0])

Notes
-----
- This module assumes the existence of model components such as:
  `RU` (set of renewable units), `T` (time set), and `renewable_gen` (generation variable).
- Cost expressions are optional and can be enabled based on use case (e.g., curtailment penalties).
- The symbolic expressions returned can be used with ConstraintList or Constraint(model.T).

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. (2023). Introdução aos Sistemas de Energia Elétrica,  Lecture Notes EELT7030/UFPR.
"""

from NaivePyDESSEM.RenewableGenerator.RenewableEquations import (
    add_renewable_cost_expression,
    add_renewable_balance_expression
)
