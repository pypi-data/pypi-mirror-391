"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Connection Bar — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines initialization routines for connection bars (nodes)
within power system operation and expansion models in Pyomo. It provides
the sets, parameters, and decision variables associated with network
buses, including demand, deficit, and phase angles for DC power flow
formulations.

Functions
---------
connection_bar_add_sets_and_params(m, data)
    Initialize sets and parameters for connection bars, including
    demand profiles and bar-specific attributes (state, slack status, etc.).

connection_bar_add_variables(m)
    Declare bar-level decision variables: deficit (unserved demand) and
    phase angle (for DC models).

Notes
-----
- Designed for integration with hydrothermal and renewable subsystems.
- The time set ``m.T`` is assumed global and will only be created if
  not already defined.
- Each bar (bus) has a time-varying demand ``demand[b,t]`` and, optionally,
  a deficit variable ``D[b,t]`` penalized by ``m.Cdef`` in the objective.
- The slack bar is identified by ``bar.slack = True`` and its phase angle
  is fixed at zero.

References
----------
[1] CEPEL, DECOMP / DESSEM Methodology Manuals, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import (RangeSet, Set, Param, Var,
                           Reals, NonNegativeReals, ConcreteModel)


def connection_bar_add_sets_and_params(m: ConcreteModel, data) -> ConcreteModel:
    """
    Initialize sets and parameters for connection bars.

    Adds the connection bar set ``m.BAR``, the demand parameter
    ``m.demand[b,t]``, and the deficit penalty ``m.Cdef``. It also records
    which bars are slack (reference) for the DC model.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which the bar sets and parameters will be added.
    data : ConnectionBarData
        Data structure containing:
        - horizon (int): number of time periods.
        - demand (dict[str, list[float]]): demand time series per bar.
        - Cdef (float): deficit cost.
        - units (dict[str, ConnectionBar]): each bar object has
          attributes ``state``, ``slack``, ``demand``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model, augmented with bar-related sets and parameters.

    Notes
    -----
    - If the model already defines ``m.T`` or ``m.Cdef``, they are not overwritten.
    - The time set is defined as ``RangeSet(1, horizon)`` if absent.
    - Each bar’s demand is initialized using its ``demand`` array
      with 0-based indexing, so ``t-1`` is used during initialization.
    """
    def _demand_init(m, b, t):
        return data.units[b].demand[t - 1]

    # Ensure global time set exists
    if not hasattr(m, "T"):
        m.T = RangeSet(1, data.horizon)
        
    # Create bar set
    bars = list(data.units.keys())
    m.CB = Set(initialize=bars)

    # Demand per bar and time
    m.d = Param(m.CB, m.T, initialize=_demand_init, within=NonNegativeReals) # demand
    slack_bars = [b for b, u in data.units.items() if getattr(u, "slack", False)]
    m.SB = Set(initialize=slack_bars)
    m.Cdef = {b: data.units[b].Cdef for b in bars}
    m.unique_bar = True if len(bars) == 1 else False

    return m


def connection_bar_add_variables(m: ConcreteModel) -> ConcreteModel:
    """
    Declare decision variables associated with connection bars.

    Adds the following variables:
    - ``m.D[b,t]`` : non-negative deficit (unserved demand) per bar and time.
    - ``m.theta[b,t]`` : phase angle of the bus voltage (radians), continuous real.

    For DC power flow models, the reference (slack) bar has its angle fixed
    to zero through a constraint or by setting bounds.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which bar variables will be added.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with bar variables included.

    Notes
    -----
    - ``m.D[b,t]`` is created even if a global deficit variable exists; each
      bar has its own local deficit component.
    - The variable ``m.theta[b]`` represents the voltage angle used in
      linearized DC power flow equations.
    - The fixing of the slack bar angle (``theta = 0``) should be performed
      externally by a constraint after this routine.
    """
    m.D = Var(m.CB, m.T, domain=NonNegativeReals) # deficit
    if not m.unique_bar:
      m.theta = Var(m.CB, m.T, domain=Reals)
    return m
