"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Renewable Generation Modeling (RenewableGenerator)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
The **RenewableGenerator** package provides a modular framework for modeling
renewable energy sources (e.g., wind and solar) in Pyomo-based dispatch and
unit commitment models. It includes standardized data types, sets, parameters,
variables, constraints, objectives, and builder functions.

Submodules
----------
RenewableDataTypes
    Dataclasses defining renewable units (e.g., expected generation profiles).
RenewableVars
    Initialization routines for Pyomo sets, parameters, and variables.
RenewableConstraints
    Constraint builders enforcing availability limits and system balance.
RenewableObjectives
    Objective function definitions for renewable-only systems.
RenewableBuilder
    High-level routines to assemble complete renewable generation models.

Notes
-----
- The renewable availability profiles (**gbar**) are treated as exogenous,
  typically coming from forecasts.
- The package is interoperable with the Hydro, Thermal, and Storage packages,
  enabling hybrid model construction.
- Consistent naming and structure ensure clarity and maintainability across
  subsystems.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""
from .RenewableGeneratorBuilder import *
from .RenewableDataTypes import *
from .RenewableEquations import *
from .RenewableConstraints import *
from .RenewableObjectives import *
from .RenewableVars import *