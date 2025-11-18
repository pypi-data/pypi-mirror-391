"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Module: Connection Bar — Symbolic Expressions for Pyomo Models

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines symbolic expressions for connection bars (buses) in
the context of integrated operation and expansion planning models (MDI).
It provides functions to build cost and balance expressions that integrate
generation, storage, and transmission subsystems within a unified
mathematical formulation.

The functions are designed for modular assembly of Pyomo-based models,
allowing each subsystem to contribute its respective terms to the global
objective function and nodal power balance constraints.

Each function performs internal verification of required components,
ensuring flexibility when operating within partially defined or staged
model configurations (e.g., single-node, multi-bar, or hybrid systems).

Intended Use
------------
- To assemble total system cost expressions including generation,
  storage, deficit, and network effects.
- To construct nodal (bus-level) power balance equations that ensure
  Kirchhoff’s law compliance across the network.

Examples
--------
>>> cost_terms = []
>>> add_connection_bar_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)

>>> balance_dict = {}
>>> add_connection_bar_balance_expression(model, t=1, p="Ponta", balance_array=balance_dict)
>>> for bar, expr in balance_dict.items():
...     model.PowerBalance.add(expr)

Notes
-----
- This module assumes that the model contains:
  `CB` (connection bars), `T` (time set), `P` (load levels),
  and subsystem modules with balance functions for
  generation, storage, and transmission.
- Cost expressions include deficit penalties (`Cdef * D[b,t,p]`)
  weighted by discount factors and load duration.
- The resulting symbolic expressions are compatible with both
  ConstraintList and indexed Constraint formulations in Pyomo.

References
----------
[1] CEPEL, DECOMP / DESSEM — Metodologia de Modelagem Hidrotérmica, 2023  
[2] Unsihuay Vila, C. (2023). Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR.
"""

from typing import List, Dict, Any
from pyomo.environ import ConcreteModel

from MDI.Generator.GeneratorEquations import (
    add_generator_balance_expression, 
    add_generator_capacity_expression
)
from MDI.Storage.StorageEquations import (
    add_storage_balance_expression, 
    add_storage_capacity_expression
)
from MDI.TransmissionLine.TransmissionLineEquations import (
    add_transmission_line_balance_expression
)

def add_connection_bar_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Append deficit penalty terms to the total cost expression.

    Constructs and appends the total cost expression associated with
    unmet demand (deficit) across all bars, time periods, and load levels.
    The cost is discounted over time and weighted by load duration.

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model containing bars, time periods, and load levels.
    cost_array : list of Pyomo expressions
        List of symbolic expressions to which the total deficit cost term
        will be appended.

    Returns
    -------
    list of Pyomo expressions
        The same list, extended with the deficit cost expression.

    Notes
    -----
    - The expression added is of the form:

      .. math::
         C_{def} = \\sum_{b,t,p} (discount_t \\cdot h_p \\cdot Cdef_b \\cdot D_{b,t,p})

    - The cost reflects the economic penalty of unserved energy and
      integrates directly into the objective function of the MDI model.
    """
    expr = sum(
        m.discounts[t] * m.level_hours[p] * m.Cdef[b] * m.D[b, t, p]
        for b in m.CB for t in m.T for p in m.P
    )
    cost_array.append(expr)
    return cost_array

def add_connection_bar_capacity_expression(
        m: ConcreteModel,
        t: Any,
        p: str,
        capacity_array: List[Any]
) -> List[Any]:
    """
    
    """
    add_generator_capacity_expression(m, t, p, capacity_array)
    add_storage_capacity_expression(m, t, p, capacity_array)
    return capacity_array

def add_connection_bar_balance_expression(
    m: ConcreteModel,
    b: Any,
    t: Any,
    p: str,
    balance_array: List[Any]
) -> List[Any]:
    """
    Construct the nodal power balance expressions for each connection bar.

    Aggregates all inflows and outflows of power at time ``t`` and load
    level ``p`` for each connection bar. Includes generation, storage,
    transmission, and deficit components.

    Mathematically, for each bar ``b``:

    .. math::

        \\sum_{g \\in G_b} P_{g,t,p}
        + \\sum_{s \\in S_b} (dis_s - ch_s)
        + \\sum_{ℓ \\in Ω_b^{in}} F_{ℓ,t}
        - \\sum_{ℓ \\in Ω_b^{out}} F_{ℓ,t}
        + D_{b,t,p}
        = D_{b,t,p}^{dem}

    Parameters
    ----------
    m : ConcreteModel
        Pyomo model instance containing subsystems and bars.
    t : int
        Time period index.
    p : str
        Load level (e.g., "Ponta" or "Fora").
    balance_array : dict
        Dictionary mapping each bar to a list of symbolic expressions
        contributing to its power balance.

    Returns
    -------
    dict
        Updated dictionary of symbolic expressions for each bar.

    Notes
    -----
    - The resulting expressions can be added as constraints via:

      >>> for bar, expr in balance_dict.items():
      >>>     model.PowerBalance.add(expr)

    - Each bar’s balance includes the local deficit term `D[b,t,p]`.
    - Transmission flows contribute with positive sign for inflow
      and negative for outflow.
    """
    add_generator_balance_expression(m, b, t, p, balance_array)
    add_storage_balance_expression(m, b, t, p, balance_array)
    add_transmission_line_balance_expression(m, b, t, p, balance_array)
    return balance_array
