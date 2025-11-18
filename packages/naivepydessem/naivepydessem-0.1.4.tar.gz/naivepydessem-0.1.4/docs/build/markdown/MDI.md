# MDI package

## Module contents

### MDI — A Didactic Expansion Planning Framework for the NaivePyDESSEM Package

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

The `MDI` package provides a modular and extensible framework for
long-term expansion planning of electric power systems.
Inspired by the methodology and architecture of CEPEL’s MDI model,
it enables the formulation, solution, and analysis of mixed-integer
expansion planning problems using Pyomo.

Although simplified for educational purposes, the framework preserves
the essential principles of real-world models, including multi-technology
dispatch coordination, storage operation, and deficit cost representation.

#### Description

The package integrates multiple energy technologies—thermal, hydraulic,
renewable, and storage—into a coherent optimization structure that
minimizes investment and operational costs while satisfying technical
and economic adequacy constraints.

It is specifically designed for academic use, research, and the
demonstration of optimization-based methodologies for energy planning,
emphasizing transparency and pedagogical clarity.

#### Submodules

Generator
: Defines the data structures, constraints, and operational cost models
  for thermal and other dispatchable generation units.

Storage
: Models energy storage systems (e.g., batteries), including state-of-charge
  dynamics, charge/discharge limits, efficiencies, and integration into
  system-wide balance and cost formulations.

YAMLLoader
: Provides a structured interface for loading problem instances from YAML
  or JSON files, including schema validation and automatic conversion
  to dataclass-based objects.

Builder
: Constructs the complete Pyomo model by invoking the relevant subsystems,
  generating the energy balance constraints, and defining the
  cost-minimizing objective function.

Solver
: Manages solver configuration and execution (e.g., GLPK, IPOPT, MindtPy),
  with optional reporting, sensitivity analysis, and feasibility diagnostics.

DataFrames
: Exports decision variable trajectories and economic indicators
  to Pandas DataFrames for post-solution analysis and visualization.

PlotSeries
: Generates time-series and comparative dispatch plots using Matplotlib.

Utils, Formatters, Reporting
: Auxiliary modules for formatting, summary reporting, model validation,
  and console visualization using Colorama.

### Notes

- Each subsystem (e.g., Generator, Storage) can be selectively activated
  or excluded through the YAML configuration interface.
- The implementation follows the conceptual logic of the MDI methodology,
  while remaining intentionally simplified for didactic transparency.
- The framework serves as a foundation for further extensions such as
  emission cost modeling, pumped storage systems, stochastic optimization,
  or multi-area coupling.
- Fully compatible with Pyomo’s modeling abstractions and solver interfaces.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*,

> Lecture Notes, EELT7030/UFPR, 2023.

## Subpackages

* [MDI.Generator package](MDI.Generator.md)
  * [Module contents](MDI.Generator.md#module-MDI.Generator)
    * [Generator Subpackage](MDI.Generator.md#generator-subpackage)
      * [Author](MDI.Generator.md#author)
      * [Summary](MDI.Generator.md#summary)
      * [Description](MDI.Generator.md#description)
      * [Modules](MDI.Generator.md#modules)
      * [Structure Overview](MDI.Generator.md#structure-overview)
      * [Exports](MDI.Generator.md#exports)
  * [Submodules](MDI.Generator.md#submodules)
  * [MDI.Generator.GeneratorBuilder module](MDI.Generator.md#module-MDI.Generator.GeneratorBuilder)
    * [Generator Builder Module](MDI.Generator.md#generator-builder-module)
      * [Author](MDI.Generator.md#id1)
      * [Summary](MDI.Generator.md#id2)
      * [Description](MDI.Generator.md#id3)
      * [Functions](MDI.Generator.md#functions)
    * [`add_generator_problem()`](MDI.Generator.md#MDI.Generator.GeneratorBuilder.add_generator_problem)
    * [`build_generators()`](MDI.Generator.md#MDI.Generator.GeneratorBuilder.build_generators)
  * [MDI.Generator.GeneratorConstraints module](MDI.Generator.md#module-MDI.Generator.GeneratorConstraints)
    * [Generator Constraints Module](MDI.Generator.md#generator-constraints-module)
      * [Author](MDI.Generator.md#id4)
      * [Summary](MDI.Generator.md#id5)
      * [Description](MDI.Generator.md#id6)
      * [Functions](MDI.Generator.md#id7)
      * [Module Dependencies](MDI.Generator.md#module-dependencies)
    * [`add_generator_investment_link_constraint()`](MDI.Generator.md#MDI.Generator.GeneratorConstraints.add_generator_investment_link_constraint)
    * [`add_generator_power_limits_constraint()`](MDI.Generator.md#MDI.Generator.GeneratorConstraints.add_generator_power_limits_constraint)
  * [MDI.Generator.GeneratorDataTypes module](MDI.Generator.md#module-MDI.Generator.GeneratorDataTypes)
    * [Generator Data Types Module](MDI.Generator.md#generator-data-types-module)
      * [Author](MDI.Generator.md#id8)
      * [Summary](MDI.Generator.md#id9)
      * [Description](MDI.Generator.md#id10)
      * [Classes](MDI.Generator.md#classes)
      * [Module Dependencies](MDI.Generator.md#id11)
    * [`GeneratorData`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorData)
      * [`GeneratorData.demand`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorData.demand)
      * [`GeneratorData.horizon`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorData.horizon)
      * [`GeneratorData.level_hours`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorData.level_hours)
      * [`GeneratorData.units`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorData.units)
    * [`GeneratorUnit`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit)
      * [`GeneratorUnit.c_inv`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit.c_inv)
      * [`GeneratorUnit.c_op`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit.c_op)
      * [`GeneratorUnit.include_cap`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit.include_cap)
      * [`GeneratorUnit.name`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit.name)
      * [`GeneratorUnit.p_max`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit.p_max)
      * [`GeneratorUnit.state`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit.state)
  * [MDI.Generator.GeneratorEquations module](MDI.Generator.md#module-MDI.Generator.GeneratorEquations)
    * [Generator Equations Module](MDI.Generator.md#generator-equations-module)
      * [Author](MDI.Generator.md#id12)
      * [Summary](MDI.Generator.md#id13)
      * [Description](MDI.Generator.md#id14)
      * [Functions](MDI.Generator.md#id15)
      * [Module Dependencies](MDI.Generator.md#id16)
    * [`add_generator_balance_expression()`](MDI.Generator.md#MDI.Generator.GeneratorEquations.add_generator_balance_expression)
    * [`add_generator_capacity_expression()`](MDI.Generator.md#MDI.Generator.GeneratorEquations.add_generator_capacity_expression)
    * [`add_generator_cost_expression()`](MDI.Generator.md#MDI.Generator.GeneratorEquations.add_generator_cost_expression)
  * [MDI.Generator.GeneratorObjectives module](MDI.Generator.md#module-MDI.Generator.GeneratorObjectives)
    * [Generator Objectives Module](MDI.Generator.md#generator-objectives-module)
      * [Author](MDI.Generator.md#id17)
      * [Summary](MDI.Generator.md#id18)
      * [Description](MDI.Generator.md#id19)
      * [Functions](MDI.Generator.md#id20)
      * [Module Dependencies](MDI.Generator.md#id21)
    * [`set_objective_generator()`](MDI.Generator.md#MDI.Generator.GeneratorObjectives.set_objective_generator)
  * [MDI.Generator.GeneratorVars module](MDI.Generator.md#module-MDI.Generator.GeneratorVars)
    * [Generator Variables and Parameters Module](MDI.Generator.md#generator-variables-and-parameters-module)
      * [Author](MDI.Generator.md#id22)
      * [Summary](MDI.Generator.md#id23)
      * [Description](MDI.Generator.md#id24)
      * [Mathematical Representation](MDI.Generator.md#mathematical-representation)
      * [Functions](MDI.Generator.md#id25)
      * [Module Dependencies](MDI.Generator.md#id26)
    * [`generator_add_sets_and_params()`](MDI.Generator.md#MDI.Generator.GeneratorVars.generator_add_sets_and_params)
    * [`generator_add_variables()`](MDI.Generator.md#MDI.Generator.GeneratorVars.generator_add_variables)
* [MDI.Storage package](MDI.Storage.md)
  * [Module contents](MDI.Storage.md#module-MDI.Storage)
    * [Storage Subpackage](MDI.Storage.md#storage-subpackage)
      * [Author](MDI.Storage.md#author)
      * [Summary](MDI.Storage.md#summary)
      * [Description](MDI.Storage.md#description)
      * [Modules](MDI.Storage.md#modules)
      * [Structure Overview](MDI.Storage.md#structure-overview)
      * [Exports](MDI.Storage.md#exports)
  * [Submodules](MDI.Storage.md#submodules)
  * [MDI.Storage.StorageBuilder module](MDI.Storage.md#module-MDI.Storage.StorageBuilder)
    * [Storage Builder Module](MDI.Storage.md#storage-builder-module)
      * [Author](MDI.Storage.md#id1)
      * [Summary](MDI.Storage.md#id2)
      * [Description](MDI.Storage.md#id3)
      * [Mathematical Overview](MDI.Storage.md#mathematical-overview)
      * [Functions](MDI.Storage.md#functions)
      * [Module Dependencies](MDI.Storage.md#module-dependencies)
    * [`add_storage_problem()`](MDI.Storage.md#MDI.Storage.StorageBuilder.add_storage_problem)
    * [`build_storage()`](MDI.Storage.md#MDI.Storage.StorageBuilder.build_storage)
  * [MDI.Storage.StorageConstraints module](MDI.Storage.md#module-MDI.Storage.StorageConstraints)
    * [Storage Constraints Module](MDI.Storage.md#storage-constraints-module)
      * [Author](MDI.Storage.md#id4)
      * [Summary](MDI.Storage.md#id5)
      * [Description](MDI.Storage.md#id6)
      * [Mathematical Formulation](MDI.Storage.md#mathematical-formulation)
      * [Functions](MDI.Storage.md#id7)
      * [Module Dependencies](MDI.Storage.md#id8)
    * [`add_storage_energy_balance_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_energy_balance_constraint)
    * [`add_storage_investment_link_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_investment_link_constraint)
    * [`add_storage_power_limits_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_power_limits_constraint)
    * [`add_storage_soc_bounds_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_soc_bounds_constraint)
  * [MDI.Storage.StorageDataTypes module](MDI.Storage.md#module-MDI.Storage.StorageDataTypes)
    * [Storage Data Types Module](MDI.Storage.md#storage-data-types-module)
      * [Author](MDI.Storage.md#id9)
      * [Summary](MDI.Storage.md#id10)
      * [Description](MDI.Storage.md#id11)
      * [Mathematical Interpretation](MDI.Storage.md#mathematical-interpretation)
      * [Usage](MDI.Storage.md#usage)
      * [Classes](MDI.Storage.md#classes)
    * [`StorageData`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData)
      * [`StorageData.horizon`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData.horizon)
      * [`StorageData.demand`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData.demand)
      * [`StorageData.level_hours`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData.level_hours)
      * [`StorageData.delta_t`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData.delta_t)
      * [`StorageData.units`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData.units)
      * [`StorageData.delta_t`](MDI.Storage.md#id0)
      * [`StorageData.demand`](MDI.Storage.md#id12)
      * [`StorageData.horizon`](MDI.Storage.md#id13)
      * [`StorageData.level_hours`](MDI.Storage.md#id14)
      * [`StorageData.units`](MDI.Storage.md#id15)
    * [`StorageUnit`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit)
      * [`StorageUnit.name`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.name)
      * [`StorageUnit.state`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.state)
      * [`StorageUnit.c_op`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.c_op)
      * [`StorageUnit.c_inv`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.c_inv)
      * [`StorageUnit.Emin`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.Emin)
      * [`StorageUnit.Emax`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.Emax)
      * [`StorageUnit.Eini`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.Eini)
      * [`StorageUnit.Pch_max`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.Pch_max)
      * [`StorageUnit.Pdis_max`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.Pdis_max)
      * [`StorageUnit.eta_c`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.eta_c)
      * [`StorageUnit.eta_d`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit.eta_d)
      * [`StorageUnit.Eini`](MDI.Storage.md#id16)
      * [`StorageUnit.Emax`](MDI.Storage.md#id17)
      * [`StorageUnit.Emin`](MDI.Storage.md#id18)
      * [`StorageUnit.Pch_max`](MDI.Storage.md#id19)
      * [`StorageUnit.Pdis_max`](MDI.Storage.md#id20)
      * [`StorageUnit.c_inv`](MDI.Storage.md#id21)
      * [`StorageUnit.c_op`](MDI.Storage.md#id22)
      * [`StorageUnit.eta_c`](MDI.Storage.md#id23)
      * [`StorageUnit.eta_d`](MDI.Storage.md#id24)
      * [`StorageUnit.name`](MDI.Storage.md#id25)
      * [`StorageUnit.state`](MDI.Storage.md#id26)
  * [MDI.Storage.StorageEquations module](MDI.Storage.md#module-MDI.Storage.StorageEquations)
    * [Storage Equations Module](MDI.Storage.md#storage-equations-module)
      * [Author](MDI.Storage.md#id27)
      * [Summary](MDI.Storage.md#id28)
      * [Description](MDI.Storage.md#id29)
      * [Mathematical Formulation](MDI.Storage.md#id30)
      * [Functions](MDI.Storage.md#id31)
      * [Module Dependencies](MDI.Storage.md#id32)
    * [`add_storage_balance_expression()`](MDI.Storage.md#MDI.Storage.StorageEquations.add_storage_balance_expression)
    * [`add_storage_capacity_expression()`](MDI.Storage.md#MDI.Storage.StorageEquations.add_storage_capacity_expression)
    * [`add_storage_cost_expression()`](MDI.Storage.md#MDI.Storage.StorageEquations.add_storage_cost_expression)
  * [MDI.Storage.StorageObjective module](MDI.Storage.md#module-MDI.Storage.StorageObjective)
    * [Storage Objective Function Module](MDI.Storage.md#storage-objective-function-module)
      * [Author](MDI.Storage.md#id33)
      * [Summary](MDI.Storage.md#id34)
      * [Description](MDI.Storage.md#id35)
      * [Mathematical Formulation](MDI.Storage.md#id36)
      * [Functions](MDI.Storage.md#id37)
    * [`set_objective_storage()`](MDI.Storage.md#MDI.Storage.StorageObjective.set_objective_storage)
  * [MDI.Storage.StorageVars module](MDI.Storage.md#module-MDI.Storage.StorageVars)
    * [Storage Variables and Parameters Module](MDI.Storage.md#storage-variables-and-parameters-module)
      * [Author](MDI.Storage.md#id38)
      * [Summary](MDI.Storage.md#id39)
      * [Description](MDI.Storage.md#id40)
      * [Mathematical Overview](MDI.Storage.md#id41)
      * [Functions](MDI.Storage.md#id42)
      * [Module Dependencies](MDI.Storage.md#id43)
    * [`storage_add_sets_and_params()`](MDI.Storage.md#MDI.Storage.StorageVars.storage_add_sets_and_params)
    * [`storage_add_variables()`](MDI.Storage.md#MDI.Storage.StorageVars.storage_add_variables)
* [MDI.cli package](MDI.cli.md)
  * [Module contents](MDI.cli.md#module-MDI.cli)
    * [NaivePyDESSEM – CLI Subpackage](MDI.cli.md#naivepydessem-cli-subpackage)
      * [Author](MDI.cli.md#author)
      * [Description](MDI.cli.md#description)
      * [Modules](MDI.cli.md#modules)
      * [Features](MDI.cli.md#features)
      * [Example Usage](MDI.cli.md#example-usage)
  * [Submodules](MDI.cli.md#submodules)
  * [MDI.cli.cli module](MDI.cli.md#module-MDI.cli.cli)
    * [MDI Command-Line Interface (CLI)](MDI.cli.md#mdi-command-line-interface-cli)
      * [Author](MDI.cli.md#id1)
      * [Summary](MDI.cli.md#summary)
      * [Description](MDI.cli.md#id2)
      * [Functions](MDI.cli.md#functions)
    * [`main()`](MDI.cli.md#MDI.cli.cli.main)
    * [`print_welcome_banner()`](MDI.cli.md#MDI.cli.cli.print_welcome_banner)
    * [`save_dataframe()`](MDI.cli.md#MDI.cli.cli.save_dataframe)
  * [MDI.cli.plot_cli module](MDI.cli.md#module-MDI.cli.plot_cli)
    * [Author](MDI.cli.md#id3)
    * [Description](MDI.cli.md#id4)
    * [Features](MDI.cli.md#id5)
    * [Categories](MDI.cli.md#categories)
    * [Dependencies](MDI.cli.md#dependencies)
    * [Usage](MDI.cli.md#usage)
    * [Quick examples](MDI.cli.md#quick-examples)
    * [`handle_control_variables()`](MDI.cli.md#MDI.cli.plot_cli.handle_control_variables)
    * [`handle_plot()`](MDI.cli.md#MDI.cli.plot_cli.handle_plot)
    * [`handle_table()`](MDI.cli.md#MDI.cli.plot_cli.handle_table)
    * [`load_dataframe()`](MDI.cli.md#MDI.cli.plot_cli.load_dataframe)
    * [`main()`](MDI.cli.md#MDI.cli.plot_cli.main)
    * [`print_welcome_banner()`](MDI.cli.md#MDI.cli.plot_cli.print_welcome_banner)
    * [`prompt()`](MDI.cli.md#MDI.cli.plot_cli.prompt)
    * [`select_columns_multi()`](MDI.cli.md#MDI.cli.plot_cli.select_columns_multi)
    * [`select_variable_columns()`](MDI.cli.md#MDI.cli.plot_cli.select_variable_columns)

## Submodules

## MDI.Builder module

### Builder Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

The **Builder** module provides the high-level orchestration routines for constructing
a complete **MDI (Modular Decision Infrastructure)** system model. It integrates
the Generator and Storage subsystems, validates YAML input data, and assembles
the optimization problem by defining constraints, objectives, and auxiliary
expressions using **Pyomo**.

#### Description

This module serves as the *entry point* for model instantiation from a YAML specification,
including validation of meta parameters, generation and storage data, and global
power balance. It encapsulates all system-level expressions such as:

- **Adequacy Constraint** — ensures total available capacity meets mean demand.
- **Power Balance** — enforces node-level balance between demand and generation.
- **Objective Function** — minimizes total system costs including generation, storage, and deficit penalties.

It also handles automatic conversion of YAML datasets into GeneratorData and
StorageData dataclasses, ensuring consistency of units, bounds, and efficiency parameters.

#### Functions

\_validate_meta(meta)
: Performs structural and numerical checks on the metadata section.

\_validate_demand(d, T)
: Validates demand profiles (currently placeholder).

\_validate_storage(storage)
: Ensures energy capacity and efficiency values are within valid physical limits.

\_validate_generator(generators)
: Validates generator attributes and required fields.

\_mk_generator_data(root)
: Factory for creating a GeneratorData instance from YAML input.

\_mk_storage_data(root)
: Factory for creating a StorageData instance from YAML input.

compute_mean_demand(m, yaml_data)
: Computes weighted mean demand over all load levels and attaches it to the model.

add_system_adequacy_expression(m)
: Adds a system adequacy constraint based on installed capacity.

build_balance_and_objective_from_yaml(model, yaml_data)
: Constructs balance constraints and total cost objective function.

build_model_from_file(path)
: High-level entry point: loads YAML, validates, builds subsystems,
  and returns a complete ConcreteModel.

### Notes

- Requires **Pyomo ≥ 6.6.0**.
- YAML input structure must contain sections: meta, generator, storage.
- All time indices (t) are assumed to start at 1 (Pyomo convention).
- The Builder supports both investment and operational formulations.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### MDI.Builder.build_balance_and_objective_from_yaml(model: ConcreteModel, yaml_data: Dict[str, Any]) → ConcreteModel

### MDI.Builder.build_model_from_file(path: str) → Tuple[ConcreteModel, Dict]

## MDI.DataFrames module

### Dataframes Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

The **Dataframes** module provides structured routines for converting
optimization results from **Pyomo** models into analytical **pandas DataFrames**.
It enables direct visualization and statistical evaluation of dispatch,
cost, and marginal values from the **MDI (Modular Decision Infrastructure)** framework.

#### Description

This module acts as a post-processing interface between the optimization
model and external data analysis tools. It extracts primal and dual
values from the **Pyomo ConcreteModel**, computes derived indicators
(e.g., marginal operation cost), and organizes the results into tabular
form suitable for export to spreadsheets, CSV, or visualization software.

Each function contributes a layer of semantic enrichment to the resulting
dataset, corresponding to a subsystem (generation, storage, cost structure).

#### Functions

add_generator_dispatch_to_dataframe(df, model)
: Extracts generator dispatch, commitment, and investment variables
  from the model and appends them to the provided DataFrame.

add_storage_dispatch_to_dataframe(df, model)
: Extracts storage charge/discharge behavior, state of charge, and
  investment decisions from the model and appends them to the DataFrame.

add_cost_to_dataframe(df, model)
: Computes total operating and investment costs, as well as marginal
  prices such as CMO (Custo Marginal de Operação) and CME (Custo Marginal
  de Expansão). Adds these metrics as new columns to the DataFrame.

build_dispatch_dataframe(model)
: High-level routine that sequentially aggregates generator, storage,
  and cost data into a single unified DataFrame.

### Notes

- Requires **pandas ≥ 2.0.0** and **Pyomo ≥ 6.6.0**.
- All numerical values are retrieved through pyomo.environ.value().
- Dual values must be available (i.e., model must have been solved
  with a solver that supports dual variable extraction).
- The notation CMO and CME corresponds respectively to:
  - *Custo Marginal de Operação* — derived from balance constraints.
  - *Custo Marginal de Expansão* — derived from adequacy constraints.
- Column naming conventions are consistent with the MDI’s export structure
  for integration with visualization dashboards and academic reports.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### MDI.DataFrames.add_cost_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

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

### MDI.DataFrames.add_generator_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

Append generator dispatch results to a pandas DataFrame.

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

### MDI.DataFrames.add_storage_dispatch_to_dataframe(df: DataFrame, model: ConcreteModel) → DataFrame

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

### MDI.DataFrames.build_dispatch_dataframe(model: ConcreteModel) → DataFrame

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

### MDI.DataFrames.compute_CME_by_period(model: ConcreteModel, solver_name: str = 'glpk', delta_E: float = 1.0, reserve_margin: float = 0.15) → dict

Compute CME (Custo Marginal de Energia) and CME de Expansão
for each time period individually via incremental perturbation.

* **Parameters:**
  * **model** (*ConcreteModel*) – Pyomo model with ‘Adequacy’ and ‘Balance’ constraints.
  * **solver_name** (*str* *,* *optional*) – MILP solver name (default: ‘glpk’).
  * **delta_E** (*float* *,* *optional*) – Increment applied to demand in each period (default: 1.0).
  * **reserve_margin** (*float* *,* *optional*) – Fractional capacity increase used in expansion case (default: 0.15).
* **Returns:**
  {
  : “Custo_Base”: float,
    “CME_energia_por_periodo”: { (p,t): value },
    “CME_expansao_por_periodo”: { (p,t): value },
    “CME_global”: float,
    “CME_expansao_global”: float

  }
* **Return type:**
  dict

## MDI.Formatters module

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

## MDI.ModelCheck module

### ModelCheck Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

The **ModelCheck** module provides lightweight structural verification
utilities for **Pyomo ConcreteModel** instances within the
**MDI (Modular Decision Infrastructure)** framework.

Its purpose is to confirm the presence of essential attributes,
sets, and variables that characterize generator and storage subsystems
before performing downstream operations such as dispatch extraction
or cost evaluation.

#### Description

Model verification plays a crucial role in ensuring robustness
and error prevention within modular optimization frameworks.
These functions perform *non-invasive integrity checks* by verifying
the existence of predefined attributes in the model object
without altering its state.

They are used extensively throughout post-processing routines
(e.g., `Dataframes`) to guarantee that operations are executed
only if the corresponding subsystem is present and properly defined.

#### Functions

has_generator_model(model)
: Verifies whether the provided model instance contains all
  mandatory components of a generator subsystem, including sets
  and decision variables for generation, commitment, and investment.

has_storage_model(model)
: Checks whether the model instance includes all necessary
  structures to represent an energy storage subsystem,
  including energy balance, charge/discharge, and state-of-charge
  variables.

#### Usage Example

```pycon
>>> from MDI.ModelCheck import has_generator_model, has_storage_model
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> has_generator_model(m)
False
>>> # After adding generator sets and variables
>>> has_generator_model(m)
True
```

### Notes

- Designed for structural validation only (no numerical evaluation).
- Returns boolean values indicating model completeness.
- Compatible with **Pyomo ≥ 6.6.0**.
- Used internally by data extraction, reporting, and consistency
  modules across the MDI framework.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### MDI.ModelCheck.has_generator_model(model: ConcreteModel) → bool

Check whether the given Pyomo model contains all components of a geerator subsystem.

This function verifies the presence of essential attributes associated with
hydropower modeling, including sets and variables related to generation,
volume, flow, and spillage.

* **Parameters:**
  **model** (*ConcreteModel*) – The Pyomo model instance to be validated.
* **Returns:**
  True if all required hydro components are present, False otherwise.
* **Return type:**
  bool

### MDI.ModelCheck.has_storage_model(model: ConcreteModel) → bool

Check whether the given Pyomo model contains all components of a storage subsystem.

This function ensures that charging, discharging, and state-of-charge variables
are defined for energy storage modeling.

* **Parameters:**
  **model** (*ConcreteModel*) – The Pyomo model instance to be validated.
* **Returns:**
  True if all required storage components are present, False otherwise.
* **Return type:**
  bool

## MDI.ModelFormatters module

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

### MDI.ModelFormatters.format_generator_model(case: Dict) → None

Print formatted information for each generator power unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘generator’ section with unit definitions.

### MDI.ModelFormatters.format_models(case: Dict) → None

Dispatch model formatting routines to subsystem-specific formatters.

* **Parameters:**
  **case** (*dict*) – Input data dictionary containing unit-level information.

### MDI.ModelFormatters.format_storage_model(case: Dict) → None

Print formatted information for each storage unit.

* **Parameters:**
  **case** (*dict*) – Dictionary containing ‘storage’ section with unit definitions.

### MDI.ModelFormatters.model_properties(case: Dict) → None

Print a concise list of subsystems included in the case (generator, thermal, etc.).

* **Parameters:**
  **case** (*dict*) – Parsed input configuration containing subsystem definitions.

### MDI.ModelFormatters.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

Uses colored and bold text to enhance readability in the terminal.

### MDI.ModelFormatters.print_welcome_message(model: ConcreteModel, case: Dict) → None

Display the full welcome message and solver configuration.

This includes the banner, solver details, and an overview of
the model components based on the input dictionary.

* **Parameters:**
  * **model** (*ConcreteModel*) – The Pyomo model instance.
  * **case** (*dict*) – Configuration dictionary loaded from YAML or JSON input.

## MDI.PlotSeries module

### PlotSeries Module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Plotting Utilities for Time Series in Power System Studies

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Description

This module provides high-level plotting routines to visualize time-indexed
variables commonly encountered in short-term operation and planning studies
of hydrothermal systems. It offers both line plots and bar plots, supporting
grouped or stacked styles.

#### Functions

plot_series(t, series_dict, title, ylabel, file)
: Plot one or more time series as line graphs, with LaTeX-compatible labels.

plot_series_bar(t, series_dict, title, ylabel, file, stacked=False, width=0.85)
: Plot multiple time series as bar charts, either grouped or stacked, with
  configurable bar width.

#### Conventions

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

## MDI.Reporting module

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

### MDI.Reporting.dispatch_summary(model: ConcreteModel) → None

Print a complete dispatch and cost summary including:
- Total generation and demand.
- Deficit and its monetary cost.
- Thermal cost breakdown (start-up, generation).
- Overall total cost from the model objective.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model instance.

### MDI.Reporting.generator_dispatch_summary(model: ConcreteModel) → None

Print unit-level generator units generation summary in MWh.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with generator subsystem.

### MDI.Reporting.storage_dispatch_summary(model: ConcreteModel) → None

Print unit-level storage discharge summary in MWh.

* **Parameters:**
  **model** (*ConcreteModel*) – Solved Pyomo model with storage subsystem.

## MDI.Solver module

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

### MDI.Solver.solve(path: str) → Tuple[ConcreteModel, Dict]

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

## MDI.Utils module

### Utils Module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

LaTeX Table Utilities for Pandas DataFrames

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Description

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

#### Functions

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

#### Parameters (Shared)

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

#### Additional Parameters

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

## MDI.YAMLLoader module

### YAMLLoader Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

The **YAMLLoader** module provides standardized routines for reading,
validating, and parsing YAML-based configuration files used by the
**MDI (Modular Decision Infrastructure)** system. It ensures consistency,
traceability, and reliability in loading structured model data such as
meta parameters, generator definitions, and storage configurations.

#### Description

YAML files serve as the primary data input format for the MDI model.
This module abstracts the YAML parsing logic to provide a clean,
reliable interface that returns a fully validated Python dictionary,
suitable for immediate use by the `Builder` module and its
subcomponents.

By encapsulating file I/O operations and schema consistency checks,
the **YAMLLoader** guarantees that the optimization routines receive
complete and well-structured data, preventing common runtime errors
related to malformed inputs.

#### Functions

yaml_loader(path: str) -> dict
: Reads and parses a YAML configuration file located at the specified path.
  Returns a structured Python dictionary suitable for direct use by
  the model builder.

### Notes

- Requires the **PyYAML** library (≥ 6.0).
- The loader assumes UTF-8 encoding by default.
- It is strongly recommended that YAML configurations follow
  a consistent hierarchical schema:

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
