"""
Storage Subpackage
==================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
The **Storage** subpackage implements all the symbolic, data, and structural
components required to model the operation and expansion of **energy storage systems** within
the broader **MDI (Modular Decision Infrastructure)** optimization framework.

Description
-----------
This subpackage defines the complete representation of storage units, including
their parameters, decision variables, constraints, and cost functions, suitable
for Mixed-Integer Linear Programming (MILP) and Mixed-Integer Nonlinear Programming (MINLP)
formulations using **Pyomo**.

Modules
-------
StorageBuilder
    High-level routines for constructing complete storage models.
StorageDataTypes
    Data classes defining the structure and typing of storage unit data.
StorageEquations
    Symbolic expressions for cost and power balance aggregation.
StorageObjective
    Objective function for total storage cost minimization.
StorageVars
    Model variables, sets, and parameters declaration.

Structure Overview
------------------
The `Storage` subpackage provides modular integration of storage subsystems
into larger system models. It follows a builder pattern to maintain
clarity and extensibility.

Typical usage:

>>> from MDI.Storage import StorageData, StorageUnit, build_storage
>>> data = StorageData(...)
>>> model = build_storage(data, include_objective=True)

Exports
-------
This `__init__.py` file re-exports all relevant symbols to simplify
namespace access.  
Users may import either individual modules or the entire storage
subsystem directly via:

>>> from MDI.Storage import *

Notes
-----
- All modules are compatible with **Pyomo 6.x**.
- Energy and power units follow the SI convention (MWh, MW).
- Cost parameters are assumed to be in consistent monetary units.

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes, EELT7030/UFPR, 2023.
"""

from .StorageBuilder import *
from .StorageDataTypes import *
from .StorageEquations import *
from .StorageObjective import *
from .StorageVars import *
