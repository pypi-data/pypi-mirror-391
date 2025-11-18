"""
Generator Builder Module
========================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines the routines responsible for constructing the generator
submodel within the MDI (Modular Didactic Infrastructure) framework. It serves
as the primary entry point for creating the Pyomo-based representation of
dispatchable generation units, their parameters, variables, constraints, and
optional objective terms.

Description
-----------
The generator builder integrates modular components defined in the companion
submodules:

- ``GeneratorVars``: Declares decision variables for generator operation and investment.
- ``GeneratorDataTypes``: Defines dataclass-based structures for handling generator input data.
- ``GeneratorConstraints``: Introduces operational, investment, and capacity constraints.
- ``GeneratorObjectives``: Builds the cost-related components of the objective function.

These functions enable flexible inclusion of generator units within the full
system model or as a standalone expansion subproblem. Each submodule follows
Pyomo’s modeling conventions and supports compositional assembly within the
broader MDI framework.

Functions
---------
build_generators(generator_data, include_objective=True)
    Creates a Pyomo ``ConcreteModel`` containing the generator submodel,
    including variables, constraints, and optionally the objective function.

add_generator_problem(m, data, include_objective=False)
    Adds generator-related sets, parameters, variables, and constraints
    to an existing Pyomo model instance.

Notes
-----
- The generator submodel can be built independently or as part of a larger
  integrated energy planning problem.
- Setting ``include_objective=False`` allows the model to be embedded in
  hierarchical or multi-objective formulations.
- This module relies on modular imports and clear dependency separation
  between data definition, variable creation, and constraint formulation.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import Param, Set, ConcreteModel
from .GeneratorVars import *
from .GeneratorDataTypes import *
from .GeneratorConstraints import *
from .GeneratorObjectives import *


def build_generators(generator_data: dict,
                     include_objective: bool = True) -> ConcreteModel:
    """
    Construct a standalone generator submodel as a Pyomo ``ConcreteModel``.

    This function acts as a wrapper that initializes a new model instance,
    populates it with generator sets, parameters, variables, and constraints,
    and optionally includes the cost-minimizing objective function.

    Parameters
    ----------
    generator_data : dict
        Dictionary or dataclass containing all generator configuration data,
        including installed capacities, operational limits, and cost coefficients.
    include_objective : bool, optional
        Whether to include the generator’s cost function in the model objective.
        Defaults to ``True``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        A fully constructed generator submodel ready for optimization.

    Notes
    -----
    - Internally, this function delegates to ``add_generator_problem()``.
    - When used in integrated expansion models, the objective term may be
      disabled to avoid duplication at the system level.
    """
    m = ConcreteModel()

    add_generator_problem(m=m,
                          data=generator_data,
                          include_objective=include_objective)

    return m


def add_generator_problem(m: ConcreteModel,
                          data: GeneratorData,
                          include_objective: bool = False) -> ConcreteModel:
    """
    Add generator components (sets, parameters, variables, and constraints)
    to an existing Pyomo model.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Existing Pyomo model instance to which generator components will be added.
    data : GeneratorData
        Dataclass or structured object containing generator-related data, such as
        power limits, costs, and investment parameters.
    include_objective : bool, optional
        Whether to append the generator objective term to the model.
        Defaults to ``False``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The input model, extended with generator-related components.

    Workflow
    --------
    1. Define generator sets and parameters via ``generator_add_sets_and_params()``.
    2. Declare operational and investment variables using ``generator_add_variables()``.
    3. Add operational constraints for generation limits and investment linkage.
    4. Optionally include cost terms in the model’s objective function.

    Notes
    -----
    - This function can be safely called multiple times for different generator
      groups or technologies.
    - The objective inclusion flag provides flexibility for hierarchical
      optimization or decomposition-based formulations.
    """
    generator_add_sets_and_params(m, data)
    generator_add_variables(m)
    add_generator_power_limits_constraint(m)
    add_generator_investment_link_constraint(m)

    if include_objective:
        set_objective_generator(m)

    return m
