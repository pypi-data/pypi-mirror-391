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

from typing import List, Dict, Any
from pyomo.environ import ConcreteModel, Var, Expression


def add_renewable_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Append renewable generation cost terms to the total cost expression list.

    This function is a placeholder or extension point for incorporating
    renewable energy cost terms into the objective function. While many
    renewable sources (e.g., wind, solar) have negligible marginal costs,
    this function allows the inclusion of opportunity costs, curtailment
    penalties, or tariffs if applicable.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing renewable variables and parameters.
    cost_array : list of expressions
        List of symbolic expressions that contribute to the total cost.

    Returns
    -------
    list of expressions
        The input list, optionally extended with renewable cost expressions.

    Notes
    -----
    - If no cost expression is required for renewables, the function simply
      returns the list unchanged.
    - This function can be expanded to include curtailment penalties or
      contracted delivery costs based on `renewable_gen` variables.
    """
    return cost_array


def add_renewable_balance_expression(
    m: ConcreteModel,
    t: Any,
    balance_array: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    Append renewable generation terms at time t to the power balance expression list.

    This function constructs a symbolic expression representing the total power
    injected by renewable sources at a given time step `t`, and appends it to
    the power balance equation. The function is compatible with modular power
    balance construction in hybrid energy system models.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing renewable generation variables.
    t : int
        Time index for which the renewable generation is evaluated.
    balance_array : dict of list of expressions
        List of symbolic expressions representing components of the power balance.

    Returns
    -------
    dict of list of expressions
        The updated list including the hydro generation term at time t.
        
    Notes
    -----
    - The model is expected to contain the following components:
      'RU' (renewable unit set), 'T' (time set), and 'renewable_gen' (generation variable).
    - This function is designed for use within a larger balance constraint rule
      such as `Constraint(model.T, rule=...)` or within a ConstraintList.
    """
    required = [
        'RU', 'T', 'renewable_gen', 'renewable_bars'
    ]
    if all(hasattr(m, attr) for attr in required):
        for r in m.RU:
          bar = m.renewable_bars[r]
          if bar not in balance_array:
              balance_array[bar] = list()
          balance_array[bar].append(m.renewable_gen[r, t])
    return balance_array
