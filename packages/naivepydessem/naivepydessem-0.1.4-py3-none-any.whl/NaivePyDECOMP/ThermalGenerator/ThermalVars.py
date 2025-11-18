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

    m.TG = Set(initialize=G)
    m.thermal_Gmin = Param(m.TG, initialize={g: data.units[g].Gmin for g in G})
    m.thermal_Gmax = Param(m.TG, initialize={g: data.units[g].Gmax for g in G})
    m.thermal_Cost = Param(m.TG, initialize={g: data.units[g].Cost for g in G})
    m.thermal_bars = {g: data.units[g].bar for g in G}

    return m


def thermal_add_variables_uc(m):
    """
    Declares decision variables for the thermal Unit Commitment (UC) model.

    Variables include continuous generation and deficit levels, 
    binary commitment/start/stop indicators, and optionally, 
    reserve and piecewise cost variables.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model where variables will be added.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with added decision variables:
        - Continuous:

          * **m.p[g, t]** : generation [MW].
          * **m.D[t]** : deficit [MW].

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> m = thermal_add_sets_and_params(m, data)
    >>> m = thermal_add_variables_uc(m, include_reserve=True, use_pwl=True)
    >>> m.p['UT1', 1].pprint()
    Variable p[UT1,1]
    Domain: NonNegativeReals

    """
    # Variáveis contínuas
    m.thermal_p = Var(m.TG, m.T, domain=NonNegativeReals)     # geração
    
    return m
