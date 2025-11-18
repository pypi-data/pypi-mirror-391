"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Module: Model Component Validators

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides a set of utility functions to verify whether a given Pyomo
`ConcreteModel` contains the essential variables, parameters, and sets required
for each subsystem in an energy dispatch problem.

The validation is modular and lightweight, designed to support the dynamic
assembly of hybrid dispatch models comprising:
- Hydropower units
- Thermal generation units
- Renewable generation sources
- Energy storage systems

These functions are typically used to determine the feasibility of operations
such as cost extraction, result formatting, or diagnostics on a per-subsystem basis.

Functions
---------
- has_hydro_model(model): Checks presence of hydropower-related variables.
- has_thermal_model(model): Checks presence of thermal generation variables.
- has_renewable_model(model): Checks presence of renewable generation variables.
- has_storage_model(model): Checks presence of storage system variables.

Usage Example
-------------
>>> if has_thermal_model(m):
>>>     print("Thermal model components detected.")

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConcreteModel
from NaivePyDESSEM.ModelCheck import (
    has_hydro_model, 
    has_renewable_model, 
    has_storage_model,
    has_connection_bar_model,
    has_transmission_line_model
)


def has_thermal_model(model: ConcreteModel) -> bool:
    """
    Check whether the given Pyomo model contains all components of a thermal subsystem.

    This function validates the existence of typical thermal dispatch variables,
    including generation, commitment status, and startup/shutdown indicators.

    Parameters
    ----------
    model : ConcreteModel
        The Pyomo model instance to be validated.

    Returns
    -------
    bool
        True if all required thermal components are present, False otherwise.

    Notes
    -----
    The required attributes are:
    - T             : Time periods.
    - TG            : Set of thermal units.
    - thermal_p     : Power generation variable.
    - thermal_Cost    : Cost parameter.
    """

    required = [
        'T', 'TG', 'thermal_p', 'thermal_Cost'
    ]
    if all(hasattr(model, attr) for attr in required):
        return True
    return False
