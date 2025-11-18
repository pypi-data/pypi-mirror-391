"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Utility: Solve Pyomo Model from YAML Configuration

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This utility builds and solves a Pyomo optimization model using input
data provided in a YAML or JSON configuration file. The solver is selected 
based on metadata, and can include support for decomposition strategies 
(e.g., MIN-DT via MindtPy).

Features:
- Automatic model construction via modular subsystems (thermal, hydro, storage, renewable).
- Solver selection and configuration via YAML metadata.
- Support for MINLP solvers such as MindtPy with strategy and time limits.
- Termination condition validation to ensure feasibility or optimality.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""


from pyomo.opt import SolverFactory, TerminationCondition
from pyomo.common.errors import ApplicationError
from pyomo.environ import ConcreteModel, value
from typing import Any, Tuple, Dict
from colorama import Fore, Style, init as colorama_init
from .Builder import build_model_from_file
from .Reporting import *
from .ModelCheck import *
from .ModelFormatters import *

colorama_init(autoreset=True)

def solve(path: str) -> Tuple[ConcreteModel, Dict]:
    """
    Build and solve a Pyomo optimization model from a configuration file.

    This function loads a model and its configuration from a structured YAML or JSON
    file using the `build_model_from_file` routine. It then selects the appropriate
    solver based on the 'meta' section, applies any solver-specific options (including
    for MIN-DT decomposition), and executes the optimization.

    Parameters
    ----------
    path : str
        Path to the configuration file containing model metadata and data sections.

    Returns
    -------
    model : ConcreteModel
        The Pyomo model after the solve routine, with variables populated.
    case : dict
        Parsed dictionary containing the original configuration, metadata,
        solver options, and problem data.

    Raises
    ------
    RuntimeError
        If the solver is not available, solve fails, or model is infeasible.
    """

    model, case = build_model_from_file(path)
    solver_str = case['meta']['Solver']
    options = case['meta'].get('Solver_Options', {})
    print_welcome_message(model, case)
    # Create solver instance
    opt = SolverFactory(solver_str)

    if not opt.available():
        raise RuntimeError(
            f"Solver '{solver_str}' is not available on this system.")

    try:
        if solver_str.lower() == 'mindtpy':
            res = opt.solve(
                model,
                mip_solver=options.get('mip_solver', 'glpk'),
                nlp_solver=options.get('nlp_solver', 'cyipopt'),
                strategy=options.get('strategy', 'OA'),
                tee=False
            )
        else:
            res = opt.solve(model, tee=False)

        # Optional: print/write results if available
        # if hasattr(res, 'write'):
        #    res.write()

        # Check termination condition
        term_cond = res.solver.termination_condition
        if term_cond not in [TerminationCondition.optimal,
                             TerminationCondition.feasible]:
            raise RuntimeError(f"Solve terminated with condition: {term_cond}")

    except ApplicationError as e:
        raise RuntimeError(f"Solver execution failed: {e}")

    dispatch_summary(model)
    hydro_dispatch_summary(model)
    thermal_dispatch_summary(model)
    renewable_dispatch_summary(model)
    storage_dispatch_summary(model)
    connection_bar_dispatch_summary(model)
    transmission_line_dispatch_summary(model)

    return model, case
