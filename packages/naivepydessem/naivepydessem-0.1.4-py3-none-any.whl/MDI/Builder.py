"""
Builder Module
==============
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
The **Builder** module provides the high-level orchestration routines for constructing
a complete **MDI (Modular Decision Infrastructure)** system model. It integrates
the Generator and Storage subsystems, validates YAML input data, and assembles
the optimization problem by defining constraints, objectives, and auxiliary
expressions using **Pyomo**.

Description
-----------
This module serves as the *entry point* for model instantiation from a YAML specification,
including validation of meta parameters, generation and storage data, and global
power balance. It encapsulates all system-level expressions such as:

- **Adequacy Constraint** — ensures total available capacity meets mean demand.  
- **Power Balance** — enforces node-level balance between demand and generation.  
- **Objective Function** — minimizes total system costs including generation, storage, and deficit penalties.

It also handles automatic conversion of YAML datasets into `GeneratorData` and
`StorageData` dataclasses, ensuring consistency of units, bounds, and efficiency parameters.

Functions
---------
_validate_meta(meta)
    Performs structural and numerical checks on the metadata section.
_validate_demand(d, T)
    Validates demand profiles (currently placeholder).
_validate_storage(storage)
    Ensures energy capacity and efficiency values are within valid physical limits.
_validate_generator(generators)
    Validates generator attributes and required fields.

_mk_generator_data(root)
    Factory for creating a `GeneratorData` instance from YAML input.
_mk_storage_data(root)
    Factory for creating a `StorageData` instance from YAML input.

compute_mean_demand(m, yaml_data)
    Computes weighted mean demand over all load levels and attaches it to the model.
add_system_adequacy_expression(m)
    Adds a system adequacy constraint based on installed capacity.

build_balance_and_objective_from_yaml(model, yaml_data)
    Constructs balance constraints and total cost objective function.

build_model_from_file(path)
    High-level entry point: loads YAML, validates, builds subsystems,
    and returns a complete `ConcreteModel`.

Notes
-----
- Requires **Pyomo ≥ 6.6.0**.  
- YAML input structure must contain sections: `meta`, `generator`, `storage`.  
- All time indices (`t`) are assumed to start at 1 (Pyomo convention).  
- The Builder supports both investment and operational formulations.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.  
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, List, Tuple
from pyomo.environ import ConcreteModel, Objective, Constraint, minimize

from MDI.Generator.GeneratorDataTypes import GeneratorData, GeneratorUnit
from MDI.Generator.GeneratorBuilder import add_generator_problem
from MDI.Generator.GeneratorEquations import add_generator_cost_expression

from MDI.Storage.StorageDataTypes import StorageData, StorageUnit
from MDI.Storage.StorageBuilder import add_storage_problem
from MDI.Storage.StorageEquations import add_storage_cost_expression

from MDI.ConnectionBar.ConnectionBarDataTypes import ConnectionBarData, ConnectionBarUnit
from MDI.ConnectionBar.ConnectionBarBuilder import add_connection_bar_problem
from MDI.ConnectionBar.ConnectionBarConstraints import (
    add_connection_bar_balance_constraints, 
    add_connection_bar_capacity_constraints
)
from MDI.ConnectionBar.ConnectionBarEquations import add_connection_bar_cost_expression

from MDI.TransmissionLine.TransmissionLineDataTypes import TransmissionLineData, TransmissionLineUnit
from MDI.TransmissionLine.TransmissionLineBuilder import add_transmission_line_problem
from MDI.TransmissionLine.TransmissionLineEquations import add_transmission_line_cost_expression

from .YAMLLoader import yaml_loader

# ============================================================================
# Validators (lightweight sanity checks)
# ============================================================================


def _validate_meta(meta: Dict[str, Any]) -> None:
    """
    Validate meta parameter.

    Parameters
    ----------
    storage : dict
        Dictionary containing meta configuration.

    Raises
    ------
    ValueError
        If meta is malformed
    """
    horizon = meta.get("horizon")
    if not isinstance(horizon, int) or horizon <= 0:
        raise ValueError("meta.horizon must be a positive integer.")


def _validate_demand(d: Dict[Any, Any], T: int) -> None:
    """
    Validate demand parameter.

    Parameters
    ----------
    storage : dict
        Dictionary containing demand configuration .

    Raises
    ------
    ValueError
        If demand is malformed
    """
    pass


def _validate_storage(storage: Dict[str, Any]) -> None:
    """
    Validate storage unit parameters.

    Parameters
    ----------
    storage : dict
        Dictionary containing storage unit configurations.

    Raises
    ------
    ValueError
        If storage unit is malformed
    """
    units = storage.get("units", {})
    for name, u in units.items():
        if not (u["Emin"] <= u["Eini"] <= u["Emax"]):
            raise ValueError(
                f"storage.units[{name}] must satisfy Emin <= Eini <= Emax.")
        for k in ("eta_c", "eta_d"):
            if not (0.0 < u[k] <= 1.0):
                raise ValueError(
                    f"storage.units[{name}].{k} must be in (0, 1].")


def _validate_generator(generators: Dict[str, Any]) -> None:
    """
    Validate generator unit parameters.

    Parameters
    ----------
    storage : dict
        Dictionary containing generator unit configurations.

    Raises
    ------
    ValueError
        If generator unit is malformed
    """
    required = [
        'GU', 'T', 'P',
        'gen_P', 'gen_c_op', 'gen_c_inv',
        'gen_y', 'gen_x'
    ]

    units = generators.get("units", {})
    for name, u in units.items():
        if all(hasattr(u, attr) for attr in required):
            raise ValueError(
                f"generator.units[{name}] is invalid.")


def _validate_connection_bars(bars: Dict[str, Any], T: int, levels: int) -> None:
    """
    Validate connection bars unit parameters.

    Parameters
    ----------
    storage : dict
        Dictionary containing connection bar unit configurations.

    Raises
    ------
    ValueError
        If connection bar unit is malformed
    """
    units = bars.get("units")
    required = ['slack', 'Cdef']
    for name, u in units.items():
        if not all(attr in u for attr in required):
            raise ValueError(
                f"bars.units[{name}] is malformed.")

        demand = u.get("demand", {})
        if len(demand.keys()) != levels:
            raise ValueError(
                f"bars.units[{name}].demand must have length {levels}.")
        for level, u in demand.items():
            if len(u) != T:
                raise ValueError(
                    f"bars.units[{name}].demand[{level}] must have length {T}.")


def _validate_transmission_lines(lines: Dict[str, Any]) -> None:
    """
    Validate transmission line unit parameters.

    Parameters
    ----------
    storage : dict
        Dictionary containing transmission lines unit configurations.

    Raises
    ------
    ValueError
        If transmission line unit is malformed
    """
    units = lines.get("units")
    required = ['model', 'b', 'pmax', 'endpoints', 'c_op', 'c_inv']

    for name, u in units.items():
        if not all(attr in u for attr in required):
            raise ValueError(
                f"lines.units[{name}] is malformed.")


# ============================================================================
# Dataclass factories
# ============================================================================


def _mk_generator_data(root: Dict[str, Any]) -> GeneratorData:

    meta = root["meta"]
    generators = root["generator"]
    H = meta["horizon"]
    units = {}
    for name, u in generators["units"].items():
        units[name] = GeneratorUnit(
            name=name,
            bar=str(u.get("bar", r"{BAR_{1}}")),
            state=int(u["state"]),
            c_op=float(u["c_op"]),
            c_inv=float(u["c_inv"]),
            p_max=float(u["p_max"]),
            include_cap=bool(u["include_cap"])
        )
    return GeneratorData(
        horizon=H,
        units=units
    )


def _mk_storage_data(root: Dict[str, Any]) -> StorageData:

    storage = root["storage"]
    meta = root["meta"]
    H = meta["horizon"]
    delta_t = float(storage.get("delta_t", meta.get("delta_t", 1.0)))
    units = {}
    for name, u in storage["units"].items():
        units[name] = StorageUnit(
            name=name,
            bar=str(u.get("bar", r"{BAR_{1}}")),
            state=int(u["state"]),
            c_op=float(u["c_op"]),
            c_inv=float(u["c_inv"]),
            Emin=float(u["Emin"]),
            Emax=float(u["Emax"]),
            Eini=float(u["Eini"]),
            Pch_max=float(u["Pch_max"]),
            Pdis_max=float(u["Pdis_max"]),
            eta_c=float(u["eta_c"]),
            eta_d=float(u["eta_d"]),
        )
    return StorageData(
        horizon=H,
        units=units,
        delta_t=delta_t
    )


def _mk_connection_bar_data(root: Dict[str, Any]) -> ConnectionBarData:
    """
    Construct a ConnectionBarData object from parsed YAML root.

    Parameters
    ----------
    root : dict
        YAML-parsed dictionary containing 'meta' and 'bars' sections.

    Returns
    -------
    ConnectionBarData
        Structured dataclass containing all parsed connection bar data.
    """
    connection_bars = root["bars"]
    meta = root["meta"]
    H = meta["horizon"]
    units = {}
    for name, u in connection_bars["units"].items():
        units[name] = ConnectionBarUnit(
            name=name,
            slack=bool(u.get("slack", False)),
            Cdef=float(u.get("Cdef", 1000.0)),
            c_pmax=float(u.get("c_pmax", 10000.0)),
            demand=u.get("demand", {})
        )
    return ConnectionBarData(
        horizon=H,
        units=units
    )


def _mk_transmission_line_data(root: Dict[str, Any]) -> TransmissionLineData:
    """
    Construct a TransmissionLineData object from parsed YAML root.

    Parameters
    ----------
    root : dict
        YAML-parsed dictionary containing 'meta' and 'lines' sections.

    Returns
    -------
    TransmissionLineData
        Structured dataclass containing all parsed transmission lines data.
    """
    transmission_lines = root["lines"]
    meta = root["meta"]
    H = meta["horizon"]
    units = {}
    for name, u in transmission_lines["units"].items():
        units[name] = TransmissionLineUnit(
            name=name,
            state=int(u["state"]),
            c_op=float(u["c_op"]),
            c_inv=float(u["c_inv"]),
            model=str(u.get("model", "dc")).lower(),
            b=float(u.get("b", 0.01)),
            pmax=float(u.get("pmax", 100.0)),
            endpoints=[str(x) for x in u.get("endpoints", [])]
        )
    return TransmissionLineData(
        horizon=H,
        units=units
    )


# ============================================================================
# Master entry point
# ============================================================================


def build_balance_and_objective_from_yaml(model: ConcreteModel, yaml_data: Dict[str, Any]) -> ConcreteModel:

    # --------------------------
    # ADEQUACY CONSTRAINT
    # --------------------------
    
    add_connection_bar_capacity_constraints(model)

    # --------------------------
    # BALANCE CONSTRAINT
    # --------------------------

    add_connection_bar_balance_constraints(model)

    # --------------------------
    # OBJECTIVE FUNCTION
    # --------------------------
    cost_terms: List[Any] = []

    if 'generator' in yaml_data:
        add_generator_cost_expression(model, cost_terms)
    if 'storage' in yaml_data:
        add_storage_cost_expression(model, cost_terms)
    if 'lines' in yaml_data:
        add_transmission_line_cost_expression(model, cost_terms)
    if 'bars' in yaml_data:
        add_connection_bar_cost_expression(model, cost_terms)

    model.OBJ = Objective(expr=sum(cost_terms), sense=minimize)

    return model


def build_model_from_file(path: str) -> Tuple[ConcreteModel, Dict]:

    root = yaml_loader(path)

    if "meta" not in root:
        raise ValueError("File must contain 'meta' sections.")

    level_precedence = root["meta"]["level_precedence"]
    level_hours = root["meta"]["level_hours"]
    parcel_investment = bool(root["meta"].get("parcel_investment", False))
    interest_rate = float(root["meta"].get("interest_rate", 0.1))
    p_base = float(root["meta"].get("p_base", 1.0))
    m = ConcreteModel()

    m.p_base = p_base
    m.level_precedence = level_precedence
    m.parcel_investment = parcel_investment
    m.interest_rate = interest_rate
    m.level_hours = level_hours
    m.P = level_precedence

    # Basic validations
    _validate_meta(root["meta"])
    T = int(root["meta"]["horizon"])

    has_valid_units = False
    # first of all, the bars
    if not "bars" in root:
        # default bar - described in meta section
        _validate_demand(root["meta"]["demand"], T)
        slack = True
        Cdef = float(root["meta"]["Cdef"])
        demand = root["meta"]["demand"]
        root["bars"] = {"units": {"{BAR_{1}}": {"slack": slack,
                                                "Cdef": Cdef,
                                                "demand": demand}}}
    if "bars" in root and root["bars"] is not None:
        _validate_connection_bars(root["bars"], T, len(level_precedence))
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

    if "generator" in root and root["generator"] is not None:
        _validate_generator(root["generator"])
        generator_data = _mk_generator_data(root)
        m = add_generator_problem(m=m,
                                  data=generator_data,
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
                         "{generators, storage}.")
    m = build_balance_and_objective_from_yaml(m, root)

    return m, root
