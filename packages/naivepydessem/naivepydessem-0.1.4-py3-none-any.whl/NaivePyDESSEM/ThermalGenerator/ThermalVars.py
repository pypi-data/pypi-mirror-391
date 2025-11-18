"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Sets, Parameters and Variables

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides the Pyomo set/parameter declarations and variable
definitions for thermal unit commitment (UC) models. It is intended to
be combined with constraint and objective builder modules.

Features
--------
- Time horizon (T) and thermal unit set (G)
- Demand profile d[t] and deficit penalty Cdef
- Unit-level parameters:
    * Pmin, Pmax  : capacity bounds
    * RU, RD      : ramp-up / ramp-down limits
    * a, b, c     : cost coefficients for MIQP (a * u + b * p + c * p²)
    * SC          : start-up (hot) cost
    * t_up, t_dn  : minimum up/down times
    * u0, p0      : initial commitment state and output
- Optional system-wide parameters:
    * Rreq[t]     : spinning reserve requirement
    * gamma[g]    : emissions factor
    * CO2Cap      : global emission/fuel cap
- Optional piecewise data:
    * pw_breaks[g], pw_costs[g] : piecewise linear cost curve points

Variables
---------
- p[g,t] : generation (MW)
- D[t]   : deficit (MW)
- r[g,t] : reserve (MW, optional)
- Cvar[g,t] : variable cost in PWL formulations (optional)
- u[g,t] : on/off state (binary)
- y[g,t] : start-up indicator (binary)
- w[g,t] : shut-down indicator (binary)

Usage
-----
Call *thermal_add_sets_and_params(m, data)* to populate a Pyomo model with
sets and parameters from a ThermalData object.

Call *thermal_add_variables_uc(m, include_reserve=True/False, use_pwl=True/False)*
to attach decision variables for UC formulations (MIQP or MILP-PWL).

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import (ConcreteModel, RangeSet, Set, Param, Var,
                           NonNegativeReals, Binary, Reals)
from .ThermalDataTypes import ThermalData

def thermal_add_sets_and_params(m: ConcreteModel, 
                                data: ThermalData) -> ConcreteModel:
    """
    Initializes sets and parameters for the thermal Unit Commitment (UC) model.

    This function maps unit-level data (technical parameters, costs, 
    initial conditions, optional reserve and emissions information, 
    and piecewise cost segments) into Pyomo sets and parameters.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to be enriched with sets and parameters.
    data : ThermalData
        Data container with attributes:
        
        - horizon : int

            Number of time periods.

        - demand : dict

            Demand profile indexed by time.

        - Cdef : float

            Cost of deficit ($/MWh).

        - units : dict

            Dictionary keyed by unit id, each with attributes
            Pmin, Pmax, RU, RD, a, b, c, SC, t_up, t_down, u0, p0,
            gamma (optional), pw_breaks (optional), pw_costs (optional).

        - Rreq : dict, optional

            Reserve requirement per period.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with sets **m.T, m.TG** and all unit/system parameters.

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> m = thermal_add_sets_and_params(m, data)
    >>> list(m.TG)
    ['UT1', 'UT2', 'UT3']
    >>> m.d[1]
    500.0
    """
    T = data.horizon
    G = list(data.units.keys())

    if not hasattr(m, "T"):
        m.T = RangeSet(1, T)

    if not hasattr(m, "d"):
        m.d = Param(m.T, initialize=data.demand, within=NonNegativeReals)
    
    if not hasattr(m, "Cdef"):
        m.Cdef = data.Cdef

    m.TG = Set(initialize=G)
    m.has_history = data.has_history
    m.thermal_Pmin = Param(m.TG, initialize={g: data.units[g].Pmin for g in G})
    m.thermal_Pmax = Param(m.TG, initialize={g: data.units[g].Pmax for g in G})
    m.thermal_RU = Param(m.TG, initialize={g: data.units[g].RU for g in G})
    m.thermal_RD = Param(m.TG, initialize={g: data.units[g].RD for g in G})
    m.thermal_a = Param(m.TG, initialize={g: data.units[g].a for g in G})
    m.thermal_b = Param(m.TG, initialize={g: data.units[g].b for g in G})
    m.thermal_c = Param(m.TG, initialize={g: data.units[g].c for g in G})
    m.thermal_SC = Param(m.TG, initialize={g: data.units[g].SC for g in G})
    m.thermal_t_up = Param(m.TG, initialize={g: data.units[g].t_up for g in G})
    m.thermal_t_dn = Param(m.TG, initialize={g: data.units[g].t_down for g in G})
    m.thermal_u0 = Param(m.TG, initialize={g: data.units[g].u0 for g in G})
    m.thermal_p0 = Param(m.TG, initialize={g: data.units[g].p0 for g in G})
    m.thermal_init_status = Param(m.TG, initialize={g: data.units[g].init_status_h for g in G})
    m.thermal_bars = {g: data.units[g].bar for g in G}
    
    if data.Rreq is not None:
        m.thermal_Rreq = Param(m.T, initialize=data.Rreq, within=NonNegativeReals)

    m.thermal_pw_breaks = {g: data.units[g].pw_breaks for g in G}
    m.thermal_pw_costs = {g: data.units[g].pw_costs for g in G}

    return m


def thermal_add_variables_uc(m, include_reserve: bool = False, use_pwl: bool = False):
    """
    Declares decision variables for the thermal Unit Commitment (UC) model.

    Variables include continuous generation and deficit levels, 
    binary commitment/start/stop indicators, and optionally, 
    reserve and piecewise cost variables.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model where variables will be added.
    include_reserve : bool, optional
        If True, reserve variables **m.r[g, t]** are created (default False).
    use_pwl : bool, optional
        If True, piecewise linear cost variables **m.Cvar[g, t]** 
        are created (default False).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with added decision variables:
        - Continuous:

          * **m.p[g, t]** : generation [MW].
          * **m.D[t]** : deficit [MW].
          * **m.r[g, t]** : reserve [MW], optional.
          * **m.Cvar[g, t]** : piecewise cost variable, optional.

        - Binary:

          * **m.u[g, t]** : commitment (on/off).
          * **m.y[g, t]** : startup indicator.
          * **m.w[g, t]** : shutdown indicator.

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> m = thermal_add_sets_and_params(m, data)
    >>> m = thermal_add_variables_uc(m, include_reserve=True, use_pwl=True)
    >>> m.p['UT1', 1].pprint()
    Variable p[UT1,1]
    Domain: NonNegativeReals

    Notes
    -----
    **Reserve modeling (**include_reserve=True**)**

    - **Advantages**: Captures spinning reserve obligations; ensures reliability
      under contingencies; critical for adequacy/security studies.
    - **Trade-offs**: Increases model size with additional variables
      **m.r[g, t]** and constraints; may slow down MILP/MIQP solution.
    - **Guidance**: Use if reserve margins are central to the study; omit in
      purely economic dispatch tests for simplicity.

    **Piecewise costs (**use_pwl=True**)**4
    
    - **Advantages**: Converts quadratic costs to MILP form; exploits strong
      LP relaxations; often faster and more scalable on large systems.
    - **Trade-offs**: Approximation error unless sufficient breakpoints are
      used; adds SOS2 or convex-combination variables, increasing model size.
    - **Guidance**: Use when quadratic costs cannot be handled efficiently
      by the chosen solver, or when MILP-only solvers are required.
    """
    # Variáveis contínuas
    m.thermal_p = Var(m.TG, m.T, domain=NonNegativeReals)     # geração
    
    if include_reserve:
        m.thermal_r = Var(m.TG, m.T, domain=NonNegativeReals)  # reserva

    if use_pwl:
        # custo variável PWL por (g,t)
        m.thermal_Cvar = Var(m.TG, m.T, domain=NonNegativeReals)

    # Binárias
    m.thermal_u = Var(m.TG, m.T, domain=Binary)  # ligada
    m.thermal_y = Var(m.TG, m.T, domain=Binary)  # start
    m.thermal_w = Var(m.TG, m.T, domain=Binary)  # stop
    return m
