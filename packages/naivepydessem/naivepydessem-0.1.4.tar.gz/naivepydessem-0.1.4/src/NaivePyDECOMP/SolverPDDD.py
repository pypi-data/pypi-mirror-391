"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Utility: Solve PDDD Pyomo Models from YAML Configuration

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
from pyomo.environ import (
    ConcreteModel, SolverFactory, Suffix,
    TerminationCondition
)
from typing import List, Dict, Tuple
from pyomo.contrib.latex_printer import latex_printer
from pyomo.common.errors import ApplicationError
from colorama import Fore, Style, init as colorama_init
from .Reporting import *
from .ModelCheck import *
from .ModelFormatters import *
from .BuilderPDDD import (
    build_pddd_data_from_file,
    build_pddd_balance_and_objective_from_yaml
)
from .Builder import build_model_from_file
from .PDDDMergeModels import generate_dummy_model
import copy

colorama_init(autoreset=True)


def fcf_from_cuts(cuts: List[Dict],
                  stage: int,
                  storage_levels: Dict) -> List:
    """
    Compute the Future Cost Function (FCF) value given a set of Benders cuts,
    assuming that the expansion point (xk) has already been absorbed into
    the intercept (rhs).

    Parameters
    ----------
    cuts : list of dict
        List of cuts. Each cut must have the format:
        {
            "stage": int                 # stage for calculation
            "rhs": float,                # adjusted intercept
            "coefs": {unit: float}       # coefficients (subgradients)
        }

    stage : int
        The index of the current stage being solved (0-based).
    storage_levels : dict
        Dictionary with current storage volumes for each hydro unit.
        Example: {"UHE1": 50, "UHE2": 80}

    Returns
    -------
    List[float]
        Value of the Future Cost Function (FCF) evaluated at the given
        storage levels.
    """
    values = []

    for cut in cuts:
        if cut["stage"] == stage:
            rhs = cut["rhs"]
            coefs = cut["coefs"]
            value = rhs + sum(coefs[unit] * storage_levels[unit]
                              for unit in coefs)
            values.append(value)
    return values


def compute_fcf(cuts: List[Dict],
                pddd_memory: List[Dict]) -> Dict:
    """
    Compute the Future Cost Function (FCF) values for all stages 
    in the PDDD framework, given a set of Benders cuts.

    This function iterates over the memory of the PDDD algorithm, 
    extracting the storage volumes for each stage and evaluating 
    the corresponding FCF approximation using the provided cuts.

    Parameters
    ----------
    cuts : List[Dict]
        List of Benders cuts. Each cut must be a dictionary with:
        {
            "rhs": float,                # adjusted intercept
            "coefs": {unit: float}       # coefficients (subgradients)
        }
    pddd_memory : List[Dict]
        List of stage-level information from the PDDD algorithm.
        Each element must include the storage volumes in the key 
        'f_volume', e.g.:
        {
            "f_volume": {"UHE1": 50, "UHE2": 80, ...}
        }

    Returns
    -------
    Dict
        Dictionary of FCF values for each stage, with keys in the 
        format "FCF_{t}" where t denotes the stage index (1-based).
        Example:
        {
            "FCF_1": [...],
            "FCF_2": [...],
            ...
        }
    """
    fcf_values: Dict = {}
    for stage in range(len(pddd_memory)-1):
        stage_fcf_values = fcf_from_cuts(cuts=cuts,
                                         stage=stage,
                                         storage_levels=pddd_memory[stage]['f_volume'])
        fcf_values[r"FCF_{" + f"{stage+1:d}" + r"}"] = stage_fcf_values
    
    return fcf_values



def solve_stage_pddd(yaml_data: Dict,
                     stage_hydros: Dict,
                     stage_storage: Dict,
                     cuts: Dict,
                     stage: int) -> Dict:
    """
    Solves a single stage of the hydrothermal dispatch problem within the 
    Deterministic Dual Dynamic Programming (PDDD) framework.

    This function constructs and solves the optimization model for a given stage,
    incorporating the current state of hydro units, operational cuts from future stages,
    and the parameters defined in the YAML configuration. It returns the resulting 
    model and relevant economic and operational variables.

    Parameters
    ----------
    yaml_data : dict
        The full configuration dictionary loaded from a YAML file, containing 
        system metadata, solver settings, and model parameters.

    stage_hydros : dict
        Dictionary describing the state of the hydro units at the current stage,
        including initial volumes, inflows, and other relevant characteristics.
    stage_storage: dict
        Dictionary describing the state of the storage units at the current stage,
        including initial energy, energy limits and other relevant characteristics.
    cuts : dict
        Dictionary containing Benders-like cuts (affine inequalities) propagated 
        from future stages, used to approximate the future cost function.

    stage : int
        The index of the current stage being solved (0-based).

    Returns
    -------
    results : dict
        Dictionary containing:

        - 'model' : ConcreteModel
            The Pyomo model instance with solved values.
        - 'hydro' : dict
            The hydro dictionary passed as input, preserved for traceability.
        - 'storage' : dict
            The storage dictionary passed as input, preserved for traceability.
        - 'total_cost' : float
            The stage cost including the estimated future cost via alpha.
        - 'alpha' : float
            The value of the cost-to-go (future cost approximation) variable.
        - 'f_volume' : dict
            Dictionary mapping each hydro plant to its final volume at the end of the stage.
        - 'cmo' : float
            The dual variable associated with the system-wide energy balance constraint (marginal cost of operation).
        - 'cma' : dict
            Dictionary mapping each hydro plant to its marginal water value 
            (dual variable of the volume balance constraint).

    Raises
    ------
    RuntimeError
        If the specified solver is not available or if the optimization does not reach 
        an optimal or feasible termination condition.

    Notes
    -----
    This function is used internally in the forward and backward passes of the PDDD algorithm
    to simulate stage-wise operations and propagate information backward via cuts.
    """

    # --------------------------
    # PROBLEM PREPARATION
    # --------------------------
    current_yaml_data = copy.deepcopy(yaml_data)
    current_yaml_data['hydro'] = stage_hydros
    if 'storage' in current_yaml_data:
        current_yaml_data['storage'] = stage_storage
    solver_str = current_yaml_data['meta']['Solver']
    options = current_yaml_data['meta'].get('Solver_Options', {})

    model = build_pddd_balance_and_objective_from_yaml(yaml_data=current_yaml_data,
                                                       stage=stage,
                                                       cuts=cuts)

    opt = SolverFactory(solver_str)

    if not opt.available():
        raise RuntimeError(f"Solver '{solver_str}' is not available")

    # --------------------------
    # PROBLEM SOLUTION
    # --------------------------
    try:
        if solver_str.lower() == 'mindtpy':
            res = opt.solve(
                model,
                mip_solver=options.get('mip_solver', 'glpk'),
                nlp_solver=options.get('nlp_solver', 'cyipopt'),
                strategy=options.get('strategy', 'OA'),
                tee=False,
                suffixes=["dual"]
            )
        else:
            res = opt.solve(model, tee=False,
                            suffixes=["dual"])


        # Check termination condition
        term_cond = res.solver.termination_condition
        if term_cond not in [TerminationCondition.optimal,
                             TerminationCondition.feasible]:
            raise RuntimeError(f"Solve terminated with condition: {term_cond}")

    except ApplicationError as e:
        raise RuntimeError(f"Solver execution failed: {e}")

    # --------------------------
    # RESULTS PREPARATION
    # --------------------------

    results: Dict = {}
    results['model'] = copy.deepcopy(model)
    results['hydro'] = copy.deepcopy(stage_hydros)
    results['storage'] = copy.deepcopy(stage_storage)
    results['total_cost'] = model.OBJ()
    results['alpha'] = model.alpha.value
    results['f_volume'] = {h: model.hydro_V[h, 1].value for h in model.HG}
    results['cmo'] = model.dual[model.Balance[1]]
    results['cma'] = {
        h: model.dual[model.hydro_volume_balance_constraint[h, 1]] for h in model.HG}

    return results


def solve_pddd(path: str,
               max_iter: int = 500,
               tol: float = 0.01,
               verbose: bool = True) -> Tuple[ConcreteModel, Dict]:
    """
    Solves the full multi-stage hydrothermal dispatch problem using the 
    Deterministic Dual Dynamic Programming (PDDD) algorithm.

    This function implements both the forward and backward passes of the 
    PDDD approach, coordinating the stage-wise resolution of subproblems, 
    the propagation of terminal volumes between stages, and the generation 
    of Benders-like cuts. The process continues until the upper-lower bound 
    convergence criterion is satisfied or the maximum number of iterations 
    is reached.

    Parameters
    ----------
    path : str
        Path to the YAML file containing the problem configuration 
        (system data, hydro parameters, solver options).

    max_iter : int, optional
        Maximum number of forward-backward iterations allowed (default is 10).

    tol : float, optional
        Convergence tolerance between ZSUP and ZINF values used as stopping 
        criterion (default is 1e-2).

    verbose : bool, optional
        Whether to print iteration logs and convergence progress (default is True).

    Returns
    -------
    model : ConcreteModel
        A dummy Pyomo model representing the structure and solution of the 
        final iteration. This is mainly for completeness and introspection.

    case : dict
        The parsed YAML case dictionary used in the PDDD process, containing 
        metadata, hydro data, and solver configurations.

    alpha_values : dict
        alpha values of future costs.

    ZINF: dict


    Raises
    ------
    RuntimeError
        If the specified solver is not available or any stage optimization fails.

    ValueError
        If no hydro data is provided in the YAML configuration.

    Notes
    -----
    - The upper bound (ZSUP) is computed cumulatively from all stages, 
      discounting the cost-to-go alpha values.
    - The lower bound (ZINF) corresponds to the cost of the first stage 
      assuming a myopic (executable) policy.
    - Cuts are generated in the backward pass and injected into earlier stages 
      to approximate the value function of future stages.
    - This implementation is pedagogical and emphasizes clarity and modularity 
      over computational performance.
    """
    # === Compatibilidade com pl único ===
    npl_model, npl_case = build_model_from_file(path)
    print_welcome_message(npl_model, npl_case)
    # === Construção dos subproblemas ===
    case = build_pddd_data_from_file(path)
    original_case = copy.deepcopy(case)
    nstages = case['meta'].get('horizon', 1)

    if 'hydro' not in case:
        raise ValueError(
            'Hydro Units must be set o perform DECOMP Like Dispatch')

    if 'thermal' not in case:
        raise ValueError(
            'Thermal Units must be set o perform DECOMP Like Dispatch')


    # === Inicializações ===
    cuts = []
    ZINF = []
    ZSUP = []

    alpha_values: Dict = {}

    alpha_values["T"] = []

    hydro_units_default = case['hydro']

    if 'storage' in case:
        storage_units_default = case['storage']
    else:
        storage_units_default = None

    memory: List[Any] = [{"model": ConcreteModel(),
                          "hydro": hydro_units_default,
                          'storage': storage_units_default,
                          "total_cost": 0.0,
                          "alpha": 0.0,
                          "f_volume": {},
                          "cmo": 0.0,
                          "cma": {}} for _ in range(nstages)]

    for iter_idx in range(max_iter):

        if verbose:
            print(f"\n--- Iteration {iter_idx + 1} ---")

        current_zsup = 0.0
        current_zinf = 0.0
        # === Forward Pass ===
        for t in range(nstages):

            stage_data = memory[t]

            results = solve_stage_pddd(yaml_data=case,
                                       stage_hydros=stage_data['hydro'],
                                       stage_storage=stage_data['storage'],
                                       cuts=cuts,
                                       stage=t)

            memory[t] = copy.deepcopy(results)

            if t < nstages - 1:

                next_stage_data = memory[t + 1]
                for uhe in stage_data['hydro']['units'].keys():
                    next_stage_data['hydro']['units'][uhe]['Vini'] = results['f_volume'][uhe]
                if 'storage' in case:
                    for sunit in stage_data['storage']['units']:
                        next_stage_data['storage']['units'][sunit]['Eini'] = value(
                            results['model'].storage_E[sunit, 1])
                memory[t+1] = copy.deepcopy(next_stage_data)

            current_zsup += results['total_cost'] - results['alpha']
            if t == 0:
                current_zinf = results['total_cost']

        
        ZSUP.append(current_zsup)

        ZINF.append(current_zinf)

        if verbose:
            print(
                f"ZINF[{iter_idx}] = {ZINF[-1]:.4f}, ZSUP[{iter_idx}] = {ZSUP[-1]:.4f}")

        if abs(ZSUP[-1] - ZINF[-1]) <= tol:
            break

        alpha_values["T"].append(sum([memory[0]['f_volume'][h] for h in memory[0]['f_volume']]))

        # === Backward Pass ===
        for t in reversed(range(nstages)):

            if t > 0:

                stage_data = memory[t]

                results = solve_stage_pddd(yaml_data=case,
                                           stage_hydros=stage_data['hydro'],
                                           stage_storage=stage_data['storage'],
                                           cuts=cuts,
                                           stage=t)

                rhs = results['total_cost']
                coefs = dict()

                for uhe in stage_data['hydro']['units']:
                    # cma = -results['cma'][uhe]
                    cma = results['cma'][uhe]
                    rhs -= cma * results['hydro']['units'][uhe]['Vini']
                    # rhs -= cma * results['model'].hydro_V[uhe, 1].value
                    coefs[uhe] = cma

                cuts.append({
                    "stage": t-1,
                    "rhs": rhs,
                    "coefs": coefs
                })

    # FCF from benders cuts

    fct_values = compute_fcf(cuts, memory)

    alpha_values["FCF_{1}"] = fct_values["FCF_{1}"]

    if verbose:
        print("\n=== PDDD Finished ===")
        print(f"Final ZINF = {ZINF[-1]:.4f}")
        print(f"Final ZSUP = {ZSUP[-1]:.4f}")
        print(
            f"Gap = {abs(ZSUP[-1] - ZINF[-1]):.4f} after {iter_idx + 1} iterations")

    z_limits = {'ZINF': ZINF,
                'ZSUP': ZSUP}
    
    model = generate_dummy_model(memory, original_case)

    dispatch_summary(model)
    hydro_dispatch_summary(model)
    thermal_dispatch_summary(model)
    renewable_dispatch_summary(model)
    storage_dispatch_summary(model)
    connection_bar_dispatch_summary(model)
    transmission_line_dispatch_summary(model)

    return model, case, alpha_values, z_limits
