"""
Storage Equations Module
========================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines **symbolic expressions** for energy storage subsystems,
used in the model composition phase to aggregate costs and power balances.
It provides reusable components for constructing higher-level formulations
(e.g., integrated generation–storage–transmission systems).

Description
-----------
Two main symbolic functions are defined:

1. **`add_storage_cost_expression()`**  
   Builds the total operational and investment cost expression of all
   storage units and appends it to a global cost array.

2. **`add_storage_balance_expression()`**  
   Builds the net energy balance expression (discharge minus charge)
   to represent the effective contribution of storage units to the system
   power balance in each time step and load level.

These expressions are not constraints by themselves, but **building blocks**
that can be embedded in multi-component optimization formulations.

Mathematical Formulation
------------------------
1. **Cost Expression**
\[
C_{storage} =
\sum_{s \in SU} \sum_{t \in T} \sum_{p \in P}
h_p \, c^{op}_s \, (P^{ch}_{s,t,p} + P^{dis}_{s,t,p})
+ \sum_{s \in SU} \sum_{t \in T}
c^{inv}_s \, x_{s,t}
\]

2. **Balance Expression**
\[
B_{storage}(t,p) =
\sum_{s \in SU} \eta_d \, P^{dis}_{s,t,p}
- \frac{1}{\eta_c} \, P^{ch}_{s,t,p}
\]

where:

| Symbol | Description |
|:--------|:------------|
| \(h_p\) | Duration of load level \(p\) (hours) |
| \(c^{op}_s\) | Operational cost per MWh |
| \(c^{inv}_s\) | Investment cost |
| \(P^{ch}_{s,t,p}\), \(P^{dis}_{s,t,p}\) | Charging/discharging power (MW) |
| \(\eta_c, \eta_d\) | Charging/discharging efficiencies |
| \(x_{s,t}\) | Binary existence variable |
| \(SU, T, P\) | Sets of storage units, time periods, and load levels |

Functions
---------
add_storage_cost_expression(m, cost_array)
    Appends the total storage cost expression to a given list of cost terms.

add_storage_balance_expression(m, t, p, balance_array)
    Appends the net storage power balance expression (discharge – charge)
    to a given list of balance terms.

Notes
-----
- The functions **do not create Pyomo constraints**; they only define symbolic
  expressions that can be aggregated later.
- Each expression is appended to an externally provided list (e.g. `cost_array`),
  allowing modular model assembly.
- The caller must ensure that all required model attributes exist before invocation.

References
----------
[1] CEPEL, *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C., *Introdução aos Sistemas de Energia Elétrica*,
    Lecture Notes, EELT7030/UFPR, 2023.

Module Dependencies
-------------------
- **Internal:** None  
- **External:** `pyomo.environ`, `typing`
"""

from typing import List, Any
from pyomo.environ import ConcreteModel, Expression


def add_storage_cost_expression(
    m: ConcreteModel,
    cost_array: List[Any]
) -> List[Any]:
    """
    Add the total cost expression of all storage units to the cost array.

    The expression combines operational and investment costs across all
    time periods and load levels, weighted by load duration.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing sets, parameters, and variables
        of the storage subsystem.
    cost_array : list of Any
        External list to which the resulting cost expression will be appended.

    Returns
    -------
    list of Any
        The updated list of cost expressions including the storage cost term.
    """
    required = [
        'SU', 'T', 'P',
        'storage_ch', 'storage_dis',
        'storage_c_op', 'storage_c_inv',
        'storage_y', 'storage_x', 'level_hours'
    ]

    if all(hasattr(m, attr) for attr in required):
        if m.parcel_investment:
            
            expr = sum(
                # Operational cost (proportional to energy moved)
                m.discounts[t] * m.level_hours[p] * m.storage_c_op[s] * (
                    m.storage_ch[s, t, p] + m.storage_dis[s, t, p]
                )
                for s in m.SU for t in m.T for p in m.P
            ) + sum(
                # Investment cost (proportional to existence)
                m. discounts[t] * m.storage_c_inv[s] * m.storage_x[s, t]
                for s in m.SU for t in m.T
            )
        else:
            expr = sum(
                # Operational cost (proportional to energy moved)
                m.discounts[t] * m.level_hours[p] * m.storage_c_op[s] * (
                    m.storage_ch[s, t, p] + m.storage_dis[s, t, p]
                )
                for s in m.SU for t in m.T for p in m.P
            ) + sum(
                # Investment cost (proportional to existence)
                m. discounts[t] * m.storage_c_inv[s] * m.storage_y[s, t]
                for s in m.SU for t in m.T
            )
        cost_array.append(expr)

    return cost_array


def add_storage_capacity_expression(
    m: ConcreteModel,
    t: Any,
    p: Any,
    capacity_array: List[Any]
) -> List[Any]:
    """
    Add the net storage capacity expression to the capacity array,
    considering only storage units that exist (x[s,t] = 1).

    The expression represents the net power contribution (discharge minus charge)
    weighted by the operational existence of the unit in the given period.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model instance containing storage sets, parameters, and variables.
    t : Any
        Time index.
    p : Any
        Load level index corresponding to the current balance term.
    capacity_array : list of Any
        External list to which the resulting expression will be appended.

    Returns
    -------
    list of Any
        Updated list of capacity expressions.
    """
    required = [
        'SU', 'T', 'P',
        'storage_Pdis_max', 'storage_x'
    ]

    if all(hasattr(m, attr) for attr in required):
        
        expr = sum(
            # Capacity available only if the storage unit exists in period t
            # since Pdis_max is in MWh/level, this must be MWh per level
            # this is the maximum eergy capacity that storage can deliver per level
            (m.storage_Pdis_max[s, p] / m.level_hours[p]) * m.storage_x[s, t]
            for s in m.SU
        )
        capacity_array.append(expr)

    return capacity_array


def add_storage_balance_expression(
    m: ConcreteModel,
    b: Any,
    t: Any,
    p: str,
    balance_array: List[Any]
) -> List[Any]:
    """
    Add the net storage balance expression to the balance array.

    The expression represents the net contribution of storage units
    to the system power balance in each time period and load level,
    considering both charge and discharge efficiencies.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance containing the relevant storage variables and parameters.
    b: Any
        Connection Bar Name
    t : Any
        Time index for which the balance expression is computed.
    p : str
        Load level index corresponding to the current balance term.
    balance_array : list of Any
        External list to which the resulting expression will be appended.

    Returns
    -------
    list of Any
        The updated list of balance expressions including the storage term.
    """
    required = [
        'SU', 'T', 'P', 'storage_bars',
        'storage_ch', 'storage_dis',
        'storage_eta_c', 'storage_eta_d'
    ]

    if all(hasattr(m, attr) for attr in required):
        temp_array: List = []
        for s in m.SU:
            bar = m.storage_bars[s]
            if bar == b:
                temp_array.append(m.storage_dis[s, t, p] - m.storage_ch[s, t, p])
        if len(temp_array) > 0:
            balance_array.append(sum(temp_array))
        
    return balance_array
