"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Symbolic Equations

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines symbolic expressions for the active power flow on transmission
lines under the DC power flow approximation. These expressions are
used as intermediate components for nodal balance equations and other
network-level constraints.

Functions
---------
add_transmission_line_flow_expression(m, t, flow_dict)
    Construct symbolic expressions for each line’s power flow at period ``t``
    and append them to the supplied dictionary.
add_transmission_line_balance_expression(m, t, balance_dict)
    Aggregate inflow and outflow terms for each bar at time ``t`` to be used
    in connection-bar power balance constraints.

Notes
-----
- The DC power flow model assumes:
    ``F_ij,t = b_ij (θ_i,t − θ_j,t)``
  where:
    - ``F_ij,t`` : active power flow (MW)
    - ``b_ij`` : susceptance (1/x_ij)
    - ``θ_i,t`` : voltage phase angle at bar i (radians)
- Line flows are positive from the first to the second endpoint in the
  ``endpoints`` list, and negative in the opposite direction.
- This module produces expressions only; the corresponding constraints
  are enforced in :mod:`TransmissionLineConstraints`.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConcreteModel
from typing import List, Dict, Any


def add_transmission_line_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Append line transmission cost terms to the total cost expression list.

    This function serves as a placeholder for incorporating cost components
    associated with  into the objective function.

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
    """
    required = ['LT', 'T', 'lines_endpoints', 'lines_flow']
    if all(hasattr(m, attr) for attr in required):
        if m.parcel_investment:
            
            expr = sum(
                # Operational cost (proportional to energy moved)
                m.discounts[t] * m.level_hours[p] * m.lines_c_op[l] * m.lines_flow[l, t, p]
                for l in m.LT for t in m.T for p in m.P
            ) + sum(
                # Investment cost (proportional to existence)
                m. discounts[t] * m.lines_c_inv[l] * m.lines_x[l, t]
                for l in m.LT for t in m.T
            )
        else:
            expr = sum(
                # Operational cost (proportional to energy moved)
                m.discounts[t] * m.level_hours[p] * m.lines_c_op[l] * m.lines_flow[l, t, p]
                for l in m.LT for t in m.T for p in m.P
            ) + sum(
                # Investment cost (proportional to existence)
                m. discounts[t] * m.lines_c_inv[l] * m.lines_y[l, t]
                for l in m.LT for t in m.T
            )
        cost_array.append(expr)
    return cost_array


def add_transmission_line_balance_expression(
        m: ConcreteModel,
        b: Any,
        t: Any,
        p: Any,
        balance_array: List[Any]) -> List[Any]:
    """
    Aggregate inflow and outflow terms for each bar at time ``t``.

    This routine computes, for each bar, the algebraic contribution
    of all connected transmission lines to the nodal power balance.

    Mathematically:
        ``Σ_in(F_ij,t) − Σ_out(F_ij,t)``
    where:
        - Incoming flows are from neighboring bars j such that line (j,i) exists.
        - Outgoing flows are from bar i to other bars j.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model containing:
        - ``m.LT`` : set of transmission lines
        - ``m.lines_endpoints[l]`` : list of bar identifiers [i, j]
        - ``m.lines_b[l]`` : susceptance (1/x)
        - ``m.theta[b,t]`` : voltage phase angle (radians)
    t : int/Any
        Time period index.    
    p : str/Any
        level index.
    balance_dict : Dict[str, List[Any]]
        Dictionary indexed by bar name. Each entry is a list of symbolic
        expressions contributing to that bar’s power balance.

    Returns
    -------
    Dict[str, List[Any]]
        The same dictionary updated with inflow/outflow contributions
        from all transmission lines.

    """
    required = ['LT', 'T', 'lines_endpoints', 'lines_flow']
    if all(hasattr(m, attr) for attr in required):
        temp_array: List = []
        for l in m.LT:
            i, j = m.lines_endpoints[l]
            expr = m.lines_flow[l, t, p]

            # Outflow from i (negative contribution)
            if i == b:
                temp_array.append(-expr)

            # Inflow to j (positive contribution)
            if j == b:
                temp_array.append(expr)
        if len(temp_array) > 0:
            balance_array.append(sum(temp_array))
        
    return balance_array
