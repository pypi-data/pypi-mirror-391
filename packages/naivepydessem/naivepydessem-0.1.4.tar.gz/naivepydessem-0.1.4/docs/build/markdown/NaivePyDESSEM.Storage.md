# NaivePyDESSEM.Storage package

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

## NaivePyDESSEM.Storage.StorageBuilder module

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

### NaivePyDESSEM.Storage.StorageBuilder.add_storage_problem(m: ConcreteModel, data: [StorageData](#NaivePyDESSEM.Storage.StorageDataTypes.StorageData), include_objective: bool = False) → ConcreteModel

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

### NaivePyDESSEM.Storage.StorageBuilder.build_storage(data: [StorageData](#NaivePyDESSEM.Storage.StorageDataTypes.StorageData), include_objective: bool = True) → ConcreteModel

Construct a complete Pyomo model for storage-only dispatch.

* **Parameters:**
  * **data** ([*StorageData*](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData)) – Input container with horizon, storage units, and time-step duration.
  * **include_objective** (*bool* *,* *optional*) – If `True`, add the storage-only balance constraint and attach the
    deficit objective (default is `True`).
* **Returns:**
  A new model configured with storage sets/params/vars/constraints and,
  optionally, the balance constraint and objective.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- The model contains:
  : * Sets: time periods (`m.T`), storage units (`m.SU`)
    * Parameters: SoC bounds/initial, power limits, efficiencies, Δt
    * Variables: SoC, charge, discharge, and (if missing) deficit
    * Constraints: SoC balance, SoC bounds, power limits
    * Optional: system balance and deficit objective

## NaivePyDESSEM.Storage.StorageConstraints module

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

### NaivePyDESSEM.Storage.StorageConstraints.add_storage_energy_balance_constraint(m)

Add storage energy (SoC) balance constraints.

Enforces conservation of energy per unit and period:

> E[s,1] = Eini[s] + eta_c[s] \* ch[s,1] \* Δt - (dis[s,1] / eta_d[s]) \* Δt
> E[s,t] = E[s,t-1] + eta_c[s] \* ch[s,t] \* Δt - (dis[s,t] / eta_d[s]) \* Δt,  t>1
* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with sets `m.SU`, `m.T`; variables `m.storage_E`,
  `m.storage_ch`, `m.storage_dis`; per-unit parameters
  `m.storage_Eini`, `m.storage_eta_c`, `m.storage_eta_d`; and
  scalar `m.storage_delta_t`.
* **Returns:**
  The same model with constraint block
  `m.storage_energy_balance_constraint`.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDESSEM.Storage.StorageConstraints.add_storage_mutual_exclusion_constraint(m)

(Optional) Prohibit simultaneous charge and discharge.

Uses a big-M logic with a binary mode variable:

> storage_ch[s,t]  <=  M[s] \* storage_mode[s,t]
> storage_dis[s,t] <=  M[s] \* (1 - storage_mode[s,t])

Assumes `m.storage_mode[s,t]` (binary) and `m.storage_M[s]` (big-M)
exist in the model.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with sets `m.SU`, `m.T`; variables `m.storage_ch`,
  `m.storage_dis`, binary `m.storage_mode`; and parameter
  `m.storage_M`.
* **Returns:**
  The same model with mutual exclusion constraints.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDESSEM.Storage.StorageConstraints.add_storage_only_balance_constraint(m)

Add system-wide balance for storage-only models.

Net injection from storage plus deficit must meet demand:

> Σ_s ( storage_dis[s,t] - storage_ch[s,t] )  +  D[t]  =  d[t]
* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with set `m.T`; variables `m.storage_ch`, `m.storage_dis`,
  `m.D`; and parameter `m.d`.
* **Returns:**
  The same model with `m.storage_only_balance_constraint`.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDESSEM.Storage.StorageConstraints.add_storage_power_limits_constraint(m)

Add charging and discharging power limits.

> 0 <= storage_ch[s,t]  <= storage_Pch_max[s]
> 0 <= storage_dis[s,t] <= storage_Pdis_max[s]
* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with sets `m.SU`, `m.T`; variables `m.storage_ch`,
  `m.storage_dis`; and parameters `m.storage_Pch_max`,
  `m.storage_Pdis_max`.
* **Returns:**
  The same model with power limit constraints.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDESSEM.Storage.StorageConstraints.add_storage_soc_bounds_constraint(m)

Add minimum/maximum SoC constraints.

> storage_Emin[s] <= storage_E[s,t] <= storage_Emax[s]
* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with sets `m.SU`, `m.T`; variable `m.storage_E`; and
  parameters `m.storage_Emin`, `m.storage_Emax`.
* **Returns:**
  The same model with upper and lower SoC bounds.
* **Return type:**
  pyomo.environ.ConcreteModel

## NaivePyDESSEM.Storage.StorageDataTypes module

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

### *class* NaivePyDESSEM.Storage.StorageDataTypes.StorageData(horizon: int, demand: Dict[int, float], units: Dict[str, [StorageUnit](#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit)], delta_t: float, Cdef: float = 1000.0)

Bases: `object`

System-wide data container for storage modeling.

* **Parameters:**
  * **horizon** (*int*) – Number of time periods in the planning horizon.
  * **demand** (*Dict* *[**int* *,* *float* *]*) – Mapping of each period `t` (1-based) to system demand (MW).
  * **units** (*Dict* *[**str* *,* [*StorageUnit*](#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit) *]*) – Mapping from unit identifier to [`StorageUnit`](#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit).
  * **delta_t** (*float*) – Time-step duration (hours), used to convert MW to MWh.
  * **Cdef** (*float* *,* *optional*) – Sets the deficit cost. Default is 1000.0

### Notes

- Typical values for `delta_t` are 1.0 (hourly) or 0.5 (30 minutes).

#### Cdef *: float* *= 1000.0*

#### delta_t *: float*

#### demand *: Dict[int, float]*

#### horizon *: int*

#### units *: Dict[str, [StorageUnit](#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit)]*

### *class* NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit(name: str, Emin: float, Emax: float, Eini: float, Pch_max: float, Pdis_max: float, eta_c: float, eta_d: float)

Bases: `object`

Data container for a battery energy storage unit.

* **Parameters:**
  * **name** (*str*) – Unique identifier of the storage unit.
  * **Emin** (*float*) – Minimum energy content (MWh).
  * **Emax** (*float*) – Maximum energy content (MWh).
  * **Eini** (*float*) – Initial energy content at the beginning of the horizon (MWh).
  * **Pch_max** (*float*) – Maximum charging power (MW).
  * **Pdis_max** (*float*) – Maximum discharging power (MW).
  * **eta_c** (*float*) – Charging efficiency in `[0, 1]`.
  * **eta_d** (*float*) – Discharging efficiency in `[0, 1]`.

### Notes

- Ensure `Emin <= Eini <= Emax` for feasibility at the first period.
- If a round-trip efficiency is provided externally, split it into
  `eta_c` and `eta_d` before creating the instance.

#### Eini *: float*

#### Emax *: float*

#### Emin *: float*

#### Pch_max *: float*

#### Pdis_max *: float*

#### eta_c *: float*

#### eta_d *: float*

#### name *: str*

## NaivePyDESSEM.Storage.StorageEquations module

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

### NaivePyDESSEM.Storage.StorageEquations.add_storage_balance_expression(m: ConcreteModel, t: Any, balance_array: List[Any]) → List[Any]

Append energy balance equations for storage units at time t to the constraint expression list.

This function constructs and appends symbolic expressions that enforce the
state-of-charge (SoC) evolution for each storage unit at time step t. The energy
balance accounts for charging and discharging flows, adjusted by their respective
efficiencies, and scaled by the time step duration.

The function distinguishes between the initial period (t == 1), where it uses the
initial energy level storage_Eini, and subsequent periods (t > 1), where it uses
the SoC from the previous period.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing storage variables and parameters.
  * **t** (*int*) – Time index at which the storage energy balance is evaluated.
  * **balance_array** (*list* *of* *expressions*) – List of constraint expressions to which the storage energy balance equation is appended.
* **Returns:**
  The updated list including the storage energy balance constraint at time t.
* **Return type:**
  list of expressions

### Notes

- The expected model components are: SU, T, storage_E
- If any required component is missing, the function returns the input list unchanged.
- The returned expressions can be used with ConstraintList or indexed Constraint(T).

### Examples

```pycon
>>> balance_terms = []
>>> add_storage_balance_expression(model, t=1, balance_array=balance_terms)
>>> model.StorageBalance.add(balance_terms[0])
```

### NaivePyDESSEM.Storage.StorageEquations.add_storage_cost_expression(m: ConcreteModel, cost_array: List[Any]) → List[Any]

Append storage-related cost terms to the total cost expression list.

This function is intended as a placeholder or extension point for
including storage system costs in the objective function of a Pyomo model.
Typical terms may include degradation penalties, charging/discharging costs,
or time-of-use price adjustments.

If no relevant storage cost expressions are defined or required, the function
simply returns the input list unchanged.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing storage system variables.
  * **cost_array** (*list* *of* *expressions*) – List of symbolic expressions used to build the total cost function.
* **Returns:**
  The input list, optionally extended with storage-related cost expressions.
* **Return type:**
  list of expressions

### Notes

- This function is designed to be compatible with modular cost composition
  involving multiple technologies (e.g., thermal, hydro, storage).
- Actual expressions should be added based on model-specific variables
  such as Pch, Pdis, SoC, or energy tariffs if available.

## NaivePyDESSEM.Storage.StorageObjective module

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

### NaivePyDESSEM.Storage.StorageObjective.set_objective_storage(m: ConcreteModel) → ConcreteModel

Attach a deficit-penalizing objective for storage-only models.

### Objective

Minimize the total cost of unmet demand across the horizon:

> minimize  sum_t Cdef \* D[t]
* **param m:**
  Model with set `m.T`, variable `m.D[t]` and parameter `m.Cdef`.
* **type m:**
  pyomo.environ.ConcreteModel
* **returns:**
  The same model with objective `m.OBJ` attached.
* **rtype:**
  pyomo.environ.ConcreteModel

## NaivePyDESSEM.Storage.StorageVars module

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

### NaivePyDESSEM.Storage.StorageVars.storage_add_sets_and_params(m: ConcreteModel, data: [StorageData](#NaivePyDESSEM.Storage.StorageDataTypes.StorageData)) → ConcreteModel

Initialize storage sets and parameters.

Adds the storage unit set, state-of-charge bounds and initial values,
power limits, (dis)charging efficiencies, and the time-step duration.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Target model to be updated.
  * **data** ([*StorageData*](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData)) – Input container with horizon, units, and `delta_t`.
* **Returns:**
  The same model with storage sets/parameters attached.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- If `m.T` already exists it is preserved; otherwise it is created
  as `RangeSet(1, data.horizon)`.
- Parameters are prefixed with `storage_` for namespacing.

### NaivePyDESSEM.Storage.StorageVars.storage_add_variables(m: ConcreteModel) → ConcreteModel

Declare storage decision variables.

Adds state-of-charge and charge/discharge power variables. If a deficit
variable does not exist in the model, a non-negative `D[t]` is created.

### Variables

storage_E[s,t]
: Energy stored at the end of period `t` (MWh).

storage_ch[s,t]
: Charging power (MW) in period `t`.

storage_dis[s,t]
: Discharging power (MW) in period `t`.

D[t]
: Deficit (MW), created only if absent.

* **param m:**
  Target model (expects sets `m.SU` and `m.T`).
* **type m:**
  pyomo.environ.ConcreteModel
* **returns:**
  The same model with storage variables attached.
* **rtype:**
  pyomo.environ.ConcreteModel
