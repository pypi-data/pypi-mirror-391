"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Utility: PDDD Synthetic Model Generator

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------

This utility provides tools to reconstruct a deterministic representation 
of a multistage dual dynamic programming (PDDD) solution as a static Pyomo 
model. It enables post-optimization analysis by aggregating decision 
variables, dual prices, volumes, and cost structures from multiple stages 
into a single structured object.

Main Functionality
------------------
The primary function exposed by this package is:

- `generate_dummy_model(pddd_solution, yaml_data)`: Constructs a 
  fully populated `ConcreteModel` that mirrors the original optimization 
  trajectory. It fixes all relevant decision variables and duals for each 
  unit (hydro, thermal, renewable, storage), and reassembles cost 
  expressions for reporting, visualization, and interpretation.

Intended Use
------------
This package is not designed to perform optimization itself. Instead, it 
serves as a post-processing tool for exporting or inspecting results from 
a PDDD optimization workflow — for example, to be used in scenario analysis, 
LaTeX export, sensitivity evaluation, or policy verification.

Dependencies
------------
- Pyomo
- A compatible solver (e.g., GLPK, CPLEX, IPOPT)
- Auxiliary model-building functions such as:
  - `add_hydraulic_cost_expression`
  - `add_thermal_cost_expression`
  - `add_storage_cost_expression`
  - `add_renewable_cost_expression`

Examples
--------
>>> from naivepydecomp.pddd import generate_dummy_model
>>> model = generate_dummy_model(pddd_solution, yaml_data)
>>> print(value(model.OBJ))

See Also
--------
solve_pddd : The iterative algorithm that produces the input data for `generate_dummy_model`.
solve_stage_pddd : Solves a single stage of the PDDD problem and stores intermediate results.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from typing import Any, Dict, List

from pyomo.environ import (
    ConcreteModel,
    Constraint,
    Objective,
    Set,
    value,
    minimize
)

from pyomo.contrib.latex_printer import latex_printer

from .ModelCheck import (
    has_hydro_model,
    has_thermal_model,
    has_renewable_model,
    has_storage_model,
    has_connection_bar_model,
    has_transmission_line_model
)

from .Builder import build_model_from_data as build_model

from NaivePyDECOMP.HydraulicGenerator.HydraulicEquations import (
    add_hydraulic_cost_expression
)

from NaivePyDECOMP.ThermalGenerator.ThermalEquations import (
    add_thermal_cost_expression
)

from NaivePyDECOMP.RenewableGenerator.RenewableEquations import (
    add_renewable_cost_expression
)

from NaivePyDECOMP.Storage.StorageEquations import (
    add_storage_cost_expression
)

from NaivePyDECOMP.ConnectionBar.ConnectionBarEquations import (
    add_connection_bar_cost_expression
)

from NaivePyDECOMP.TransmissionLine.TransmissionLineEquations import (
    add_transmission_line_cost_expression
)

def generate_dummy_model(pddd_solution: List[Any],
                         yaml_data: Dict) -> ConcreteModel:
    """
    Generates a synthetic Pyomo model representing the structure and results 
    of a full PDDD (Deterministic Dual Dynamic Programming) optimization process.

    This function aggregates relevant decision variables and dual information 
    across all stages and stores them as fixed model components. It is useful 
    for analyzing and exporting the solution in a structured and interpretable 
    Pyomo `ConcreteModel`, without performing any further optimization.

    Parameters
    ----------
    pddd_solution : List
        List containing the results of each stage of the PDDD algorithm, 
        including model objects, decision variables, shadow prices, volumes, 
        and costs for each time stage.

    yaml_data : dict
        Dictionary parsed from the YAML configuration file, containing system 
        metadata, unit definitions (hydro, thermal, renewable, storage), cost 
        parameters, and other structural data used during model construction.

    Returns
    -------
    model : ConcreteModel
        A fully populated Pyomo `ConcreteModel` object that encapsulates:
        - Fixed decision variables from hydro, thermal, renewable, and storage units.
        - Cost terms and expressions used in the original optimization.
        - Final values of market price (CMO), deficit penalty, and alpha values.
        - Sets for all units and time stages.

    Notes
    -----
    - The returned model is not intended to be solved again, but rather to 
      serve as a reference for results visualization, report generation, or 
      post-analysis.
    - The cost components are reassembled using the same structure as in the 
      original model, using the `add_*_cost_expression` helper functions.
    - The model object stores one time step ahead (nstages + 1) for correct 
      alignment with stage-based formulations.

    Raises
    ------
    KeyError
        If expected keys or values are missing from `pddd_solution` or `yaml_data`.

    See Also
    --------
    solve_pddd : Function that produces the input `pddd_solution` dictionary.
    """

    model, _ = build_model(root=yaml_data)

    for constraint in model.component_objects(Constraint, active=True):
        constraint.deactivate()

    start_model = pddd_solution[0]['model']

    if has_hydro_model(start_model):

        for t in model.T:
            for h in model.HG:
                model.hydro_Q[h, t] = value(
                    pddd_solution[t-1]['model'].hydro_Q[h, 1])
                model.hydro_V[h, t] = value(
                    pddd_solution[t-1]['model'].hydro_V[h, 1])
                model.hydro_S[h, t] = value(
                    pddd_solution[t-1]['model'].hydro_S[h, 1])
                model.hydro_G[h, t] = value(
                    pddd_solution[t-1]['model'].hydro_G[h, 1])

        model.CMA = {(h, t): -value(
            pddd_solution[t-1]['cma'][h]) for h in model.HG for t in model.T}
        model.FC = {t: value(pddd_solution[t-1]['alpha']) for t in model.T}

    model.CMO = {t: value(pddd_solution[t-1]['cmo']) for t in model.T}
    model.alpha = {t: value(pddd_solution[t-1]['alpha']) for t in model.T}

    if has_thermal_model(start_model):
        for t in model.T:
            for g in model.TG:
                model.thermal_p[g, t] = value(
                    pddd_solution[t-1]['model'].thermal_p[g, 1])

    if has_renewable_model(start_model):
        for t in model.T:
            for r in model.RU:
                model.renewable_gen[r, t] = value(
                    pddd_solution[t-1]['model'].renewable_gen[r, 1])

    if has_storage_model(start_model):
        for t in model.T:
            for s in model.SU:
                model.storage_E[s, t] = value(
                    pddd_solution[t-1]['model'].storage_E[s, 1])
                model.storage_ch[s, t] = value(
                    pddd_solution[t-1]['model'].storage_ch[s, 1])
                model.storage_dis[s, t] = value(
                    pddd_solution[t-1]['model'].storage_dis[s, 1])
    
    if has_connection_bar_model(start_model):
        for t in model.T:
            for b in model.CB:
                model.D[b, t] = value(pddd_solution[t-1]['model'].D[b, 1])
                if not model.unique_bar:
                    model.theta[b, t] = value(pddd_solution[t-1]['model'].theta[b, 1])
 
    if has_transmission_line_model(start_model):
        for t in model.T:
            for l in model.LT:
                model.lines_flow[l, t] = value(pddd_solution[t-1]['model'].lines_flow[l, 1])

    return model
