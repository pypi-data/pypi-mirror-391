"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Model Builder

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides a high-level builder function for thermal UC models.
It orchestrates the composition of Pyomo model objects by combining:

- Sets and parameters (*thermal_components.thermal_add_sets_and_params*)
- Variables (*thermal_components.thermal_add_variables_uc*)
- Constraint families (*thermal_constraints*)
- Objective functions (*thermal_objectives*)
- Optional features:
    * Reserve provision and requirement constraints
    * Emissions/fuel caps
    * Piecewise-linear (PWL) variable cost representation

Builder Function
----------------
*build_thermal_uc(data, objective, include_reserve, include_objective)*

Parameters:

- data            : ThermalData object with horizon, demand, and unit info
- objective       : "miqp" (quadratic) or "pwl" (piecewise linear)
- include_reserve : bool, add reserve variables/constraints if True
- include_objective : bool, add objective function

Returns:

- A fully assembled Pyomo ConcreteModel ready to be solved by MILP/MIQP solvers
  (e.g., Gurobi, CPLEX, SCIP) or MINLP solvers (via MindtPy with glpk/Ipopt).
 
Usage
-----
This is the main entry point to generate UC test cases from ThermalData
instances. It ensures consistency across modules and allows easy switching
between formulations.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""
import copy
from pyomo.environ import ConcreteModel
from .ThermalVars import thermal_add_sets_and_params, thermal_add_variables_uc
from .ThermalConstraints import (
    thermal_add_balance_constraint,
    thermal_add_capacity_constraint
)
from .ThermalObjectives import set_objective_thermo
from .ThermalDataTypes import ThermalData

from typing import Dict

def build_thermal_uc(
    data: ThermalData,
    include_objective: bool = True
) -> ConcreteModel:
    """
    Builds a modular thermal Unit Commitment (UC) Pyomo model.

    This function integrates all sets, parameters, variables, 
    constraints, and objectives required for the thermal UC problem.
    The model may be constructed with either a quadratic cost 
    function (MIQP) or a piecewise linear cost approximation (PWL).
    Optional constraints for spinning reserve and global emissions 
    caps are also supported.

    Parameters
    ----------
    data : object
        Data container providing unit and system information.
        Must include:

        - demand profile
        - unit technical parameters (min/max power, ramps, 
          minimum up/down times, costs, etc.)
    
    include_objective: optional, bool
        hj
          
    Returns
    -------
    pyomo.environ.ConcreteModel
        A fully constructed Pyomo model ready for solving 
        with a MILP/MIQP solver.

    Examples
    --------
    >>> from pyomo.opt import SolverFactory
    >>> from NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder import build_thermal_uc
    >>> model = build_thermal_uc(
    ...     data
    ... )
    >>> opt = SolverFactory("gurobi")
    >>> results = opt.solve(model)
    >>> print(results.solver.termination_condition)
    optimal

    """
    m = ConcreteModel()

    m = add_thermal_problem(m=m,
                            data=data,
                            include_objective=include_objective)

    return m


def add_thermal_problem(m: ConcreteModel,
                        data: ThermalData,
                        include_objective: bool = False) -> ConcreteModel:
    """
    Assemble a thermal unit-commitment (UC) problem in Pyomo.

    This builder configures a thermal UC optimization model by attaching sets,
    parameters, decision variables, and standard operational constraints. It
    supports both MIQP (quadratic cost) and PWL (piecewise linear cost)
    formulations, with optional reserve requirements and objective definition.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which the thermal UC problem will be added.
    data : ThermalData
        Input data structure containing unit characteristics, cost parameters,
        horizon length, demand, reserve requirements, and initial conditions.
    include_objective : bool, optional
        If True, attach the cost-minimization objective function
        appropriate for the chosen cost type (default False).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with thermal UC constraints and, if enabled,
        the objective function.

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> m = add_thermal_problem(m, data, objective="miqp",
    ...                         include_objective=True)
    >>> type(m)
    <class 'pyomo.core.base.PyomoModel.ConcreteModel'>
    """

    thermal_add_sets_and_params(m, data)
    thermal_add_variables_uc(m)

    thermal_add_capacity_constraint(m)

    if include_objective:
        thermal_add_balance_constraint(m)
        set_objective_thermo(m)

    return m


def add_thermal_subproblem(m: ConcreteModel,
                           data: ThermalData,
                           stage: int) -> ConcreteModel:
    """
    Assemble a thermal unit-commitment (UC) subproblem in Pyomo.

    This builder configures a thermal UC optimization model by attaching sets,
    parameters, decision variables, and standard operational constraints. It
    supports both MIQP (quadratic cost) and PWL (piecewise linear cost)
    formulations, with optional reserve requirements and objective definition.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which the thermal UC problem will be added.
    data : ThermalData
        Input data structure containing unit characteristics, cost parameters,
        horizon length, demand, reserve requirements, and initial conditions.
    stage : int
        the stage subproblem, informed for data copying

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with thermal UC constraints and, if enabled,
        the objective function.

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> m = add_thermal_problem(m, data, objective="miqp",
    ...                         include_objective=True)
    >>> type(m)
    <class 'pyomo.core.base.PyomoModel.ConcreteModel'>
    """
    # data copy
    subproblem_data = copy.deepcopy(data)
    subproblem_data.horizon = 1
    thermal_add_sets_and_params(m, subproblem_data)
    thermal_add_variables_uc(m)

    thermal_add_capacity_constraint(m)

    return m

