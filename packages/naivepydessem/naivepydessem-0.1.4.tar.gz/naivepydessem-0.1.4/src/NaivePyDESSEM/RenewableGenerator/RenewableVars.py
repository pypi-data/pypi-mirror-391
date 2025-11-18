"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Sets, Parameters, and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides initialization routines for renewable generation
within unit-commitment and dispatch models in Pyomo. It defines the sets,
parameters, and decision variables required to incorporate renewable
units (e.g., wind or solar) into short-term planning formulations.

Functions
---------
renewable_add_sets_and_params(m, data)
    Initialize sets and parameters for renewable units, including the
    renewable unit set and availability profiles ``gbar``.
renewable_add_variables(m)
    Declare renewable generation decision variables and, if not present,
    the deficit variable.

Notes
-----
- Availability profiles ``gbar`` are assumed to be exogenous, deterministic,
  and aligned with the planning horizon.
- The module is designed for integration with hydro and thermal
  subsystems, ensuring that common components such as time set ``m.T``,
  demand ``m.d``, and deficit penalty ``m.Cdef`` are not redefined if
  already present.
- Renewable generation is always bounded above by its availability; the
  actual capacity constraint should be added separately.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import (RangeSet, Set, Param, Var,
                           NonNegativeReals, Binary, Reals)

from pyomo.environ import ConcreteModel
from .RenewableDataTypes import RenewableData


def renewable_add_sets_and_params(m: ConcreteModel, 
                                  data: RenewableData) -> ConcreteModel:
    """
    Initialize sets and parameters for renewable units in a Pyomo model.

    Adds the renewable unit set, the renewable availability parameter
    ``renewable_gbar[r,t]``, and ensures that the time set ``m.T``, demand
    ``m.d``, and deficit penalty ``m.Cdef`` exist. If those components are
    already present in the model, they are not overwritten.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which renewable sets and parameters will be added.
    data : RenewableData
        Input data structure containing the planning horizon, demand profile,
        deficit penalty, and renewable units with their availability series.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with renewable sets and parameters attached.

    Notes
    -----
    - The set ``m.RU`` indexes renewable units.
    - The parameter ``m.renewable_gbar[r,t]`` stores the available generation
      (MW) of unit ``r`` at period ``t``.
    - The list ``gbar`` in each :class:`RenewableUnit` is assumed to be 0-based,
      so initialization uses ``t-1`` when accessing it.
    - If the model already contains ``m.T``, ``m.d``, or ``m.Cdef``, they are
      left unchanged to allow integration with thermal/hydro subsystems.
    """
    def _gbar_init(m, r, t):
        return data.units[r].gbar[t-1] 
    
    T = data.horizon
    R = list(data.units.keys())

    if not hasattr(m, "T"):
        m.T = RangeSet(1, T)

    if not hasattr(m, "d"):
        m.d = Param(m.T, initialize=data.demand, within=NonNegativeReals)
    
    if not hasattr(m, "Cdef"):
        m.Cdef = data.Cdef
        
    m.RU = Set(initialize=R)

    m.renewable_bars = {r: data.units[r].bar for r in R}

    m.renewable_gbar = Param(m.RU, m.T, initialize=_gbar_init, within=NonNegativeReals)

    return m



def renewable_add_variables(m: ConcreteModel) -> ConcreteModel:
    """
    Declare renewable generation and deficit decision variables.

    Adds the continuous non-negative variable ``m.renewable_gen[r,t]`` for
    renewable generation and, if not already present, the deficit variable
    ``m.D[t]``.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which renewable variables will be added.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with renewable generation and deficit variables.

    Notes
    -----
    - ``m.renewable_gen[r,t]`` represents the actual dispatched renewable
      generation (MW) for unit ``r`` at time ``t``.
    - ``m.D[t]`` represents unmet demand (MW) at time ``t``. It is created
      only if not already defined in the model, ensuring compatibility with
      other subsystems (thermal, hydro, batteries).
    - Both variables are continuous and non-negative.
    """
    
    m.renewable_gen = Var(m.RU, m.T, within=NonNegativeReals)
    return m

