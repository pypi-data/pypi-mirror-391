"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Piecewise Linear Cost Module

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines utilities to construct piecewise-linear (PWL) cost
functions for thermal unit commitment (UC) models in Pyomo. It enables
the replacement of quadratic variable costs with linear approximations
compatible with MILP solvers.

Features
--------
- Builds Cvar[g,t] = f(p[g,t]) using Pyomo's *Piecewise* component.
- Supports convex-combination (SOS2) representation.
- Enforces equality Cvar[g,t] = C_PWL(p[g,t]).
- Allows unit-specific breakpoints (pw_breaks[g]) and cost values
  (pw_costs[g]) for accurate curve fitting.

Requirements
------------
- A Pyomo model with:

    * m.p[g,t]   : generation variable (MW)
    * m.Cvar[g,t]: PWL cost variable (R$/h)
    * m.pw_breaks[g], m.pw_costs[g] defined as lists of (x, f(x))
      points per unit g.

Usage
-----
Call *thermal_add_piecewise_cost(m)* after sets, parameters, and variables have
been added. For each unit g ∈ G and time t ∈ T, a PWL relation is built.

Example
-------
pw_breaks = [0, 150, 300, 455]
pw_costs  = [0, 2500, 6000, 10000]

Cvar[g,t] is constrained such that:

    Cvar[g,t] = Piecewise(p[g,t]; pw_breaks, pw_costs)

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import Piecewise, Constraint


def thermal_add_piecewise_cost(m):
    """
    Add piecewise-linear generation cost expression Cvar[g,t] = C_PWL_g(p[g,t]).

    For each thermal unit g and time period t, this function constructs a
    piecewise-linear (PWL) cost expression using predefined breakpoints
    and cost values. The implementation uses the 'CC' (convex combination)
    method with equality enforcement.

    Requirements
    ------------
    m : pyomo.environ.ConcreteModel
        The Pyomo model must include:

            - m.Cvar[g, t] : cost variable
            - m.p[g, t] : power generation variable
            - m.thermal_pw_breaks[g] : list of breakpoints (strictly increasing)
            - m.thermal_pw_costs[g] : list of corresponding cost values

    Raises
    ------
    ValueError
        If a unit g has undefined or mismatched `pw_breaks` and `pw_costs`.

    Returns
    -------
    ConcreteModel
        The modified model with one Piecewise component per unit.

    Notes
    -----
    - Each unit g must define a consistent pair of lists: `pw_breaks[g]` and
      `pw_costs[g]`, with identical length.
    - Internally, the function uses `pyomo.environ.Piecewise` with:
        - Index set: model.T
        - Representation: 'CC' (convex combination with SOS2 variables)
        - Constraint type: 'EQ' (enforces equality between cost and function value)
    - Each unit g receives a component named 'pw_{g}'.

    Examples
    --------
    >>> model = thermal_add_piecewise_cost(model)
    >>> model.pw_G1.pprint()
    Piecewise component for thermal unit G1 over time.
    """
    for g in m.TG:
        xpts = m.thermal_pw_breaks[g]
        ypts = m.thermal_pw_costs[g]
        if xpts is None or ypts is None:
            raise ValueError(f"Unidade {g} sem definição PWL (breaks/costs).")
        if len(xpts) != len(ypts):
            raise ValueError(
                f"PWL inconsistente em {g}: len(breaks)!=len(costs).")
        # Uma Piecewise por (g,t) para permitir curvas distintas por unidade
        comp_name = f"pw_{g}"
        setattr(m, comp_name, Piecewise(
            m.T,  # index set
            # y_var indexed: Cvar[g,t]
            vardata={(t): m.Cvar[g, t] for t in m.T},
            # x_var indexed: p[g,t]
            input={(t): m.p[g, t] for t in m.T},
            pw_pts=xpts,
            pw_constr_type='EQ',   # igualdade custo = f(p)
            f_rule=ypts,           # valores de custo nos pontos
            pw_repn='CC'           # convex combination (usa SOS2)
        ))
    return m
