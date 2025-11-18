"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Configuration Pre-Processor for Model Inputs

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Utilities to load and normalize model configuration files (YAML/JSON) before
instantiating optimization models. The module provides:

1) A LaTeX-friendly renaming utility for unit identifiers, preserving downstream 
   compatibility with report/plot labels.
2) A deep-copy pre-processor that standardizes sections and optionally transforms
   unit names and their upstreams references.
3) A YAML loader that combines parsing and pre-processing into a single entry point.

This pre-processing ensures consistent, side-effect-free structures that are
directly consumable by subsequent builders (hydro, thermal, renewable, storage).

Functions
---------
key_replace(key)
    Convert identifiers for LaTeX.
pre_process(config_dict, transform_names=True)
    Deep-copy and normalize a configuration dictionary, optionally transforming
    unit names and upstream references in sections that contain units.
yaml_loader(file, transform_names=True)
    Load a YAML file and return a processed configuration dictionary suitable
    for model building.

Notes
-----
- Only the **first** underscore in an identifier is used to create the subscript;
  remaining underscores are kept verbatim inside the subscript block.
- Sections without a units field are copied verbatim.
- All operations are performed on deep copies; the original inputs are not modified.

Examples
--------
>>> cfg = yaml_loader("case.yaml", transform_names=True)
>>> list(cfg["hydro"]["units"].keys())
['{UHE_{1}}', '{UHE_{2}}']

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from __future__ import annotations

import copy
from typing import Any, Dict
import yaml


def key_replace(key: str) -> str:
    """
    Convert a unit identifier of the form NAME_index into a LaTeX-friendly
    token with a braced subscript.

    The function partitions the input at the first underscore and returns
    the formatted string {HEAD_{TAIL}}. If the input contains no
    underscore, the original key is returned unchanged.

    Parameters
    ----------
    key : str
        Unit identifier, typically in the form "PLANT_1" or "UT_10".

    Returns
    -------
    str
        The LaTeX-ready identifier. For example, "UT_10" becomes
        "{UT_{10}}". If no underscore is present, the function returns
        the input key unmodified.

    Examples
    --------
    >>> key_replace("UHE_1")
    '{UHE_{1}}'
    >>> key_replace("UT10")
    'UT10'
    >>> key_replace("PLANT_UNIT_1")
    '{PLANT_{UNIT_1}}'

    Notes
    -----
    Only the first underscore is considered for partitioning; the remainder
    of the string (including additional underscores) is kept verbatim inside
    the subscript block.
    """
    head, sep, tail = key.partition("_")
    if not sep:
        return key
    return f"{{{head}_{{{tail}}}}}"

def _transform_units(
    units: Dict[str, Dict[str, Any]], *, transform_names: bool
) -> Dict[str, Dict[str, Any]]:
    """
    Rename unit identifiers and optionally transform their upstream references.

    This function processes a dictionary of units, typically found in
    sections such as hydro, thermal, or renewable of a model
    configuration. Each unit key may be reformatted using the `key_replace`
    function to produce LaTeX-compatible identifiers. In addition, if the
    unit data includes an upstreams field, its entries are likewise
    transformed to match the new naming.

    If `transform_names` is set to False, all unit names and upstreams are
    preserved as-is, and only a deep copy of the input structure is returned.

    Parameters
    ----------
    units : dict of str -> dict
        A dictionary mapping unit names (e.g., "UHE_1") to their respective
        parameter dictionaries.
    transform_names : bool
        If True, unit names and upstream references are reformatted using
        LaTeX-compliant subscripts via `key_replace`. If False, original
        names are preserved and only deep-copying is performed.

    Returns
    -------
    dict of str -> dict
        A new dictionary where unit keys (and any 'upstreams' lists) have been
        processed according to the `transform_names` flag. The original input
        is never modified.

    Examples
    --------
    >>> units = {
    ...     "UHE_1": {"Qmin": 0, "upstreams": ["UHE_0"]},
    ...     "UHE_2": {"Qmin": 5, "upstreams": []}
    ... }
    >>> _transform_units(units, transform_names=True)
    {'{UHE_{1}}': {'Qmin': 0, 'upstreams': ['{UHE_{0}}']},
     '{UHE_{2}}': {'Qmin': 5, 'upstreams': []}}

    Notes
    -----
    - The function assumes that `units` is a flat dictionary (non-nested by time).
    - If any unit entry lacks the 'upstreams' field, no transformation is applied to it.
    - This function is typically called internally during model pre-processing.
    """

    out: Dict[str, Dict[str, Any]] = {}
    for unit, data in units.items():
        new_key = key_replace(unit) if transform_names else unit
        value = copy.deepcopy(data)
        if isinstance(value, dict):
            if "upstreams" in value and value["upstreams"] is not None:
                value["upstreams"] = (
                    [key_replace(u) for u in value["upstreams"]] if transform_names
                    else list(value["upstreams"])
                )
            if "bar" in value and value["bar"] is not None:
                value["bar"] = key_replace(value["bar"]) if transform_names else value["bar"]
            if 'endpoints' in value and value['endpoints'] is not None:
                value["endpoints"] = (
                    [key_replace(u) for u in value["endpoints"]] if transform_names
                    else list(value["endpoints"])
                )
        out[new_key] = value
    return out


def pre_process(config_dict: Dict[str, Any], *, transform_names: bool = True) -> Dict[str, Any]:
    """
    Construct a processed configuration dictionary from raw input, with optional name transformation.

    This function prepares a structured configuration dictionary for modeling use by:
    
    - copying the meta section unchanged,
    - applying deep copies to all other sections,
    - and optionally transforming unit names and upstream references in each section
      that contains a units block (e.g., hydro, thermal, renewable).

    The transformation of unit names and upstream references
    is controlled by the transform_names flag. The function does not modify the input
    dictionary in-place.

    Parameters
    ----------
    config_dict : dict
        Raw configuration dictionary loaded from a YAML file or equivalent source.
        Expected to contain a meta section and any number of other sections such as
        hydro, thermal, renewable, or storage.
    transform_names : bool, optional
        Whether to apply LaTeX-compatible formatting to unit names and upstreams
        using key_replace. If False, names are preserved as-is.
        Default is True.

    Returns
    -------
    dict
        A fully processed configuration dictionary with all subsections and units
        properly structured. The returned dictionary is a deep copy and does not
        share references with the input.

    Examples
    --------
    >>> pre_process({
    ...     "meta": {"horizon": 24},
    ...     "hydro": {
    ...         "units": {
    ...             "UHE_1": {"Qmin": 0.0, "upstreams": ["UHE_0"]}
    ...         }
    ...     }
    ... }, transform_names=True)
    {'meta': {'horizon': 24},
     'hydro': {
         'units': {
             '{UHE_{1}}': {'Qmin': 0.0, 'upstreams': ['{UHE_{0}}']}
         }
     }}

    Notes
    -----
    - Sections without a units field are copied verbatim.
    - If units is present but not a dictionary, it is ignored safely.
    - This function is intended as a preprocessing step before model instantiation.
    """

    result: Dict[str, Any] = {}
    for section, value in config_dict.items():
        if section == "meta":
            result["meta"] = copy.deepcopy(value)
            continue

        if isinstance(value, dict):
            section_copy = {k: copy.deepcopy(v) for k, v in value.items() if k != "units"}
            if "units" in value and isinstance(value["units"], dict):
                section_copy["units"] = _transform_units(
                    value["units"], transform_names=transform_names
                )
            result[section] = section_copy
        else:
            result[section] = copy.deepcopy(value)
    return result


def yaml_loader(file: str, *, transform_names: bool = True) -> Dict[str, Any]:
    """
    Load a YAML configuration file and apply structural pre-processing.

    This function reads a YAML-formatted file and parses it into a Python dictionary.
    After loading, it invokes the `pre_process` routine to deep-copy all sections,
    standardize the structure, and optionally apply LaTeX-style name transformations
    to unit identifiers and upstream references.

    The resulting configuration is ready for use in optimization models or simulation
    routines that require consistent internal naming and indexing.

    Parameters
    ----------
    file : str
        Path to the YAML file containing the case configuration.
    transform_names : bool, optional
        Whether to apply LaTeX-friendly formatting to unit names (e.g., UT_1 => {UT_{1}})
        and update upstream references accordingly. If False, original names are preserved.
        Default is True.

    Returns
    -------
    dict
        A processed configuration dictionary with all metadata and units structured
        consistently. This dictionary is independent of the raw file contents.

    Raises
    ------
    ValueError
        If the YAML file is empty, malformed, or does not contain a valid dictionary structure.

    Examples
    --------
    >>> config = yaml_loader("caso.yaml")
    >>> config["hydro"]["units"].keys()
    dict_keys(['{UHE_{1}}', '{UHE_{2}}'])

    Notes
    -----
    - The input file must be UTF-8 encoded and must define a top-level dictionary.
    - All nested structures are copied safely; no mutation occurs on the raw parsed data.
    - This function is the recommended entry point for loading structured model input files.
    """

    with open(file, "r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if data is None:
        raise ValueError("Arquivo YAML vazio ou inválido.")
    return pre_process(data, transform_names=transform_names)
