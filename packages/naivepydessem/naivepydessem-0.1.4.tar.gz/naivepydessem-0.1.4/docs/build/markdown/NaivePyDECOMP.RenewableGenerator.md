# NaivePyDECOMP.RenewableGenerator package

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

## NaivePyDECOMP.RenewableGenerator.RenewableConstraints module

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

## NaivePyDECOMP.RenewableGenerator.RenewableDataTypes module

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

## NaivePyDECOMP.RenewableGenerator.RenewableEquations module

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

## NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder module

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

### NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder.add_renewable_subproblem(m: ConcreteModel, data: [RenewableData](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData), stage: int) → ConcreteModel

Add renewable dispatch problem structure to a Pyomo model.

This routine attaches all renewable-related components to an existing
`ConcreteModel`. It initializes sets, parameters, variables, and the
renewable capacity constraints. Optionally, it also includes the balance
constraint and renewable objective.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which renewable problem components will be added.
  * **data** ([*RenewableData*](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData)) – Input data structure containing horizon, demand, units, and
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

## NaivePyDECOMP.RenewableGenerator.RenewableObjectives module

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

## NaivePyDECOMP.RenewableGenerator.RenewableVars module

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
