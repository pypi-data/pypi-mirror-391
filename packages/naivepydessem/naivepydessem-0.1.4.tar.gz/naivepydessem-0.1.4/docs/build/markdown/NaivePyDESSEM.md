# NaivePyDESSEM package

## Module contents

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: NaivePyDESSEM

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

The `NaivePyDESSEM` package provides a modular, extensible, and pedagogically
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

* [NaivePyDESSEM.HydraulicGenerator package](NaivePyDESSEM.HydraulicGenerator.md)
  * [Module contents](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator)
    * [Author](NaivePyDESSEM.HydraulicGenerator.md#author)
    * [Description](NaivePyDESSEM.HydraulicGenerator.md#description)
    * [Submodules](NaivePyDESSEM.HydraulicGenerator.md#submodules)
  * [Submodules](NaivePyDESSEM.HydraulicGenerator.md#id1)
  * [NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH)
    * [Author](NaivePyDESSEM.HydraulicGenerator.md#id2)
    * [Description](NaivePyDESSEM.HydraulicGenerator.md#id3)
    * [`constant_productivity_fph()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH.constant_productivity_fph)
  * [NaivePyDESSEM.HydraulicGenerator.ExactFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.ExactFPH)
    * [Author](NaivePyDESSEM.HydraulicGenerator.md#id4)
    * [Description](NaivePyDESSEM.HydraulicGenerator.md#id5)
    * [`fph_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ExactFPH.fph_factory)
    * [`polynomial_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ExactFPH.polynomial_factory)
    * [`rho_colina_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ExactFPH.rho_colina_factory)
  * [NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints)
    * [Hydropower Constraints Module for Multi-Mode Generation Modeling](NaivePyDESSEM.HydraulicGenerator.md#hydropower-constraints-module-for-multi-mode-generation-modeling)
      * [Imported Dependencies](NaivePyDESSEM.HydraulicGenerator.md#imported-dependencies)
      * [Functions](NaivePyDESSEM.HydraulicGenerator.md#functions)
      * [Model Requirements](NaivePyDESSEM.HydraulicGenerator.md#model-requirements)
    * [`add_hydro_balance_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_balance_constraint)
    * [`add_hydro_generation_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_generation_constraint)
    * [`add_hydro_qmax_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_qmax_constraint)
    * [`add_hydro_qmin_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_qmin_constraint)
    * [`add_hydro_volume_continuity_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_continuity_constraint)
    * [`add_hydro_volume_max_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_max_constraint)
    * [`add_hydro_volume_meta_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_meta_constraint)
    * [`add_hydro_volume_mim_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_mim_constraint)
    * [`hydro_total_inflow_expr()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.hydro_total_inflow_expr)
  * [NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes)
    * [Hydraulic System Data Classes for Reservoir Optimization](NaivePyDESSEM.HydraulicGenerator.md#hydraulic-system-data-classes-for-reservoir-optimization)
      * [Overview](NaivePyDESSEM.HydraulicGenerator.md#overview)
      * [Conventions and Units](NaivePyDESSEM.HydraulicGenerator.md#conventions-and-units)
    * [`HydraulicData`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData)
      * [`HydraulicData.Cdef`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData.Cdef)
      * [`HydraulicData.demand`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData.demand)
      * [`HydraulicData.horizon`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData.horizon)
      * [`HydraulicData.units`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData.units)
      * [`HydraulicData.zeta`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData.zeta)
      * [`HydraulicData.zeta_vol`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData.zeta_vol)
    * [`HydraulicUnit`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)
      * [`HydraulicUnit.Qmax`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Qmax)
      * [`HydraulicUnit.Qmin`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Qmin)
      * [`HydraulicUnit.Vini`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Vini)
      * [`HydraulicUnit.Vmax`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Vmax)
      * [`HydraulicUnit.Vmeta`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Vmeta)
      * [`HydraulicUnit.Vmin`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.Vmin)
      * [`HydraulicUnit.a`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.a)
      * [`HydraulicUnit.afluencia`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.afluencia)
      * [`HydraulicUnit.b`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.b)
      * [`HydraulicUnit.compute_total_inflow`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.compute_total_inflow)
      * [`HydraulicUnit.losses`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.losses)
      * [`HydraulicUnit.mode`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.mode)
      * [`HydraulicUnit.name`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.name)
      * [`HydraulicUnit.p`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.p)
      * [`HydraulicUnit.pe`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.pe)
      * [`HydraulicUnit.rho`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.rho)
      * [`HydraulicUnit.upstreams`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit.upstreams)
  * [NaivePyDESSEM.HydraulicGenerator.HydraulicEquations module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicEquations)
    * [Author](NaivePyDESSEM.HydraulicGenerator.md#id6)
    * [Description](NaivePyDESSEM.HydraulicGenerator.md#id7)
    * [Intended Use](NaivePyDESSEM.HydraulicGenerator.md#intended-use)
    * [`add_hydraulic_balance_expression()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicEquations.add_hydraulic_balance_expression)
    * [`add_hydraulic_cost_expression()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicEquations.add_hydraulic_cost_expression)
  * [NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder)
    * [Hydropower Dispatch Model Builder](NaivePyDESSEM.HydraulicGenerator.md#hydropower-dispatch-model-builder)
      * [Supported generation modes (per unit)](NaivePyDESSEM.HydraulicGenerator.md#supported-generation-modes-per-unit)
      * [Functions](NaivePyDESSEM.HydraulicGenerator.md#id8)
      * [Modeling Conventions and Units](NaivePyDESSEM.HydraulicGenerator.md#modeling-conventions-and-units)
    * [`add_hydro_problem()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_problem)
    * [`build_FPHs()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.build_FPHs)
    * [`build_hydro_dispatch()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.build_hydro_dispatch)
  * [NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives)
    * [Objective Function for Pure Hydropower Dispatch](NaivePyDESSEM.HydraulicGenerator.md#objective-function-for-pure-hydropower-dispatch)
      * [Functions](NaivePyDESSEM.HydraulicGenerator.md#id9)
      * [Modeling Conventions and Units](NaivePyDESSEM.HydraulicGenerator.md#id10)
    * [`set_objective_hydro()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives.set_objective_hydro)
  * [NaivePyDESSEM.HydraulicGenerator.HydraulicVars module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicVars)
    * [Hydropower Model Initialization: Sets, Parameters, and Variables](NaivePyDESSEM.HydraulicGenerator.md#hydropower-model-initialization-sets-parameters-and-variables)
      * [Functions](NaivePyDESSEM.HydraulicGenerator.md#id11)
      * [Modeling Conventions and Units](NaivePyDESSEM.HydraulicGenerator.md#id12)
    * [`hydralic_add_variables_g()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicVars.hydralic_add_variables_g)
    * [`hydraulyc_add_sets_and_params()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicVars.hydraulyc_add_sets_and_params)
  * [NaivePyDESSEM.HydraulicGenerator.PEFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.PEFPH)
    * [Author](NaivePyDESSEM.HydraulicGenerator.md#id13)
    * [Description](NaivePyDESSEM.HydraulicGenerator.md#id14)
    * [`fph_pe_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.PEFPH.fph_pe_factory)
  * [NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH)
    * [Author](NaivePyDESSEM.HydraulicGenerator.md#id15)
    * [Description](NaivePyDESSEM.HydraulicGenerator.md#id16)
    * [`simplified_constant_productivity_fph()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH.simplified_constant_productivity_fph)
* [NaivePyDESSEM.RenewableGenerator package](NaivePyDESSEM.RenewableGenerator.md)
  * [Module contents](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator)
    * [Author](NaivePyDESSEM.RenewableGenerator.md#author)
    * [Description](NaivePyDESSEM.RenewableGenerator.md#description)
    * [Submodules](NaivePyDESSEM.RenewableGenerator.md#submodules)
  * [Submodules](NaivePyDESSEM.RenewableGenerator.md#id1)
  * [NaivePyDESSEM.RenewableGenerator.RenewableConstraints module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableConstraints)
    * [Author](NaivePyDESSEM.RenewableGenerator.md#id2)
    * [Description](NaivePyDESSEM.RenewableGenerator.md#id3)
    * [Functions](NaivePyDESSEM.RenewableGenerator.md#functions)
    * [`add_renewable_balance_constraint()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableConstraints.add_renewable_balance_constraint)
    * [`add_renewable_capacity_constraints()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableConstraints.add_renewable_capacity_constraints)
  * [NaivePyDESSEM.RenewableGenerator.RenewableDataTypes module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableDataTypes)
    * [Author](NaivePyDESSEM.RenewableGenerator.md#id4)
    * [Description](NaivePyDESSEM.RenewableGenerator.md#id5)
    * [Classes](NaivePyDESSEM.RenewableGenerator.md#classes)
    * [`RenewableData`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData)
      * [`RenewableData.Cdef`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData.Cdef)
      * [`RenewableData.demand`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData.demand)
      * [`RenewableData.horizon`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData.horizon)
      * [`RenewableData.units`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData.units)
    * [`RenewableUnit`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit)
      * [`RenewableUnit.gbar`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit.gbar)
      * [`RenewableUnit.name`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit.name)
  * [NaivePyDESSEM.RenewableGenerator.RenewableEquations module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableEquations)
    * [Author](NaivePyDESSEM.RenewableGenerator.md#id6)
    * [Description](NaivePyDESSEM.RenewableGenerator.md#id7)
    * [Intended Use](NaivePyDESSEM.RenewableGenerator.md#intended-use)
    * [`add_renewable_balance_expression()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableEquations.add_renewable_balance_expression)
    * [`add_renewable_cost_expression()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableEquations.add_renewable_cost_expression)
  * [NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder)
    * [Author](NaivePyDESSEM.RenewableGenerator.md#id8)
    * [Description](NaivePyDESSEM.RenewableGenerator.md#id9)
    * [Functions](NaivePyDESSEM.RenewableGenerator.md#id10)
    * [`add_renewable_problem()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder.add_renewable_problem)
    * [`build_renewables()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder.build_renewables)
  * [NaivePyDESSEM.RenewableGenerator.RenewableObjectives module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableObjectives)
    * [Author](NaivePyDESSEM.RenewableGenerator.md#id11)
    * [Description](NaivePyDESSEM.RenewableGenerator.md#id12)
    * [Functions](NaivePyDESSEM.RenewableGenerator.md#id13)
    * [`set_objective_renewable()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableObjectives.set_objective_renewable)
  * [NaivePyDESSEM.RenewableGenerator.RenewableVars module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableVars)
    * [Author](NaivePyDESSEM.RenewableGenerator.md#id14)
    * [Description](NaivePyDESSEM.RenewableGenerator.md#id15)
    * [Functions](NaivePyDESSEM.RenewableGenerator.md#id16)
    * [`renewable_add_sets_and_params()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableVars.renewable_add_sets_and_params)
    * [`renewable_add_variables()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableVars.renewable_add_variables)
* [NaivePyDESSEM.Storage package](NaivePyDESSEM.Storage.md)
  * [Module contents](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage)
    * [Author](NaivePyDESSEM.Storage.md#author)
    * [Description](NaivePyDESSEM.Storage.md#description)
    * [Submodules](NaivePyDESSEM.Storage.md#submodules)
  * [Submodules](NaivePyDESSEM.Storage.md#id1)
  * [NaivePyDESSEM.Storage.StorageBuilder module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageBuilder)
    * [Author](NaivePyDESSEM.Storage.md#id2)
    * [Description](NaivePyDESSEM.Storage.md#id3)
    * [Functions](NaivePyDESSEM.Storage.md#functions)
    * [`add_storage_problem()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageBuilder.add_storage_problem)
    * [`build_storage()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageBuilder.build_storage)
  * [NaivePyDESSEM.Storage.StorageConstraints module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageConstraints)
    * [Author](NaivePyDESSEM.Storage.md#id4)
    * [Description](NaivePyDESSEM.Storage.md#id5)
    * [Functions](NaivePyDESSEM.Storage.md#id6)
    * [`add_storage_energy_balance_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_energy_balance_constraint)
    * [`add_storage_mutual_exclusion_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_mutual_exclusion_constraint)
    * [`add_storage_only_balance_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_only_balance_constraint)
    * [`add_storage_power_limits_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_power_limits_constraint)
    * [`add_storage_soc_bounds_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_soc_bounds_constraint)
  * [NaivePyDESSEM.Storage.StorageDataTypes module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageDataTypes)
    * [Author](NaivePyDESSEM.Storage.md#id7)
    * [Description](NaivePyDESSEM.Storage.md#id8)
    * [Classes](NaivePyDESSEM.Storage.md#classes)
    * [`StorageData`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData)
      * [`StorageData.Cdef`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData.Cdef)
      * [`StorageData.delta_t`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData.delta_t)
      * [`StorageData.demand`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData.demand)
      * [`StorageData.horizon`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData.horizon)
      * [`StorageData.units`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData.units)
    * [`StorageUnit`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit)
      * [`StorageUnit.Eini`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.Eini)
      * [`StorageUnit.Emax`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.Emax)
      * [`StorageUnit.Emin`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.Emin)
      * [`StorageUnit.Pch_max`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.Pch_max)
      * [`StorageUnit.Pdis_max`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.Pdis_max)
      * [`StorageUnit.eta_c`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.eta_c)
      * [`StorageUnit.eta_d`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.eta_d)
      * [`StorageUnit.name`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit.name)
  * [NaivePyDESSEM.Storage.StorageEquations module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageEquations)
    * [Author](NaivePyDESSEM.Storage.md#id9)
    * [Description](NaivePyDESSEM.Storage.md#id10)
    * [Intended Use](NaivePyDESSEM.Storage.md#intended-use)
    * [`add_storage_balance_expression()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageEquations.add_storage_balance_expression)
    * [`add_storage_cost_expression()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageEquations.add_storage_cost_expression)
  * [NaivePyDESSEM.Storage.StorageObjective module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageObjective)
    * [Author](NaivePyDESSEM.Storage.md#id11)
    * [Description](NaivePyDESSEM.Storage.md#id12)
    * [Functions](NaivePyDESSEM.Storage.md#id13)
    * [`set_objective_storage()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageObjective.set_objective_storage)
  * [NaivePyDESSEM.Storage.StorageVars module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageVars)
    * [Author](NaivePyDESSEM.Storage.md#id14)
    * [Description](NaivePyDESSEM.Storage.md#id15)
    * [Functions](NaivePyDESSEM.Storage.md#id16)
    * [`storage_add_sets_and_params()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageVars.storage_add_sets_and_params)
    * [`storage_add_variables()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageVars.storage_add_variables)
* [NaivePyDESSEM.ThermalGenerator package](NaivePyDESSEM.ThermalGenerator.md)
  * [Module contents](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#author)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#description)
    * [Submodules](NaivePyDESSEM.ThermalGenerator.md#submodules)
  * [Submodules](NaivePyDESSEM.ThermalGenerator.md#id1)
  * [NaivePyDESSEM.ThermalGenerator.ThermalConstraints module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalConstraints)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#id2)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#id3)
    * [Constraint Families](NaivePyDESSEM.ThermalGenerator.md#constraint-families)
    * [Usage](NaivePyDESSEM.ThermalGenerator.md#usage)
    * [`thermal_add_balance_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_balance_constraint)
    * [`thermal_add_capacity_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_capacity_constraint)
    * [`thermal_add_min_up_down_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_min_up_down_constraint)
    * [`thermal_add_ramps_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_ramps_constraint)
    * [`thermal_add_reserve_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_reserve_constraint)
    * [`thermal_add_startup_shutdown_logic_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_startup_shutdown_logic_constraint)
  * [NaivePyDESSEM.ThermalGenerator.ThermalDataTypes module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalDataTypes)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#id4)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#id5)
    * [Notation (per unit g and time t)](NaivePyDESSEM.ThermalGenerator.md#notation-per-unit-g-and-time-t)
    * [Typical objective (MIQP form)](NaivePyDESSEM.ThermalGenerator.md#typical-objective-miqp-form)
    * [Usage](NaivePyDESSEM.ThermalGenerator.md#id6)
    * [Intended pairing](NaivePyDESSEM.ThermalGenerator.md#intended-pairing)
    * [`ThermalData`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData)
      * [`ThermalData.Cdef`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData.Cdef)
      * [`ThermalData.Rreq`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData.Rreq)
      * [`ThermalData.demand`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData.demand)
      * [`ThermalData.has_history`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData.has_history)
      * [`ThermalData.horizon`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData.horizon)
      * [`ThermalData.units`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData.units)
    * [`ThermalUnit`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit)
      * [`ThermalUnit.Pmax`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.Pmax)
      * [`ThermalUnit.Pmin`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.Pmin)
      * [`ThermalUnit.RD`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.RD)
      * [`ThermalUnit.RU`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.RU)
      * [`ThermalUnit.SC`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.SC)
      * [`ThermalUnit.a`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.a)
      * [`ThermalUnit.b`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.b)
      * [`ThermalUnit.c`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.c)
      * [`ThermalUnit.gamma`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.gamma)
      * [`ThermalUnit.init_status_h`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.init_status_h)
      * [`ThermalUnit.name`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.name)
      * [`ThermalUnit.p0`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.p0)
      * [`ThermalUnit.pw_breaks`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.pw_breaks)
      * [`ThermalUnit.pw_costs`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.pw_costs)
      * [`ThermalUnit.t_down`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.t_down)
      * [`ThermalUnit.t_up`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.t_up)
      * [`ThermalUnit.u0`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit.u0)
  * [NaivePyDESSEM.ThermalGenerator.ThermalEquations module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalEquations)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#id7)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#id8)
    * [Intended Use](NaivePyDESSEM.ThermalGenerator.md#intended-use)
    * [`add_thermal_balance_expression()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalEquations.add_thermal_balance_expression)
    * [`add_thermal_cost_expression()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalEquations.add_thermal_cost_expression)
  * [NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#id9)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#id10)
    * [Builder Function](NaivePyDESSEM.ThermalGenerator.md#builder-function)
    * [Usage](NaivePyDESSEM.ThermalGenerator.md#id11)
    * [`add_thermal_problem()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_problem)
    * [`build_thermal_uc()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder.build_thermal_uc)
  * [NaivePyDESSEM.ThermalGenerator.ThermalObjectives module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalObjectives)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#id12)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#id13)
    * [Usage](NaivePyDESSEM.ThermalGenerator.md#id14)
    * [`set_objective_thermo_miqp()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalObjectives.set_objective_thermo_miqp)
    * [`set_objective_thermo_pwl()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalObjectives.set_objective_thermo_pwl)
  * [NaivePyDESSEM.ThermalGenerator.ThermalPieceWise module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalPieceWise)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#id15)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#id16)
    * [Features](NaivePyDESSEM.ThermalGenerator.md#features)
    * [Requirements](NaivePyDESSEM.ThermalGenerator.md#requirements)
    * [Usage](NaivePyDESSEM.ThermalGenerator.md#id17)
    * [`thermal_add_piecewise_cost()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalPieceWise.thermal_add_piecewise_cost)
  * [NaivePyDESSEM.ThermalGenerator.ThermalVars module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalVars)
    * [Author](NaivePyDESSEM.ThermalGenerator.md#id19)
    * [Description](NaivePyDESSEM.ThermalGenerator.md#id20)
    * [Features](NaivePyDESSEM.ThermalGenerator.md#id21)
    * [Variables](NaivePyDESSEM.ThermalGenerator.md#variables)
    * [Usage](NaivePyDESSEM.ThermalGenerator.md#id22)
    * [`thermal_add_sets_and_params()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalVars.thermal_add_sets_and_params)
    * [`thermal_add_variables_uc()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalVars.thermal_add_variables_uc)
* [NaivePyDESSEM.cli package](NaivePyDESSEM.cli.md)
  * [Module contents](NaivePyDESSEM.cli.md#module-NaivePyDESSEM.cli)
    * [NaivePyDESSEM – CLI Subpackage](NaivePyDESSEM.cli.md#naivepydessem-cli-subpackage)
      * [Author](NaivePyDESSEM.cli.md#author)
      * [Description](NaivePyDESSEM.cli.md#description)
      * [Modules](NaivePyDESSEM.cli.md#modules)
      * [Features](NaivePyDESSEM.cli.md#features)
      * [Example Usage](NaivePyDESSEM.cli.md#example-usage)
  * [Submodules](NaivePyDESSEM.cli.md#submodules)
  * [NaivePyDESSEM.cli.cli module](NaivePyDESSEM.cli.md#module-NaivePyDESSEM.cli.cli)
    * [Author](NaivePyDESSEM.cli.md#id1)
    * [Description](NaivePyDESSEM.cli.md#id2)
    * [Features](NaivePyDESSEM.cli.md#id3)
    * [Dependencies](NaivePyDESSEM.cli.md#dependencies)
    * [Usage](NaivePyDESSEM.cli.md#usage)
    * [`main()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.cli.main)
    * [`print_welcome_banner()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.cli.print_welcome_banner)
    * [`save_dataframe()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.cli.save_dataframe)
  * [NaivePyDESSEM.cli.plot_cli module](NaivePyDESSEM.cli.md#module-NaivePyDESSEM.cli.plot_cli)
    * [Author](NaivePyDESSEM.cli.md#id4)
    * [Description](NaivePyDESSEM.cli.md#id5)
    * [Features](NaivePyDESSEM.cli.md#id6)
    * [Categories](NaivePyDESSEM.cli.md#categories)
    * [Dependencies](NaivePyDESSEM.cli.md#id7)
    * [Usage](NaivePyDESSEM.cli.md#id8)
    * [Quick examples](NaivePyDESSEM.cli.md#quick-examples)
    * [`handle_control_variables()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.handle_control_variables)
    * [`handle_plot()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.handle_plot)
    * [`handle_table()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.handle_table)
    * [`load_dataframe()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.load_dataframe)
    * [`main()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.main)
    * [`print_welcome_banner()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.print_welcome_banner)
    * [`prompt()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.prompt)
    * [`select_columns_multi()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.select_columns_multi)
    * [`select_variable_columns()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.select_variable_columns)

## Submodules

## NaivePyDESSEM.Builder module

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

### NaivePyDESSEM.Builder.build_balance_and_objective_from_yaml(model: ConcreteModel, yaml_data: Dict[str, Any]) → ConcreteModel

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

### NaivePyDESSEM.Builder.build_model_from_file(path: str) → Tuple[ConcreteModel, Dict]

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

## NaivePyDESSEM.DataFrames module

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

### NaivePyDESSEM.DataFrames.add_cost_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

Append cost components and total demand/deficit to the DataFrame.

This function computes and appends the variable generation cost,
startup cost, deficit cost, and total cost per time period.
It also includes total generation, demand, and deficit series.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to which cost components will be appended.
  * **model** (*ConcreteModel*) – A Pyomo model instance with thermal and system-wide cost variables.
* **Returns:**
  The updated DataFrame including cost components and energy balance data.
* **Return type:**
  pd.DataFrame

### NaivePyDESSEM.DataFrames.add_hydro_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

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

### NaivePyDESSEM.DataFrames.add_renewable_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

Append renewable generation results to a pandas DataFrame.

This function extracts renewable generation values from the Pyomo model
and appends them to the provided DataFrame, one column per renewable unit.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to which the results will be appended.
  * **model** (*ConcreteModel*) – A Pyomo model instance containing renewable generation variables.
* **Returns:**
  The updated DataFrame including renewable generation.
* **Return type:**
  pd.DataFrame

### NaivePyDESSEM.DataFrames.add_storage_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

Append storage dispatch results to a pandas DataFrame.

This function extracts charging, discharging, net output,
and state of charge (SoC) values from the Pyomo model and
adds them as columns to the DataFrame.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to which the results will be appended.
  * **model** (*ConcreteModel*) – A Pyomo model instance containing storage unit variables.
* **Returns:**
  The updated DataFrame including storage dispatch results.
* **Return type:**
  pd.DataFrame

### NaivePyDESSEM.DataFrames.add_thermal_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

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

### NaivePyDESSEM.DataFrames.build_dispatch_dataframe(model: ConcreteModel) → DataFrame

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

## NaivePyDESSEM.Formatters module

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
energy dispatch problems solved by NaivePyDESSEM.

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

### NaivePyDESSEM.Formatters.format_brl(value: float) → str

Format a floating-point number as a Brazilian-style currency string.

This function converts a numeric value into a string formatted with
periods as thousand separators and a comma as the decimal mark,
following the standard Brazilian notation (e.g., R$ 1.234,56).

* **Parameters:**
  **value** (*float*) – The numeric value to format.
* **Returns:**
  The formatted string representing the value in BRL-style.
* **Return type:**
  str

### Examples

```pycon
>>> format_brl(1234567.89)
'1.234.567,89'
```

```pycon
>>> format_brl(42)
'42,00'
```

### Notes

- No currency symbol (e.g., ‘R$’) is included in the output.
- Internally, uses Python formatting and string replacement.

## NaivePyDESSEM.ModelCheck module

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

### NaivePyDESSEM.ModelCheck.has_hydro_model(model: ConcreteModel) → bool

Check whether the given Pyomo model contains all components of a hydro subsystem.

This function verifies the presence of essential attributes associated with
hydropower modeling, including sets and variables related to generation,
volume, flow, and spillage.

* **Parameters:**
  **model** (*ConcreteModel*) – The Pyomo model instance to be validated.
* **Returns:**
  True if all required hydro components are present, False otherwise.
* **Return type:**
  bool

### Notes

The required attributes are:
- T         : Time periods.
- HG        : Set of hydro units.
- hydro_G   : Hydropower generation variable.
- hydro_V   : Reservoir volume variable.
- hydro_Q   : Turbined flow variable.
- hydro_S   : Spillage flow variable.

### NaivePyDESSEM.ModelCheck.has_renewable_model(model: ConcreteModel) → bool

Check whether the given Pyomo model contains all components of a renewable subsystem.

This function verifies whether the model has the necessary sets and variables
to support renewable generation units.

* **Parameters:**
  **model** (*ConcreteModel*) – The Pyomo model instance to be validated.
* **Returns:**
  True if all required renewable components are present, False otherwise.
* **Return type:**
  bool

### Notes

The required attributes are:
- T               : Time periods.
- RU              : Set of renewable units.
- renewable_gen   : Renewable generation variable.

### NaivePyDESSEM.ModelCheck.has_storage_model(model: ConcreteModel) → bool

Check whether the given Pyomo model contains all components of a storage subsystem.

This function ensures that charging, discharging, and state-of-charge variables
are defined for energy storage modeling.

* **Parameters:**
  **model** (*ConcreteModel*) – The Pyomo model instance to be validated.
* **Returns:**
  True if all required storage components are present, False otherwise.
* **Return type:**
  bool

### Notes

The required attributes are:
- T              : Time periods.
- SU             : Set of storage units.
- storage_dis    : Discharging power variable.
- storage_ch     : Charging power variable.
- storage_E      : Energy (state-of-charge) variable.

### NaivePyDESSEM.ModelCheck.has_thermal_model(model: ConcreteModel) → bool

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
- thermal_u     : Commitment status variable (binary).
- thermal_w     : Shutdown indicator variable (binary).
- thermal_y     : Startup indicator variable (binary).
- thermal_SC    : Start-up cost parameter.

## NaivePyDESSEM.ModelFormatters module

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

Use this module as part of the pre-solve interface of NaivePyDESSEM to
provide clarity and visual feedback about the simulation setup.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.ModelFormatters.format_hydro_model(case: Dict) → None

Print formatted information for each hydropower unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘hydro’ section with unit definitions.

### NaivePyDESSEM.ModelFormatters.format_models(case: Dict) → None

Dispatch model formatting routines to subsystem-specific formatters.

* **Parameters:**
  **case** (*dict*) – Input data dictionary containing unit-level information.

### NaivePyDESSEM.ModelFormatters.format_renewable_model(case: Dict) → None

Print formatted information for each renewable generation unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘renewable’ section with unit definitions.

### NaivePyDESSEM.ModelFormatters.format_storage_model(case: Dict) → None

Print formatted information for each storage unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘storage’ section with unit definitions.

### NaivePyDESSEM.ModelFormatters.format_thermal_model(case: Dict) → None

Print formatted information for each thermal generation unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘thermal’ section with unit definitions.

### NaivePyDESSEM.ModelFormatters.model_properties(case: Dict) → None

Print a concise list of subsystems included in the case (hydro, thermal, etc.).

* **Parameters:**
  **case** (*dict*) – Parsed input configuration containing subsystem definitions.

### NaivePyDESSEM.ModelFormatters.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

Uses colored and bold text to enhance readability in the terminal.

### NaivePyDESSEM.ModelFormatters.print_welcome_message(model: ConcreteModel, case: Dict) → None

Display the full welcome message and solver configuration.

This includes the banner, solver details, and an overview of
the model components based on the input dictionary.

* **Parameters:**
  * **model** (*ConcreteModel*) – The Pyomo model instance.
  * **case** (*dict*) – Configuration dictionary loaded from YAML or JSON input.

## NaivePyDESSEM.PlotSeries module

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

### NaivePyDESSEM.PlotSeries.get_distinct_colors(n: int, cmap_name: str = 'tab20') → list[str]

Generate a list of visually distinct colors.

* **Parameters:**
  * **n** (*int*) – Number of colors to generate.
  * **cmap_name** (*str* *,* *optional*) – Name of the Matplotlib colormap to use (default is ‘tab10’).
* **Returns:**
  **colors** – List of hex color strings usable in Matplotlib.
* **Return type:**
  list of str

### NaivePyDESSEM.PlotSeries.plot_series(t: Sequence, series_dict: Dict[str, Sequence[float]], title: str, ylabel: str, file: str, xlabel: str = 'Estágio - T (h)') → None

Plot one or more time series as line graphs.

This function generates a line plot for multiple time-indexed series
and saves the resulting figure to a file. Each series is drawn with a
distinct line style and included in the legend. The x-axis represents
discrete time stages, while the y-axis corresponds to the variable of
interest (e.g., power, flow, volume).

* **Parameters:**
  * **t** (*Sequence*) – Ordered sequence of time stages to be used as the x-axis values.
  * **series_dict** (*Dict* *[**str* *,* *Sequence* *[**float* *]* *]*) – Dictionary mapping labels to numeric sequences. Each sequence must
    have the same length as t. Labels may include LaTeX math ($…$).
  * **title** (*str*) – Title of the plot, displayed at the top of the figure.
  * **ylabel** (*str*) – Label for the y-axis.
  * **xlabel** (*str*) – Label for the x-axis.
  * **file** (*str*) – Output file path where the figure will be saved (e.g., PNG, PDF).
* **Returns:**
  The function saves the generated plot to file.
* **Return type:**
  None

### Notes

- The figure is sized at 8 \* 5 inches and saved at 600 dpi resolution.
- A grid is shown to facilitate reading values.
- The legend is automatically constructed from the provided labels.

### Examples

```pycon
>>> t = range(1, 5)
>>> data = {"U_{1}": [100, 120, 130, 140], "U_{2}": [90, 110, 125, 150]}
>>> plot_series(t, data, title="Hydropower Generation", ylabel="MW",
...             file="generation.png")
# Saves a line plot with two curves to 'generation.png'.
```

### NaivePyDESSEM.PlotSeries.plot_series_bar(t: Sequence, series_dict: Dict[str, Sequence[float]], title: str, ylabel: str, file: str, \*, xlabel: str = 'Estágio - T (h)', stacked: bool = False, width: float = 0.85) → None

Plot multiple time series as bar charts, either grouped or stacked.

This function generates a bar chart visualization for a set of time-indexed
series and saves it to a file. The bars can be rendered side-by-side
(grouped) or stacked to show composition. Each series is labeled and
included in the legend. The x-axis corresponds to discrete time stages.

* **Parameters:**
  * **t** (*Sequence*) – Ordered sequence of time stages to be used as x-axis labels.
  * **series_dict** (*Dict* *[**str* *,* *Sequence* *[**float* *]* *]*) – Dictionary mapping series labels to their corresponding numeric values.
    All series must have the same length as t.
  * **title** (*str*) – Title of the plot.
  * **ylabel** (*str*) – Label for the y-axis
  * **xlabel** (*str*) – Label for the x-axis.
  * **file** (*str*) – Output file path where the figure will be saved (e.g., PNG, PDF).
  * **stacked** (*bool* *,* *optional*) – If True, plot stacked bars (suitable for compositional views such as
    generation mix). If False, plot grouped bars. Default is False.
  * **width** (*float* *,* *optional*) – Width of the bars. For grouped mode, this value determines the total
    group width. Default is 0.85.
* **Returns:**
  The function saves the generated plot to file.
* **Return type:**
  None

### Notes

- The output figure is saved with 600 dpi resolution and tight bounding box.
- When stacked mode is enabled or only a single series is provided,
  values are drawn cumulatively (top of each other).
- Legend columns are adapted to the number of series.

### Examples

```pycon
>>> t = range(1, 5)
>>> data = {"A": [1, 2, 3, 4], "B": [2, 3, 4, 5]}
>>> plot_series_bar(t, data, title="Example", ylabel="MW", file="out.png")
# Produces and saves a grouped bar chart to 'out.png'.
```

```pycon
>>> plot_series_bar(t, data, title="Stacked", ylabel="MW",
...                 file="out_stacked.png", stacked=True)
# Produces and saves a stacked bar chart to 'out_stacked.png'.
```

## NaivePyDESSEM.Reporting module

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
- Compatible with modular NaivePyDESSEM subsystem architecture.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.Reporting.dispatch_summary(model: ConcreteModel) → None

Print a complete dispatch and cost summary including:
- Total generation and demand.
- Deficit and its monetary cost.
- Thermal cost breakdown (start-up, generation).
- Overall total cost from the model objective.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model instance.

### NaivePyDESSEM.Reporting.hydro_dispatch_summary(model: ConcreteModel) → None

Print unit-level hydropower generation summary in MWh.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with hydropower subsystem.

### NaivePyDESSEM.Reporting.renewable_dispatch_summary(model: ConcreteModel) → None

Print unit-level renewable generation summary in MWh.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with renewable subsystem.

### NaivePyDESSEM.Reporting.storage_dispatch_summary(model: ConcreteModel) → None

Print unit-level storage discharge summary in MWh.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with storage subsystem.

### NaivePyDESSEM.Reporting.thermal_dispatch_summary(model: ConcreteModel) → None

Print unit-level thermal generation summary in MWh.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with thermal subsystem.

## NaivePyDESSEM.Solver module

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

### NaivePyDESSEM.Solver.solve(path: str) → Tuple[ConcreteModel, Dict]

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

## NaivePyDESSEM.Utils module

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

### NaivePyDESSEM.Utils.binary_df_to_colored_latex(df: DataFrame, \*, caption: str = 'Variáveis U, Y e W horárias', label: str = 'tab:bin_table', one_color: str = 'oncell', zero_color: str = 'white', column_format: str | None = None, floatfmt: str = '{:d}', size_cmd: str = '\\\\small') → str

Convert a binary (0/1) pandas DataFrame into a colored LaTeX table.

Cells with value 1 are filled using `\cellcolor{one_color}`; zeros keep
the background set by `zero_color` (default: white). Row labels are
automatically wrapped in math mode (`$...$`). The returned string
contains a complete LaTeX `table` environment with an inner `tabular`.

* **Parameters:**
  * **df** (*pandas.DataFrame*) – Binary matrix to render. The index holds row labels
    (e.g., `'U_{UT_{1}}'`) and the columns are time steps
    (e.g., `0..23`).
  * **caption** (*str* *,* *optional*) – Caption to place under the table in LaTeX.
  * **label** (*str* *,* *optional*) – LaTeX label used for `\ref{...}`.
  * **one_color** (*str* *,* *optional*) – Name of a LaTeX color (defined in the document preamble) used to
    fill cells equal to 1. Example: `"oncell"`.
  * **zero_color** (*str* *,* *optional*) – Background color for cells equal to 0 (default: `"white"`).
  * **column_format** (*str* *or* *None* *,* *optional*) – Column specification for the `tabular` environment
    (e.g., `"l*{24}{c}"`). If `None`, a default is inferred from the
    number of columns.
  * **floatfmt** (*str* *,* *optional*) – Format string used to render numeric entries (e.g., `"{:d}"`).
  * **size_cmd** (*str* *,* *optional*) – LaTeX size command applied inside the table
    (e.g., `"\small"`, `"\scriptsize"`).
* **Returns:**
  LaTeX code for the complete table, ready to paste into your document.
* **Return type:**
  str

### Notes

- Requires `\usepackage[table]{xcolor}` (or a package providing
  `\cellcolor`). Also ensure the color given by `one_color` is defined
  in the preamble, e.g., `\definecolor{oncell}{RGB}{230,240,255}`.
- The function expects a boolean/binary DataFrame. Values other than 0/1
  are rendered using `floatfmt` and will not be colored.
- Row labels are emitted in math mode: `$<label>$`.

### Examples

```pycon
>>> latex = binary_df_to_colored_latex(
...     df,
...     caption="Hourly U, Y and W variables",
...     label="tab:uyw",
...     one_color="oncell",
... )
>>> print(latex[:30])
\begin{table}[ht]
```

### NaivePyDESSEM.Utils.custom_df_to_latex(df: DataFrame, \*, caption: str = 'Table', label: str = 'tab:table', column_format: str | None = None, size_cmd: str = '\\\\small', bold_math_cmd: str = '\\\\mathbf') → str

Render a pandas DataFrame as a LaTeX table with bold header and bold first column.

This function produces a complete LaTeX `table` environment (with
`tabular` inside) using `booktabs` rules. The column headers are
boldfaced. The first column (index) is also boldfaced. Any math-mode
fragments inside **bolded** cells (i.e., header cells and first-column
cells) are additionally set in bold math using the chosen command
(default: `\boldsymbol`). Inline math is detected if delimited by
`$...$` or `\(...\)`. Non-math text in bolded cells is wrapped
with `\textbf{...}`.

* **Parameters:**
  * **df** (*pandas.DataFrame*) – Table to render. The DataFrame’s index becomes the first (row-label)
    column. The index name (if any) is used for the top-left header cell.
  * **caption** (*str* *,* *optional*) – Caption for the LaTeX table.
  * **label** (*str* *,* *optional*) – LaTeX label used with `\ref{...}`.
  * **column_format** (*str* *or* *None* *,* *optional*) – Column specification for the `tabular` environment. If `None`,
    it defaults to left alignment for the first column and centered
    alignment for the remaining columns (i.e., `"l" + "c"*ncols`).
  * **size_cmd** (*str* *,* *optional*) – A LaTeX size command applied inside the table (e.g., `"\small"`,
    `"\scriptsize"`).
  * **bold_math_cmd** (*str* *,* *optional*) – Command used to bold math fragments (e.g., `"\boldsymbol"` or
    `"\bm"`). Ensure the corresponding package is loaded.
* **Returns:**
  LaTeX code for the complete table, ready to paste into a document.
* **Return type:**
  str

### Notes

- Requires `\usepackage{booktabs}` and a package providing the chosen
  math-bold command (e.g., `\usepackage{amsmath}` for `\boldsymbol`,
  or `\usepackage{bm}` for `\bm`).
- Math detection is applied **only** to bolded cells (header and first
  column). Other cells are emitted verbatim (no escaping is performed).
- If a math fragment is *already* bold (e.g., contains `\boldsymbol{...}`
  or `\bm{...}` or `\mathbf{...}`), it is left unchanged.

### Examples

```pycon
>>> import pandas as pd
>>> df = pd.DataFrame([[1, 2], [3, 4]], index=[r"$x_1$", r"$x_2$"], columns=["t=1", "t=2"])
>>> print(df_to_latex_bold_firstcol_header(df, caption="Example", label="tab:ex")[:60])
\begin{table}[!ht]
```

## NaivePyDESSEM.YAMLLoader module

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

### NaivePyDESSEM.YAMLLoader.key_replace(key: str) → str

Convert a unit identifier of the form NAME_index into a LaTeX-friendly
token with a braced subscript.

The function partitions the input at the first underscore and returns
the formatted string {HEAD_{TAIL}}. If the input contains no
underscore, the original key is returned unchanged.

* **Parameters:**
  **key** (*str*) – Unit identifier, typically in the form “PLANT_1” or “UT_10”.
* **Returns:**
  The LaTeX-ready identifier. For example, “UT_10” becomes
  “{UT_{10}}”. If no underscore is present, the function returns
  the input key unmodified.
* **Return type:**
  str

### Examples

```pycon
>>> key_replace("UHE_1")
'{UHE_{1}}'
>>> key_replace("UT10")
'UT10'
>>> key_replace("PLANT_UNIT_1")
'{PLANT_{UNIT_1}}'
```

### Notes

Only the first underscore is considered for partitioning; the remainder
of the string (including additional underscores) is kept verbatim inside
the subscript block.

### NaivePyDESSEM.YAMLLoader.pre_process(config_dict: Dict[str, Any], \*, transform_names: bool = True) → Dict[str, Any]

Construct a processed configuration dictionary from raw input, with optional name transformation.

This function prepares a structured configuration dictionary for modeling use by:

- copying the meta section unchanged,
- applying deep copies to all other sections,
- and optionally transforming unit names and upstream references in each section
  that contains a units block (e.g., hydro, thermal, renewable).

The transformation of unit names and upstream references
is controlled by the transform_names flag. The function does not modify the input
dictionary in-place.

* **Parameters:**
  * **config_dict** (*dict*) – Raw configuration dictionary loaded from a YAML file or equivalent source.
    Expected to contain a meta section and any number of other sections such as
    hydro, thermal, renewable, or storage.
  * **transform_names** (*bool* *,* *optional*) – Whether to apply LaTeX-compatible formatting to unit names and upstreams
    using key_replace. If False, names are preserved as-is.
    Default is True.
* **Returns:**
  A fully processed configuration dictionary with all subsections and units
  properly structured. The returned dictionary is a deep copy and does not
  share references with the input.
* **Return type:**
  dict

### Examples

```pycon
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
```

### Notes

- Sections without a units field are copied verbatim.
- If units is present but not a dictionary, it is ignored safely.
- This function is intended as a preprocessing step before model instantiation.

### NaivePyDESSEM.YAMLLoader.yaml_loader(file: str, \*, transform_names: bool = True) → Dict[str, Any]

Load a YAML configuration file and apply structural pre-processing.

This function reads a YAML-formatted file and parses it into a Python dictionary.
After loading, it invokes the pre_process routine to deep-copy all sections,
standardize the structure, and optionally apply LaTeX-style name transformations
to unit identifiers and upstream references.

The resulting configuration is ready for use in optimization models or simulation
routines that require consistent internal naming and indexing.

* **Parameters:**
  * **file** (*str*) – Path to the YAML file containing the case configuration.
  * **transform_names** (*bool* *,* *optional*) – Whether to apply LaTeX-friendly formatting to unit names (e.g., UT_1 => {UT_{1}})
    and update upstream references accordingly. If False, original names are preserved.
    Default is True.
* **Returns:**
  A processed configuration dictionary with all metadata and units structured
  consistently. This dictionary is independent of the raw file contents.
* **Return type:**
  dict
* **Raises:**
  **ValueError** – If the YAML file is empty, malformed, or does not contain a valid dictionary structure.

### Examples

```pycon
>>> config = yaml_loader("caso.yaml")
>>> config["hydro"]["units"].keys()
dict_keys(['{UHE_{1}}', '{UHE_{2}}'])
```

### Notes

- The input file must be UTF-8 encoded and must define a top-level dictionary.
- All nested structures are copied safely; no mutation occurs on the raw parsed data.
- This function is the recommended entry point for loading structured model input files.
