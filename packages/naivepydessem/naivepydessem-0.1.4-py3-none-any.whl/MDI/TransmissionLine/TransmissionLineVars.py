"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines initialization routines for transmission lines
within DC power flow formulations in Pyomo. It provides the sets,
parameters, and decision variables associated with transmission
circuits, including susceptance, flow limits, and endpoint
connectivity between connection bars.

Functions
---------
transmission_line_add_sets_and_params(m, data)
    Initialize sets and parameters for transmission lines, including
    susceptance, flow capacity, and bar-to-bar connectivity.
transmission_line_add_variables(m)
    Declare line-level decision variables representing active power
    flows for each line and time period.

Notes
-----
- Designed for integration with connection-bar models and other
  subsystems (hydro, thermal, renewable, storage).
- The time set ``m.T`` is assumed global and will only be created if
  not already defined.
- Each line connects two bars defined by its ``endpoints`` attribute.
- The parameters ``b``, ``pmax`` and ``endpoints`` are initialized
  directly from the data structure :class:`TransmissionLineData`.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import (RangeSet, Set, Param, Var,
                           Reals, NonNegativeReals, Binary, ConcreteModel)


def transmission_line_add_sets_and_params(m: ConcreteModel, data) -> ConcreteModel:
    """
    Initialize sets and parameters for transmission lines.

    Adds the transmission line set ``m.LT`` and associated dictionaries
    of electrical parameters: susceptance ``b``, flow limit ``pmax``,
    and connection endpoints (``bar_i``, ``bar_j``). The model type and
    other metadata may also be stored for each line.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which transmission-line sets and parameters
        will be added.
    data : TransmissionLineData
        Data structure containing:
        - ``horizon`` (int): number of time periods.
        - ``units`` (dict[str, TransmissionLineUnit]): mapping of line
          identifiers to their attributes (model, b, pmax, endpoints).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model, augmented with transmission-line sets and parameters.

    Notes
    -----
    - If the model already defines ``m.T``, it will not be overwritten.
    - The time set is defined as ``RangeSet(1, horizon)`` if absent.
    - The parameter mappings are stored as Python dictionaries for
      efficient access during constraint construction.
    """

    # Ensure global time set exists
    if not hasattr(m, "T"):
        m.T = RangeSet(1, data.horizon)

    # discounts
    if not hasattr(m, 'discounts'):
      m.discounts = Param(
          m.T,
          initialize={t: 1 / ((1 + m.interest_rate) ** (t - 1)) for t in m.T},
          within=NonNegativeReals
      )
    
    # Create line set
    lines = list(data.units.keys())
    m.LT = Set(initialize=lines)

    # Store parameters as dictionaries (non-Param for flexibility)
    m.lines_transmission_model = {l: data.units[l].model for l in lines}
    m.lines_b = {l: data.units[l].b for l in lines}
    m.lines_pmax = {l: data.units[l].pmax for l in lines}
    m.lines_endpoints = {l: data.units[l].endpoints for l in lines}

    # Cost and state parameters
    m.lines_c_inv = Param(m.LT, initialize={l: data.units[l].c_inv for l in lines})
    m.lines_c_op = Param(m.LT, initialize={l: data.units[l].c_op for l in lines})
    m.lines_state = Param(m.LT, initialize={l: data.units[l].state for l in lines})

    return m


def transmission_line_add_variables(m: ConcreteModel) -> ConcreteModel:
    """
    Declare decision variables for transmission lines.

    Adds the continuous real variable ``m.lines_flow[l,t]``, representing
    the active power flow (MW) through line ``l`` at time period ``t``.
    The variable may assume positive or negative values, indicating
    direction of flow between the two connected bars.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which transmission-line variables will be added.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with line flow variables included.

    Notes
    -----
    - The sign convention follows the DC power flow equation:
      ``F_ij,t = b_ij * (θ_i,t - θ_j,t)``.
    - Line capacity limits (±pmax) are typically imposed in a separate
      constraint function (see :mod:`TransmissionLineConstraints`).
    """
    m.lines_flow = Var(m.LT, m.T, m.P, domain=Reals)    
    # Binary investment and operational decision variables
    m.lines_y = Var(m.LT, m.T, within=Binary)  # investment decision
    m.lines_x = Var(m.LT, m.T, within=Binary)  # cumulative existence
    return m
