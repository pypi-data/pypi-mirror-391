"""
YAMLLoader Module
=================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
The **YAMLLoader** module provides standardized routines for reading,
validating, and parsing YAML-based configuration files used by the
**MDI (Modular Decision Infrastructure)** system. It ensures consistency,
traceability, and reliability in loading structured model data such as
meta parameters, generator definitions, and storage configurations.

Description
-----------
YAML files serve as the primary data input format for the MDI model.
This module abstracts the YAML parsing logic to provide a clean,
reliable interface that returns a fully validated Python dictionary,
suitable for immediate use by the :mod:`Builder` module and its
subcomponents.

By encapsulating file I/O operations and schema consistency checks,
the **YAMLLoader** guarantees that the optimization routines receive
complete and well-structured data, preventing common runtime errors
related to malformed inputs.

Functions
---------
yaml_loader(path: str) -> dict
    Reads and parses a YAML configuration file located at the specified path.
    Returns a structured Python dictionary suitable for direct use by
    the model builder.

Notes
-----
- Requires the **PyYAML** library (≥ 6.0).  
- The loader assumes UTF-8 encoding by default.  
- It is strongly recommended that YAML configurations follow
  a consistent hierarchical schema:
  

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.YAMLLoader import yaml_loader