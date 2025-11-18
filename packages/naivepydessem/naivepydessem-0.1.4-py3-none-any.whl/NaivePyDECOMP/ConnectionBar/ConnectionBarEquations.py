"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Module: Connection Bar — Composite Balance Expression Builder

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides high-level expression utilities that construct
the nodal power balance for each connection bar (bus) in Pyomo-based
optimization models. It aggregates generation and flow contributions
from all subsystems — hydraulic, thermal, renewable, storage, and
transmission — and includes the deficit variable when present.

The resulting symbolic expressions can be used to assemble the
system-wide balance constraints in MW, ensuring dimensional and
physical consistency across all integrated subsystems.

Functions
---------
add_connection_bar_balance_expression(m, t, balance_array)
    Assemble the complete nodal balance expression at period ``t``
    by aggregating power injections and withdrawals from all
    subsystems connected to each bar.

Notes
-----
- This module acts as a bridge between subsystem formulations
  (hydro, thermal, renewable, storage, and transmission) and the
  connection-bar layer.
- All terms are represented in **MW**.
- The function is modular: if any subsystem is absent, its
  contribution is automatically skipped.
- The aggregated balance for each bar includes:
    * Generation terms (hydro, thermal, renewable)
    * Storage net injection (discharge − charge)
    * Transmission inflow/outflow
    * Deficit variable (if defined)

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023  
[2] Unsihuay Vila, C. (2023). *Introdução aos Sistemas de Energia Elétrica*.  
    Lecture Notes, EELT7030/UFPR.
"""

from typing import List, Dict, Any
from pyomo.environ import ConcreteModel

from NaivePyDESSEM.ConnectionBar.ConnectionBarEquations import (
    add_connection_bar_cost_expression
)

from NaivePyDECOMP.HydraulicGenerator.HydraulicEquations import add_hydraulic_balance_expression
from NaivePyDECOMP.ThermalGenerator.ThermalEquations import add_thermal_balance_expression
from NaivePyDECOMP.RenewableGenerator.RenewableEquations import add_renewable_balance_expression
from NaivePyDECOMP.Storage.StorageEquations import add_storage_balance_expression
from NaivePyDECOMP.TransmissionLine.TransmissionLineEquations import add_transmission_line_balance_expression


def add_connection_bar_balance_expression(
    m: ConcreteModel,
    t: Any,
    balance_array: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    Assemble the complete nodal power balance expression by bar for period ``t``.

    This function aggregates all energy contributions associated with each
    connection bar, combining subsystem injections (generation and storage)
    and withdrawals (demand and deficit). The resulting symbolic expressions
    can be integrated into the global power balance constraints or stored for
    later use in decomposition-based algorithms.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing the subsystem components and decision variables.
        Expected elements include:
            - ``HG`` : hydro unit set
            - ``TG`` : thermal unit set
            - ``RU`` : renewable unit set
            - ``SU`` : storage unit set
            - ``LT`` : transmission line set
            - ``D[b,t]`` : deficit variable (MW)
    t : int
        Time index for which the balance expressions are evaluated.
    balance_array : dict[str, list[expression]]
        Dictionary mapping each bar to a list of symbolic expressions that
        contribute to its power balance.

    Returns
    -------
    dict[str, list[expression]]
        Updated dictionary including all subsystem contributions and the
        deficit term for each connection bar at time ``t``.

    Notes
    -----
    - The final nodal balance for bar ``b`` at time ``t`` has the general form:
        ``Σ_generation + Σ_storage + Σ_transmission + D[b,t] = Demand[b,t]``
    - The function ensures that only existing subsystems (declared in ``m``)
      are considered, avoiding errors in partial model configurations.
    - All terms are expressed in MW and consistent with the global system base.

    Examples
    --------
    >>> balance_terms = {}
    >>> add_connection_bar_balance_expression(model, t=3, balance_array=balance_terms)
    >>> for bar, expr in balance_terms.items():
    ...     model.Balance.add(sum(expr) == model.d[bar, 3])

    References
    ----------
    [1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023  
    [2] Unsihuay Vila, C. (2023). *Introdução aos Sistemas de Energia Elétrica*.  
        Lecture Notes, EELT7030/UFPR.
    """
    temp_balance_array: Dict = {}
    add_hydraulic_balance_expression(m, t, temp_balance_array)
    add_thermal_balance_expression(m, t, temp_balance_array)
    add_renewable_balance_expression(m, t, temp_balance_array)
    add_storage_balance_expression(m, t, temp_balance_array)
    add_transmission_line_balance_expression(m, t, temp_balance_array)

    for bar in temp_balance_array:
        balance_array[bar] = sum(temp_balance_array[bar]) + m.D[bar, t]
    return balance_array
