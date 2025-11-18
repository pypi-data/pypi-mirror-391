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

from pyomo.environ import ConcreteModel
from .ThermalVars import thermal_add_sets_and_params, thermal_add_variables_uc
from .ThermalConstraints import (
    thermal_add_balance_constraint,
    thermal_add_capacity_constraint,
    thermal_add_startup_shutdown_logic_constraint,
    thermal_add_ramps_constraint,
    thermal_add_min_up_down_constraint,
    thermal_add_reserve_constraint
)
from .ThermalObjectives import set_objective_thermo_miqp, set_objective_thermo_pwl
from .ThermalPieceWise import thermal_add_piecewise_cost
from .ThermalDataTypes import ThermalData


def build_thermal_uc(
    data: ThermalData,
    objective: str = "miqp", # deprecated
    include_reserve: bool = False,
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
    
    objective : {"miqp", "pwl"}, optional
        Type of objective function to use:
    
        - "miqp": quadratic cost coefficients (a, b, c).
        - "pwl" : piecewise linear cost with SOS2/linearization.
           Default is "miqp".
    
    include_reserve : bool, optional
        Whether to include spinning reserve variables and 
        reserve requirement constraints (default False).

    Returns
    -------
    pyomo.environ.ConcreteModel
        A fully constructed Pyomo model ready for solving 
        with a MILP/MIQP solver.

    Examples
    --------
    >>> from pyomo.opt import SolverFactory
    >>> from NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder import build_thermal_uc
    >>> model = build_thermal_uc(
    ...     data,
    ...     objective="pwl",
    ...     include_reserve=True,
    ...     include_emissions=True
    ... )
    >>> opt = SolverFactory("gurobi")
    >>> results = opt.solve(model)
    >>> print(results.solver.termination_condition)
    optimal

    Notes
    -----
    - Reserve constraints require that reserve variables r[g, t] 
      are declared during variable creation.
    - The piecewise linear objective uses SOS2 variables or 
      McCormick envelopes for convexification.
    """
    m = ConcreteModel()

    m = add_thermal_problem(m=m,
                            data=data,
                            objective=objective,
                            include_reserve=include_reserve,
                            include_objective=include_objective)

    return m


def add_thermal_problem(m: ConcreteModel,
                        data: ThermalData,
                        objective: str = "miqp", # deprecated
                        include_reserve: bool = False,
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
    objective : str, optional
        Cost modeling approach. Options:
        - "miqp" : quadratic production cost (default),
        - "pwl"  : piecewise linear production cost.
    include_reserve : bool, optional
        If True, include spinning reserve variables and constraints
        (default False).
    include_objective : bool, optional
        If True, attach the cost-minimization objective function
        appropriate for the chosen cost type (default False).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model with thermal UC constraints and, if enabled,
        the objective function.

    Notes
    -----
    - Core constraints include: balance, capacity, startup/shutdown logic,
      ramping, and minimum up/down times.
    - When include_reserve=True, a reserve requirement constraint is added.
    - When objective="pwl" and include_objective=True, piecewise cost
      variables and constraints are attached along with the linear objective.
    - When objective="miqp" and include_objective=True, a quadratic
      cost objective is set.
    - This routine assumes that *thermal_add_sets_and_params* and
      *thermal_add_variables_uc* are available and correctly configured.

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> m = add_thermal_problem(m, data, objective="miqp",
    ...                         include_reserve=True,
    ...                         include_objective=True)
    >>> type(m)
    <class 'pyomo.core.base.PyomoModel.ConcreteModel'>
    """

    thermal_add_sets_and_params(m, data)
    use_pwl = (objective.lower() == "pwl")
    thermal_add_variables_uc(
        m, include_reserve=include_reserve, use_pwl=use_pwl)

    thermal_add_capacity_constraint(m, include_reserve=include_reserve)
    thermal_add_startup_shutdown_logic_constraint(m)
    thermal_add_ramps_constraint(m)
    thermal_add_min_up_down_constraint(m)

    if include_reserve:
        thermal_add_reserve_constraint(m)

    if include_objective:
        thermal_add_balance_constraint(m)
        set_objective_thermo_miqp(m)

    return m
