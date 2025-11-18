"""
Storage Variables and Parameters Module
=======================================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines all **sets, parameters, and decision variables**
related to the **energy storage subsystem** of the MDI optimization framework.
It provides the symbolic foundation required by the storage constraints
and objective function.

Description
-----------
Two main functions are implemented:

1. **`storage_add_sets_and_params(m, data)`**  
   Initializes all Pyomo sets and parameters related to the storage units,
   including physical limits, efficiencies, operational costs, and time structure.

2. **`storage_add_variables(m)`**  
   Declares the decision variables for charging, discharging,
   energy state, and investment decisions.

The storage formulation supports a **multi-patamar (load level)** representation
and can be embedded seamlessly within larger optimization systems
that couple generation, transmission, and storage components.

Mathematical Overview
---------------------
**Continuous variables**
\[
\begin{align}
E_{s,t,p} &\ge 0 \quad &\text{(stored energy)} \\
P^{ch}_{s,t,p} &\ge 0 \quad &\text{(charging power)} \\
P^{dis}_{s,t,p} &\ge 0 \quad &\text{(discharging power)}
\end{align}
\]

**Binary variables**
\[
\begin{align}
x_{s,t} &\in \{0,1\} \quad &\text{(existence of unit)} \\
y_{s,t} &\in \{0,1\} \quad &\text{(investment decision)}
\end{align}
\]

Parameters are defined for:
- Energy bounds \(E^{min}, E^{max}, E^{ini}\)
- Power limits \(P^{ch,max}, P^{dis,max}\)
- Efficiencies \(\eta_c, \eta_d\)
- Costs \(c_{op}, c_{inv}\)
- State \(x_{0}\)
- Duration of time step \(\Delta t\)

Functions
---------
storage_add_sets_and_params(m, data)
    Define the sets and parameters related to the storage subsystem.

storage_add_variables(m)
    Define the decision variables associated with energy, power, and investment.

Notes
-----
- The function automatically initializes missing time and patamar sets (`m.T`, `m.P`)
  when they are not yet defined in the parent model.
- The formulation is fully compatible with a mixed-integer linear structure (MILP).
- The energy is represented in MWh, power in MW, and costs in monetary units.

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,
    EELT7030/UFPR, 2023.

Module Dependencies
-------------------
- **Internal:** ``StorageDataTypes``  
- **External:** ``pyomo.environ`` (RangeSet, Set, Param, Var, NonNegativeReals, Binary, ConcreteModel)
"""

from pyomo.environ import (
    RangeSet, Set, Param, Var, NonNegativeReals, Binary, ConcreteModel
)
from .StorageDataTypes import StorageData


def storage_add_sets_and_params(m: ConcreteModel,
                                data: StorageData) -> ConcreteModel:
    """
    Define the sets and parameters for the storage subsystem.

    Initializes all symbolic structures needed for the storage model,
    including time horizon, load levels, physical parameters, and
    investment-related costs.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance to which sets and parameters will be added.
    data : StorageData
        Structured data object containing the full specification of
        the storage units and demand profiles.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The model instance with all sets and parameters defined.
    """
    # Time horizon and basic sets
    T = data.horizon
    U = list(data.units.keys())

    # Time and patamar sets
    if not hasattr(m, "T"):
        m.T = RangeSet(1, T)

    # discounts
    if not hasattr(m, 'discounts'):
      m.discounts = Param(
          m.T,
          initialize={t: 1 / ((1 + m.interest_rate) ** (t - 1)) for t in m.T},
          within=NonNegativeReals
      )

    # Storage unit set
    m.SU = Set(initialize=U)

    # Scalar parameters
    if not hasattr(m, "storage_delta_t"):
        m.storage_delta_t = Param(initialize=data.delta_t)

    # Per-unit parameters
    m.storage_Emin = Param(m.SU, initialize={u: data.units[u].Emin for u in U})
    m.storage_Emax = Param(m.SU, initialize={u: data.units[u].Emax for u in U})
    m.storage_Eini = Param(m.SU, initialize={u: data.units[u].Eini for u in U})
    m.storage_Pch_max = Param(m.SU, m.P, initialize={(u, p): data.units[u].Pch_max for u in U for p in m.P})
    m.storage_Pdis_max = Param(m.SU, m.P, initialize={(u, p): data.units[u].Pdis_max for u in U for p in m.P})
    m.storage_eta_c = Param(m.SU, initialize={u: data.units[u].eta_c for u in U})
    m.storage_eta_d = Param(m.SU, initialize={u: data.units[u].eta_d for u in U})
    m.storage_M = {u: data.units[u].Emax for u in U}

    # Cost and state parameters
    m.storage_c_inv = Param(m.SU, initialize={u: data.units[u].c_inv for u in U})
    m.storage_c_op = Param(m.SU, initialize={u: data.units[u].c_op for u in U})
    m.storage_state = Param(m.SU, initialize={u: data.units[u].state for u in U})
    m.storage_bars = {u: data.units[u].bar for u in U}

    return m


def storage_add_variables(m: ConcreteModel) -> ConcreteModel:
    """
    Define the decision variables for the storage subsystem.

    Includes continuous and binary variables representing:
    - Energy stored
    - Charging/discharging power
    - Construction and operational existence decisions

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance where variables will be defined.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The model instance with all storage-related variables declared.
    """
    # Energy and power variables
    m.storage_E = Var(m.SU, m.T, m.P, within=NonNegativeReals)
    m.storage_ch = Var(m.SU, m.T, m.P, within=NonNegativeReals)
    m.storage_dis = Var(m.SU, m.T, m.P, within=NonNegativeReals)
    m.storage_cap = Var(m.SU, m.T, m.P, within=NonNegativeReals)
    m.storage_mode = Var(m.SU, m.T, m.P, domain=Binary)

    # Investment and operational binary variables
    m.storage_y = Var(m.SU, m.T, within=Binary)  # Construction decision
    m.storage_x = Var(m.SU, m.T, within=Binary)  # Operational existence

    return m
