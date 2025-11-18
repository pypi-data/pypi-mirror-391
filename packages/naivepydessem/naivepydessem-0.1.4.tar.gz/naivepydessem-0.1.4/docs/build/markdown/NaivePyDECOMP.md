# NaivePyDECOMP package

## Module contents

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: NaivePyDECOMP

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

The `NaivePyDECOMP` package provides a modular, extensible, and pedagogically
oriented framework for short-term power system operation planning. Inspired by the
methodology and architecture of CEPEL’s DESSEM model, it enables the construction,
solution, and analysis of mixed-integer optimization models based on Pyomo.

Designed for academic use, the framework supports detailed modeling of thermal,
hydraulic, renewable, and storage resources, and integrates these components
into a coherent multi-technology dispatch problem, including unit commitment,
deficit handling, and economic trade-offs.

### Submodules

HydraulicGenerator
: Defines the data structures, constraints, and productivity models for
  hydropower generation units, including reservoir dynamics, turbine flows,
  and different formulations of head and productivity (constant, specific, exact).

ThermalGenerator
: Models thermal units with quadratic or piecewise-linear cost functions,
  ramping constraints, commitment logic, startup/shutdown dynamics, and reserve provision.

RenewableGenerator
: Represents non-dispatchable renewable units such as wind and solar,
  enforcing production bounds based on availability (gbar).

Storage
: Models energy storage systems (e.g., batteries), capturing state-of-charge dynamics,
  charge/discharge power limits, efficiencies, and optional integration into
  the balance and objective.

YAMLLoader
: Provides the interface for loading problem instances from structured YAML or JSON files,
  including validation and conversion into dataclass objects.

Builder
: Constructs a complete Pyomo model from the YAML data, invoking the appropriate
  subsystems and assembling the balance constraint and cost-minimizing objective.

Solver
: Handles the selection and execution of solvers (e.g., GLPK, IPOPT, MindtPy),
  with optional reporting and solution validation.

DataFrames
: Exports decision variable trajectories and economic indicators to Pandas DataFrames
  for further analysis and visualization.

PlotSeries
: Generates basic time-series plots of dispatch results using Matplotlib.

Utils, Formatters, Reporting
: Auxiliary modules for formatting, printing summaries, validating model structure,
  and providing colored console outputs using Colorama.

### Notes

- The package is intentionally modular: each subsystem (Thermal, Hydro, Renewable, Storage)
  can be activated or omitted via the YAML interface.
- While conceptually aligned with DESSEM, the implementation is simplified and transparent,
  allowing students and researchers to explore, extend, and test new ideas.
- Extensions such as emission penalties, pumped storage, stochastic scenarios,
  or multi-area coupling can be added atop this foundation.
- Fully compatible with Pyomo’s expressive modeling capabilities and solver interface.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## Subpackages

* [NaivePyDECOMP.HydraulicGenerator package](NaivePyDECOMP.HydraulicGenerator.md)
  * [Module contents](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator)
    * [Author](NaivePyDECOMP.HydraulicGenerator.md#author)
    * [Description](NaivePyDECOMP.HydraulicGenerator.md#description)
    * [Submodules](NaivePyDECOMP.HydraulicGenerator.md#submodules)
  * [Submodules](NaivePyDECOMP.HydraulicGenerator.md#id1)
  * [NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints)
    * [Hydropower Constraints Module for Multi-Mode Generation Modeling](NaivePyDECOMP.HydraulicGenerator.md#hydropower-constraints-module-for-multi-mode-generation-modeling)
      * [Imported Dependencies](NaivePyDECOMP.HydraulicGenerator.md#imported-dependencies)
      * [Functions](NaivePyDECOMP.HydraulicGenerator.md#functions)
      * [Model Requirements](NaivePyDECOMP.HydraulicGenerator.md#model-requirements)
    * [`add_hydro_volume_continuity_constraint()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_continuity_constraint)
  * [NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes)
    * [Description](NaivePyDECOMP.HydraulicGenerator.md#id2)
    * [Overview](NaivePyDECOMP.HydraulicGenerator.md#overview)
    * [Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#conventions-and-units)
    * [`HydraulicData`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)
      * [`HydraulicData.Cdef`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData.Cdef)
      * [`HydraulicData.demand`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData.demand)
      * [`HydraulicData.horizon`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData.horizon)
      * [`HydraulicData.units`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData.units)
    * [`HydraulicUnit`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)
      * [`HydraulicUnit.Qmax`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Qmax)
      * [`HydraulicUnit.Qmin`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Qmin)
      * [`HydraulicUnit.Vini`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Vini)
      * [`HydraulicUnit.Vmax`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Vmax)
      * [`HydraulicUnit.Vmin`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Vmin)
      * [`HydraulicUnit.afluencia`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.afluencia)
      * [`HydraulicUnit.compute_total_inflow`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.compute_total_inflow)
      * [`HydraulicUnit.name`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.name)
      * [`HydraulicUnit.p`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.p)
      * [`HydraulicUnit.upstreams`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.upstreams)
  * [NaivePyDECOMP.HydraulicGenerator.HydraulicEquations module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicEquations)
    * [Author](NaivePyDECOMP.HydraulicGenerator.md#id3)
    * [Description](NaivePyDECOMP.HydraulicGenerator.md#id4)
    * [Intended Use](NaivePyDECOMP.HydraulicGenerator.md#intended-use)
  * [NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder)
    * [Description](NaivePyDECOMP.HydraulicGenerator.md#id5)
    * [Supported generation modes (per unit)](NaivePyDECOMP.HydraulicGenerator.md#supported-generation-modes-per-unit)
    * [Functions](NaivePyDECOMP.HydraulicGenerator.md#id6)
    * [Modeling Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#modeling-conventions-and-units)
    * [`add_hydro_problem()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_problem)
    * [`add_hydro_subproblem()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_subproblem)
    * [`build_FPHs()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.build_FPHs)
    * [`build_hydro_dispatch()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.build_hydro_dispatch)
  * [NaivePyDECOMP.HydraulicGenerator.HydraulicObjectives module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicObjectives)
    * [Description](NaivePyDECOMP.HydraulicGenerator.md#id7)
    * [Functions](NaivePyDECOMP.HydraulicGenerator.md#id8)
    * [Modeling Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#id9)
  * [NaivePyDECOMP.HydraulicGenerator.HydraulicVars module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicVars)
    * [Description](NaivePyDECOMP.HydraulicGenerator.md#id10)
    * [Functions](NaivePyDECOMP.HydraulicGenerator.md#id11)
    * [Modeling Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#id12)
    * [`hydraulyc_add_sets_and_params()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicVars.hydraulyc_add_sets_and_params)
  * [NaivePyDECOMP.HydraulicGenerator.SimplifiedConstantProductivityFPH module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.SimplifiedConstantProductivityFPH)
    * [Author](NaivePyDECOMP.HydraulicGenerator.md#id13)
    * [Description](NaivePyDECOMP.HydraulicGenerator.md#id14)
* [NaivePyDECOMP.RenewableGenerator package](NaivePyDECOMP.RenewableGenerator.md)
  * [Module contents](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator)
    * [Author](NaivePyDECOMP.RenewableGenerator.md#author)
    * [Description](NaivePyDECOMP.RenewableGenerator.md#description)
    * [Submodules](NaivePyDECOMP.RenewableGenerator.md#submodules)
  * [Submodules](NaivePyDECOMP.RenewableGenerator.md#id1)
  * [NaivePyDECOMP.RenewableGenerator.RenewableConstraints module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableConstraints)
    * [Author](NaivePyDECOMP.RenewableGenerator.md#id2)
    * [Description](NaivePyDECOMP.RenewableGenerator.md#id3)
    * [Functions](NaivePyDECOMP.RenewableGenerator.md#functions)
  * [NaivePyDECOMP.RenewableGenerator.RenewableDataTypes module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableDataTypes)
    * [Author](NaivePyDECOMP.RenewableGenerator.md#id4)
    * [Description](NaivePyDECOMP.RenewableGenerator.md#id5)
    * [Classes](NaivePyDECOMP.RenewableGenerator.md#classes)
  * [NaivePyDECOMP.RenewableGenerator.RenewableEquations module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableEquations)
    * [Author](NaivePyDECOMP.RenewableGenerator.md#id6)
    * [Description](NaivePyDECOMP.RenewableGenerator.md#id7)
    * [Intended Use](NaivePyDECOMP.RenewableGenerator.md#intended-use)
  * [NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder)
    * [Author](NaivePyDECOMP.RenewableGenerator.md#id8)
    * [Description](NaivePyDECOMP.RenewableGenerator.md#id9)
    * [Functions](NaivePyDECOMP.RenewableGenerator.md#id10)
    * [`add_renewable_subproblem()`](NaivePyDECOMP.RenewableGenerator.md#NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder.add_renewable_subproblem)
  * [NaivePyDECOMP.RenewableGenerator.RenewableObjectives module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableObjectives)
    * [Author](NaivePyDECOMP.RenewableGenerator.md#id11)
    * [Description](NaivePyDECOMP.RenewableGenerator.md#id12)
    * [Functions](NaivePyDECOMP.RenewableGenerator.md#id13)
  * [NaivePyDECOMP.RenewableGenerator.RenewableVars module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableVars)
    * [Author](NaivePyDECOMP.RenewableGenerator.md#id14)
    * [Description](NaivePyDECOMP.RenewableGenerator.md#id15)
    * [Functions](NaivePyDECOMP.RenewableGenerator.md#id16)
* [NaivePyDECOMP.Storage package](NaivePyDECOMP.Storage.md)
  * [Module contents](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage)
    * [Author](NaivePyDECOMP.Storage.md#author)
    * [Description](NaivePyDECOMP.Storage.md#description)
    * [Submodules](NaivePyDECOMP.Storage.md#submodules)
  * [Submodules](NaivePyDECOMP.Storage.md#id1)
  * [NaivePyDECOMP.Storage.StorageBuilder module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageBuilder)
    * [Author](NaivePyDECOMP.Storage.md#id2)
    * [Description](NaivePyDECOMP.Storage.md#id3)
    * [Functions](NaivePyDECOMP.Storage.md#functions)
    * [`add_storage_subproblem()`](NaivePyDECOMP.Storage.md#NaivePyDECOMP.Storage.StorageBuilder.add_storage_subproblem)
  * [NaivePyDECOMP.Storage.StorageConstraints module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageConstraints)
    * [Author](NaivePyDECOMP.Storage.md#id4)
    * [Description](NaivePyDECOMP.Storage.md#id5)
    * [Functions](NaivePyDECOMP.Storage.md#id6)
  * [NaivePyDECOMP.Storage.StorageDataTypes module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageDataTypes)
    * [Author](NaivePyDECOMP.Storage.md#id7)
    * [Description](NaivePyDECOMP.Storage.md#id8)
    * [Classes](NaivePyDECOMP.Storage.md#classes)
  * [NaivePyDECOMP.Storage.StorageEquations module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageEquations)
    * [Author](NaivePyDECOMP.Storage.md#id9)
    * [Description](NaivePyDECOMP.Storage.md#id10)
    * [Intended Use](NaivePyDECOMP.Storage.md#intended-use)
  * [NaivePyDECOMP.Storage.StorageObjective module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageObjective)
    * [Author](NaivePyDECOMP.Storage.md#id11)
    * [Description](NaivePyDECOMP.Storage.md#id12)
    * [Functions](NaivePyDECOMP.Storage.md#id13)
  * [NaivePyDECOMP.Storage.StorageVars module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageVars)
    * [Author](NaivePyDECOMP.Storage.md#id14)
    * [Description](NaivePyDECOMP.Storage.md#id15)
    * [Functions](NaivePyDECOMP.Storage.md#id16)
* [NaivePyDECOMP.ThermalGenerator package](NaivePyDECOMP.ThermalGenerator.md)
  * [Module contents](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator)
    * [Author](NaivePyDECOMP.ThermalGenerator.md#author)
    * [Description](NaivePyDECOMP.ThermalGenerator.md#description)
    * [Submodules](NaivePyDECOMP.ThermalGenerator.md#submodules)
  * [Submodules](NaivePyDECOMP.ThermalGenerator.md#id1)
  * [NaivePyDECOMP.ThermalGenerator.ThermalConstraints module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalConstraints)
    * [Author](NaivePyDECOMP.ThermalGenerator.md#id2)
    * [Description](NaivePyDECOMP.ThermalGenerator.md#id3)
    * [Constraint Families](NaivePyDECOMP.ThermalGenerator.md#constraint-families)
    * [Usage](NaivePyDECOMP.ThermalGenerator.md#usage)
    * [`thermal_add_balance_constraint()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalConstraints.thermal_add_balance_constraint)
    * [`thermal_add_capacity_constraint()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalConstraints.thermal_add_capacity_constraint)
  * [NaivePyDECOMP.ThermalGenerator.ThermalDataTypes module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalDataTypes)
    * [Author](NaivePyDECOMP.ThermalGenerator.md#id4)
    * [Description](NaivePyDECOMP.ThermalGenerator.md#id5)
    * [Notation (per unit g and time t)](NaivePyDECOMP.ThermalGenerator.md#notation-per-unit-g-and-time-t)
    * [Typical objective (MIQP form)](NaivePyDECOMP.ThermalGenerator.md#typical-objective-miqp-form)
    * [Usage](NaivePyDECOMP.ThermalGenerator.md#id6)
    * [Intended pairing](NaivePyDECOMP.ThermalGenerator.md#intended-pairing)
    * [`ThermalData`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)
      * [`ThermalData.Cdef`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData.Cdef)
      * [`ThermalData.demand`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData.demand)
      * [`ThermalData.horizon`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData.horizon)
      * [`ThermalData.units`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData.units)
    * [`ThermalUnit`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit)
      * [`ThermalUnit.Cost`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit.Cost)
      * [`ThermalUnit.Gmax`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit.Gmax)
      * [`ThermalUnit.Gmin`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit.Gmin)
      * [`ThermalUnit.name`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit.name)
  * [NaivePyDECOMP.ThermalGenerator.ThermalEquations module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalEquations)
    * [Author](NaivePyDECOMP.ThermalGenerator.md#id7)
    * [Description](NaivePyDECOMP.ThermalGenerator.md#id8)
    * [Intended Use](NaivePyDECOMP.ThermalGenerator.md#intended-use)
    * [`add_thermal_balance_expression()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalEquations.add_thermal_balance_expression)
    * [`add_thermal_cost_expression()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalEquations.add_thermal_cost_expression)
  * [NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder)
    * [Author](NaivePyDECOMP.ThermalGenerator.md#id9)
    * [Description](NaivePyDECOMP.ThermalGenerator.md#id10)
    * [Builder Function](NaivePyDECOMP.ThermalGenerator.md#builder-function)
    * [Usage](NaivePyDECOMP.ThermalGenerator.md#id11)
    * [`add_thermal_problem()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_problem)
    * [`add_thermal_subproblem()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_subproblem)
    * [`build_thermal_uc()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.build_thermal_uc)
    * [`thermo_update_model()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.thermo_update_model)
  * [NaivePyDECOMP.ThermalGenerator.ThermalObjectives module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalObjectives)
    * [Author](NaivePyDECOMP.ThermalGenerator.md#id12)
    * [Description](NaivePyDECOMP.ThermalGenerator.md#id13)
    * [Usage](NaivePyDECOMP.ThermalGenerator.md#id14)
    * [`set_objective_thermo()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalObjectives.set_objective_thermo)
  * [NaivePyDECOMP.ThermalGenerator.ThermalVars module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalVars)
    * [Author](NaivePyDECOMP.ThermalGenerator.md#id15)
    * [Description](NaivePyDECOMP.ThermalGenerator.md#id16)
    * [Features](NaivePyDECOMP.ThermalGenerator.md#features)
    * [Variables](NaivePyDECOMP.ThermalGenerator.md#variables)
    * [Usage](NaivePyDECOMP.ThermalGenerator.md#id17)
    * [`thermal_add_sets_and_params()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalVars.thermal_add_sets_and_params)
    * [`thermal_add_variables_uc()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalVars.thermal_add_variables_uc)
* [NaivePyDECOMP.cli package](NaivePyDECOMP.cli.md)
  * [Module contents](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli)
    * [NaivePyDECOMP – CLI Subpackage](NaivePyDECOMP.cli.md#naivepydecomp-cli-subpackage)
      * [Author](NaivePyDECOMP.cli.md#author)
      * [Description](NaivePyDECOMP.cli.md#description)
      * [Modules](NaivePyDECOMP.cli.md#modules)
      * [Features](NaivePyDECOMP.cli.md#features)
      * [Example Usage](NaivePyDECOMP.cli.md#example-usage)
  * [Submodules](NaivePyDECOMP.cli.md#submodules)
  * [NaivePyDECOMP.cli.cli module](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli.cli)
    * [Author](NaivePyDECOMP.cli.md#id1)
    * [Description](NaivePyDECOMP.cli.md#id2)
    * [Features](NaivePyDECOMP.cli.md#id3)
    * [Dependencies](NaivePyDECOMP.cli.md#dependencies)
    * [Usage](NaivePyDECOMP.cli.md#usage)
    * [`main()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.cli.main)
    * [`print_welcome_banner()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.cli.print_welcome_banner)
    * [`save_dataframe()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.cli.save_dataframe)
  * [NaivePyDECOMP.cli.pddd_cli module](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli.pddd_cli)
    * [Author](NaivePyDECOMP.cli.md#id4)
    * [Description](NaivePyDECOMP.cli.md#id5)
    * [Features](NaivePyDECOMP.cli.md#id6)
    * [Dependencies](NaivePyDECOMP.cli.md#id7)
    * [Usage](NaivePyDECOMP.cli.md#id8)
    * [`main()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.pddd_cli.main)
    * [`print_welcome_banner()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.pddd_cli.print_welcome_banner)
    * [`save_dataframe()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.pddd_cli.save_dataframe)
  * [NaivePyDECOMP.cli.plot_cli module](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli.plot_cli)
    * [Author](NaivePyDECOMP.cli.md#id9)
    * [Description](NaivePyDECOMP.cli.md#id10)
    * [Features](NaivePyDECOMP.cli.md#id11)
    * [Categories](NaivePyDECOMP.cli.md#categories)
    * [Dependencies](NaivePyDECOMP.cli.md#id12)
    * [Usage](NaivePyDECOMP.cli.md#id13)
    * [Quick examples](NaivePyDECOMP.cli.md#quick-examples)
    * [`handle_plot()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.handle_plot)
    * [`handle_table()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.handle_table)
    * [`load_dataframe()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.load_dataframe)
    * [`main()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.main)
    * [`print_welcome_banner()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.print_welcome_banner)
    * [`prompt()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.prompt)
    * [`select_columns_multi()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.select_columns_multi)
    * [`select_variable_columns()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.select_variable_columns)

## Submodules

## NaivePyDECOMP.Builder module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Model Builder from YAML Configuration

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

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
- Modular assembly of each subsystem’s variables and constraints.
- Construction of system-wide power balance constraint.
- Cost-based objective function including startup, generation, and deficit costs.

### Usage

Use build_model_from_file(path) as the main entry point.

Ensure the YAML file has at least a meta section and one
of the technology sections: hydro, thermal, renewable, or storage.

* **returns:**
  - Pyomo ConcreteModel ready for optimization.
  - Parsed dictionary representing the structured case.
* **rtype:**
  Tuple[ConcreteModel, dict]

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.Builder.build_balance_and_objective_from_yaml(model: ConcreteModel, yaml_data: Dict[str, Any]) → ConcreteModel

Construct the system-wide power balance constraint and total cost objective.

This function scans the parsed YAML content to determine which technologies
(thermal, hydro, storage, renewable) are present, and invokes their respective
expression builders to construct:

- model.Balance: a time-indexed Constraint for supply-demand balance
- model.OBJ: an Objective for cost minimization

* **Parameters:**
  * **model** (*ConcreteModel*) – A Pyomo model with required sets and variables already declared.
  * **yaml_data** (*dict*) – Parsed YAML dictionary with subsections for each technology.
* **Returns:**
  The input model with balance constraints and objective function added.
* **Return type:**
  ConcreteModel

### NaivePyDECOMP.Builder.build_model_from_data(root: Dict) → Tuple[ConcreteModel, Dict]

build subsystem models from data.

* **Parameters:**
  **root** (*str*) – system description.
* **Returns:**
  A tuple with the builded model and the parsed case file
* **Return type:**
  Tuple[pyomo.environ.ConcreteModel, Dict]
* **Raises:**
  **ValueError** – On structural or validation errors in the input file.

### NaivePyDECOMP.Builder.build_model_from_file(path: str) → Tuple[ConcreteModel, Dict]

Load master data from YAML/JSON and build subsystem models.

* **Parameters:**
  **path** (*str*) – Path to a YAML file with sections: meta, demand, and one or
  more of {hydro, thermal, renewable, storage}.
* **Returns:**
  A tuple with the builded model and the parsed case file
* **Return type:**
  Tuple[pyomo.environ.ConcreteModel, Dict]
* **Raises:**
  **ValueError** – On structural or validation errors in the input file.

## NaivePyDECOMP.BuilderPDDD module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Model Builder from YAML Configuration

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

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
- Modular assembly of each subsystem’s variables and constraints.
- Construction of system-wide power balance constraint.
- Cost-based objective function including startup, generation, and deficit costs.

### Usage

Use build_model_from_file(path) as the main entry point.

Ensure the YAML file has at least a meta section and one
of the technology sections: hydro, thermal, renewable, or storage.

* **returns:**
  - Pyomo ConcreteModel ready for optimization.
  - Parsed dictionary representing the structured case.
* **rtype:**
  Tuple[ConcreteModel, dict]

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.BuilderPDDD.build_pddd_balance_and_objective_from_yaml(yaml_data: Dict[str, Any], stage: int, cuts: List[Any]) → ConcreteModel

Construct the system-wide power balance constraint and total cost objective
along with the model itself.

This function scans the parsed YAML content to determine which technologies
(thermal, hydro, storage, renewable) are present, and invokes their respective
expression builders to construct:

- PDDD Model
- model.Balance: a time-indexed Constraint for supply-demand balance
- model.OBJ: an Objective for cost minimization

* **Parameters:**
  * **yaml_data** (*dict*) – Parsed YAML dictionary with subsections for each technology.
  * **stage** (*int*) – PDDD Stage
* **Returns:**
  The input model with balance constraints and objective function added.
* **Return type:**
  ConcreteModel

### NaivePyDECOMP.BuilderPDDD.build_pddd_data_from_file(path: str) → Dict

Load master data from YAML/JSON and build subsystem models.

* **Parameters:**
  **path** (*str*) – Path to a YAML file with sections: meta, demand, and one or
  more of {hydro, thermal, renewable, storage}.
* **Returns:**
  the parsed case file
* **Return type:**
  Dict
* **Raises:**
  **ValueError** – On structural or validation errors in the input file.

## NaivePyDECOMP.DataFrames module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Utility: Build Dispatch DataFrame from Pyomo Model Results

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This utility extracts time series of dispatch decisions from a solved
Pyomo model and compiles them into a structured pandas DataFrame. It
supports hydropower, thermal generation, renewable sources, and storage
systems. The output can be used for reporting, visualization, or export
to CSV.

Main components extracted:
- Hydropower: turbined flow, storage volume, generation, spillage.
- Thermal: power output, on/off status, startup/shutdown, reserves.
- Renewable: available generation by unit.
- Storage: charge/discharge power, net injection, state of charge.
- System-wide: demand, deficit, cost components (variable, startup, deficit).

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.DataFrames.add_cost_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

Append cost components, demand/deficit, total generation,
and marginal cost (CMO) to the DataFrame.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to which cost components will be appended.
  * **model** (*ConcreteModel*) – A Pyomo model instance with thermal, hydro, and balance constraints.
* **Returns:**
  The updated DataFrame including cost components, energy balance data,
  and marginal cost of operation (CMO).
* **Return type:**
  pd.DataFrame

### NaivePyDECOMP.DataFrames.add_hydro_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

Append hydropower dispatch results to a pandas DataFrame.

This function extracts the turbined flow, storage volume, hydropower
generation, and spillage from a Pyomo model and appends them to the
given DataFrame, one column per unit and variable.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to which the results will be appended. It may be empty.
  * **model** (*ConcreteModel*) – A Pyomo model instance containing hydropower variables.
* **Returns:**
  The updated DataFrame including hydropower dispatch results.
* **Return type:**
  pd.DataFrame

### NaivePyDECOMP.DataFrames.add_thermal_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

Append thermal dispatch results to a pandas DataFrame.

This function extracts generation, commitment (on/off), startup, shutdown,
and reserve values from the Pyomo model and appends them to the given
DataFrame. Optional variables such as reserve (r), startup (y), and
shutdown (w) are included if present.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to which the results will be appended. It may be empty.
  * **model** (*ConcreteModel*) – A Pyomo model instance containing thermal generation variables.
* **Returns:**
  The updated DataFrame including thermal dispatch results.
* **Return type:**
  pd.DataFrame

### NaivePyDECOMP.DataFrames.build_dispatch_dataframe(model: ConcreteModel) → DataFrame

Build a full dispatch DataFrame with generation, cost, and balance data.

This function aggregates the dispatch results from all subsystems
(hydropower, thermal, renewable, storage) along with cost components
into a single structured pandas DataFrame.

* **Parameters:**
  **model** (*ConcreteModel*) – A Pyomo model instance containing subsystem variables and time horizon.
* **Returns:**
  A DataFrame with all relevant dispatch results and economic metrics.
* **Return type:**
  pd.DataFrame

## NaivePyDECOMP.Formatters module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Utility: Format Numbers in Brazilian Currency Style

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides a helper function to format numerical values in the
Brazilian currency style: periods as thousand separators and commas for
decimals (e.g., 1234567.89 → ‘1.234.567,89’).

It is intended for producing human-readable cost reports or summaries in
energy dispatch problems solved by NaivePyDECOMP.

### Examples

```pycon
>>> format_brl(1234567.89)
'1.234.567,89'
```

```pycon
>>> format_brl(42.5)
'42,50'
```

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## NaivePyDECOMP.ModelCheck module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Model Component Validators

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides a set of utility functions to verify whether a given Pyomo
ConcreteModel contains the essential variables, parameters, and sets required
for each subsystem in an energy dispatch problem.

The validation is modular and lightweight, designed to support the dynamic
assembly of hybrid dispatch models comprising:
- Hydropower units
- Thermal generation units
- Renewable generation sources
- Energy storage systems

These functions are typically used to determine the feasibility of operations
such as cost extraction, result formatting, or diagnostics on a per-subsystem basis.

### Functions

- has_hydro_model(model): Checks presence of hydropower-related variables.
- has_thermal_model(model): Checks presence of thermal generation variables.
- has_renewable_model(model): Checks presence of renewable generation variables.
- has_storage_model(model): Checks presence of storage system variables.

### Usage Example

```pycon
>>> if has_thermal_model(m):
>>>     print("Thermal model components detected.")
```

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.ModelCheck.has_thermal_model(model: ConcreteModel) → bool

Check whether the given Pyomo model contains all components of a thermal subsystem.

This function validates the existence of typical thermal dispatch variables,
including generation, commitment status, and startup/shutdown indicators.

* **Parameters:**
  **model** (*ConcreteModel*) – The Pyomo model instance to be validated.
* **Returns:**
  True if all required thermal components are present, False otherwise.
* **Return type:**
  bool

### Notes

The required attributes are:
- T             : Time periods.
- TG            : Set of thermal units.
- thermal_p     : Power generation variable.
- thermal_Cost    : Cost parameter.

## NaivePyDECOMP.ModelFormatters module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Utility: Welcome Message and Model Summary Printer

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This utility provides formatted, color-enhanced terminal output using the
colorama library to display a welcome banner, solver configuration,
and model characteristics. It is intended to improve the user experience
by offering clear diagnostics and summaries prior to model solving.

Features include:
- Welcome banner with project and author information.
- Display of solver name and strategy.
- Pretty-printed summary of subsystems included in the dispatch problem.
- Parameter visualization for hydraulic, thermal, renewable, and storage units.

Use this module as part of the pre-solve interface of NaivePyDECOMP to
provide clarity and visual feedback about the simulation setup.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.ModelFormatters.format_hydro_model(case: Dict) → None

Print formatted information for each hydropower unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘hydro’ section with unit definitions.

### NaivePyDECOMP.ModelFormatters.format_models(case: Dict) → None

Dispatch model formatting routines to subsystem-specific formatters.

* **Parameters:**
  **case** (*dict*) – Input data dictionary containing unit-level information.

### NaivePyDECOMP.ModelFormatters.format_thermal_model(case: Dict) → None

Print formatted information for each thermal generation unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘thermal’ section with unit definitions.

### NaivePyDECOMP.ModelFormatters.model_properties(case: Dict) → None

Print a concise list of subsystems included in the case (hydro, thermal, etc.).

* **Parameters:**
  **case** (*dict*) – Parsed input configuration containing subsystem definitions.

### NaivePyDECOMP.ModelFormatters.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

Uses colored and bold text to enhance readability in the terminal.

### NaivePyDECOMP.ModelFormatters.print_welcome_message(model: ConcreteModel, case: Dict) → None

Display the full welcome message and solver configuration.

This includes the banner, solver details, and an overview of
the model components based on the input dictionary.

* **Parameters:**
  * **model** (*ConcreteModel*) – The Pyomo model instance.
  * **case** (*dict*) – Configuration dictionary loaded from YAML or JSON input.

## NaivePyDECOMP.PlotSeries module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Plotting Utilities for Time Series in Power System Studies

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides high-level plotting routines to visualize time-indexed
variables commonly encountered in short-term operation and planning studies
of hydrothermal systems. It offers both line plots and bar plots, supporting
grouped or stacked styles.

### Functions

plot_series(t, series_dict, title, ylabel, file)
: Plot one or more time series as line graphs, with LaTeX-compatible labels.

plot_series_bar(t, series_dict, title, ylabel, file, stacked=False, width=0.85)
: Plot multiple time series as bar charts, either grouped or stacked, with
  configurable bar width.

### Conventions

- The time axis is discrete, typically representing hourly stages
  (e.g., t = 1, …, 24).
- Input series must be aligned with the time axis.
- Labels provided in series_dict are rendered in math mode
  to enable LaTeX-style notation in figures.
- Output files are saved with 600 dpi resolution and tight bounding boxes.

### Notes

- Figures are generated using Matplotlib and saved to the given file path
  (PNG, PDF, or other supported formats).
- The functions are designed for clarity in academic and technical reports,
  especially when documenting hydrothermal dispatch and unit-commitment results.
- Grid lines, legends, and axis labels are automatically formatted for
  readability.

### Examples

Render a simple time series plot:

```pycon
>>> t = range(1, 5)
>>> data = {"U_{1}": [100, 120, 130, 140], "U_{2}": [90, 110, 125, 150]}
>>> plot_series(t, data, title="Hydropower Generation", ylabel="MW",
...             file="generation.png")
```

Render a stacked bar plot:

```pycon
>>> data = {"Hydro": [200, 220, 210], "Thermal": [300, 280, 290]}
>>> t = [1, 2, 3]
>>> plot_series_bar(t, data, title="Generation Mix", ylabel="MW",
...                 file="mix.png", stacked=True)
```

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## NaivePyDECOMP.PDDDMergeModels module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Utility: PDDD Synthetic Model Generator

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This utility provides tools to reconstruct a deterministic representation
of a multistage dual dynamic programming (PDDD) solution as a static Pyomo
model. It enables post-optimization analysis by aggregating decision
variables, dual prices, volumes, and cost structures from multiple stages
into a single structured object.

### Main Functionality

The primary function exposed by this package is:

- generate_dummy_model(pddd_solution, yaml_data): Constructs a
  fully populated ConcreteModel that mirrors the original optimization
  trajectory. It fixes all relevant decision variables and duals for each
  unit (hydro, thermal, renewable, storage), and reassembles cost
  expressions for reporting, visualization, and interpretation.

### Intended Use

This package is not designed to perform optimization itself. Instead, it
serves as a post-processing tool for exporting or inspecting results from
a PDDD optimization workflow — for example, to be used in scenario analysis,
LaTeX export, sensitivity evaluation, or policy verification.

### Dependencies

- Pyomo
- A compatible solver (e.g., GLPK, CPLEX, IPOPT)
- Auxiliary model-building functions such as:
  - add_hydraulic_cost_expression
  - add_thermal_cost_expression
  - add_storage_cost_expression
  - add_renewable_cost_expression

### Examples

```pycon
>>> from naivepydecomp.pddd import generate_dummy_model
>>> model = generate_dummy_model(pddd_solution, yaml_data)
>>> print(value(model.OBJ))
```

#### SEE ALSO
`solve_pddd`
: The iterative algorithm that produces the input data for generate_dummy_model.

`solve_stage_pddd`
: Solves a single stage of the PDDD problem and stores intermediate results.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.PDDDMergeModels.generate_dummy_model(pddd_solution: List[Any], yaml_data: Dict) → ConcreteModel

Generates a synthetic Pyomo model representing the structure and results
of a full PDDD (Deterministic Dual Dynamic Programming) optimization process.

This function aggregates relevant decision variables and dual information
across all stages and stores them as fixed model components. It is useful
for analyzing and exporting the solution in a structured and interpretable
Pyomo ConcreteModel, without performing any further optimization.

* **Parameters:**
  * **pddd_solution** (*List*) – List containing the results of each stage of the PDDD algorithm,
    including model objects, decision variables, shadow prices, volumes,
    and costs for each time stage.
  * **yaml_data** (*dict*) – Dictionary parsed from the YAML configuration file, containing system
    metadata, unit definitions (hydro, thermal, renewable, storage), cost
    parameters, and other structural data used during model construction.
* **Returns:**
  **model** – A fully populated Pyomo ConcreteModel object that encapsulates:
  - Fixed decision variables from hydro, thermal, renewable, and storage units.
  - Cost terms and expressions used in the original optimization.
  - Final values of market price (CMO), deficit penalty, and alpha values.
  - Sets for all units and time stages.
* **Return type:**
  ConcreteModel

### Notes

- The returned model is not intended to be solved again, but rather to
  serve as a reference for results visualization, report generation, or
  post-analysis.
- The cost components are reassembled using the same structure as in the
  original model, using the add_\*_cost_expression helper functions.
- The model object stores one time step ahead (nstages + 1) for correct
  alignment with stage-based formulations.

* **Raises:**
  **KeyError** – If expected keys or values are missing from pddd_solution or yaml_data.

#### SEE ALSO
`solve_pddd`
: Function that produces the input pddd_solution dictionary.

## NaivePyDECOMP.Reporting module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Utility: Post-Solve Dispatch Summary and Cost Reports

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module contains functions to summarize dispatch results after solving
a Pyomo-based optimization problem. It prints total generation, cost breakdowns,
and unit-level summaries for hydropower, thermal, renewable, and storage technologies.

Features:
- Total cost, demand, deficit and thermal cost components.
- Per-unit dispatch summaries with color-enhanced output (via colorama).
- Compatible with modular NaivePyDECOMP subsystem architecture.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.Reporting.dispatch_summary(model: ConcreteModel) → None

Print a complete dispatch and cost summary including:
- Total generation and demand.
- Deficit and its monetary cost.
- Thermal cost breakdown (start-up, generation).
- Overall total cost from the model objective.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model instance.

### NaivePyDECOMP.Reporting.hydro_dispatch_summary(model: ConcreteModel) → None

Print unit-level hydropower generation summary in MWmed.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with hydropower subsystem.

### NaivePyDECOMP.Reporting.renewable_dispatch_summary(model: ConcreteModel) → None

Print unit-level renewable generation summary in MWmed.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with renewable subsystem.

### NaivePyDECOMP.Reporting.storage_dispatch_summary(model: ConcreteModel) → None

Print unit-level storage discharge summary in MWmed.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with storage subsystem.

### NaivePyDECOMP.Reporting.thermal_dispatch_summary(model: ConcreteModel) → None

Print unit-level thermal generation summary in MWmed.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with thermal subsystem.

## NaivePyDECOMP.SolverPDDD module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Utility: Solve PDDD Pyomo Models from YAML Configuration

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This utility builds and solves a Pyomo optimization model using input
data provided in a YAML or JSON configuration file. The solver is selected
based on metadata, and can include support for decomposition strategies
(e.g., MIN-DT via MindtPy).

Features:
- Automatic model construction via modular subsystems (thermal, hydro, storage, renewable).
- Solver selection and configuration via YAML metadata.
- Support for MINLP solvers such as MindtPy with strategy and time limits.
- Termination condition validation to ensure feasibility or optimality.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.SolverPDDD.compute_fcf(cuts: List[Dict], pddd_memory: List[Dict]) → Dict

Compute the Future Cost Function (FCF) values for all stages
in the PDDD framework, given a set of Benders cuts.

This function iterates over the memory of the PDDD algorithm,
extracting the storage volumes for each stage and evaluating
the corresponding FCF approximation using the provided cuts.

* **Parameters:**
  * **cuts** (*List* *[**Dict* *]*) – 

    List of Benders cuts. Each cut must be a dictionary with:
    {
    > ”rhs”: float,                # adjusted intercept
    > “coefs”: {unit: float}       # coefficients (subgradients)

    }
  * **pddd_memory** (*List* *[**Dict* *]*) – 

    List of stage-level information from the PDDD algorithm.
    Each element must include the storage volumes in the key
    ‘f_volume’, e.g.:
    {
    > ”f_volume”: {“UHE1”: 50, “UHE2”: 80, …}

    }
* **Returns:**
  Dictionary of FCF values for each stage, with keys in the
  format “FCF_{t}” where t denotes the stage index (1-based).
  Example:
  {
  > ”FCF_1”: […],
  > “FCF_2”: […],
  > …

  }
* **Return type:**
  Dict

### NaivePyDECOMP.SolverPDDD.fcf_from_cuts(cuts: List[Dict], stage: int, storage_levels: Dict) → List

Compute the Future Cost Function (FCF) value given a set of Benders cuts,
assuming that the expansion point (xk) has already been absorbed into
the intercept (rhs).

* **Parameters:**
  * **cuts** (*list* *of* *dict*) – 

    List of cuts. Each cut must have the format:
    {
    > ”stage”: int                 # stage for calculation
    > “rhs”: float,                # adjusted intercept
    > “coefs”: {unit: float}       # coefficients (subgradients)

    }
  * **stage** (*int*) – The index of the current stage being solved (0-based).
  * **storage_levels** (*dict*) – Dictionary with current storage volumes for each hydro unit.
    Example: {“UHE1”: 50, “UHE2”: 80}
* **Returns:**
  Value of the Future Cost Function (FCF) evaluated at the given
  storage levels.
* **Return type:**
  List[float]

### NaivePyDECOMP.SolverPDDD.solve_pddd(path: str, max_iter: int = 500, tol: float = 0.01, verbose: bool = True) → Tuple[ConcreteModel, Dict]

Solves the full multi-stage hydrothermal dispatch problem using the
Deterministic Dual Dynamic Programming (PDDD) algorithm.

This function implements both the forward and backward passes of the
PDDD approach, coordinating the stage-wise resolution of subproblems,
the propagation of terminal volumes between stages, and the generation
of Benders-like cuts. The process continues until the upper-lower bound
convergence criterion is satisfied or the maximum number of iterations
is reached.

* **Parameters:**
  * **path** (*str*) – Path to the YAML file containing the problem configuration
    (system data, hydro parameters, solver options).
  * **max_iter** (*int* *,* *optional*) – Maximum number of forward-backward iterations allowed (default is 10).
  * **tol** (*float* *,* *optional*) – Convergence tolerance between ZSUP and ZINF values used as stopping
    criterion (default is 1e-2).
  * **verbose** (*bool* *,* *optional*) – Whether to print iteration logs and convergence progress (default is True).
* **Returns:**
  * **model** (*ConcreteModel*) – A dummy Pyomo model representing the structure and solution of the
    final iteration. This is mainly for completeness and introspection.
  * **case** (*dict*) – The parsed YAML case dictionary used in the PDDD process, containing
    metadata, hydro data, and solver configurations.
  * **alpha_values** (*dict*) – alpha values of future costs.
  * **ZINF** (*dict*)
* **Raises:**
  * **RuntimeError** – If the specified solver is not available or any stage optimization fails.
  * **ValueError** – If no hydro data is provided in the YAML configuration.

### Notes

- The upper bound (ZSUP) is computed cumulatively from all stages,
  discounting the cost-to-go alpha values.
- The lower bound (ZINF) corresponds to the cost of the first stage
  assuming a myopic (executable) policy.
- Cuts are generated in the backward pass and injected into earlier stages
  to approximate the value function of future stages.
- This implementation is pedagogical and emphasizes clarity and modularity
  over computational performance.

### NaivePyDECOMP.SolverPDDD.solve_stage_pddd(yaml_data: Dict, stage_hydros: Dict, stage_storage: Dict, cuts: Dict, stage: int) → Dict

Solves a single stage of the hydrothermal dispatch problem within the
Deterministic Dual Dynamic Programming (PDDD) framework.

This function constructs and solves the optimization model for a given stage,
incorporating the current state of hydro units, operational cuts from future stages,
and the parameters defined in the YAML configuration. It returns the resulting
model and relevant economic and operational variables.

* **Parameters:**
  * **yaml_data** (*dict*) – The full configuration dictionary loaded from a YAML file, containing
    system metadata, solver settings, and model parameters.
  * **stage_hydros** (*dict*) – Dictionary describing the state of the hydro units at the current stage,
    including initial volumes, inflows, and other relevant characteristics.
  * **stage_storage** (*dict*) – Dictionary describing the state of the storage units at the current stage,
    including initial energy, energy limits and other relevant characteristics.
  * **cuts** (*dict*) – Dictionary containing Benders-like cuts (affine inequalities) propagated
    from future stages, used to approximate the future cost function.
  * **stage** (*int*) – The index of the current stage being solved (0-based).
* **Returns:**
  **results** – Dictionary containing:
  - ’model’
    : The Pyomo model instance with solved values.
  - ’hydro’
    : The hydro dictionary passed as input, preserved for traceability.
  - ’storage’
    : The storage dictionary passed as input, preserved for traceability.
  - ’total_cost’
    : The stage cost including the estimated future cost via alpha.
  - ’alpha’
    : The value of the cost-to-go (future cost approximation) variable.
  - ’f_volume’
    : Dictionary mapping each hydro plant to its final volume at the end of the stage.
  - ’cmo’
    : The dual variable associated with the system-wide energy balance constraint (marginal cost of operation).
  - ’cma’
    : Dictionary mapping each hydro plant to its marginal water value
      (dual variable of the volume balance constraint).
* **Return type:**
  dict
* **Raises:**
  **RuntimeError** – If the specified solver is not available or if the optimization does not reach
      an optimal or feasible termination condition.

### Notes

This function is used internally in the forward and backward passes of the PDDD algorithm
to simulate stage-wise operations and propagate information backward via cuts.

## NaivePyDECOMP.Solver module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Utility: Solve Pyomo Model from YAML Configuration

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This utility builds and solves a Pyomo optimization model using input
data provided in a YAML or JSON configuration file. The solver is selected
based on metadata, and can include support for decomposition strategies
(e.g., MIN-DT via MindtPy).

Features:
- Automatic model construction via modular subsystems (thermal, hydro, storage, renewable).
- Solver selection and configuration via YAML metadata.
- Support for MINLP solvers such as MindtPy with strategy and time limits.
- Termination condition validation to ensure feasibility or optimality.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.Solver.solve(path: str) → Tuple[ConcreteModel, Dict]

Build and solve a Pyomo optimization model from a configuration file.

This function loads a model and its configuration from a structured YAML or JSON
file using the build_model_from_file routine. It then selects the appropriate
solver based on the ‘meta’ section, applies any solver-specific options (including
for MIN-DT decomposition), and executes the optimization.

* **Parameters:**
  **path** (*str*) – Path to the configuration file containing model metadata and data sections.
* **Returns:**
  * **model** (*ConcreteModel*) – The Pyomo model after the solve routine, with variables populated.
  * **case** (*dict*) – Parsed dictionary containing the original configuration, metadata,
    solver options, and problem data.
* **Raises:**
  **RuntimeError** – If the solver is not available, solve fails, or model is infeasible.

## NaivePyDECOMP.Utils module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

LaTeX Table Utilities for Pandas DataFrames

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides helpers to render pandas DataFrames as LaTeX tables with
custom styling aimed at scientific and engineering reports. It includes:

- `binary_df_to_colored_latex`: Renders a binary matrix (0/1) as a colored
  LaTeX table, highlighting ones and zeros with configurable colors and
  producing a complete `table` environment.
- `custom_df_to_latex`: Renders a generic (non-binary) DataFrame as a LaTeX
  table with bold headers (and bold math within headers), using `booktabs`
  rules and producing a complete `table` environment.

Both functions omit the DataFrame index from the LaTeX output by design,
emitting only the column headers and data cells.

### Functions

binary_df_to_colored_latex
: Render a binary (0/1) DataFrame as a colored LaTeX table. Cells equal to 1
  are filled with `one_color`; cells equal to 0 use `zero_color`.
  Non-binary values, if present, are formatted with `floatfmt` and not
  color-filled. The index is not included in the output.

custom_df_to_latex
: Render a generic DataFrame as a LaTeX table using `booktabs` rules with a
  bold header row. Inline math fragments in header cells  are additionally set
  in bold math using `bold_math_cmd`.
  The index is not included in the output.

### Parameters (Shared)

df
: The input table to render. Only the DataFrame **columns** are emitted;
  the index is always omitted from the LaTeX output.

caption
: Caption text for the LaTeX `table` environment.

label
: Label for cross-referencing with `\ref{...}`.

column_format
: Column specification for the LaTeX `tabular` environment. If `None`,
  a default is inferred based on the number of columns (all centered).

size_cmd
: LaTeX size command applied inside the table (e.g., `\small`, `\scriptsize`).

### Additional Parameters

one_color
: (For `binary_df_to_colored_latex`) LaTeX color name for cells with value 1.

zero_color
: (For `binary_df_to_colored_latex`) LaTeX background color name for cells
  with value 0.

floatfmt
: (For `binary_df_to_colored_latex`) Format string for numeric entries that
  are not 0/1 (e.g., `"{:d}"` or `"{:.0f}"`).

bold_math_cmd
: (For `custom_df_to_latex`) Command for bolding inline math in header cells,
  e.g., `\mathbf`, `\boldsymbol`, or `\bm`. Ensure the corresponding
  LaTeX package is loaded.

* **returns:**
  * *str* – A complete LaTeX `table` environment (including an inner `tabular` and
    a `\resizebox{\textwidth}{!}{...}` wrapper) ready to paste into a
    LaTeX document.
  * *Requirements*
  *  *————*
  * **- Python packages** (`pandas`, `numpy`, `re` (standard library).)
  *  *- LaTeX packages* –
    - For both functions: `graphicx` (for `\resizebox`), `booktabs` (for `custom_df_to_latex`).
    - For coloring: `xcolor` with the `table` option (provides `\cellcolor`).
      Colors such as `oncell` and `white` must be defined in the preamble.
    - For bold math: `amsmath`, `bm`, or any package compatible with `bold_math_cmd`.

### Notes

- Both functions assume the DataFrame columns represent displayable headers.
  If numeric, they are commonly used as time periods. Pre-formatting is advised.
- `binary_df_to_colored_latex` coerces values to integers for coloring.
  Non-binary values are rendered using `floatfmt` but receive no coloring.
- `custom_df_to_latex` skips escaping in data cells, assuming LaTeX-safe input.

### Examples

Render a binary status matrix with colored cells:

```pycon
>>> import pandas as pd
>>> df = pd.DataFrame([[1, 0, 1], [0, 0, 1]])
>>> tex = binary_df_to_colored_latex(
...     df,
...     caption="Hourly U, Y, and W variables",
...     label="tab:uyw",
...     one_color="oncell",
...     zero_color="white",
...     floatfmt="{:d}"
... )
>>> print(tex.splitlines()[0])
\begin{table}[!ht]
```

Render a numeric table with bold headers and math-aware bolding:

```pycon
>>> df2 = pd.DataFrame(
...     [[1.0, 2.0], [3.5, 4.25]],
...     columns=[r"$t=1$", r"\(t=2\)"]
... )
>>> tex2 = custom_df_to_latex(
...     df2,
...     caption="Example Table",
...     label="tab:example",
...     bold_math_cmd="\mathbf"
... )
>>> "\toprule" in tex2
True
```

#### SEE ALSO
`pandas.DataFrame.to_latex`
: Built-in (less specialized) LaTeX export.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## NaivePyDECOMP.YAMLLoader module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Configuration Pre-Processor for Model Inputs

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Utilities to load and normalize model configuration files (YAML/JSON) before
instantiating optimization models. The module provides:

1. A LaTeX-friendly renaming utility for unit identifiers, preserving downstream
   compatibility with report/plot labels.
2. A deep-copy pre-processor that standardizes sections and optionally transforms
   unit names and their upstreams references.
3. A YAML loader that combines parsing and pre-processing into a single entry point.

This pre-processing ensures consistent, side-effect-free structures that are
directly consumable by subsequent builders (hydro, thermal, renewable, storage).

### Functions

key_replace(key)
: Convert identifiers for LaTeX.

pre_process(config_dict, transform_names=True)
: Deep-copy and normalize a configuration dictionary, optionally transforming
  unit names and upstream references in sections that contain units.

yaml_loader(file, transform_names=True)
: Load a YAML file and return a processed configuration dictionary suitable
  for model building.

### Notes

- Only the **first** underscore in an identifier is used to create the subscript;
  remaining underscores are kept verbatim inside the subscript block.
- Sections without a units field are copied verbatim.
- All operations are performed on deep copies; the original inputs are not modified.

### Examples

```pycon
>>> cfg = yaml_loader("case.yaml", transform_names=True)
>>> list(cfg["hydro"]["units"].keys())
['{UHE_{1}}', '{UHE_{2}}']
```

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
