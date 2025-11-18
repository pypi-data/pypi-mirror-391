# NaivePyDESSEM.RenewableGenerator package

## Module contents

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Renewable Generation Modeling (RenewableGenerator)

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

The **RenewableGenerator** package provides a modular framework for modeling
renewable energy sources (e.g., wind and solar) in Pyomo-based dispatch and
unit commitment models. It includes standardized data types, sets, parameters,
variables, constraints, objectives, and builder functions.

### Submodules

RenewableDataTypes
: Dataclasses defining renewable units (e.g., expected generation profiles).

RenewableVars
: Initialization routines for Pyomo sets, parameters, and variables.

RenewableConstraints
: Constraint builders enforcing availability limits and system balance.

RenewableObjectives
: Objective function definitions for renewable-only systems.

RenewableBuilder
: High-level routines to assemble complete renewable generation models.

### Notes

- The renewable availability profiles (**gbar**) are treated as exogenous,
  typically coming from forecasts.
- The package is interoperable with the Hydro, Thermal, and Storage packages,
  enabling hybrid model construction.
- Consistent naming and structure ensure clarity and maintainability across
  subsystems.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## Submodules

## NaivePyDESSEM.RenewableGenerator.RenewableConstraints module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Constraints

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module defines the operational constraints for renewable generation
within Pyomo-based unit commitment and dispatch models. It enforces both
the per-unit generation availability limits and the system-wide energy
balance when only renewable units and deficit are considered.

### Functions

add_renewable_capacity_constraints(m)
: Enforce that renewable generation for each unit and period does not
  exceed the exogenous availability profile `gbar`.

add_renewable_balance_constraint(m)
: Enforce the energy balance by equating total renewable generation
  plus deficit to the system demand at each time period.

### Notes

- The capacity constraints guarantee that `renewable_gen[r,t]` is bounded
  above by `renewable_gbar[r,t]`, which typically comes from forecasts.
- The balance constraint is suitable for renewable-only models. In hybrid
  models (thermal + hydro + renewables), a combined balance formulation
  must be applied instead.
- The deficit variable `D[t]` provides feasibility when renewable
  generation cannot meet demand.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.RenewableGenerator.RenewableConstraints.add_renewable_balance_constraint(m)

Add the system-wide energy balance constraint for renewable-only models.

Enforces, for each period `t`, that the total renewable generation
plus the deficit variable equals the system demand:

> sum_r renewable_gen[r,t] + D[t] == d[t]
* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model containing:
  - Sets: `m.RU` (renewable units), `m.T` (time periods)
  - Variables: `m.renewable_gen[r,t]` (MW), `m.D[t]` (MW, deficit)
  - Parameters: `m.d[t]` (MW, demand)
* **Returns:**
  The same model with constraint block
  `m.renewable_balance_constraint`.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- This balance assumes a system composed solely of renewable units
  and deficit. For hybrid systems (hydro, thermal, renewables),
  a combined balance constraint should be implemented.
- The deficit variable `m.D[t]` allows feasibility in case
  renewable generation is insufficient to meet demand.

### NaivePyDESSEM.RenewableGenerator.RenewableConstraints.add_renewable_capacity_constraints(m)

Add renewable capacity (availability) constraints.

For each renewable unit `r` and time period `t`, the dispatched
renewable generation cannot exceed its available potential
(exogenous profile `gbar`):

> renewable_gen[r,t] <= renewable_gbar[r,t]
* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model containing:
  - Sets: `m.RU` (renewable units), `m.T` (time periods)
  - Variables: `m.renewable_gen[r,t]` (MW)
  - Parameters: `m.renewable_gbar[r,t]` (MW, availability profile)
* **Returns:**
  The same model with constraint block
  `m.renewable_cap_constraint`.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- Ensures that renewable generation respects exogenous availability.
- The availability parameter `m.renewable_gbar` is typically
  initialized from forecast profiles or scenario data.

## NaivePyDESSEM.RenewableGenerator.RenewableDataTypes module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Generation Data Structures

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module defines lightweight data classes for representing renewable
generation units (e.g., wind and solar) and their aggregated system-level
data. These structures serve as standardized inputs for optimization
models of unit commitment and dispatch in Pyomo.

### Classes

RenewableUnit
: Encapsulates the characteristics of a single renewable unit, including
  identifier and time-varying availability profile.

RenewableData
: Aggregates renewable units with system-wide parameters such as horizon,
  demand profile, and deficit penalty cost.

### Notes

- The exogenous availability profiles are represented as deterministic
  time series (MW) and aligned with the planning horizon.
- The classes are designed for seamless integration into Pyomo-based
  optimization formulations, ensuring consistency with similar structures
  for thermal and hydro subsystems.
- Extend these classes as needed to incorporate stochastic scenarios or
  uncertainty modeling for renewable availability.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### *class* NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData(horizon: int, demand: Dict[int, float], units: Dict[str, [RenewableUnit](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit)], Cdef: float = 1000.0)

Bases: `object`

System-wide data structure for renewable generation modeling.

* **Parameters:**
  * **horizon** (*int*) – Number of periods in the planning horizon.
  * **demand** (*Dict* *[**int* *,* *float* *]*) – Mapping of each period `t` (1-based) to system demand (MW).
  * **units** (*Dict* *[**str* *,* [*RenewableUnit*](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit) *]*) – Dictionary mapping unit identifiers to their respective
    [`RenewableUnit`](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit) objects.
  * **Cdef** (*float* *,* *optional*) – Penalty cost for unmet demand (R$/MWh), default is `1000.0`.

### Notes

- `units` can include heterogeneous renewable technologies such as
  wind turbines, photovoltaic plants, or run-of-river hydro, provided
  they are represented by [`RenewableUnit`](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit).
- `Cdef` defines the cost of deficit used in the optimization
  objective when renewables are integrated into dispatch problems.
- This class is typically consumed by Pyomo-based optimization models
  for renewable-aware unit commitment or economic dispatch.

#### Cdef *: float* *= 1000.0*

#### demand *: Dict[int, float]*

#### horizon *: int*

#### units *: Dict[str, [RenewableUnit](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit)]*

### *class* NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit(name: str, gbar: List[float])

Bases: `object`

Data container for a renewable generating unit (e.g., wind or solar).

* **Parameters:**
  * **name** (*str*) – Unique identifier for the renewable unit (e.g., `'PV1'`, `'WTG3'`).
  * **gbar** (*List* *[**float* *]*) – Time series of expected available generation (MW) for each
    planning period. Typically derived from forecasts or
    historical profiles.

### Notes

- The list `gbar` is assumed to have length equal to the system
  planning horizon. Access is usually aligned as `gbar[t-1]` for
  period `t` (1-based index).
- Variability and uncertainty of renewables are represented through
  this exogenous availability profile rather than decision variables.

#### gbar *: List[float]*

#### name *: str*

## NaivePyDESSEM.RenewableGenerator.RenewableEquations module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Renewable Model Expression Utilities for Pyomo Optimization

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides helper functions to construct symbolic expressions
related to renewable energy generation in Pyomo-based optimization models.
The expressions generated here can be used to assemble power balance
constraints and, when applicable, cost functions that include renewable
generation impacts such as curtailment penalties or contractual delivery.

The functions are designed to operate modularly, enabling integration
into hybrid models that combine thermal, hydro, storage, and renewable
sources in a unified dispatch or expansion framework.

Each function verifies the availability of required model components
before contributing expressions, allowing for flexible integration
without error propagation in partially defined models.

### Intended Use

- To support the incremental construction of power balance constraints
  by including generation terms from renewable units.
- To optionally incorporate renewable-related cost components, including
  penalties or market mechanisms.

### Examples

```pycon
>>> cost_terms = []
>>> add_renewable_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)
```

```pycon
>>> balance_terms = []
>>> add_renewable_balance_expression(model, t=5, balance_array=balance_terms)
>>> model.PowerBalance.add(balance_terms[0])
```

### Notes

- This module assumes the existence of model components such as:
  RU (set of renewable units), T (time set), and renewable_gen (generation variable).
- Cost expressions are optional and can be enabled based on use case (e.g., curtailment penalties).
- The symbolic expressions returned can be used with ConstraintList or Constraint(model.T).

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. (2023). Introdução aos Sistemas de Energia Elétrica,  Lecture Notes EELT7030/UFPR.

### NaivePyDESSEM.RenewableGenerator.RenewableEquations.add_renewable_balance_expression(m: ConcreteModel, t: Any, balance_array: List[Any]) → List[Any]

Append renewable generation terms at time t to the power balance expression list.

This function constructs a symbolic expression representing the total power
injected by renewable sources at a given time step t, and appends it to
the power balance equation. The function is compatible with modular power
balance construction in hybrid energy system models.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing renewable generation variables.
  * **t** (*int*) – Time index for which the renewable generation is evaluated.
  * **balance_array** (*list* *of* *expressions*) – List of symbolic expressions contributing to the power balance equation.
* **Returns:**
  The updated list including the total renewable generation at time t.
* **Return type:**
  list of expressions

### Notes

- The model is expected to contain the following components:
  ‘RU’ (renewable unit set), ‘T’ (time set), and ‘renewable_gen’ (generation variable).
- This function is designed for use within a larger balance constraint rule
  such as Constraint(model.T, rule=…) or within a ConstraintList.

### NaivePyDESSEM.RenewableGenerator.RenewableEquations.add_renewable_cost_expression(m: ConcreteModel, cost_array: List[Any]) → List[Any]

Append renewable generation cost terms to the total cost expression list.

This function is a placeholder or extension point for incorporating
renewable energy cost terms into the objective function. While many
renewable sources (e.g., wind, solar) have negligible marginal costs,
this function allows the inclusion of opportunity costs, curtailment
penalties, or tariffs if applicable.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing renewable variables and parameters.
  * **cost_array** (*list* *of* *expressions*) – List of symbolic expressions that contribute to the total cost.
* **Returns:**
  The input list, optionally extended with renewable cost expressions.
* **Return type:**
  list of expressions

### Notes

- If no cost expression is required for renewables, the function simply
  returns the list unchanged.
- This function can be expanded to include curtailment penalties or
  contracted delivery costs based on renewable_gen variables.

## NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Model Builder

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides high-level builders for renewable-only optimization
models in Pyomo. It assembles the complete model structure by combining
sets, parameters, variables, constraints, and optionally the objective
function for renewable generation systems.

### Functions

build_renewables(data, include_objective=True)
: Create a new `ConcreteModel` pre-populated with renewable unit
  commitment and dispatch components.

add_renewable_problem(m, data, include_objective=False)
: Add renewable-related sets, parameters, variables, constraints,
  and optionally the objective function to an existing Pyomo model.

### Notes

- Suitable for renewable-only systems (e.g., wind and solar). For hybrid
  hydrothermal-renewable systems, the balance constraint and objective
  must be adapted accordingly.
- The availability profiles are deterministic and exogenous, provided
  by the `RenewableData` structure.
- The optional objective minimizes deficit costs and enforces demand
  balance when `include_objective=True`.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder.add_renewable_problem(m: ConcreteModel, data: [RenewableData](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData), include_objective: bool = False) → ConcreteModel

Add renewable dispatch problem structure to a Pyomo model.

This routine attaches all renewable-related components to an existing
`ConcreteModel`. It initializes sets, parameters, variables, and the
renewable capacity constraints. Optionally, it also includes the balance
constraint and renewable objective.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which renewable problem components will be added.
  * **data** ([*RenewableData*](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData)) – Input data structure containing horizon, demand, units, and
    availability profiles.
  * **include_objective** (*bool* *,* *optional*) – If `True`, add the balance constraint and renewable objective
    function (default is `False`).
* **Returns:**
  The updated model with renewable sets, parameters, variables,
  constraints, and optionally the objective.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- Constraints added:
  : * Renewable generation capacity limits
    * Renewable balance (if `include_objective=True`)
- The objective minimizes deficit cost and optionally penalizes
  renewable spill (depending on implementation of
  `set_objective_renewable()`).
- This builder is intended for renewable-only systems. For mixed
  hydro/thermal/renewable dispatch, a combined balance formulation
  is required.

### NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder.build_renewables(data: [RenewableData](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData), include_objective: bool = True) → ConcreteModel

Construct a complete Pyomo model for renewable-only dispatch.

This high-level builder creates a new `ConcreteModel` instance and
populates it with sets, parameters, variables, constraints, and optionally
the objective for renewable generation systems. It calls
[`add_renewable_problem()`](#NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder.add_renewable_problem) internally.

* **Parameters:**
  * **data** ([*RenewableData*](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData)) – Input data structure with horizon, demand profile, deficit penalty,
    and renewable units with their availability profiles.
  * **include_objective** (*bool* *,* *optional*) – If `True`, add the renewable balance constraint and objective
    function (default is `True`).
* **Returns:**
  A new Pyomo model fully configured for renewable-only dispatch.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- The model contains:
  : * Sets: time periods, renewable units
    * Parameters: demand, availability (`gbar`), deficit penalty
    * Variables: renewable generation, deficit
    * Constraints: capacity limits, and optionally balance
    * Objective: deficit-penalizing minimization (if enabled)
- For integration with hydro/thermal systems, use combined builders.

## NaivePyDESSEM.RenewableGenerator.RenewableObjectives module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Objective Function

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Defines the objective function for renewable-only dispatch models in Pyomo.
The objective minimizes the total cost of unmet demand (deficit) over the
planning horizon. It uses the deficit penalty parameter `Cdef` to quantify
the economic impact of unserved energy.

### Functions

set_objective_renewable(m)
: Attach a minimization objective to the model, penalizing unmet demand.

### Notes

- This objective is designed for renewable-only systems, where generation
  is fully determined by availability and no explicit fuel costs exist.
- The deficit variable `D[t]` ensures feasibility when renewable
  generation cannot meet the demand `d[t]`.
- The penalty coefficient `Cdef` should be chosen high enough to
  discourage deficits under normal conditions.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.RenewableGenerator.RenewableObjectives.set_objective_renewable(m)

Define the objective function for renewable-only dispatch models.

The objective minimizes the total penalty associated with unmet demand
(deficit) across the planning horizon. This is expressed as:

> minimize  sum_t Cdef \* D[t]

where:
- `D[t]` is the deficit variable (MW) at time period `t`.
- `Cdef` is the penalty coefficient for unserved energy (e.g., $/MWh).

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model with:
  - Set: `m.T` (time periods)
  - Variable: `m.D[t]` (deficit at time `t`)
  - Parameter: `m.Cdef` (deficit penalty cost)
* **Returns:**
  The same model with objective function `m.OBJ` attached, set for
  minimization.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- This formulation is intended for renewable-only systems, where
  generation costs are absent and the only economic penalty comes
  from unmet demand.
- Ensure that the penalty `Cdef` is set to a sufficiently high value
  so that the optimizer prioritizes meeting demand whenever possible.
- The objective does not account for renewable curtailment or spill
  penalties. If such penalties are desired, they must be added explicitly.

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> m.T = [1, 2, 3]
>>> m.D = {t: 0 for t in m.T}  # deficit variables (mocked here)
>>> m.Cdef = 1000.0
>>> _ = set_objective_renewable(m)
>>> m.OBJ.pprint()  
```

## NaivePyDESSEM.RenewableGenerator.RenewableVars module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Sets, Parameters, and Variables

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides initialization routines for renewable generation
within unit-commitment and dispatch models in Pyomo. It defines the sets,
parameters, and decision variables required to incorporate renewable
units (e.g., wind or solar) into short-term planning formulations.

### Functions

renewable_add_sets_and_params(m, data)
: Initialize sets and parameters for renewable units, including the
  renewable unit set and availability profiles `gbar`.

renewable_add_variables(m)
: Declare renewable generation decision variables and, if not present,
  the deficit variable.

### Notes

- Availability profiles `gbar` are assumed to be exogenous, deterministic,
  and aligned with the planning horizon.
- The module is designed for integration with hydro and thermal
  subsystems, ensuring that common components such as time set `m.T`,
  demand `m.d`, and deficit penalty `m.Cdef` are not redefined if
  already present.
- Renewable generation is always bounded above by its availability; the
  actual capacity constraint should be added separately.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.RenewableGenerator.RenewableVars.renewable_add_sets_and_params(m: ConcreteModel, data: [RenewableData](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData)) → ConcreteModel

Initialize sets and parameters for renewable units in a Pyomo model.

Adds the renewable unit set, the renewable availability parameter
`renewable_gbar[r,t]`, and ensures that the time set `m.T`, demand
`m.d`, and deficit penalty `m.Cdef` exist. If those components are
already present in the model, they are not overwritten.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which renewable sets and parameters will be added.
  * **data** ([*RenewableData*](#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData)) – Input data structure containing the planning horizon, demand profile,
    deficit penalty, and renewable units with their availability series.
* **Returns:**
  The same model with renewable sets and parameters attached.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- The set `m.RU` indexes renewable units.
- The parameter `m.renewable_gbar[r,t]` stores the available generation
  (MW) of unit `r` at period `t`.
- The list `gbar` in each `RenewableUnit` is assumed to be 0-based,
  so initialization uses `t-1` when accessing it.
- If the model already contains `m.T`, `m.d`, or `m.Cdef`, they are
  left unchanged to allow integration with thermal/hydro subsystems.

### NaivePyDESSEM.RenewableGenerator.RenewableVars.renewable_add_variables(m: ConcreteModel) → ConcreteModel

Declare renewable generation and deficit decision variables.

Adds the continuous non-negative variable `m.renewable_gen[r,t]` for
renewable generation and, if not already present, the deficit variable
`m.D[t]`.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which renewable variables will be added.
* **Returns:**
  The same model with renewable generation and deficit variables.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- `m.renewable_gen[r,t]` represents the actual dispatched renewable
  generation (MW) for unit `r` at time `t`.
- `m.D[t]` represents unmet demand (MW) at time `t`. It is created
  only if not already defined in the model, ensuring compatibility with
  other subsystems (thermal, hydro, batteries).
- Both variables are continuous and non-negative.
