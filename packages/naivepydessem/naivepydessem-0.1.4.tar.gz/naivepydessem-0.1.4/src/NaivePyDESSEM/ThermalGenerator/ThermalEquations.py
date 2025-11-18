"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Model Expression Utilities for Pyomo Optimization

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides helper functions to construct symbolic expressions
related to thermal power generation in Pyomo models. These expressions
can be incrementally assembled and used in constraints (e.g., power balance)
or in the objective function (e.g., cost minimization).

Functions are designed to be modular and composable, allowing the user to
build lists of partial expressions from multiple sources (e.g., thermal,
hydro, renewable, storage) and sum them later into complete constraints
or cost functions.

All functions operate safely: they first verify the presence of required
model components (e.g., sets, variables, parameters) before contributing
expressions. If components are missing, the expressions are skipped
silently, enabling flexible model composition.

Intended Use
------------
- To support modular construction of the objective function, especially
  when not all energy sources are known in advance.
- To build power balance equations at each time step by aggregating
  contributions from thermal and other sources.

Examples
--------
>>> cost_terms = []
>>> add_thermal_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)

>>> balance_terms = []
>>> add_thermal_balance_expression(model, t=5, balance_terms)
>>> model.BalanceConstraint[5] = Constraint(expr=sum(balance_terms) == model.Demand[5])

Notes
-----
- All expressions returned are Pyomo symbolic expressions.
- This module assumes the model follows the naming convention:
  'thermal_p', 'thermal_u', 'thermal_y', 'thermal_SC', etc.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from typing import List, Dict, Any
from pyomo.environ import ConcreteModel, Var, Expression


def add_thermal_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Append thermal generation cost terms to the total cost expression list,
    if the required model components are present.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing thermal data.
    cost_array : list of expressions
        List of symbolic expressions to be used in the objective function.

    Returns
    -------
    list of expressions
        The updated list including thermal cost terms if available.
    """
    required = [
        'TG', 'T', 'thermal_c', 'thermal_b', 'thermal_a',
        'thermal_p', 'thermal_u', 'thermal_y', 'thermal_SC'
    ]
    if all(hasattr(m, attr) for attr in required):
        quad = sum(
            m.thermal_c[g] * m.thermal_p[g, t]**2 +
            m.thermal_b[g] * m.thermal_p[g, t] +
            m.thermal_a[g] * m.thermal_u[g, t]
            for g in m.TG for t in m.T
        )
        starts = sum(
            m.thermal_SC[g] * m.thermal_y[g, t]
            for g in m.TG for t in m.T
        )
        cost_array.append(quad + starts)
    return cost_array


def add_thermal_balance_expression(
    m: ConcreteModel,
    t: Any,
    balance_array: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    Append the thermal generation expression at a given time step t
    to the balance equation expression list.

    This is intended for use in constructing hybrid or modular power
    balance constraints where multiple sources (thermal, hydro, solar, etc.)
    contribute to the total injected power at each time step.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model containing the thermal variables.
    t : int
        Time index for which the expression should be generated.
    balance_array : dict of list of expressions
        List of symbolic expressions representing components of the power balance.

    Returns
    -------
    dict of list of expressions
        The updated list including the hydro generation term at time t.
    """
    if hasattr(m, 'TG') and hasattr(m, 'thermal_p'):
        for g in m.TG:
            bar = m.thermal_bars[g]
            if bar not in balance_array:
                balance_array[bar] = list()
            balance_array[bar].append(m.thermal_p[g, t])
    return balance_array

