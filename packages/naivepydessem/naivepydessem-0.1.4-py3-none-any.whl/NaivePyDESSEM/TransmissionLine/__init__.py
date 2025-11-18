"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: TransmissionLine

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
The ``TransmissionLine`` package defines the modular representation of
transmission circuits for DC power flow formulations within Pyomo-based
optimization frameworks. It encapsulates the data structures, variables,
symbolic equations, constraints, and builder routines that describe the
physical and operational behavior of power transmission networks.

Modules
-------
TransmissionLineDataTypes
    Defines the data classes (:class:`TransmissionLineUnit`,
    :class:`TransmissionLineData`) describing the physical and
    economic characteristics of each circuit, including
    susceptance, power limits, and endpoints.
TransmissionLineVars
    Declares decision variables associated with transmission lines,
    such as active power flow for each line and time period.
TransmissionLineEquations
    Provides symbolic equations that express DC power flow relations
    and nodal contributions of line flows to system balance.
TransmissionLineConstraints
    Implements physical constraints for transmission lines:
    - DC flow definition: ``F_ij,t = b_ij (θ_i,t − θ_j,t)``
    - For transport model power flow is just as is
    - Symmetric flow limits: ``−pmax_ij ≤ F_ij,t ≤ pmax_ij``
TransmissionLineBuilder
    High-level model constructor that integrates variables and
    constraints, assembling the complete transmission-line
    subsystem for DC power flow models.

Notes
-----
- The package is designed for hierarchical integration with
  :mod:`ConnectionBar` modules, forming the complete DC power
  flow network.
- The formulation supports both operational (fixed network)
  and expansion (candidate lines) applications, consistent
  with the methodologies of DECOMP, DESSEM, and MDI.
- Each module can be used independently or through the
  unified builder :func:`build_transmission_lines`.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from .TransmissionLineDataTypes import *
from .TransmissionLineVars import *
from .TransmissionLineEquations import *
from .TransmissionLineConstraints import *
from .TransmissionLineBuilder import *
