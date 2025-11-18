"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Generation Data Structures

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module defines lightweight data classes for representing renewable
generation units (e.g., wind and solar) and their aggregated system-level
data. These structures serve as standardized inputs for optimization
models of unit commitment and dispatch in Pyomo.

Classes
-------
RenewableUnit
    Encapsulates the characteristics of a single renewable unit, including
    identifier and time-varying availability profile.
RenewableData
    Aggregates renewable units with system-wide parameters such as horizon,
    demand profile, and deficit penalty cost.

Notes
-----
- The exogenous availability profiles are represented as deterministic
  time series (MW) and aligned with the planning horizon.
- The classes are designed for seamless integration into Pyomo-based
  optimization formulations, ensuring consistency with similar structures
  for thermal and hydro subsystems.
- Extend these classes as needed to incorporate stochastic scenarios or
  uncertainty modeling for renewable availability.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RenewableUnit:
    """
    Data container for a renewable generating unit (e.g., wind or solar).

    Parameters
    ----------
    name : str
        Unique identifier for the renewable unit (e.g., ``'PV1'``, ``'WTG3'``).
    bar: str
        Connection bar of the Unit (defaults to BAR_1)
    gbar : List[float]
        Time series of expected available generation (MW) for each
        planning period. Typically derived from forecasts or
        historical profiles.

    Notes
    -----
    - The list ``gbar`` is assumed to have length equal to the system
      planning horizon. Access is usually aligned as ``gbar[t-1]`` for
      period ``t`` (1-based index).
    - Variability and uncertainty of renewables are represented through
      this exogenous availability profile rather than decision variables.
    """
    name: str
    bar: str
    gbar: List[float]


@dataclass
class RenewableData:
    """
    System-wide data structure for renewable generation modeling.

    Parameters
    ----------
    horizon : int
        Number of periods in the planning horizon.
    units : Dict[str, RenewableUnit]
        Dictionary mapping unit identifiers to their respective
        :class:`RenewableUnit` objects.

    Notes
    -----
    - ``units`` can include heterogeneous renewable technologies such as
      wind turbines, photovoltaic plants, or run-of-river hydro, provided
      they are represented by :class:`RenewableUnit`.
    - ``Cdef`` defines the cost of deficit used in the optimization
      objective when renewables are integrated into dispatch problems.
    - This class is typically consumed by Pyomo-based optimization models
      for renewable-aware unit commitment or economic dispatch.
    """
    horizon: int
    units: Dict[str, RenewableUnit]
