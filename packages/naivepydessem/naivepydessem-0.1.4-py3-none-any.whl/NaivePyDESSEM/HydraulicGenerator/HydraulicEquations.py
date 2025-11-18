"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Hydraulic Model Expression Utilities for Pyomo Optimization

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides helper functions to construct symbolic expressions
related to energy hydraulic systems in Pyomo-based optimization models.
These expressions can be incrementally assembled and integrated into
constraints (e.g., energy balance) or cost functions (e.g.,
generation costs).

The functions are designed to support modular model construction and
hybrid system integration. They can be used in conjunction with other
technology modules (e.g., thermal, hydro, renewable) to build power
balance constraints and system-wide cost objectives.

All expressions are symbolic and compatible with Pyomo's modeling
framework. Each function includes safeguards to ensure that required
model components exist before attempting to generate expressions.

Intended Use
------------
- To append hydraulic-related cost and energy balance expressions to lists
  that contribute to the overall objective function and constraint set.
- To modularize and standardize hydraulic modeling across different hybrid
  energy system configurations.

Examples
--------
>>> cost_terms = []
>>> add_hydraulic_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)

>>> balance_terms = []
>>> add_hydraulic_balance_expression(model, t=5, balance_array=balance_terms)
>>> model.HydraulicBalance.add(balance_terms[0])

Notes
-----
- This module assumes that hydraulic behavior is modeled using variables such as
  `hydro_G`.
- The structure is compatible with Pyomo's ConstraintList and indexed Constraint(T).
- Expressions are constructed incrementally and can be combined with other
  sources (e.g., thermal, renewable) in hybrid dispatch models.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023..
"""
from typing import List, Dict, Any
from pyomo.environ import ConcreteModel, Var, Expression


def add_hydraulic_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Append hydroelectric generation cost terms to the total cost expression list.

    This function serves as a placeholder for incorporating cost components
    associated with hydroelectric operation into the objective function.
    Although hydro generation typically has negligible marginal cost,
    certain formulations may include opportunity costs, spill penalties,
    or environmental constraints as cost terms.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing hydroelectric generation variables.
    cost_array : list of expressions
        List of symbolic expressions used in constructing the total system cost.

    Returns
    -------
    list of expressions
        The input list, optionally extended with hydro-related cost expressions.

    Notes
    -----
    - In many cases, this function may return the original list unchanged.
    - It may be extended to include penalties for deviation from targets,
      reservoir violations, or environmental compensation.
    """
    expr = 0.3 * sum(m.hydro_S[h, t] for h in m.HG for t in m.T)
    cost_array.append(expr)
    return cost_array


def add_hydraulic_balance_expression(
    m: ConcreteModel,
    t: Any,
    balance_array: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    Append hydroelectric generation terms at time t to the power balance expression list.

    This function constructs a symbolic expression representing the total hydroelectric
    power generation at a given time step `t`, summed over all hydro units defined
    in the model. The resulting expression can be integrated into modular power
    balance constraints.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing hydro generation variables.
    t : int
        Time index at which the hydro contribution is evaluated.
    balance_array : dict of list of expressions
        List of symbolic expressions representing components of the power balance.

    Returns
    -------
    dict of list of expressions
        The updated list including the hydro generation term at time t.

    Notes
    -----
    - The model is expected to contain:
      'HG' (set of hydro units), 'T' (time set), and 'hydro_G' (generation variable).
    - The function returns the input list unchanged if any component is missing.
    - This function is designed for integration into hybrid dispatch frameworks
      that include thermal, hydraulic, and renewable sources.
    """
    required = [
        'HG', 'T', 'hydro_G', 'hydro_bars'
    ]

    if all(hasattr(m, attr) for attr in required):
      for h in m.HG:
          bar = m.hydro_bars[h]
          if bar not in balance_array:
              balance_array[bar] = list()
          balance_array[bar].append(m.hydro_G[h, t])
    
    return balance_array

