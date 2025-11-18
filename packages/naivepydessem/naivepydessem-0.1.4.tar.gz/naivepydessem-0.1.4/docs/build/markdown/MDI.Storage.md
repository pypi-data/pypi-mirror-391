# MDI.Storage package

## Module contents

### Storage Subpackage

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

The **Storage** subpackage implements all the symbolic, data, and structural
components required to model the operation and expansion of **energy storage systems** within
the broader **MDI (Modular Decision Infrastructure)** optimization framework.

#### Description

This subpackage defines the complete representation of storage units, including
their parameters, decision variables, constraints, and cost functions, suitable
for Mixed-Integer Linear Programming (MILP) and Mixed-Integer Nonlinear Programming (MINLP)
formulations using **Pyomo**.

#### Modules

StorageBuilder
: High-level routines for constructing complete storage models.

StorageDataTypes
: Data classes defining the structure and typing of storage unit data.

StorageEquations
: Symbolic expressions for cost and power balance aggregation.

StorageObjective
: Objective function for total storage cost minimization.

StorageVars
: Model variables, sets, and parameters declaration.

#### Structure Overview

The Storage subpackage provides modular integration of storage subsystems
into larger system models. It follows a builder pattern to maintain
clarity and extensibility.

Typical usage:

```pycon
>>> from MDI.Storage import StorageData, StorageUnit, build_storage
>>> data = StorageData(...)
>>> model = build_storage(data, include_objective=True)
```

#### Exports

This \_\_init_\_.py file re-exports all relevant symbols to simplify
namespace access.
Users may import either individual modules or the entire storage
subsystem directly via:

```pycon
>>> from MDI.Storage import *
```

### Notes

- All modules are compatible with **Pyomo 6.x**.
- Energy and power units follow the SI convention (MWh, MW).
- Cost parameters are assumed to be in consistent monetary units.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes, EELT7030/UFPR, 2023.

## Submodules

## MDI.Storage.StorageBuilder module

### Storage Builder Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the construction logic of the **energy storage subsystem**
within the MDI optimization framework. It provides high-level builder functions
that assemble the complete storage model — including sets, parameters,
variables, constraints, and the objective function — from structured input data.

#### Description

Two functions are defined in this module:

1. **\`build_storage(data, include_objective=True)\`**
   Creates and initializes a standalone Pyomo model for the storage subsystem,
   suitable for testing or modular integration.
2. **\`add_storage_problem(m, data, include_objective=False)\`**
   Extends an existing Pyomo model with the complete storage problem definition,
   including constraints and (optionally) the objective function.

The builder integrates all necessary symbolic components:
sets and parameters, decision variables, constraints on power,
energy balance, state-of-charge (SoC), and investment logic.

#### Mathematical Overview

The storage subsystem typically includes the following formulations:

**Energy balance**
[
E_{t} = E_{t-1} + eta_c P^{ch}_{t} -
rac{1}{eta_d} P^{dis}_{t}
]

**Power limits**
[
0 leq P^{ch}_{t}, P^{dis}_{t} leq P^{max} , x_{t}
]

**State of charge bounds**
[
E^{min} leq E_{t} leq E^{max}
]

**Investment linkage**
[
x_{t} = x_{t-1} + y_{t}
]

where:
- (E_t): energy stored at period *t*
- (P^{ch}_t, P^{dis}_t): charging/discharging power
- (eta_c, eta_d): charging/discharging efficiencies
- (x_t, y_t): operational and investment binary decisions

#### Functions

build_storage(data, include_objective=True)
: Creates and returns a complete Pyomo model for the storage subsystem.

add_storage_problem(m, data, include_objective=False)
: Adds the storage problem definition to an existing model.

### Notes

- The include_objective flag controls whether the subsystem-level
  objective (minimization of total storage cost) is included.
- The modular structure mirrors that of the generator subsystem
  to ensure composability within hybrid systems (hydrothermal or
  generation-storage models).
- All internal components (sets, variables, constraints) are
  imported from specialized modules to maintain separation of concerns.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,

> EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:**
  - `StorageDataTypes`
  - `StorageObjective`
  - `StorageVars`
  - `StorageConstraints`
- **External:**
  - `pyomo.environ` (ConcreteModel, Objective, minimize)

### MDI.Storage.StorageBuilder.add_storage_problem(m: ConcreteModel, data: [StorageData](#MDI.Storage.StorageDataTypes.StorageData), include_objective: bool = False) → ConcreteModel

Add the complete storage problem definition to a given model.

Extends an existing Pyomo model with the full symbolic formulation of
the energy storage subsystem, including all relevant constraints and,
optionally, the objective function.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which the storage subsystem will be appended.
  * **data** ([*StorageData*](#MDI.Storage.StorageDataTypes.StorageData)) – Structured data object defining all storage parameters and time horizon.
  * **include_objective** (*bool* *,* *optional*) – If True, includes the storage cost minimization objective. Default is False.
* **Returns:**
  The same model instance extended with storage sets, variables,
  constraints, and (optionally) the objective function.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

The following constraints are added to the model:
- Power limits (charging/discharging capacity)
- Energy balance (state-of-charge dynamics)
- Investment linkage (capacity expansion logic)
- SoC bounds (minimum and maximum limits)

### MDI.Storage.StorageBuilder.build_storage(data: [StorageData](#MDI.Storage.StorageDataTypes.StorageData), include_objective: bool = True) → ConcreteModel

Build a standalone Pyomo model for the storage subsystem.

This function creates a new ConcreteModel instance and populates it
with all the sets, parameters, variables, and constraints required to
represent an energy storage unit within the optimization framework.

* **Parameters:**
  * **data** ([*StorageData*](#MDI.Storage.StorageDataTypes.StorageData)) – Structured input data describing storage characteristics and parameters.
  * **include_objective** (*bool* *,* *optional*) – If True, includes the subsystem objective function. Default is True.
* **Returns:**
  A fully defined storage model ready for integration or standalone analysis.
* **Return type:**
  pyomo.environ.ConcreteModel

## MDI.Storage.StorageConstraints module

### Storage Constraints Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines all **physical and operational constraints** for the
energy storage subsystem of the MDI optimization model.
It ensures consistency between energy balance, power limits, state-of-charge
(SoC) boundaries, and investment linkage dynamics.

#### Description

Four main constraint groups are provided:

1. **Energy Balance Constraint**
   Ensures conservation of stored energy over time, accounting for
   charging/discharging power and round-trip efficiency.
2. **SoC Bounds Constraint**
   Enforces upper and lower limits on the energy stored as a function
   of installed capacity and operational state.
3. **Power Limits Constraint**
   Restricts the charging and discharging power to their respective
   maximum values.
4. **Investment Link Constraint**
   Links investment decisions with the operational availability of
   storage units across time.

#### Mathematical Formulation

**Energy balance**
[
E_{s,t} = E_{s,t-1} +
eta_c P^{ch}_{s,t} Delta t -

rac{P^{dis}_{s,t}}{eta_d} Delta t
]

**SoC bounds**
[
E^{min}_s x_{s,t} leq E_{s,t} leq E^{max}_s x_{s,t}
]

**Power limits**
[
0 leq P^{ch}_{s,t} leq P^{ch,max}_s x_{s,t}
quad   ext{and}quad
0 leq P^{dis}_{s,t} leq P^{dis,max}_s x_{s,t}
]

**Investment linkage**
[
x_{s,t} = x_{s,t-1} + y_{s,t}
]

where:
- (E_{s,t}) — state of charge (MWh)
- (P^{ch}_{s,t}), (P^{dis}_{s,t}) — charging/discharging power (MW)
- (eta_c, eta_d) — charging/discharging efficiencies
- (x_{s,t}) — operational existence of storage unit (s)
- (y_{s,t}) — binary investment decision
- (Delta t) — duration of time step (hours)

#### Functions

add_storage_energy_balance_constraint(m)
: Adds the intertemporal energy conservation constraint.

add_storage_soc_bounds_constraint(m)
: Adds the upper and lower bounds on the state of charge.

add_storage_power_limits_constraint(m)
: Adds the power limit constraints for charging and discharging.

add_storage_investment_link_constraint(m)
: Adds the investment linkage constraint ensuring logical consistency
  between existence and new builds.

### Notes

- The formulation assumes uniform time steps ((Delta t)) across the horizon.
- Charging and discharging are modeled as separate nonnegative variables.
- Constraints are fully compatible with multi-level (patamar) formulations.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,

> EELT7030/UFPR, 2023.

#### Module Dependencies

- **External:** `pyomo.environ.Constraint`

### MDI.Storage.StorageConstraints.add_storage_energy_balance_constraint(m)

Add the state-of-charge (SoC) energy balance constraint.

Defines the recursive relationship for the stored energy as a function
of previous state, charging/discharging flows, efficiencies, and
time-step duration.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing storage-related sets, variables,
  and parameters.
* **Returns:**
  The model with the energy balance constraint added.
* **Return type:**
  pyomo.environ.ConcreteModel

### MDI.Storage.StorageConstraints.add_storage_investment_link_constraint(m)

Add the investment linkage constraint for storage units.

Defines the relationship between construction decisions and
operational availability across time periods.
Ensures that the existence variable accumulates investments
over the planning horizon.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing the investment and operational variables.
* **Returns:**
  The model with investment linkage and initial-state constraints applied.
* **Return type:**
  pyomo.environ.ConcreteModel

### MDI.Storage.StorageConstraints.add_storage_power_limits_constraint(m)

Add charging and discharging power limit constraints.

Ensures that the charging and discharging power of each storage
unit does not exceed its respective rated capacity.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance with storage-related variables and parameters.
* **Returns:**
  The model with charging and discharging power limits enforced.
* **Return type:**
  pyomo.environ.ConcreteModel

### MDI.Storage.StorageConstraints.add_storage_soc_bounds_constraint(m)

Add upper and lower bounds on the state of charge (SoC).

Enforces that the stored energy remains within defined physical
limits as a function of the installed capacity and operational state.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing storage sets, variables, and parameters.
* **Returns:**
  The model with SoC boundary constraints applied.
* **Return type:**
  pyomo.environ.ConcreteModel

## MDI.Storage.StorageDataTypes module

### Storage Data Types Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the fundamental **data structures** that describe
the technical, economic, and operational attributes of **energy storage units**.
It serves as the foundation for building symbolic Pyomo models used in
optimization formulations for system operation and expansion.

#### Description

Two main dataclasses are defined:

1. **\`StorageUnit\`**
   Represents a single energy storage unit, including its operational
   parameters, efficiency characteristics, and economic coefficients.
2. **\`StorageData\`**
   Aggregates all input data required to formulate a storage optimization
   problem, including horizon definition, demand, level duration,
   and a collection of StorageUnit instances.

Both classes provide a lightweight, strongly typed data interface for
Python–Pyomo integration, facilitating modular problem definition
and reproducible experiment design.

#### Mathematical Interpretation

Each storage unit *s* is characterized by:

- ( E_{min}, E_{max}, E_{ini} ): Minimum, maximum, and initial energy levels.
- ( P^{ch}_{max}, P^{dis}_{max} ): Maximum charging and discharging powers.
- ( eta_c, eta_d ): Charging and discharging efficiencies.
- ( c_{op}, c_{inv} ): Operating and investment costs.
- ( state ): Binary indicator of existing capacity (0 or 1).

The StorageData structure encapsulates:

- Temporal horizon ( T )
- Demand curves by patamar and time
- Duration of load levels (in hours)
- Dictionary of StorageUnit definitions.

#### Usage

Instances of StorageData are typically created from preprocessed
input datasets and passed directly to model-construction functions such as:

```pycon
>>> from .StorageBuilder import build_storage
>>> model = build_storage(data=storage_data)
```

#### Classes

StorageUnit
: Defines the parameters of a single storage unit.

StorageData
: Encapsulates all data required for the formulation of the storage problem.

### Notes

- This data structure is **independent of Pyomo** and can be serialized
  or deserialized to JSON for reproducibility.
- Units follow the SI convention: MWh for energy, MW for power, and
  monetary units for costs.

### References

[1] CEPEL, *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C., *Introdução aos Sistemas de Energia Elétrica*,

> Lecture Notes, EELT7030/UFPR, 2023.

### *class* MDI.Storage.StorageDataTypes.StorageData(horizon: int, demand: Dict[str, List[float]], level_hours: Dict[str, float], delta_t: float, units: Dict[str, [StorageUnit](#MDI.Storage.StorageDataTypes.StorageUnit)])

Bases: `object`

Aggregates all data required for the storage optimization problem.

#### horizon

Number of discrete time periods in the planning horizon.

* **Type:**
  int

#### demand

Dictionary of demand profiles, organized by
patamar and time index.

* **Type:**
  Dict[str, List[float]]

#### level_hours

Duration (in hours) associated with each demand level.

* **Type:**
  Dict[str, float]

#### delta_t

Time step (years) used in the energy balance equations.

* **Type:**
  float

#### units

Dictionary of storage units indexed by their identifiers.

* **Type:**
  Dict[str, [StorageUnit](#MDI.Storage.StorageDataTypes.StorageUnit)]

#### delta_t *: float*

#### demand *: Dict[str, List[float]]*

#### horizon *: int*

#### level_hours *: Dict[str, float]*

#### units *: Dict[str, [StorageUnit](#MDI.Storage.StorageDataTypes.StorageUnit)]*

### *class* MDI.Storage.StorageDataTypes.StorageUnit(name: str, state: int, c_op: float, c_inv: float, Emin: float, Emax: float, Eini: float, Pch_max: float, Pdis_max: float, eta_c: float, eta_d: float)

Bases: `object`

Defines the parameters of a single storage unit.

#### name

Identifier of the storage unit.

* **Type:**
  str

#### state

Initial state (0 = not installed, 1 = existing).

* **Type:**
  int

#### c_op

Operational cost (per MWh of discharge or equivalent).

* **Type:**
  float

#### c_inv

Investment cost (annualized).

* **Type:**
  float

#### Emin

Minimum stored energy capacity (MWh).

* **Type:**
  float

#### Emax

Maximum stored energy capacity (MWh).

* **Type:**
  float

#### Eini

Initial stored energy at the beginning of the horizon (MWh).

* **Type:**
  float

#### Pch_max

Maximum charging power (MW).

* **Type:**
  float

#### Pdis_max

Maximum discharging power (MW).

* **Type:**
  float

#### eta_c

Charging efficiency (fraction between 0 and 1).

* **Type:**
  float

#### eta_d

Discharging efficiency (fraction between 0 and 1).

* **Type:**
  float

#### Eini *: float*

#### Emax *: float*

#### Emin *: float*

#### Pch_max *: float*

#### Pdis_max *: float*

#### c_inv *: float*

#### c_op *: float*

#### eta_c *: float*

#### eta_d *: float*

#### name *: str*

#### state *: int*

## MDI.Storage.StorageEquations module

### Storage Equations Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines **symbolic expressions** for energy storage subsystems,
used in the model composition phase to aggregate costs and power balances.
It provides reusable components for constructing higher-level formulations
(e.g., integrated generation–storage–transmission systems).

#### Description

Two main symbolic functions are defined:

1. **\`add_storage_cost_expression()\`**
   Builds the total operational and investment cost expression of all
   storage units and appends it to a global cost array.
2. **\`add_storage_balance_expression()\`**
   Builds the net energy balance expression (discharge minus charge)
   to represent the effective contribution of storage units to the system
   power balance in each time step and load level.

These expressions are not constraints by themselves, but **building blocks**
that can be embedded in multi-component optimization formulations.

#### Mathematical Formulation

1. **Cost Expression**
[
C_{storage} =
sum_{s in SU} sum_{t in T} sum_{p in P}
h_p , c^{op}_s , (P^{ch}_{s,t,p} + P^{dis}_{s,t,p})
+ sum_{s in SU} sum_{t in T}
c^{inv}_s , x_{s,t}
]

2. **Balance Expression**
[
B_{storage}(t,p) =
sum_{s in SU} eta_d , P^{dis}_{s,t,p}
-
rac{1}{eta_c} , P^{ch}_{s,t,p}
]

where:

Symbol | Description |
<br/>

```
|:--------|
```

:————|
| (h_p) | Duration of load level (p) (hours) |
| (c^{op}_s) | Operational cost per MWh |
| (c^{inv}_s) | Investment cost |
| (P^{ch}_{s,t,p}), (P^{dis}_{s,t,p}) | Charging/discharging power (MW) |
| (eta_c, eta_d) | Charging/discharging efficiencies |
| (x_{s,t}) | Binary existence variable |
| (SU, T, P) | Sets of storage units, time periods, and load levels |

#### Functions

add_storage_cost_expression(m, cost_array)
: Appends the total storage cost expression to a given list of cost terms.

add_storage_balance_expression(m, t, p, balance_array)
: Appends the net storage power balance expression (discharge – charge)
  to a given list of balance terms.

### Notes

- The functions **do not create Pyomo constraints**; they only define symbolic
  expressions that can be aggregated later.
- Each expression is appended to an externally provided list (e.g. cost_array),
  allowing modular model assembly.
- The caller must ensure that all required model attributes exist before invocation.

### References

[1] CEPEL, *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C., *Introdução aos Sistemas de Energia Elétrica*,

> Lecture Notes, EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:** None
- **External:** pyomo.environ, typing

### MDI.Storage.StorageEquations.add_storage_balance_expression(m: ConcreteModel, t: Any, p: Any, balance_array: List[Any]) → List[Any]

Add the net storage balance expression to the balance array.

The expression represents the net contribution of storage units
to the system power balance in each time period and load level,
considering both charge and discharge efficiencies.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing the relevant storage variables and parameters.
  * **t** (*Any*) – Time index for which the balance expression is computed.
  * **p** (*Any*) – Load level index corresponding to the current balance term.
  * **balance_array** (*list* *of* *Any*) – External list to which the resulting expression will be appended.
* **Returns:**
  The updated list of balance expressions including the storage term.
* **Return type:**
  list of Any

### MDI.Storage.StorageEquations.add_storage_capacity_expression(m: ConcreteModel, t: Any, p: Any, capacity_array: List[Any]) → List[Any]

Add the net storage capacity expression to the capacity array.

The expression represents the net contribution of storage units
to the system capacity in each time period and load level.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing the relevant storage variables and parameters.
  * **t** (*Any*) – Time index for which the capacity expression is computed.
  * **p** (*Any*) – Load level index corresponding to the current capacity term.
  * **capacity_array** (*list* *of* *Any*) – External list to which the resulting expression will be appended.
* **Returns:**
  The updated list of capacity expressions including the storage term.
* **Return type:**
  list of Any

### MDI.Storage.StorageEquations.add_storage_cost_expression(m: ConcreteModel, cost_array: List[Any]) → List[Any]

Add the total cost expression of all storage units to the cost array.

The expression combines operational and investment costs across all
time periods and load levels, weighted by load duration.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing sets, parameters, and variables
    of the storage subsystem.
  * **cost_array** (*list* *of* *Any*) – External list to which the resulting cost expression will be appended.
* **Returns:**
  The updated list of cost expressions including the storage cost term.
* **Return type:**
  list of Any

## MDI.Storage.StorageObjective module

### Storage Objective Function Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the **objective function** for the energy storage subsystem,
used in the Mixed-Integer Linear Programming (MILP) formulation of the
operation and expansion planning problem.

#### Description

The objective function represents the **total system cost** associated
with the operation and investment of storage units.
It aggregates two main cost components:

1. **Operational Cost (c_op)** — proportional to the total amount of energy moved
   (charging and discharging), weighted by the duration of each load level.
2. **Investment Cost (c_inv)** — proportional to the existence of installed
   capacity throughout the planning horizon.

Both cost components are expressed as additive terms in a global minimization
objective, consistent with standard formulations in expansion planning models.

#### Mathematical Formulation

The objective function is defined as:

[
min ; Z =
sum_{s in SU} sum_{t in T} sum_{p in P}

> h_p , c^{op}_s , (P^{ch}_{s,t,p} + P^{dis}_{s,t,p})
+ sum_{s in SU} sum_{t in T}
  c^{inv}_s , x_{s,t}

]

where:

Symbol | Description |
<br/>

```
|:--------|
```

:————|
| (h_p) | Duration of load level (p) (hours) |
| (c^{op}_s) | Operational cost of unit (s) (per MWh) |
| (c^{inv}_s) | Investment cost of unit (s) |
| (P^{ch}_{s,t,p}) | Charging power (MW) |
| (P^{dis}_{s,t,p}) | Discharging power (MW) |
| (x_{s,t}) | Binary existence variable |
| (SU, T, P) | Sets of storage units, time steps, and load levels |

#### Functions

set_objective_storage(m)
: Adds the objective function to the Pyomo model, minimizing total storage costs.

### Notes

- The function assumes that all sets, parameters, and variables
  have already been defined (typically via storage_add_sets_and_params
  and storage_add_variables).
- Units are consistent with the rest of the framework:
  MW for power, MWh for energy, and monetary units for costs.
- The resulting objective is fully compatible with mixed-integer solvers
  such as CBC, GLPK, or commercial solvers (Gurobi, CPLEX).

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes, UFPR, 2023.

### MDI.Storage.StorageObjective.set_objective_storage(m: ConcreteModel) → ConcreteModel

Define the total cost minimization objective for the storage subsystem.

This function constructs a Pyomo Objective expression that
aggregates operational and investment costs for all storage units
across time steps and load levels.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing all sets, parameters, and variables
  related to the storage subsystem.
* **Returns:**
  The same model instance, now with an attached objective function
  named OBJ.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> # (Assume sets and parameters already defined)
>>> set_objective_storage(m)
>>> print(m.OBJ.sense)
minimize
```

## MDI.Storage.StorageVars module

### Storage Variables and Parameters Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines all **sets, parameters, and decision variables**
related to the **energy storage subsystem** of the MDI optimization framework.
It provides the symbolic foundation required by the storage constraints
and objective function.

#### Description

Two main functions are implemented:

1. **\`storage_add_sets_and_params(m, data)\`**
   Initializes all Pyomo sets and parameters related to the storage units,
   including physical limits, efficiencies, operational costs, and time structure.
2. **\`storage_add_variables(m)\`**
   Declares the decision variables for charging, discharging,
   energy state, and investment decisions.

The storage formulation supports a **multi-patamar (load level)** representation
and can be embedded seamlessly within larger optimization systems
that couple generation, transmission, and storage components.

#### Mathematical Overview

**Continuous variables**
[
egin{align}
E_{s,t,p} &ge 0 quad &        ext{(stored energy)} P^{ch}_{s,t,p} &ge 0 quad &   ext{(charging power)} P^{dis}_{s,t,p} &ge 0 quad &  ext{(discharging power)}
end{align}
]

**Binary variables**
[
egin{align}
x_{s,t} &in {0,1} quad &    ext{(existence of unit)} y_{s,t} &in {0,1} quad &    ext{(investment decision)}
end{align}
]

Parameters are defined for:
- Energy bounds (E^{min}, E^{max}, E^{ini})
- Power limits (P^{ch,max}, P^{dis,max})
- Efficiencies (eta_c, eta_d)
- Costs (c_{op}, c_{inv})
- State (x_{0})
- Duration of time step (Delta t)

#### Functions

storage_add_sets_and_params(m, data)
: Define the sets and parameters related to the storage subsystem.

storage_add_variables(m)
: Define the decision variables associated with energy, power, and investment.

### Notes

- The function automatically initializes missing time and patamar sets (m.T, m.P)
  when they are not yet defined in the parent model.
- The formulation is fully compatible with a mixed-integer linear structure (MILP).
- The energy is represented in MWh, power in MW, and costs in monetary units.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,

> EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:** `StorageDataTypes`
- **External:** `pyomo.environ` (RangeSet, Set, Param, Var, NonNegativeReals, Binary, ConcreteModel)

### MDI.Storage.StorageVars.storage_add_sets_and_params(m: ConcreteModel, data: [StorageData](#MDI.Storage.StorageDataTypes.StorageData)) → ConcreteModel

Define the sets and parameters for the storage subsystem.

Initializes all symbolic structures needed for the storage model,
including time horizon, load levels, physical parameters, and
investment-related costs.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance to which sets and parameters will be added.
  * **data** ([*StorageData*](#MDI.Storage.StorageDataTypes.StorageData)) – Structured data object containing the full specification of
    the storage units and demand profiles.
* **Returns:**
  The model instance with all sets and parameters defined.
* **Return type:**
  pyomo.environ.ConcreteModel

### MDI.Storage.StorageVars.storage_add_variables(m: ConcreteModel) → ConcreteModel

Define the decision variables for the storage subsystem.

Includes continuous and binary variables representing:
- Energy stored
- Charging/discharging power
- Construction and operational existence decisions

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance where variables will be defined.
* **Returns:**
  The model instance with all storage-related variables declared.
* **Return type:**
  pyomo.environ.ConcreteModel
