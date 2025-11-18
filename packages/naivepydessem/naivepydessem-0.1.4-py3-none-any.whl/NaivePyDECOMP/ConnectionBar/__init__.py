"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: ConnectionBar

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
The ``ConnectionBar`` package defines a modular abstraction of electrical
connection bars (buses) for DC power flow formulations within Pyomo-based
optimization frameworks. It encapsulates data structures, variable
definitions, constraint formulations, symbolic equation builders, and
model assembly routines used in operation and expansion studies such as
DECOMP, DESSEM, and the MDI model.

Modules
-------
ConnectionBarDataTypes
    Defines the data classes (:class:`ConnectionBarUnit`,
    :class:`ConnectionBarData`) that describe the electrical and
    operational attributes of each bar, including demand, state,
    and slack configuration.

ConnectionBarVars
    Declares sets, parameters, and decision variables for connection bars,
    such as phase angles (``θ_b``) and deficit variables (``D[b,t]``),
    ensuring consistency with system-wide formulations.

ConnectionBarConstraints
    Implements the physical and operational constraints of the subsystem:
    - Slack-bar reference condition (θ = 0)
    - Angular limits for non-slack bars (−π ≤ θ ≤ π)
    - Nodal power balance (Kirchhoff’s 1st Law)

ConnectionBarEquations
    Provides modular symbolic expression builders used to assemble the
    nodal power balance equation by integrating hydro, thermal, renewable,
    storage, and transmission contributions.

ConnectionBarBuilder
    High-level model constructor that orchestrates all components,
    producing a complete Pyomo ``ConcreteModel`` configured with the
    relevant sets, variables, and constraints for each connection bar.

Notes
-----
- The package is designed for hierarchical integration with higher-level
  systems involving generation and transmission models.
- It serves as the foundation for hybrid and multi-bar DC formulations
  in short-term (DESSEM), medium-term (DECOMP), and long-term (MDI)
  optimization contexts.
- Each module can be used independently or assembled through
  :func:`build_connection_bars`.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from .ConnectionBarDataTypes import *
from .ConnectionBarVars import *
from .ConnectionBarConstraints import *
from .ConnectionBarEquations import *
from .ConnectionBarBuilder import *
