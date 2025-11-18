"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Energy Storage Modeling (Storage)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
The **Storage** package provides a modular framework for incorporating
battery energy storage systems (BESS) into Pyomo-based dispatch and unit
commitment models. It defines the necessary data structures, sets,
parameters, variables, constraints, objectives, and builder functions
to assemble storage-only or hybrid optimization models.

Submodules
----------
StorageDataTypes
    Dataclasses for storage units and system-level configuration.
StorageVars
    Initialization of Pyomo sets, parameters, and variables.
StorageConstraints
    Constraint builders (SoC balance, bounds, power limits, etc.).
StorageObjectives
    Objective function definitions for storage-only models.
StorageBuilder
    High-level routines to assemble complete storage models.

Notes
-----
- The package is designed to be interoperable with the Hydro, Thermal,
  and Renewable packages, enabling the construction of hybrid models.
- Naming conventions are consistent across subsystems for clarity and
  maintainability.
- Extensions (e.g., cycling cost, degradation models) can be added
  within this package without altering the external interface.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""
from .StorageBuilder import *
from .StorageDataTypes import *
from .StorageDataTypes import *
from .StorageEquations import *
from .StorageObjective import *
from .StorageVars import *
