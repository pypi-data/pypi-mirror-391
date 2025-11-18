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

from NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes import HydraulicData, HydraulicUnit
from NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder import add_hydro_problem
from NaivePyDESSEM.HydraulicGenerator.HydraulicEquations import add_hydraulic_cost_expression

from NaivePyDESSEM.ThermalGenerator.ThermalDataTypes import ThermalData, ThermalUnit
from NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder import add_thermal_problem
from NaivePyDESSEM.ThermalGenerator.ThermalEquations import add_thermal_cost_expression

from NaivePyDESSEM.RenewableGenerator.RenewableDataTypes import RenewableData, RenewableUnit
from NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder import add_renewable_problem
from NaivePyDESSEM.RenewableGenerator.RenewableEquations import add_renewable_cost_expression

from NaivePyDESSEM.Storage.StorageDataTypes import StorageData, StorageUnit
from NaivePyDESSEM.Storage.StorageBuilder import add_storage_problem
from NaivePyDESSEM.Storage.StorageEquations import add_storage_cost_expression

from NaivePyDESSEM.ConnectionBar.ConnectionBarDataTypes import ConnectionBarData, ConnectionBarUnit
from NaivePyDESSEM.ConnectionBar.ConnectionBarBuilder import add_connection_bar_problem
from NaivePyDESSEM.ConnectionBar.ConnectionBarEquations import add_connection_bar_cost_expression
from NaivePyDESSEM.ConnectionBar.ConnectionBarConstraints import add_connection_bar_balance_constraints

from NaivePyDESSEM.TransmissionLine.TransmissionLineDataTypes import TransmissionLineData, TransmissionLineUnit
from NaivePyDESSEM.TransmissionLine.TransmissionLineBuilder import add_transmission_line_problem
from NaivePyDESSEM.TransmissionLine.TransmissionLineEquations import add_transmission_line_cost_expression

from .YAMLLoader import yaml_loader

# ============================================================================
# Validators (lightweight sanity checks)
# ============================================================================


def _validate_meta(meta: Dict[str, Any]) -> None:
    """
    Validate the 'meta' section of the input dictionary.

    Ensures that the 'horizon' parameter exists and is a positive integer.

    Parameters
    ----------
    meta : dict
        Dictionary containing metadata fields, including 'horizon'.

    Raises
    ------
    ValueError
        If 'horizon' is missing, not an integer, or not positive.

    """

    horizon = meta.get("horizon")
    if not isinstance(horizon, int) or horizon <= 0:
        raise ValueError("meta.horizon must be a positive integer.")


def _validate_demand(d: Dict[Any, Any], T: int) -> None:
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

    if len(d) != T:
        raise ValueError(f"demand must have exactly {T} entries (1..{T}).")


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
        if not (u["Pmin"] <= u["Pmax"]):
            raise ValueError(
                f"thermal.units[{name}] must satisfy Pmin <= Pmax.")
        for k in ("RU", "RD"):
            if u[k] < 0:
                raise ValueError(
                    f"thermal.units[{name}].{k} must be non-negative.")


def _validate_renewable(renewable: Dict[str, Any], T: int) -> None:
    """
    Validate renewable unit generation profiles.

    Ensures that each renewable unit has a generation time series
    (gbar) of correct length.

    Parameters
    ----------
    renewable : dict
        Dictionary containing renewable units and their generation vectors.
    T : int
        Expected number of time steps.

    Raises
    ------
    ValueError
        If the length of gbar does not match the time horizon.
    """

    units = renewable.get("units", {})
    for name, u in units.items():
        g = u.get("gbar", [])
        if len(g) != T:
            raise ValueError(
                f"renewable.units[{name}].gbar must have length {T}.")


def _validate_storage(storage: Dict[str, Any]) -> None:
    """
    Validate storage unit parameters and efficiencies.

    Ensures that initial energy is within bounds, and that charge/discharge
    efficiencies are within the (0, 1] interval.

    Parameters
    ----------
    storage : dict
        Dictionary containing storage unit configurations.

    Raises
    ------
    ValueError
        If Emin > Eini > Emax is not satisfied or if η_c or η_d are invalid.
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


def _validate_connection_bars(bars: Dict[str, Any], T: int) -> None:
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
        demand = u.get("demand", [])
        if len(demand) != T:
            raise ValueError(
                f"bars.units[{name}].demand must have length {T}.")


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
    required = ['model', 'b', 'pmax', 'endpoints']

    for name, u in units.items():
        if not all(attr in u for attr in required):
            raise ValueError(
                f"lines.units[{name}] is malformed.")

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
            Vmeta=float(u["Vmeta"]),
            Vini=float(u["Vini"]),
            afluencia=[float(x) for x in u["afluencia"]],
            upstreams=u.get("upstreams", None),
            a=u.get("a", None),
            b=u.get("b", None),
            rho=u.get("rho", None),
            losses=u.get("losses", None),
            pe=u.get("pe", None),
            p=float(u.get("p", 0.0)),
            mode=u.get("mode", "constant"),
            compute_total_inflow=bool(u.get("compute_total_inflow", True)),
        )
    return HydraulicData(
        horizon=H,
        units=units,
        zeta=float(hydro.get("zeta", 9.81/1000)),
        zeta_vol=float(hydro.get("zeta_vol", 3600/1e6)),
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

    units = {}
    for name, u in thermal["units"].items():
        units[name] = ThermalUnit(
            name=name,
            bar=str(u.get("bar", r"{BAR_{1}}")),
            Pmin=float(u["Pmin"]),
            Pmax=float(u["Pmax"]),
            RU=float(u["RU"]),
            RD=float(u["RD"]),
            a=float(u.get("a", 0.0)),
            b=float(u.get("b", 0.0)),
            c=float(u.get("c", 0.0)),
            SC=float(u.get("SC", 0.0)),
            t_up=float(u.get("t_up", 1.0)),
            t_down=float(u.get("t_down", 1.0)),
            u0=int(u.get("u0", 0)),
            p0=float(u.get("p0", 0.0)),
            pw_breaks=u.get("pw_breaks", None),
            pw_costs=u.get("pw_costs", None),
            gamma=float(u.get("gamma", 0.0)),
            init_status_h=float(u.get("init_status_h", 0.0))
        )

    Rreq = None
    if "Rreq" in thermal:
        if thermal["Rreq"] is not None:
            Rreq = {int(k+1): float(v) for k, v in enumerate(thermal["Rreq"])}

    return ThermalData(
        horizon=H,
        units=units,
        Rreq=Rreq,
        has_history=meta.get("has_history", False)
    )


def _mk_renewable_data(root: Dict[str, Any]) -> RenewableData:
    """
    Construct a RenewableData object from parsed YAML root.

    Converts renewable unit generation profiles (gbar) into internal
    dataclass structure for model integration.

    Parameters
    ----------
    root : dict
        YAML-parsed dictionary containing 'meta' and 'renewable' sections.

    Returns
    -------
    RenewableData
        Structured dataclass containing all parsed renewable data.
    """

    meta = root["meta"]
    ren = root["renewable"]
    H = meta["horizon"]

    units = {}
    for name, u in ren["units"].items():
        units[name] = RenewableUnit(
            name=name,
            bar=str(u.get("bar", r"{BAR_{1}}")),
            gbar=[float(x) for x in u["gbar"]],
        )

    return RenewableData(
        horizon=H,
        units=units,
    )


def _mk_storage_data(root: Dict[str, Any]) -> StorageData:
    """
    Construct a StorageData object from parsed YAML root.

    Extracts energy limits, initial conditions, and charge/discharge constraints
    into a structured dataclass for use in the storage submodel.

    Parameters
    ----------
    root : dict
        YAML-parsed dictionary containing 'meta' and 'storage' sections.

    Returns
    -------
    StorageData
        Structured dataclass containing all parsed storage data.
    """

    storage = root["storage"]
    meta = root["meta"]
    H = meta["horizon"]
    delta_t = float(storage.get("delta_t", meta.get("delta_t", 1.0)))
    units = {}
    for name, u in storage["units"].items():
        units[name] = StorageUnit(
            name=name,
            bar=str(u.get("bar", r"{BAR_{1}}")),
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
        delta_t=delta_t,
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
            demand=[float(x) for x in u.get("demand", [])]
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
        more of {hydro, thermal, renewable, storage, bars, lines}.

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

    if "meta" not in root:
        raise ValueError("File must contain 'meta' section.")

    m = ConcreteModel()
    m.p_base = float(root["meta"].get("p_base", 1.0))

    balance_expressions = []

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
        demand = [float(x) for x in root["meta"]["demand"]]
        root["bars"] = {"units": {"{BAR_{1}}":{"slack": slack,
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
                                objective="miqp",  # deprecated
                                include_reserve=thermal_data.Rreq is not None,
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
                         "{hydro, thermal, renewable, storage, bars, lines}.")
    m = build_balance_and_objective_from_yaml(m, root)

    return m, root
