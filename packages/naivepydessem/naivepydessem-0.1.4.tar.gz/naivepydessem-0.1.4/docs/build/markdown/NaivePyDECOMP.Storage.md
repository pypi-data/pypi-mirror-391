# NaivePyDECOMP.Storage package

## Module contents

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Energy Storage Modeling (Storage)

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

The **Storage** package provides a modular framework for incorporating
battery energy storage systems (BESS) into Pyomo-based dispatch and unit
commitment models. It defines the necessary data structures, sets,
parameters, variables, constraints, objectives, and builder functions
to assemble storage-only or hybrid optimization models.

### Submodules

StorageDataTypes
: Dataclasses for storage units and system-level configuration.

StorageVars
: Initialization of Pyomo sets, parameters, and variables.

StorageConstraints
: Constraint builders (SoC balance, bounds, power limits, etc.).

StorageObjectives
: Objective function definitions for storage-only models.

StorageBuilder
: High-level routines to assemble complete storage models.

### Notes

- The package is designed to be interoperable with the Hydro, Thermal,
  and Renewable packages, enabling the construction of hybrid models.
- Naming conventions are consistent across subsystems for clarity and
  maintainability.
- Extensions (e.g., cycling cost, degradation models) can be added
  within this package without altering the external interface.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## Submodules

## NaivePyDECOMP.Storage.StorageBuilder module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage — Model Builder

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

High-level builders for storage-only optimization models in Pyomo. This
module assembles the complete model structure by combining storage sets,
parameters, variables, constraints, and an optional objective function.

### Functions

build_storage(data, include_objective=True)
: Create a new `ConcreteModel` with storage components and, optionally,
  the balance constraint and objective.

add_storage_problem(m, data, include_objective=False)
: Add storage components (sets/params/vars/constraints) to an existing
  model and, optionally, attach the balance constraint and objective.

### Notes

- The default objective minimizes deficit cost (no explicit storage
  operating costs). If you have cycling costs or degradation penalties,
  replace the objective accordingly.
- For hybrid systems (hydro/thermal/renewables + storage), prefer a
  combined system balance and a joint objective in a higher-level builder.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.Storage.StorageBuilder.add_storage_subproblem(m: ConcreteModel, data: [StorageData](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData), stage: int) → ConcreteModel

Add storage dispatch problem structure to an existing model.

This routine initializes storage sets and parameters, declares decision
variables, and attaches operational constraints. Optionally, it enforces
a storage-only system balance and adds a deficit-penalizing objective.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Target model to be updated.
  * **data** ([*StorageData*](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData)) – Input container with horizon, units, and time-step duration.
  * **include_objective** (*bool* *,* *optional*) – If `True`, add the storage-only balance constraint and attach the
    deficit objective (default is `False`).
* **Returns:**
  The updated model with storage components and, optionally, the
  balance constraint and objective.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- Constraints added (always):
  : * Energy (SoC) balance
    * SoC bounds (min/max)
    * Charge/discharge power limits
- If `include_objective=True`:
  : * Add storage-only balance: Σ(dis − ch) + D = d
    * Attach deficit objective

## NaivePyDECOMP.Storage.StorageConstraints module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Energy Storage — Constraints

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module defines the operational constraints for battery energy storage
systems (BESS) within Pyomo-based dispatch and unit commitment models.
The formulation is consistent with the hydraulic and renewable modules,
ensuring interoperability in hybrid optimization frameworks.

### Functions

add_storage_energy_balance_constraint(m)
: Enforce intertemporal state-of-charge balance with charge/discharge
  efficiencies and time-step duration.

add_storage_soc_bounds_constraint(m)
: Impose minimum and maximum state-of-charge limits.

add_storage_power_limits_constraint(m)
: Impose per-period charging and discharging power limits.

add_storage_mutual_exclusion_constraint(m)
: (Optional) Prohibit simultaneous charging and discharging through a
  big-M formulation with binary mode variables.

add_storage_only_balance_constraint(m)
: Enforce system-wide balance for storage-only models, equating net
  injection plus deficit to the demand at each period.

### Notes

- The efficiencies (`eta_c`, `eta_d`) can be specified per stage or
  derived from a round-trip value split by the user.
- For hybrid models (hydro, thermal, renewable, storage), the global
  balance should be implemented at a higher builder level.
- The formulation assumes a fixed period duration `delta_t` in hours,
  used to convert power (MW) to energy (MWh).

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## NaivePyDECOMP.Storage.StorageDataTypes module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage Bank — Data Structures

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Lightweight data classes for battery energy storage systems (BESS). These
structures provide standardized inputs for Pyomo-based unit commitment and
dispatch models.

### Classes

StorageUnit
: Parameters of a single storage unit (SoC bounds, power limits,
  efficiencies, initial state).

StorageData
: System-level container that aggregates storage units and common
  parameters such as time-step duration.

### Notes

- The efficiencies can be specified per stage (charge/discharge) or derived
  from a round-trip value split across both stages by the user before
  instantiation.
- The time-step duration `delta_t` (hours) converts power (MW) to energy
  (MWh) in the state-of-charge balance.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## NaivePyDECOMP.Storage.StorageEquations module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Storage Model Expression Utilities for Pyomo Optimization

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides helper functions to construct symbolic expressions
related to energy storage systems in Pyomo-based optimization models.
These expressions can be incrementally assembled and integrated into
constraints (e.g., state-of-charge evolution) or cost functions (e.g.,
charging/discharging costs).

The functions are designed to support modular model construction and
hybrid system integration. They can be used in conjunction with other
technology modules (e.g., thermal, hydro, renewable) to build power
balance constraints and system-wide cost objectives.

All expressions are symbolic and compatible with Pyomo’s modeling
framework. Each function includes safeguards to ensure that required
model components exist before attempting to generate expressions.

### Intended Use

- To append storage-related cost and energy balance expressions to lists
  that contribute to the overall objective function and constraint set.
- To modularize and standardize storage modeling across different hybrid
  energy system configurations.

### Examples

```pycon
>>> cost_terms = []
>>> add_storage_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)
```

```pycon
>>> balance_terms = []
>>> add_storage_balance_expression(model, t=5, balance_array=balance_terms)
>>> model.StorageBalance.add(balance_terms[0])
```

### Notes

- This module assumes that storage behavior is modeled using variables such as:
  storage_E, storage_ch, storage_dis, storage_Eini,
  and parameters like storage_eta_c, storage_eta_d, and storage_delta_t.
- The structure is compatible with Pyomo’s ConstraintList and indexed Constraint(T).
- Expressions are constructed incrementally and can be combined with other
  sources (e.g., thermal, hydro) in hybrid dispatch models.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023..

## NaivePyDECOMP.Storage.StorageObjective module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage — Objective Function

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Defines the objective function for storage-only dispatch models in Pyomo.
The formulation minimizes the total penalty cost associated with unmet
demand (deficit) over the planning horizon, using the parameter `Cdef`.

### Functions

set_objective_storage(m)
: Attach a minimization objective to the model that penalizes unmet
  demand through `Cdef * D[t]`.

### Notes

- This objective is tailored for storage-only systems without explicit
  operating or cycling costs.
- The penalty coefficient `Cdef` should be chosen sufficiently high
  to discourage deficits under normal operating conditions.
- For hybrid models (hydro, thermal, renewable, storage), a combined
  system-wide objective should be defined at a higher level.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## NaivePyDECOMP.Storage.StorageVars module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage — Sets, Parameters, and Variables

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Provides initialization routines for adding storage-related sets, parameters,
and decision variables to Pyomo-based dispatch and unit commitment models.
This module ensures a consistent interface for modeling battery energy storage
systems (BESS) across different formulations.

### Functions

storage_add_sets_and_params(m, data)
: Initialize sets and Pyomo parameters for storage units, including
  state-of-charge bounds, initial conditions, power limits, efficiencies,
  and time-step duration.

storage_add_variables(m)
: Declare continuous decision variables for state-of-charge, charging
  power, and discharging power. If absent, also define a deficit variable
  for feasibility.

### Notes

- Parameters are namespaced with the prefix `storage_` for clarity and
  compatibility with other subsystems (hydro, thermal, renewable).
- The time-step duration (`delta_t`) converts power (MW) to energy (MWh)
  within the state-of-charge balance equation.
- The variables are declared as non-negative and continuous. Binary
  variables may be added in other modules if mutual exclusion between
  charge and discharge is required.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
