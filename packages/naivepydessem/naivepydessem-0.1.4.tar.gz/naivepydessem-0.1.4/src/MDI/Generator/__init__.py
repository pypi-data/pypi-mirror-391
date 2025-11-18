"""
Generator Subpackage
====================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
The **Generator** subpackage provides a complete and modular implementation of
**dispatchable generation units** within the MDI (Modular Decision Infrastructure)
framework, forming the core component of the operation and expansion
planning model.

Description
-----------
This subpackage defines all necessary components to represent thermal and
dispatchable generation systems in **Pyomo**, including data typing, variables,
constraints, and objectives. It supports integration with storage and other
energy technologies under a unified optimization environment.

Modules
-------
GeneratorBuilder
    High-level routines for constructing the generator subsystem model.
GeneratorDataTypes
    Data classes describing generator unit parameters and data structures.
GeneratorEquations
    Symbolic expressions for generator cost and balance aggregation.
GeneratorObjectives
    Objective function for total generation cost minimization.
GeneratorVars
    Sets, parameters, and decision variables declaration.

Structure Overview
------------------
The `Generator` subpackage follows a modular and pedagogical architecture,
allowing incremental assembly and analysis of generation models.

Example
-------
>>> from MDI.Generator import GeneratorData, GeneratorUnit, build_generators
>>> data = GeneratorData(...)
>>> model = build_generators(data, include_objective=True)

Exports
-------
This `__init__.py` file re-exports all relevant symbols to simplify
namespace imports.  
Modules can be accessed individually or as a unified subsystem:

>>> from MDI.Generator import *

Notes
-----
- Each component of the subpackage is fully compatible with **Pyomo 6.x**.
- Generation costs are modeled through both operational and investment terms.
- Units follow the SI convention (MW for power, monetary units for cost).
- The implementation is pedagogically aligned with the MDI methodology
  and CEPEL’s DESSEM conceptual framework.

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes, EELT7030/UFPR, 2023.
"""

from .GeneratorBuilder import *
from .GeneratorDataTypes import *
from .GeneratorEquations import *
from .GeneratorObjectives import *
from .GeneratorVars import *
