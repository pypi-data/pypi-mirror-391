"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Connection Bar Data Structures

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines lightweight data classes for representing
connection bars (buses) in power system operation and expansion
models. Each connection bar encapsulates its electrical state,
demand profile, and configuration parameters. The aggregated
system-level data structure (`ConnectionBarData`) groups all
bars with the planning horizon and deficit penalty cost.

Classes
-------
ConnectionBarUnit
    Represents a single connection bar (bus) with demand profile,
    slack flag, and operational attributes.

ConnectionBarData
    Aggregates multiple connection bars with common parameters
    such as planning horizon, system-level demand reference, and
    deficit cost.

Notes
-----
- The demand profile of each bar is expressed as a deterministic
  time series aligned with the planning horizon.
- These structures serve as standardized inputs for Pyomo-based
  formulations of DECOMP, DESSEM, or the abstracted MDI model.
- Extend as needed to include locational data, voltage levels,
  or stochastic demand scenarios.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ConnectionBarUnit:
    """
    Data container for an electrical connection bar (bus).

    Parameters
    ----------
    name : str
        Unique identifier for the bar (e.g., ``'BAR_1'``).    
    slack : bool
        True if the bar is the system reference (angle fixed at 0 rad).
    Cdef : float, optional
        Penalty cost for unmet demand (R$/MWh). Default is ``500.0``.
    c_pmax: float, optional
        Max power of the deficit (MW)
    demand : dict of {str: list of float}
        Nested dictionary containing demand data per load level and time period.
        Example structure:
        ``{"Ponta": [500, 550, 600], "Fora": [300, 320, 350]}``

    Notes
    -----
    - The ``demand`` list length must equal the planning horizon.
    - The attribute ``slack`` is used to define the voltage angle reference
      in DC power flow formulations.
    - The fields ``c_op`` and ``c_inv`` are placeholders for compatibility
      with expansion models (MDI), though typically unused in operation models.
    """
    name: str
    slack: bool
    Cdef: float
    c_pmax: float
    demand: Dict[str, List[float]]


@dataclass
class ConnectionBarData:
    """
    System-wide data structure for connection bars.

    Parameters
    ----------
    horizon : int
        Number of planning periods.
    units : Dict[str, ConnectionBarUnit]
        Mapping of bar identifiers to their :class:`ConnectionBarUnit` instances.

    Notes
    -----
    - The attribute ``units`` aggregates all bars of the system.
    - ``Cdef`` is used to penalize deficit variables ``D[b,t]`` in the objective.
    - In hierarchical models, this class provides the bar-level data consumed
      by the module :mod:`ConnectionBarVariables`.
    """
    horizon: int
    units: Dict[str, ConnectionBarUnit]
