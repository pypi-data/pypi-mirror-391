"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Thermal Generation Modeling (ThermalGenerator)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
The **ThermalGenerator** package provides a modular framework for modeling
thermal generation units in Pyomo-based unit commitment and dispatch models.
It includes data structures, sets, parameters, variables, constraints,
objectives, and builder functions for both quadratic (MIQP) and piecewise-linear
(MILP) cost formulations.

Submodules
----------
ThermalDataTypes
    Dataclasses defining thermal unit parameters and system-wide data.
ThermalVars
    Initialization routines for Pyomo sets, parameters, and variables.
ThermalConstraints
    Constraint builders (balance, capacity, reserve, ramping, min up/down).
ThermalObjectives
    Objective function definitions (quadratic and piecewise-linear).
ThermalPiecewiseCost
    Utilities for building piecewise-linear cost functions.
ThermalBuilder
    High-level routines to assemble complete thermal generation models.

Notes
-----
- Supports MIQP and MILP formulations, enabling flexibility in solver choice.
- Reserve, emissions, and startup/shutdown costs can be included as needed.
- Designed for interoperability with Hydro, Renewable, and Storage packages
  to support hybrid hydrothermal-renewable models.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""
from .ThermalConstraints import *
from .ThermalDataTypes import *
from .ThermalEquations import *
from .ThermalGeneratorBuilder import *
from .ThermalObjectives import *
from .ThermalPieceWise import *
from .ThermalVars import *