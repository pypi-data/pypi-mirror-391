"""
Generator Equations Module
==========================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines the objective-related expressions for the generation
subsystem in the MDI framework. It formulates both the **operational cost**
and **energy balance** expressions, which are later aggregated into the
system-level optimization model.

Description
-----------
The functions in this module generate symbolic expressions that represent
the two principal aspects of the generation subproblem:

1. **Operational and investment cost function** —  
   Represents the total cost of operation and expansion over the planning
   horizon, including both variable and fixed investment terms.

   \[
   C_{gen} = 
   \sum_{g,t,p} h_p \, c^{op}_g \, P_{g,t,p}
   \;+\;
   \sum_{g,t} c^{inv}_g \, x_{g,t}
   \]

   where  
   - \(h_p\) denotes the duration (hours) of load level \(p\),  
   - \(c^{op}_g\) is the operational cost of generator \(g\),  
   - \(c^{inv}_g\) is the investment cost per MW of capacity,  
   - \(P_{g,t,p}\) is the power generation level,  
   - \(x_{g,t}\) indicates if the unit is available at time \(t\).

2. **Generation balance expression** —  
   Computes the total available generation for each time period and load
   level, serving as input to system-level energy balance constraints:

   \[
   G_{bal}(t,p) = \sum_{g} P_{g,t,p}
   \]

Functions
---------
add_generator_cost_expression(m, cost_array)
    Builds and appends the generator cost expression to the provided array.

add_generator_balance_expression(m, t, p, balance_array)
    Builds and appends the generation balance expression for a given time
    period and load level to the provided array.

Notes
-----
- Both expressions are appended to lists (``cost_array`` or ``balance_array``)
  to allow modular composition of objectives and constraints in composite models.
- Missing attributes silently skip expression creation to maintain model integrity.
- This design enables dynamic integration of subsystems (e.g., storage, hydro,
  or renewable modules) under a unified optimization framework.

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,
    EELT7030/UFPR, 2023.

Module Dependencies
-------------------
- **Internal:** ``MDI.GeneratorVars``, ``MDI.GeneratorConstraints``  
- **External:** ``pyomo.environ (ConcreteModel)``, ``typing``
"""

from typing import List, Dict, Any
from pyomo.environ import ConcreteModel


def add_generator_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Build and append the generator cost expression to the provided list.

    This function constructs the total cost expression, including both
    operational and investment components, over all generators, time periods,
    and demand levels. The expression is appended to ``cost_array`` to allow
    aggregation with other subsystem costs.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing generator-related sets, variables, and parameters.
    cost_array : list of pyomo expressions
        List to which the total generator cost expression will be appended.

    Returns
    -------
    list of pyomo expressions
        The same list, extended with the generator cost expression.

    Notes
    -----
    The total generation cost is defined as:

    .. math::

        C_{gen} =
        \\sum_{g,t,p} h_p \\, c^{op}_g \\, P_{g,t,p}
        + \\sum_{g,t} c^{inv}_g \\, x_{g,t}

    where:
    - :math:`h_p` is the duration (hours) of load level :math:`p`;
    - :math:`c^{op}_g` is the operational cost per MWh;
    - :math:`c^{inv}_g` is the investment cost per MW;
    - :math:`P_{g,t,p}` and :math:`x_{g,t}` are decision variables.

    The resulting expression is symbolic and compatible with Pyomo objectives.
    """
    required = [
        'GU', 'T', 'P',
        'gen_P', 'gen_c_op', 'gen_c_inv',
        'gen_y', 'gen_x', 'level_hours'
    ]

    if all(hasattr(m, attr) for attr in required):
        if m.parcel_investment:
            expr = sum(
                # Operational cost (proportional to energy generated)
                m.discounts[t] * m.level_hours[p] * m.gen_c_op[g] * m.gen_P[g, t, p]
                for g in m.GU for t in m.T for p in m.P
            ) + sum(
                # Investment cost (proportional to installed capacity)
                m.discounts[t] * m.gen_c_inv[g] * m.gen_x[g, t]
                for g in m.GU for t in m.T
            )
        else:
            expr = sum(
                # Operational cost (proportional to energy generated)
                m.discounts[t] * m.level_hours[p] * m.gen_c_op[g] * m.gen_P[g, t, p]
                for g in m.GU for t in m.T for p in m.P
            ) + sum(
                # Investment cost (proportional to installed capacity)
                m.discounts[t] * m.gen_c_inv[g] * m.gen_y[g, t]
                for g in m.GU for t in m.T
            )
        cost_array.append(expr)

    return cost_array


def add_generator_capacity_expression(
    m: ConcreteModel,
    t: Any,
    p: Any,
    capacity_array: List[Any]
) -> List[Any]:
    """
    Build and append the generation capacity expression for a given time and level.

    Computes the total generation capacity across all units for the specified
    time period and demand level, and appends it to ``capacity_array``.
    The result serves as the left-hand side of the system-level
    generation capacity constraint.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing generator sets and variables.
    t : Any
        Time period index.
    p : Any
        Load level index.
    capacity_array : list of pyomo expressions
        List to which the generation capacity expression will be appended.

    Returns
    -------
    list of pyomo expressions
        The same list, extended with the generation capacity expression.

    Notes
    -----
    The capacity expression is defined as:

    .. math::

        G_{bal}(t,p) = \\sum_{g} P_{g,t,p}

    representing the total available generation at each period and load level.
    """
    required = [
        'GU', 'T', 'P', 'gen_pmax'
    ]

    if all(hasattr(m, attr) for attr in required):
        expr = sum(
            # Net power generation by unit and load level
            m.gen_pmax[g] * m.gen_x[g, t]
            for g in m.GU if m.gen_include_cap[g] == True
        )
        capacity_array.append(expr)

    return capacity_array


def add_generator_balance_expression(
    m: ConcreteModel,
    b: Any,
    t: Any,
    p: Any,
    balance_array: List[Any]
) -> List[Any]:
    """
    Build and append the generation balance expression for a given time and level.

    Computes the total power generated across all units for the specified
    time period and demand level, and appends it to ``balance_array``.
    The result serves as the left-hand side of the system-level
    energy balance constraint.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing generator sets and variables.
    b: Any
        Connection Bar Name
    t : Any
        Time period index.
    p : Any
        Load level index.
    balance_array : list of pyomo expressions
        List to which the generation balance expression will be appended.

    Returns
    -------
    list of pyomo expressions
        The same list, extended with the generation balance expression.

    Notes
    -----
    The balance expression is defined as:

    .. math::

        G_{bal}(t,p) = \\sum_{g} P_{g,t,p}

    representing the total available generation at each period and load level.
    """
    required = [
        'GU', 'T', 'P', 'gen_P', 'gen_bars'
    ]

    if all(hasattr(m, attr) for attr in required):
        temp_array: List = []
        for g in m.GU:
          bar = m.gen_bars[g]
          if bar == b:
              temp_array.append(m.gen_P[g, t, p])
        if len(temp_array) > 0:
            balance_array.append(sum(temp_array))
        
    return balance_array
