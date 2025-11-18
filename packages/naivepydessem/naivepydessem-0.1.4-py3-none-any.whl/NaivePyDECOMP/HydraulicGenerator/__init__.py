"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Hydraulic Generation Modeling (HydraulicGenerator)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
The ``HydraulicGenerator`` package provides a modular framework for modeling
hydropower systems in Pyomo-based dispatch and unit commitment models. It
includes flexible hydropower production functions (FPH), reservoir balance
constraints, and terminal storage requirements.

Submodules
----------
HydraulicDataTypes
    Dataclasses defining hydropower unit and system-wide data.
HydraulicVars
    Initialization routines for Pyomo sets, parameters, and variables.
HydraulicConstraints
    Constraint builders (generation, reservoir balance, SoC limits, targets).
HydraulicObjectives
    Objective function definitions for hydro-only models.
HydraulicGeneratorBuilder
    High-level routines to assemble complete hydropower dispatch models.
    Simple FPH based on constant productivity.
SimplifiedConstantProductivityFPH
    Didactic constant productivity model (simplified).

Notes
-----
- Multiple FPH modes are supported (constant, simplified, specific, exact).
- Reservoir mass balance constraints ensure intertemporal consistency.
- Designed for interoperability with Thermal, Renewable, and Storage packages
  in hybrid models.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""
from .HydraulicGeneratorBuilder import *
from .HydraulicDataTypes import *
from .HydraulicEquations import *
from .HydraulicGeneratorBuilder import *
from .HydraulicObjectives import *
from .SimplifiedConstantProductivityFPH import *
