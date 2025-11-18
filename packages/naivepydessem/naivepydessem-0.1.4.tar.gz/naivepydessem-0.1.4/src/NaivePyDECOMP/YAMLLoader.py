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
from NaivePyDESSEM.YAMLLoader import (
    yaml_loader
)
