# MDI.Generator package

## Module contents

### Generator Subpackage

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

The **Generator** subpackage provides a complete and modular implementation of
**dispatchable generation units** within the MDI (Modular Decision Infrastructure)
framework, forming the core component of the operation and expansion
planning model.

#### Description

This subpackage defines all necessary components to represent thermal and
dispatchable generation systems in **Pyomo**, including data typing, variables,
constraints, and objectives. It supports integration with storage and other
energy technologies under a unified optimization environment.

#### Modules

GeneratorBuilder
: High-level routines for constructing the generator subsystem model.

GeneratorDataTypes
: Data classes describing generator unit parameters and data structures.

GeneratorEquations
: Symbolic expressions for generator cost and balance aggregation.

GeneratorObjectives
: Objective function for total generation cost minimization.

GeneratorVars
: Sets, parameters, and decision variables declaration.

#### Structure Overview

The Generator subpackage follows a modular and pedagogical architecture,
allowing incremental assembly and analysis of generation models.

### Example

```pycon
>>> from MDI.Generator import GeneratorData, GeneratorUnit, build_generators
>>> data = GeneratorData(...)
>>> model = build_generators(data, include_objective=True)
```

#### Exports

This \_\_init_\_.py file re-exports all relevant symbols to simplify
namespace imports.
Modules can be accessed individually or as a unified subsystem:

```pycon
>>> from MDI.Generator import *
```

### Notes

- Each component of the subpackage is fully compatible with **Pyomo 6.x**.
- Generation costs are modeled through both operational and investment terms.
- Units follow the SI convention (MW for power, monetary units for cost).
- The implementation is pedagogically aligned with the MDI methodology
  and CEPEL’s DESSEM conceptual framework.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes, EELT7030/UFPR, 2023.

## Submodules

## MDI.Generator.GeneratorBuilder module

### Generator Builder Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the routines responsible for constructing the generator
submodel within the MDI (Modular Didactic Infrastructure) framework. It serves
as the primary entry point for creating the Pyomo-based representation of
dispatchable generation units, their parameters, variables, constraints, and
optional objective terms.

#### Description

The generator builder integrates modular components defined in the companion
submodules:

- `GeneratorVars`: Declares decision variables for generator operation and investment.
- `GeneratorDataTypes`: Defines dataclass-based structures for handling generator input data.
- `GeneratorConstraints`: Introduces operational, investment, and capacity constraints.
- `GeneratorObjectives`: Builds the cost-related components of the objective function.

These functions enable flexible inclusion of generator units within the full
system model or as a standalone expansion subproblem. Each submodule follows
Pyomo’s modeling conventions and supports compositional assembly within the
broader MDI framework.

#### Functions

build_generators(generator_data, include_objective=True)
: Creates a Pyomo `ConcreteModel` containing the generator submodel,
  including variables, constraints, and optionally the objective function.

add_generator_problem(m, data, include_objective=False)
: Adds generator-related sets, parameters, variables, and constraints
  to an existing Pyomo model instance.

### Notes

- The generator submodel can be built independently or as part of a larger
  integrated energy planning problem.
- Setting `include_objective=False` allows the model to be embedded in
  hierarchical or multi-objective formulations.
- This module relies on modular imports and clear dependency separation
  between data definition, variable creation, and constraint formulation.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### MDI.Generator.GeneratorBuilder.add_generator_problem(m: ConcreteModel, data: [GeneratorData](#MDI.Generator.GeneratorDataTypes.GeneratorData), include_objective: bool = False) → ConcreteModel

Add generator components (sets, parameters, variables, and constraints)
to an existing Pyomo model.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Existing Pyomo model instance to which generator components will be added.
  * **data** ([*GeneratorData*](#MDI.Generator.GeneratorDataTypes.GeneratorData)) – Dataclass or structured object containing generator-related data, such as
    power limits, costs, and investment parameters.
  * **include_objective** (*bool* *,* *optional*) – Whether to append the generator objective term to the model.
    Defaults to `False`.
* **Returns:**
  * *pyomo.environ.ConcreteModel* – The input model, extended with generator-related components.
  * *Workflow*
  *  *——–*
  * 1. Define generator sets and parameters via `generator_add_sets_and_params()`.
  * 1. Declare operational and investment variables using `generator_add_variables()`.
  * *3. Add operational constraints for generation limits and investment linkage.*
  * *4. Optionally include cost terms in the model’s objective function.*

### Notes

- This function can be safely called multiple times for different generator
  groups or technologies.
- The objective inclusion flag provides flexibility for hierarchical
  optimization or decomposition-based formulations.

### MDI.Generator.GeneratorBuilder.build_generators(generator_data: dict, include_objective: bool = True) → ConcreteModel

Construct a standalone generator submodel as a Pyomo `ConcreteModel`.

This function acts as a wrapper that initializes a new model instance,
populates it with generator sets, parameters, variables, and constraints,
and optionally includes the cost-minimizing objective function.

* **Parameters:**
  * **generator_data** (*dict*) – Dictionary or dataclass containing all generator configuration data,
    including installed capacities, operational limits, and cost coefficients.
  * **include_objective** (*bool* *,* *optional*) – Whether to include the generator’s cost function in the model objective.
    Defaults to `True`.
* **Returns:**
  A fully constructed generator submodel ready for optimization.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- Internally, this function delegates to `add_generator_problem()`.
- When used in integrated expansion models, the objective term may be
  disabled to avoid duplication at the system level.

## MDI.Generator.GeneratorConstraints module

### Generator Constraints Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the operational and investment constraints associated with
dispatchable generation units in the MDI framework. These constraints ensure that
generation power levels remain within admissible technical limits and that
investment decisions are properly linked across the planning horizon.

#### Description

The generator constraints implemented here enforce:

1. **Operational bounds**:
   Ensures that each unit’s generation output lies between its minimum and maximum
   power levels whenever it is operational.
2. **Investment linkage**:
   Establishes a temporal dependency between the binary investment decision variables
   (gen_y) and the operational availability variables (gen_x), guaranteeing
   consistent activation of units across consecutive time periods.

These constraints are intended to be modular and easily extensible for more
sophisticated generation formulations (e.g., ramping limits, minimum up/down
times, or emission constraints).

#### Functions

add_generator_power_limits_constraint(m)
: Adds upper and lower power output constraints for each generator and time step.

add_generator_investment_link_constraint(m)
: Adds the logical linkage between investment and operational state variables
  across the planning horizon.

### Notes

- Both constraints assume that the model already defines sets `GU`, `T`, and `P`,
  as well as parameters `gen_Pmin` and `gen_Pmax`.
- The investment linkage formulation assumes chronological time indexing.
- These formulations align with the expansion-phase component of the MDI methodology.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:** `MDI.GeneratorVars`, `MDI.GeneratorDataTypes`
- **External:** `pyomo.environ (Constraint, ConcreteModel)`

### MDI.Generator.GeneratorConstraints.add_generator_investment_link_constraint(m: ConcreteModel) → ConcreteModel

Add investment linkage constraints between generator states and investment decisions.

These constraints ensure temporal consistency between investment decisions
(gen_y) and operational availability (gen_x) throughout the planning horizon.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model containing generator-related variables and sets.
* **Returns:**
  * *pyomo.environ.ConcreteModel* – The same model instance, extended with investment linkage constraints.
  * *Workflow*
  *  *——–*
  * *1. Initialization constraint* –
    - At the first period, equate `gen_y[g, 1]` with the initial state `gen_state[g]`.
  * *2. Temporal linkage constraint* –
    - Enforce that `x[g, t] = x[g, t-1] + y[g, t]` for `t > 1`,
      ensuring capacity accumulation through time.

### Notes

- The binary variable `gen_y` represents new investments.
- The binary variable `gen_x` denotes whether the generator is operational.
- `gen_state` specifies the pre-existing operational state at the start of the horizon.
- Skips constraint definition if any required model components are missing.

### MDI.Generator.GeneratorConstraints.add_generator_power_limits_constraint(m: ConcreteModel) → ConcreteModel

Add operational power limits for dispatchable generation units.

This constraint ensures that the generation output of each unit remains within
its technical minimum and maximum power levels whenever the unit is operational.
The constraint is applied over all generators, time periods, and demand levels.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model containing generator sets, parameters, and decision variables.
* **Returns:**
  The same model instance, extended with upper and lower generation limits.
* **Return type:**
  pyomo.environ.ConcreteModel
* **Raises:**
  * **AttributeError** – If any required model attribute is missing (e.g., `gen_P`, `gen_Pmax`).
  * **Workflow** – 
  * **--------** – 
  * **1. For each generator****,** **period****,** **and demand level****,** **define:** – 
    - Upper limit: $P_{g,t,p} \leq P^{max}_g \cdot x_{g,t}$
          - Lower limit: $P_{g,t,p} \geq P^{min}_g \cdot x_{g,t}$
  * **2. Skip constraint creation if the required attributes are not defined.** – 

### Notes

- `gen_x[g, t]` represents whether the generator is active at time `t`.
- This constraint does not include ramping or minimum up/down time conditions,
  which should be defined in a separate submodule.

## MDI.Generator.GeneratorDataTypes module

### Generator Data Types Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the fundamental data structures used to represent
generator-related parameters within the MDI framework. It provides
strongly typed and structured interfaces for input parsing, parameter
validation, and model population using the Pyomo environment.

#### Description

The dataclasses defined here encapsulate both unit-level and
system-level information required to formulate the generation expansion
and dispatch problem. They are designed for clarity, immutability,
and direct compatibility with YAML and JSON data sources.

- **GeneratorUnit** represents the technical and economic attributes
  of a single dispatchable generating unit.
- **GeneratorData** aggregates all generator units, demand data,
  time discretization, and system-level configuration parameters
  required to construct the generator submodel.

#### Classes

GeneratorUnit
: Defines a single generation unit, including operational state,
  investment cost, and technical limits.

GeneratorData
: Defines a complete data structure for the generator subsystem,
  including time horizon, demand, load levels, and the collection of
  generation units.

### Notes

- These dataclasses are typically populated by the YAMLLoader module
  before model construction.
- Attribute names are intentionally consistent with the Pyomo
  model variable and parameter nomenclature.
- The design supports type checking and explicit serialization
  to facilitate reproducibility in energy system research.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:** None (independent data layer)
- **External:** `dataclasses`, `typing`

### *class* MDI.Generator.GeneratorDataTypes.GeneratorData(horizon: int, demand: Dict[str, List[float]], level_hours: Dict[str, float], units: Dict[str, [GeneratorUnit](#MDI.Generator.GeneratorDataTypes.GeneratorUnit)])

Bases: `object`

Aggregated dataset for the generator subsystem.

Encapsulates all time-related and unit-level data required to
build the generator component of the MDI model, including
demand series, temporal discretization, and technology set.

* **Parameters:**
  * **horizon** (*int*) – Number of time periods in the planning horizon.
  * **demand** (*dict* *of*  *{str: list* *of* *float}*) – Nested dictionary containing demand data per load level and time period.
    Example structure:
    `{"Ponta": [500, 550, 600], "Fora": [300, 320, 350]}`
  * **level_hours** (*dict* *of*  *{str: float}*) – Mapping between demand levels (e.g., ‘Ponta’, ‘Fora’) and their
    respective duration in hours.
  * **units** (*dict* *of*  *{str: GeneratorUnit}*) – Dictionary mapping unit identifiers to their respective
    `GeneratorUnit` dataclass instances.

### Notes

- This structure is typically created by the YAMLLoader and passed
  to `GeneratorBuilder` for model initialization.
- The data are designed to be serializable and interoperable
  with other modules of the MDI framework.

#### demand *: Dict[str, List[float]]*

#### horizon *: int*

#### level_hours *: Dict[str, float]*

#### units *: Dict[str, [GeneratorUnit](#MDI.Generator.GeneratorDataTypes.GeneratorUnit)]*

### *class* MDI.Generator.GeneratorDataTypes.GeneratorUnit(name: str, state: int, c_op: float, c_inv: float, p_max: float, include_cap: bool)

Bases: `object`

Representation of a single dispatchable generation unit.

This dataclass stores the economic and technical parameters
of each generator used in the optimization model, such as
operational state, variable and fixed costs, and rated capacity.

* **Parameters:**
  * **name** (*str*) – Unique identifier of the generation unit.
  * **state** (*int*) – Initial operational state of the unit (1 if already built, 0 otherwise).
  * **c_op** (*float*) – Variable operational cost (e.g., fuel or maintenance) in R$/MWh.
  * **c_inv** (*float*) – Investment cost associated with capacity expansion in R$
  * **p_max** (*float*) – Maximum generation capacity (MW) of the unit.
  * **include_cap** (*whether to include in capacity restriction* *or* *not*)

### Notes

- `state` is used to define the initial operational availability
  within the planning horizon.
- These attributes are directly mapped into Pyomo parameters
  via the generator builder module.

#### c_inv *: float*

#### c_op *: float*

#### include_cap *: bool*

#### name *: str*

#### p_max *: float*

#### state *: int*

## MDI.Generator.GeneratorEquations module

### Generator Equations Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the objective-related expressions for the generation
subsystem in the MDI framework. It formulates both the **operational cost**
and **energy balance** expressions, which are later aggregated into the
system-level optimization model.

#### Description

The functions in this module generate symbolic expressions that represent
the two principal aspects of the generation subproblem:

1. **Operational and investment cost function** —
   Represents the total cost of operation and expansion over the planning
   horizon, including both variable and fixed investment terms.

   [
   C_{gen} =
   sum_{g,t,p} h_p , c^{op}_g , P_{g,t,p}
   ;+;
   sum_{g,t} c^{inv}_g , x_{g,t}
   ]

   where
   - (h_p) denotes the duration (hours) of load level (p),
   - (c^{op}_g) is the operational cost of generator (g),
   - (c^{inv}_g) is the investment cost per MW of capacity,
   - (P_{g,t,p}) is the power generation level,
   - (x_{g,t}) indicates if the unit is available at time (t).
2. **Generation balance expression** —
   Computes the total available generation for each time period and load
   level, serving as input to system-level energy balance constraints:

   [
   G_{bal}(t,p) = sum_{g} P_{g,t,p}
   ]

#### Functions

add_generator_cost_expression(m, cost_array)
: Builds and appends the generator cost expression to the provided array.

add_generator_balance_expression(m, t, p, balance_array)
: Builds and appends the generation balance expression for a given time
  period and load level to the provided array.

### Notes

- Both expressions are appended to lists (`cost_array` or `balance_array`)
  to allow modular composition of objectives and constraints in composite models.
- Missing attributes silently skip expression creation to maintain model integrity.
- This design enables dynamic integration of subsystems (e.g., storage, hydro,
  or renewable modules) under a unified optimization framework.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,

> EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:** `MDI.GeneratorVars`, `MDI.GeneratorConstraints`
- **External:** `pyomo.environ (ConcreteModel)`, `typing`

### MDI.Generator.GeneratorEquations.add_generator_balance_expression(m: ConcreteModel, t: Any, p: Any, balance_array: List[Any]) → List[Any]

Build and append the generation balance expression for a given time and level.

Computes the total power generated across all units for the specified
time period and demand level, and appends it to `balance_array`.
The result serves as the left-hand side of the system-level
energy balance constraint.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model containing generator sets and variables.
  * **t** (*Any*) – Time period index.
  * **p** (*Any*) – Load level index.
  * **balance_array** (*list* *of* *pyomo expressions*) – List to which the generation balance expression will be appended.
* **Returns:**
  The same list, extended with the generation balance expression.
* **Return type:**
  list of pyomo expressions

### Notes

The balance expression is defined as:

$$
G_{bal}(t,p) = \sum_{g} P_{g,t,p}
$$

representing the total available generation at each period and load level.

### MDI.Generator.GeneratorEquations.add_generator_capacity_expression(m: ConcreteModel, t: Any, p: Any, capacity_array: List[Any]) → List[Any]

Build and append the generation capacity expression for a given time and level.

Computes the total generation capacity across all units for the specified
time period and demand level, and appends it to `capacity_array`.
The result serves as the left-hand side of the system-level
generation capacity constraint.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model containing generator sets and variables.
  * **t** (*Any*) – Time period index.
  * **p** (*Any*) – Load level index.
  * **capacity_array** (*list* *of* *pyomo expressions*) – List to which the generation capacity expression will be appended.
* **Returns:**
  The same list, extended with the generation capacity expression.
* **Return type:**
  list of pyomo expressions

### Notes

The capacity expression is defined as:

$$
G_{bal}(t,p) = \sum_{g} P_{g,t,p}
$$

representing the total available generation at each period and load level.

### MDI.Generator.GeneratorEquations.add_generator_cost_expression(m: ConcreteModel, cost_array: List[Any]) → List[Any]

Build and append the generator cost expression to the provided list.

This function constructs the total cost expression, including both
operational and investment components, over all generators, time periods,
and demand levels. The expression is appended to `cost_array` to allow
aggregation with other subsystem costs.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model containing generator-related sets, variables, and parameters.
  * **cost_array** (*list* *of* *pyomo expressions*) – List to which the total generator cost expression will be appended.
* **Returns:**
  The same list, extended with the generator cost expression.
* **Return type:**
  list of pyomo expressions

### Notes

The total generation cost is defined as:

$$
C_{gen} =
\sum_{g,t,p} h_p \, c^{op}_g \, P_{g,t,p}
+ \sum_{g,t} c^{inv}_g \, x_{g,t}
$$

where:
- $h_p$ is the duration (hours) of load level $p$;
- $c^{op}_g$ is the operational cost per MWh;
- $c^{inv}_g$ is the investment cost per MW;
- $P_{g,t,p}$ and $x_{g,t}$ are decision variables.

The resulting expression is symbolic and compatible with Pyomo objectives.

## MDI.Generator.GeneratorObjectives module

### Generator Objectives Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the **objective function** for the generator
subsystem within the MDI framework. The formulation represents the
total operational and investment cost to be minimized across the
planning horizon.

#### Description

The generator objective aggregates both the **variable operating cost**
and the **investment cost** associated with generator units.
The total objective function is defined as follows:

[
min_{P, x}
; C_{gen} =
sum_{g,t,p} ig( c^{op}_g , P_{g,t,p}
;+;
c^{inv}_g , x_{g,t} ig)
]

where:
- (c^{op}_g) — variable operating cost of generator (g);
- (c^{inv}_g) — investment cost of generator (g);
- (P_{g,t,p}) — power generated by unit (g) at time (t) and load level (p);
- (x_{g,t}) — binary or continuous variable indicating the generator’s active state.

The resulting expression is assigned as a Pyomo Objective with sense
minimize.

#### Functions

set_objective_generator(m)
: Builds and attaches the total generator cost objective to the Pyomo model.

### Notes

- The objective expression is scalar and represents the sum of all
  operational and investment expenditures within the generator subsystem.
- All required variables and parameters must be defined in the model prior
  to calling this function.
- This formulation can be combined with additional objectives (e.g.,
  emissions minimization, reliability indices) within a multi-objective
  optimization framework.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,

> EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:** Generator data and variable definitions.
- **External:** `pyomo.environ` (Objective, minimize)

### MDI.Generator.GeneratorObjectives.set_objective_generator(m)

Define and attach the generator cost minimization objective.

Constructs the total cost function for the generator subsystem,
including operational and investment costs, and registers it as
a Pyomo objective with sense of minimization.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing generator sets, parameters,
  and decision variables.
* **Returns:**
  The same model instance with an additional attribute `OBJ`
  representing the total generator cost objective.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

The objective is mathematically defined as:

$$
\min_{P,x} C_{gen} =
\sum_{g,t,p} ig( c^{op}_g \, P_{g,t,p}
+ c^{inv}_g \, x_{g,t} ig)
$$

This formulation captures both operational and investment costs
across all generator units, time periods, and demand levels.

## MDI.Generator.GeneratorVars module

### Generator Variables and Parameters Module

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module defines the **sets**, **parameters**, and **decision variables**
for the generator subsystem of the MDI optimization model.
It provides the necessary data-to-model mapping between structured input
(GeneratorData) and symbolic Pyomo model components.

#### Description

Two main functions are provided:

1. **\`generator_add_sets_and_params()\`**
   Initializes all sets, mappings, and scalar parameters from structured
   input data. It ensures consistency between the data schema and the
   model’s symbolic representation.
2. **\`generator_add_variables()\`**
   Defines the Pyomo decision variables representing generation levels
   and investment states.

The structure follows the standard formulation of generation expansion
and operation problems, enabling full reproducibility and modular
integration within larger system models.

#### Mathematical Representation

**Decision variables**

[
egin{align}
P_{g,t,p} &ge 0 &quad&        ext{Power generated by unit } g         ext{ at time } t,       ext{ level } p y_{g,t} &in {0,1} &quad&    ext{Investment decision for unit } g    ext{ at time } t x_{g,t} &in {0,1} &quad&    ext{Operational state (existing) of unit } g    ext{ at time } t
end{align}
]

**Parameters**

[
egin{align}
p^{max}_g &:   ext{Maximum generation capacity of unit } g c^{op}_g &:     ext{Variable operational cost of unit } g c^{inv}_g &:    ext{Investment cost of unit } g 

> ext{state}_g &:         ext{Initial operational status (built or not)} 

h_p &:  ext{Duration (hours) of demand level } p
end{align}
]

#### Functions

generator_add_sets_and_params(m, data)
: Initializes all sets and parameters in the model based on structured input.

generator_add_variables(m)
: Defines decision variables for generation, investment, and operational state.

### Notes

- The resulting model components are compliant with the naming conventions
  used throughout the MDI package.
- Demand values (m.d) are retained in their dictionary structure for
  compatibility with subsequent constraint and objective definitions.
- The binary variables gen_y and gen_x can be relaxed to continuous
  domains for convex approximations or LP relaxations.

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*, Lecture Notes,

> EELT7030/UFPR, 2023.

#### Module Dependencies

- **Internal:** `GeneratorDataTypes`
- **External:** `pyomo.environ` (RangeSet, Set, Param, Var, NonNegativeReals, Binary)

### MDI.Generator.GeneratorVars.generator_add_sets_and_params(m: ConcreteModel, data: [GeneratorData](#MDI.Generator.GeneratorDataTypes.GeneratorData)) → ConcreteModel

Initialize generator-related sets and parameters in the model.

This function converts structured data into Pyomo components,
including time, unit, and demand level sets, as well as the
associated economic and technical parameters for each generator.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance to which the sets and parameters will be added.
  * **data** ([*GeneratorData*](#MDI.Generator.GeneratorDataTypes.GeneratorData)) – Structured generator data object containing all relevant
    attributes (units, demand, horizon, and level hours).
* **Returns:**
  The model with newly created sets, parameters, and demand data.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

The following components are created:

- Sets:
  - `T`: time periods (1..horizon)
  - `P`: load levels
  - `GU`: generator units
- Parameters:
  - `gen_pmax`: maximum generation capacity (MW)
  - `gen_c_op`: variable operational cost (R$/MWh)
  - `gen_c_inv`: investment cost (R$/MW)
  - `gen_state`: initial availability status (binary)
  - `level_hours`: duration of each load level (hours)

### MDI.Generator.GeneratorVars.generator_add_variables(m: ConcreteModel) → ConcreteModel

Define decision variables for the generator subsystem.

Creates Pyomo decision variables representing generation output,
investment decisions, and cumulative operational existence for
each generator, time period, and load level.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model instance containing the sets previously defined
  by `generator_add_sets_and_params`.
* **Returns:**
  The same model, extended with generator-related decision variables.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

The following variables are created:

- `gen_P[g,t,p]` — Power generated by unit *g* at time *t* and level *p* (MW).
  Domain: $\mathbb{R}_+$
- `gen_y[g,t]` — Binary investment decision (1 if built at *t*, 0 otherwise).
  Domain: $\{0,1\}$
- `gen_x[g,t]` — Binary variable representing existing or active capacity at *t*.
  Domain: $\{0,1\}$
