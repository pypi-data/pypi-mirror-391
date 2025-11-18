

"""
Generator Data Types Module
===========================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines the fundamental data structures used to represent
generator-related parameters within the MDI framework. It provides
strongly typed and structured interfaces for input parsing, parameter
validation, and model population using the Pyomo environment.

Description
-----------
The dataclasses defined here encapsulate both unit-level and
system-level information required to formulate the generation expansion
and dispatch problem. They are designed for clarity, immutability,
and direct compatibility with YAML and JSON data sources.

- **GeneratorUnit** represents the technical and economic attributes
  of a single dispatchable generating unit.

- **GeneratorData** aggregates all generator units, demand data,
  time discretization, and system-level configuration parameters
  required to construct the generator submodel.

Classes
-------
GeneratorUnit
    Defines a single generation unit, including operational state,
    investment cost, and technical limits.

GeneratorData
    Defines a complete data structure for the generator subsystem,
    including time horizon, demand, load levels, and the collection of
    generation units.

Notes
-----
- These dataclasses are typically populated by the YAMLLoader module
  before model construction.
- Attribute names are intentionally consistent with the Pyomo
  model variable and parameter nomenclature.
- The design supports type checking and explicit serialization
  to facilitate reproducibility in energy system research.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

Module Dependencies
-------------------
- **Internal:** None (independent data layer)
- **External:** ``dataclasses``, ``typing``
"""

from dataclasses import dataclass
from typing import Dict, Union, List


@dataclass
class GeneratorUnit:
    """
    Representation of a single dispatchable generation unit.

    This dataclass stores the economic and technical parameters
    of each generator used in the optimization model, such as
    operational state, variable and fixed costs, and rated capacity.

    Parameters
    ----------
    name : str
        Unique identifier of the generation unit.
    state : int
        Initial operational state of the unit (1 if already built, 0 otherwise).
    c_op : float
        Variable operational cost (e.g., fuel or maintenance) in R$/MWh.
    c_inv : float
        Investment cost associated with capacity expansion in R$
    p_max : float
        Maximum generation capacity (MW) of the unit.
    include_cap: whether to include in capacity restriction or not

    Notes
    -----
    - ``state`` is used to define the initial operational availability
      within the planning horizon.
    - These attributes are directly mapped into Pyomo parameters
      via the generator builder module.
    """
    name: str
    bar: str
    state: int
    c_op: float
    c_inv: float
    p_max: float
    include_cap: bool


@dataclass
class GeneratorData:
    """
    Aggregated dataset for the generator subsystem.

    Encapsulates all time-related and unit-level data required to
    build the generator component of the MDI model, including
    demand series, temporal discretization, and technology set.

    Parameters
    ----------
    horizon : int
        Number of time periods in the planning horizon.
    level_hours : dict of {str: float}
        Mapping between demand levels (e.g., 'Ponta', 'Fora') and their
        respective duration in hours.
    units : dict of {str: GeneratorUnit}
        Dictionary mapping unit identifiers to their respective
        ``GeneratorUnit`` dataclass instances.

    Notes
    -----
    - This structure is typically created by the YAMLLoader and passed
      to ``GeneratorBuilder`` for model initialization.
    - The data are designed to be serializable and interoperable
      with other modules of the MDI framework.
    """
    horizon: int
    units: Dict[str, GeneratorUnit]
