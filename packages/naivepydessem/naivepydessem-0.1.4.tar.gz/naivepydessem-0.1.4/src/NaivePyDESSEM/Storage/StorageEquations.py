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

from typing import List, Dict, Any
from pyomo.environ import ConcreteModel, Var, Expression


def add_storage_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Append storage-related cost terms to the total cost expression list.

    This function is intended as a placeholder or extension point for
    including storage system costs in the objective function of a Pyomo model.
    Typical terms may include degradation penalties, charging/discharging costs,
    or time-of-use price adjustments.

    If no relevant storage cost expressions are defined or required, the function
    simply returns the input list unchanged.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing storage system variables.
    cost_array : list of expressions
        List of symbolic expressions used to build the total cost function.

    Returns
    -------
    list of expressions
        The input list, optionally extended with storage-related cost expressions.

    Notes
    -----
    - This function is designed to be compatible with modular cost composition
      involving multiple technologies (e.g., thermal, hydro, storage).
    - Actual expressions should be added based on model-specific variables
      such as `Pch`, `Pdis`, `SoC`, or energy tariffs if available.
    """
    return cost_array


def add_storage_balance_expression(
    m: ConcreteModel,
    t: Any,
    balance_array: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    Append energy balance equations for storage units at time t to the constraint expression list.

    This function constructs and appends symbolic expressions that enforce the
    state-of-charge (SoC) evolution for each storage unit at time step `t`. The energy
    balance accounts for charging and discharging flows, adjusted by their respective
    efficiencies, and scaled by the time step duration.

    The function distinguishes between the initial period (`t == 1`), where it uses the
    initial energy level `storage_Eini`, and subsequent periods (`t > 1`), where it uses
    the SoC from the previous period.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing storage variables and parameters.
    t : int
        Time index at which the storage energy balance is evaluated.
    balance_array : dict of list of expressions
        List of symbolic expressions representing components of the power balance.

    Returns
    -------
    dict of list of expressions
        The updated list including the hydro generation term at time t.

    Notes
    -----
    - The expected model components are: SU, T, storage_E
    - If any required component is missing, the function returns the input list unchanged.
    - The returned expressions can be used with `ConstraintList` or indexed `Constraint(T)`.

    Examples
    --------
    >>> balance_terms = []
    >>> add_storage_balance_expression(model, t=1, balance_array=balance_terms)
    >>> model.StorageBalance.add(balance_terms[0])
    """
    required = [
        'SU', 'T', 'storage_dis', 'storage_ch', 'storage_bars'
    ]
    if all(hasattr(m, attr) for attr in required):
        for s in m.SU:
            bar = m.storage_bars[s]
            if bar not in balance_array:
                balance_array[bar] = list()
            balance_array[bar].append(m.storage_dis[s, t] 
                   -  m.storage_ch[s, t])
    return balance_array
