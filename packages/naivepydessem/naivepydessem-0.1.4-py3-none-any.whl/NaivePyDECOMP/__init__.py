
"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Package: NaivePyDECOMP

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
The ``NaivePyDECOMP`` package provides a modular, extensible, and pedagogically
oriented framework for short-term power system operation planning. Inspired by the
methodology and architecture of CEPEL’s DESSEM model, it enables the construction,
solution, and analysis of mixed-integer optimization models based on Pyomo.

Designed for academic use, the framework supports detailed modeling of thermal,
hydraulic, renewable, and storage resources, and integrates these components
into a coherent multi-technology dispatch problem, including unit commitment,
deficit handling, and economic trade-offs.

Submodules
----------
HydraulicGenerator
    Defines the data structures, constraints, and productivity models for
    hydropower generation units, including reservoir dynamics, turbine flows,
    and different formulations of head and productivity (constant, specific, exact).
    
ThermalGenerator
    Models thermal units with quadratic or piecewise-linear cost functions,
    ramping constraints, commitment logic, startup/shutdown dynamics, and reserve provision.
    
RenewableGenerator
    Represents non-dispatchable renewable units such as wind and solar,
    enforcing production bounds based on availability (gbar).
    
Storage
    Models energy storage systems (e.g., batteries), capturing state-of-charge dynamics,
    charge/discharge power limits, efficiencies, and optional integration into
    the balance and objective.

ConnectionBar (New in version 0.1.4)
    Represents the nodal structure of the network, defining the electrical buses (bars) 
    that aggregate demand, generation, deficit, and angular reference variables. Provides sets,
    parameters, variables, and constraints for the nodal balance equations in MW, with optional 
    angular limits and slack-bar reference handling.

TransmissionLine (New in version 0.1.4)
    Models the physical interconnections between bars, using the DC power flow or transport 
    formulations. Defines sets, parameters, and variables for line flows, susceptances,
    capacities, and investment states, including both existing  and candidate circuits. 
    Fully compatible with hybrid DC/transport network representations.

YAMLLoader
    Provides the interface for loading problem instances from structured YAML or JSON files,
    including validation and conversion into dataclass objects.

Builder
    Constructs a complete Pyomo model from the YAML data, invoking the appropriate
    subsystems and assembling the balance constraint and cost-minimizing objective.

Solver
    Handles the selection and execution of solvers (e.g., GLPK, IPOPT, MindtPy),
    with optional reporting and solution validation.

DataFrames
    Exports decision variable trajectories and economic indicators to Pandas DataFrames
    for further analysis and visualization.

PlotSeries
    Generates basic time-series plots of dispatch results using Matplotlib.

Utils, Formatters, Reporting
    Auxiliary modules for formatting, printing summaries, validating model structure,
    and providing colored console outputs using Colorama.

Notes
-----
- The package is intentionally modular: each subsystem (Thermal, Hydro, Renewable, Storage)
  can be activated or omitted via the YAML interface.
- While conceptually aligned with DESSEM, the implementation is simplified and transparent,
  allowing students and researchers to explore, extend, and test new ideas.
- Extensions such as emission penalties, pumped storage, stochastic scenarios,
  or multi-area coupling can be added atop this foundation.
- Fully compatible with Pyomo’s expressive modeling capabilities and solver interface.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from .HydraulicGenerator import *
from .ThermalGenerator import *
from .RenewableGenerator import *
from .Storage import *
from .ConnectionBar import *
from .TransmissionLine import *
from .DataFrames import *
from .PlotSeries import *
from .Utils import *
from .Formatters import *
from .ModelCheck import *
from .ModelFormatters import *
from .Reporting import *
from .YAMLLoader import *
from .Builder import *
from .Solver import *
