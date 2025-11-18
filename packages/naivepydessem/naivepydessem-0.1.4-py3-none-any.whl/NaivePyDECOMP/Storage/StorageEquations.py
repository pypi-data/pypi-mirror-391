"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Storage Model Expression Utilities for Pyomo Optimization

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides helper functions to construct symbolic expressions
related to energy storage systems in Pyomo-based optimization models.
These expressions can be incrementally assembled and integrated into
constraints (e.g., state-of-charge evolution) or cost functions (e.g.,
charging/discharging costs).

The functions are designed to support modular model construction and
hybrid system integration. They can be used in conjunction with other
technology modules (e.g., thermal, hydro, renewable) to build power
balance constraints and system-wide cost objectives.

All expressions are symbolic and compatible with Pyomo's modeling
framework. Each function includes safeguards to ensure that required
model components exist before attempting to generate expressions.

Intended Use
------------
- To append storage-related cost and energy balance expressions to lists
  that contribute to the overall objective function and constraint set.
- To modularize and standardize storage modeling across different hybrid
  energy system configurations.

Examples
--------
>>> cost_terms = []
>>> add_storage_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)

>>> balance_terms = []
>>> add_storage_balance_expression(model, t=5, balance_array=balance_terms)
>>> model.StorageBalance.add(balance_terms[0])

Notes
-----
- This module assumes that storage behavior is modeled using variables such as:
  `storage_E`, `storage_ch`, `storage_dis`, `storage_Eini`,
  and parameters like `storage_eta_c`, `storage_eta_d`, and `storage_delta_t`.
- The structure is compatible with Pyomo's ConstraintList and indexed Constraint(T).
- Expressions are constructed incrementally and can be combined with other
  sources (e.g., thermal, hydro) in hybrid dispatch models.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023..
"""

from NaivePyDESSEM.Storage.StorageEquations import (
    add_storage_balance_expression,
    add_storage_cost_expression
)
