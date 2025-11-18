"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Module: Model Builder from YAML Configuration

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides a unified interface for constructing a Pyomo-based
economical dispatch model from structured YAML or JSON input files.
It supports integration of multiple subsystems, including:

- Hydraulic generation units (UHEs)
- Thermal generation units (UTs)
- Renewable generators
- Storage systems (batteries or reservoirs)
- Deficit penalty model

The model construction includes:

- Validation of structural consistency in input data.
- Object-oriented dataclass translation of YAML structures.
- Modular assembly of each subsystem's variables and constraints.
- Construction of system-wide power balance constraint.
- Cost-based objective function including startup, generation, and deficit costs.

Usage
-----
Use `build_model_from_file(path)` as the main entry point.

Ensure the YAML file has at least a `meta` section and one
of the technology sections: `hydro`, `thermal`, `renewable`, or `storage`.

Returns
-------
Tuple[ConcreteModel, dict]
    - Pyomo ConcreteModel ready for optimization.
    - Parsed dictionary representing the structured case.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""


from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple
from pyomo.environ import ConcreteModel, Objective, Constraint, minimize

from NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes import HydraulicData, HydraulicUnit
from NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder import add_hydro_problem
from NaivePyDECOMP.HydraulicGenerator.HydraulicEquations import add_hydraulic_cost_expression

from NaivePyDECOMP.ThermalGenerator.ThermalDataTypes import ThermalData, ThermalUnit
from NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder import add_thermal_problem
from NaivePyDECOMP.ThermalGenerator.ThermalEquations import add_thermal_cost_expression

from NaivePyDECOMP.RenewableGenerator.RenewableDataTypes import RenewableData, RenewableUnit
from NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder import add_renewable_problem
from NaivePyDECOMP.RenewableGenerator.RenewableEquations import add_renewable_cost_expression

from NaivePyDECOMP.Storage.StorageDataTypes import StorageData, StorageUnit
from NaivePyDECOMP.Storage.StorageBuilder import add_storage_problem
from NaivePyDECOMP.Storage.StorageEquations import add_storage_cost_expression

from NaivePyDECOMP.ConnectionBar.ConnectionBarDataTypes import ConnectionBarData, ConnectionBarUnit
from NaivePyDECOMP.ConnectionBar.ConnectionBarBuilder import add_connection_bar_problem
from NaivePyDECOMP.ConnectionBar.ConnectionBarEquations import add_connection_bar_cost_expression
from NaivePyDECOMP.ConnectionBar.ConnectionBarConstraints import add_connection_bar_balance_constraints

from NaivePyDECOMP.TransmissionLine.TransmissionLineDataTypes import TransmissionLineData, TransmissionLineUnit
from NaivePyDECOMP.TransmissionLine.TransmissionLineBuilder import add_transmission_line_problem
from NaivePyDECOMP.TransmissionLine.TransmissionLineEquations import add_transmission_line_cost_expression

from .YAMLLoader import yaml_loader

from NaivePyDESSEM.Builder import (
    _validate_meta,
    _validate_demand,
    _validate_renewable,
    _validate_storage,
    _validate_connection_bars,
    _validate_transmission_lines,
    _mk_renewable_data,
    _mk_storage_data,
    _mk_connection_bar_data,
    _mk_transmission_line_data
)

# ============================================================================
# Validators (lightweight sanity checks)
# ============================================================================


def _validate_hydro(hydro: Dict[str, Any], T: int) -> None:
    """
    Validate the structure and length of the demand time series.

    Ensures that the demand dictionary has exactly T entries with
    consecutive integer keys starting from 1.

    Parameters
    ----------
    d : dict
        Dictionary mapping time indices to demand values.
    T : int
        Expected length of the time horizon.

    Raises
    ------
    ValueError
        If demand length or index sequence is incorrect.

    """

    units = hydro.get("units", {})
    for name, u in units.items():
        af = u.get("afluencia", [])
        if len(af) != T:
            raise ValueError(
                f"hydro.units[{name}].afluencia must have length {T}.")
        if not (u["Vmin"] <= u["Vini"] <= u["Vmax"]):
            raise ValueError(
                f"hydro.units[{name}] must satisfy Vmin <= Vini <= Vmax.")
        if not (u["Qmin"] <= u["Qmax"]):
            raise ValueError(f"hydro.units[{name}] must satisfy Qmin <= Qmax.")

        if not (u["p"] <= 1):
            raise ValueError(f"hydro.units[{name}] must satisfy p <= 1.")


def _validate_thermal(thermal: Dict[str, Any]) -> None:
    """
    Validate thermal unit configuration for consistency.

    Checks that capacity bounds and ramp limits are well-defined
    and non-negative for all thermal units.

    Parameters
    ----------
    thermal : dict
        Dictionary containing thermal units and parameters.

    Raises
    ------
    ValueError
        If Pmin > Pmax or if ramp-up/ramp-down limits are negative.

    """

    units = thermal.get("units", {})
    for name, u in units.items():
        if not (u["Gmin"] <= u["Gmax"]):
            raise ValueError(
                f"thermal.units[{name}] must satisfy Pmin <= Pmax.")

# ============================================================================
# Dataclass factories
# ============================================================================


def _mk_hydraulic_data(root: Dict[str, Any]) -> HydraulicData:
    """
    Construct a HydraulicData object from parsed YAML root.

    Parses and converts all hydraulic unit fields and global hydro parameters
    into a strongly typed HydraulicData structure.

    Parameters
    ----------
    root : dict
        YAML-parsed dictionary containing 'meta' and 'hydro' sections.

    Returns
    -------
    HydraulicData
        Structured dataclass containing all parsed hydro data.
    """

    meta = root["meta"]
    hydro = root["hydro"]
    # demanda “global” veio em root["demand"]
    H = meta["horizon"]
    units = {}
    for name, u in hydro["units"].items():
        units[name] = HydraulicUnit(
            name=name,
            bar=str(u.get("bar", r"{BAR_{1}}")),
            Qmin=float(u["Qmin"]),
            Qmax=float(u["Qmax"]),
            Vmin=float(u["Vmin"]),
            Vmax=float(u["Vmax"]),
            Vini=float(u["Vini"]),
            afluencia=[float(x) for x in u["afluencia"]],
            upstreams=u.get("upstreams", None),
            p=float(u.get("p", 0.0)),
            compute_total_inflow=bool(u.get("compute_total_inflow", True)),
        )
    return HydraulicData(
        horizon=H,
        units=units
    )


def _mk_thermal_data(root: Dict[str, Any]) -> ThermalData:
    """
    Construct a ThermalData object from parsed YAML root.

    Parses unit-level thermal data including cost coefficients, startup costs,
    and minimum up/down times, as well as reserve requirements.

    Parameters
    ----------
    root : dict
        YAML-parsed dictionary containing 'meta' and 'thermal' sections.

    Returns
    -------
    ThermalData
        Structured dataclass containing all parsed thermal data.
    """

    meta = root["meta"]
    thermal = root["thermal"]
    H = meta["horizon"]
    demand = {int(k+1): float(v) for k, v in enumerate(meta["demand"])}

    units = {}
    for name, u in thermal["units"].items():
        units[name] = ThermalUnit(
            name=name,
            bar=str(u.get("bar", r"{BAR_{1}}")),
            Gmin=float(u["Gmin"]),
            Gmax=float(u["Gmax"]),
            Cost=float(u["Cost"])
        )

    return ThermalData(
        horizon=H,
        units=units,
    )


# ============================================================================
# Master entry point
# ============================================================================

def build_balance_and_objective_from_yaml(model: ConcreteModel, yaml_data: Dict[str, Any]) -> ConcreteModel:
    """
    Construct the system-wide power balance constraint and total cost objective.

    This function scans the parsed YAML content to determine which technologies
    (thermal, hydro, storage, renewable) are present, and invokes their respective
    expression builders to construct:

    - model.Balance: a time-indexed Constraint for supply-demand balance
    - model.OBJ: an Objective for cost minimization

    Parameters
    ----------
    model : ConcreteModel
        A Pyomo model with required sets and variables already declared.
    yaml_data : dict
        Parsed YAML dictionary with subsections for each technology.

    Returns
    -------
    ConcreteModel
        The input model with balance constraints and objective function added.
    """
    # --------------------------
    #  BALANCE CONSTRAINT
    # --------------------------

    add_connection_bar_balance_constraints(model)

    # --------------------------
    # OBJECTIVE FUNCTION
    # --------------------------
    cost_terms: List[Any] = []

    if 'thermal' in yaml_data:
        add_thermal_cost_expression(model, cost_terms)
    if 'hydro' in yaml_data:
        add_hydraulic_cost_expression(model, cost_terms)
    if 'storage' in yaml_data:
        add_storage_cost_expression(model, cost_terms)
    if 'renewable' in yaml_data:
        add_renewable_cost_expression(model, cost_terms)
    if 'bars' in yaml_data:
        add_connection_bar_cost_expression(model, cost_terms)
    if 'lines' in yaml_data:
        add_transmission_line_cost_expression(model, cost_terms)

    # a fonte déficit

    cost_terms.append(sum(model.Cdef[b]*model.D[b, t]
                      for b in model.CB for t in model.T))

    model.OBJ = Objective(expr=sum(cost_terms), sense=minimize)

    return model


def build_model_from_file(path: str) -> Tuple[ConcreteModel, Dict]:
    """
    Load master data from YAML/JSON and build subsystem models.

    Parameters
    ----------
    path : str
        Path to a YAML file with sections: meta, demand, and one or
        more of {hydro, thermal, renewable, storage}.

    Returns
    -------
    Tuple[pyomo.environ.ConcreteModel, Dict]
        A tuple with the builded model and the parsed case file

    Raises
    ------
    ValueError
        On structural or validation errors in the input file.
    """

    root = yaml_loader(path)
    return build_model_from_data(root)


def build_model_from_data(root: Dict) -> Tuple[ConcreteModel, Dict]:
    """
    build subsystem models from data.

    Parameters
    ----------
    root : str
        system description.

    Returns
    -------
    Tuple[pyomo.environ.ConcreteModel, Dict]
        A tuple with the builded model and the parsed case file

    Raises
    ------
    ValueError
        On structural or validation errors in the input file.
    """

    if "meta" not in root:
        raise ValueError("File must contain 'meta' sections.")

    m = ConcreteModel()

    # Basic validations
    _validate_meta(root["meta"])
    T = int(root["meta"]["horizon"])
    m.p_base = float(root["meta"].get("p_base", 1.0))
    has_valid_units = False

    # first of all, the bars
    if not "bars" in root:
        # default bar - described in meta section
        _validate_demand(root["meta"]["demand"], T)
        slack = True
        Cdef = float(root["meta"]["Cdef"])
        demand = [float(x) for x in root["meta"]["demand"]]
        root["bars"] = {"units": {"{BAR_{1}}": {"slack": slack,
                                                "Cdef": Cdef,
                                                "demand": demand}}}

    if "bars" in root and root["bars"] is not None:
        _validate_connection_bars(root["bars"], T)
        bar_data = _mk_connection_bar_data(root)
        m = add_connection_bar_problem(m=m,
                                       data=bar_data,
                                       include_objective=False)

    if "lines" in root and root["lines"] is not None:
        _validate_transmission_lines(root["lines"])
        bar_data = _mk_transmission_line_data(root)
        m = add_transmission_line_problem(m=m,
                                          data=bar_data,
                                          include_objective=False)

    if "hydro" in root and root["hydro"] is not None:
        _validate_hydro(root["hydro"], T)
        hydro_data = _mk_hydraulic_data(root)
        m = add_hydro_problem(m=m,
                              data=hydro_data,
                              include_objective=False)
        has_valid_units = True

    if "thermal" in root and root["thermal"] is not None:
        _validate_thermal(root["thermal"])
        thermal_data = _mk_thermal_data(root)
        m = add_thermal_problem(m=m,
                                data=thermal_data,
                                include_objective=False)
        has_valid_units = True

    if "renewable" in root and root["renewable"] is not None:
        _validate_renewable(root["renewable"], T)
        renewable_data = _mk_renewable_data(root)
        m = add_renewable_problem(m=m,
                                  data=renewable_data,
                                  include_objective=False)
        has_valid_units = True

    if "storage" in root and root["storage"] is not None:
        _validate_storage(root["storage"])
        storage_data = _mk_storage_data(root)
        m = add_storage_problem(m=m,
                                data=storage_data,
                                include_objective=False)
        has_valid_units = True

    if not has_valid_units:
        raise ValueError("No buildable sections found. Provide at least one of "
                         "{hydro, thermal, renewable, storage}.")
    m = build_balance_and_objective_from_yaml(m, root)

    return m, root
