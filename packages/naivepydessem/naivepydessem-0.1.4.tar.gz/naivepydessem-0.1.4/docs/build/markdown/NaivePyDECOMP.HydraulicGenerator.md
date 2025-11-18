# NaivePyDECOMP.HydraulicGenerator package

## Module contents

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Hydraulic Generation Modeling (HydraulicGenerator)

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

The `HydraulicGenerator` package provides a modular framework for modeling
hydropower systems in Pyomo-based dispatch and unit commitment models. It
includes flexible hydropower production functions (FPH), reservoir balance
constraints, and terminal storage requirements.

### Submodules

HydraulicDataTypes
: Dataclasses defining hydropower unit and system-wide data.

HydraulicVars
: Initialization routines for Pyomo sets, parameters, and variables.

HydraulicConstraints
: Constraint builders (generation, reservoir balance, SoC limits, targets).

HydraulicObjectives
: Objective function definitions for hydro-only models.

HydraulicGeneratorBuilder
: High-level routines to assemble complete hydropower dispatch models.
  Simple FPH based on constant productivity.

SimplifiedConstantProductivityFPH
: Didactic constant productivity model (simplified).

### Notes

- Multiple FPH modes are supported (constant, simplified, specific, exact).
- Reservoir mass balance constraints ensure intertemporal consistency.
- Designed for interoperability with Thermal, Renewable, and Storage packages
  in hybrid models.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## Submodules

## NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints module

### Hydropower Constraints Module for Multi-Mode Generation Modeling

This module implements hydropower-related constraints for Unit Commitment
and Dispatch models in Pyomo. It supports multiple representations of the
hydraulic production function (FPH), including constant productivity,
specific productivity (fixed head), simplified polynomial approximations,
and exact head-dependent formulations.

The functions herein enforce:
- Generation computation using plant-specific FPH callables;
- Reservoir mass balance via continuity constraints;
- Upstream water aggregation for cascaded systems (no travel time);
- Final storage requirements;
- System-wide demand balance for hydropower-only settings.

Each hydropower mode (constant, specific, exact, simplified) must be
associated with a callable set in the model attribute m.hydro_FPH[h].
The upstream connectivity and inflows must be available as
m.hydro_upstreams[h] and m.hydro_afluencia[h][t-1], respectively.
This module assumes **no routing delay** between cascaded plants.

This interface is compatible with Pyomo-based MILP/MIQP dispatch models
and is intended to interoperate cleanly with thermal subsystems when a
combined balance is used elsewhere.

#### Imported Dependencies

- pyomo.environ.Constraint

#### Functions

- add_hydro_generation_constraint(m)
- hydro_total_inflow_expr(m, h, t)
- add_hydro_qmin_constraint(m)
- add_hydro_qmax_constraint(m)
- add_hydro_volume_continuity_constraint(m)
- add_hydro_volume_max_constraint(m)
- add_hydro_volume_mim_constraint(m)
- add_hydro_balance_constraint(m)

#### Model Requirements

Sets
: m.HG : hydropower units
  m.T  : time periods

Variables
: m.hydro_V[h,t] : storage volume (hm^3)
  m.hydro_Q[h,t] : turbined discharge (hm^3)
  m.hydro_S[h,t] : spill discharge (m^3/s)
  m.hydro_G[h,t] : hydropower generation (MW)
  m.D[t]         : deficit (MW), if used

Parameters
: m.hydro_Vini[h]  : initial storage (hm^3)
  m.hydro_Vmin[h]  : minimum storage (hm^3)
  m.hydro_Vmax[h]  : maximum storage (hm^3)
  m.hydro_afluencia[h][t-1] : natural inflow (m^3/s), 0-based external array
  m.hydro_upstreams[h]      : collection of upstream units for h
  m.hydro_FPH[h]            : callable FPH(Q,V,S) => MW
  m.hydro_compute_total_inflow[h] : bool flag to aggregate upstream releases
  m.horizon : last period index, if used for terminal constraints
  m.d[t]    : demand (MW), if hydropower-only balance is applied

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_continuity_constraint(m)

Add reservoir mass balance (water continuity) constraints.

Updates stored volume using natural + upstream inflows (no delay),
turbined discharge, and spill. Uses the initial storage at the first
period.

For each (h, t):
: if t == 1:
  : m.hydro_V[h,1] == m.hydro_Vini[h]
    : + m.hydro_zeta_vol \* (Inflow(h,1) - Q[h,1] - S[h,1])
  <br/>
  else:
  : m.hydro_V[h,t] == m.hydro_V[h,t-1]
    : + m.hydro_zeta_vol \* (Inflow(h,t) - Q[h,t] - S[h,t])

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Model with variables m.hydro_V, m.hydro_Q, m.hydro_S,
  sets m.HG, m.T, and parameters
  m.hydro_zeta_vol, m.hydro_Vini. Inflow is given by
  `hydro_total_inflow_expr()`.
* **Returns:**
  Constraint block m.hydro_volume_balance_constraint added to the model.
* **Return type:**
  pyomo.core.expr.relational.EqualityExpression

### Notes

m.hydro_zeta_vol converts flow (m^3/s) into volume (hm^3) over one period
(e.g., 3600 / 1e6 for hourly steps).

## NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Hydraulic System Data Classes for Reservoir Optimization

### Description

This module defines data classes for modeling structural and operational
characteristics of hydroelectric systems in short-term dispatch and
unit-commitment studies. The classes are designed to serve as a clean
interface between problem data and Pyomo-based optimization models.

### Overview

Two classes are provided:

- `HydraulicUnit`: describes a single hydro plant, including storage bounds,
  turbined-flow limits, initial/terminal volumes, natural inflows, cascade
  topology, and optional coefficients for alternative FPH (hydropower
  production function) modes.
- `HydraulicData`: encapsulates system-wide information such as planning
  horizon, hourly demand, plant map, and conversion/penalty constants.

### Conventions and Units

- Time is discretized in periods `t = 1, …, horizon` (integers).
- Discharges (Q, S) are in hm^3.
- Storage volumes (V) are in hm^3.

### Notes

- Cascade routing: this data layer assumes **no travel time**. If routing
  delays are relevant, they should be handled in the modeling layer.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### *class* NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData(horizon: int, demand: Dict[int, float], units: Dict[str, [HydraulicUnit](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)], Cdef: float = 1000.0)

Bases: `object`

System-wide hydropower data for planning and dispatch.

* **Parameters:**
  * **horizon** (*int*) – Number of time periods in the planning horizon.
  * **demand** (*Dict* *[**int* *,* *float* *]*) – Mapping from period `t` (1-based) to system demand (MW).
  * **units** (*Dict* *[**str* *,* [*HydraulicUnit*](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit) *]*) – Map from plant name to its `HydraulicUnit` data structure.
  * **Cdef** (*float* *,* *optional*) – Penalty cost for unmet demand (R$/MWh), to be used by objectives in
    optimization models. Default is `1000.0`.

### Notes

- The dictionary `demand` is assumed to be 1-based (`t = 1..horizon`).
  If your data are 0-based, map them accordingly before constructing this
  object.
- The interpretation of `zeta` depends on where power conversion is
  performed (inside the FPH callable or in the model).

#### Cdef *: float* *= 1000.0*

#### demand *: Dict[int, float]*

#### horizon *: int*

#### units *: Dict[str, [HydraulicUnit](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)]*

### *class* NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit(name: str, Qmin: float, Qmax: float, Vmin: float, Vmax: float, Vini: float, afluencia: List[float], upstreams: List[str] | None = None, p: List[float] | None = None, compute_total_inflow: bool = True)

Bases: `object`

Hydropower plant data container.

* **Parameters:**
  * **name** (*str*) – Unique identifier of the hydro plant.
  * **Qmin** (*float*) – Minimum allowed turbined flow (hm^3).
  * **Qmax** (*float*) – Maximum allowed turbined flow (hm^3).
  * **Vmin** (*float*) – Minimum storage volume (hm^3).
  * **Vmax** (*float*) – Maximum storage volume (hm^3).
  * **Vini** (*float*) – Initial storage volume at the beginning of the horizon (hm^3).
  * **afluencia** (*List* *[**float* *]*) – Natural inflow time series (hm^3); external, 0-based list aligned
    with model periods (accessed as `afluencia[t-1]`).
  * **upstreams** (*List* *[**str* *]* *,* *optional*) – List of immediate upstream plant names that feed this unit.
    Defaults to `None` (treated as no upstreams).
  * **p** (*List* *[**float* *]*) – Global productivity coefficient (used in constant/simplified models;
    unit interpretation depends on how head is handled in the FPH).
  * **mode** (*str* *,* *optional*) – Generation-mode selector. Valid options include
    {“constant”, “specific”, “exact”, “simplified”}.
    Default is “constant”.
  * **compute_total_inflow** (*bool* *,* *optional*) – If `True`, total inflow will include upstream releases in addition
    to exogenous natural inflow in expressions that support it.
    Default is `True`.

#### Qmax *: float*

#### Qmin *: float*

#### Vini *: float*

#### Vmax *: float*

#### Vmin *: float*

#### afluencia *: List[float]*

#### compute_total_inflow *: bool* *= True*

#### name *: str*

#### p *: List[float]* *= None*

#### upstreams *: List[str]* *= None*

## NaivePyDECOMP.HydraulicGenerator.HydraulicEquations module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Hydraulic Model Expression Utilities for Pyomo Optimization

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides helper functions to construct symbolic expressions
related to energy hydraulic systems in Pyomo-based optimization models.
These expressions can be incrementally assembled and integrated into
constraints (e.g., energy balance) or cost functions (e.g.,
generation costs).

The functions are designed to support modular model construction and
hybrid system integration. They can be used in conjunction with other
technology modules (e.g., thermal, hydro, renewable) to build power
balance constraints and system-wide cost objectives.

All expressions are symbolic and compatible with Pyomo’s modeling
framework. Each function includes safeguards to ensure that required
model components exist before attempting to generate expressions.

### Intended Use

- To append hydraulic-related cost and energy balance expressions to lists
  that contribute to the overall objective function and constraint set.
- To modularize and standardize hydraulic modeling across different hybrid
  energy system configurations.

### Examples

```pycon
>>> cost_terms = []
>>> add_hydraulic_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)
```

```pycon
>>> balance_terms = []
>>> add_hydraulic_balance_expression(model, t=5, balance_array=balance_terms)
>>> model.HydraulicBalance.add(balance_terms[0])
```

### Notes

- This module assumes that hydraulic behavior is modeled using variables such as
  hydro_G.
- The structure is compatible with Pyomo’s ConstraintList and indexed Constraint(T).
- Expressions are constructed incrementally and can be combined with other
  sources (e.g., thermal, renewable) in hybrid dispatch models.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023..

## NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Hydropower Dispatch Model Builder

### Description

This module defines the construction logic for assembling a **hydropower-only**
optimization model in Pyomo. It integrates the full sequence of:

- Set and parameter initialization,
- Decision variable declaration,
- Piecewise or analytical hydropower production modeling (FPH),
- Operational constraints,
- Objective function (optional).

### Supported generation modes (per unit)

- Constant productivity
- Specific productivity with fixed head
- Exact head-dependent generation with nonlinear losses
- Simplified constant productivity (didactic)

### Functions

build_FPHs(m, data)
: Initialize the hydropower production function (FPH) callable for each unit.

build_hydro_dispatch(data, include_objective=True)
: Assemble a complete Pyomo model for hydropower dispatch optimization.

### Modeling Conventions and Units

- Time periods are indexed as integers t = 1, …, horizon.
- Turbined and spill discharges (Q, S): hm^3.
- Storage volume (V): hm^3.
- Power (G) and demand (d): MWh.

### Notes

- This builder targets **pure hydropower** systems. To include thermal units,
  couple with a combined system balance elsewhere.
- The callable stored in m.hydro_FPH[h] must accept the signature
  FPH(Q, V, S) → MW and be consistent with model units.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_problem(m: ConcreteModel, data: [HydraulicData](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData), include_objective: bool = False) → ConcreteModel

Assemble a hydropower dispatch problem in Pyomo.

This builder configures a Pyomo model for reservoir-based hydropower
optimization. It attaches sets, parameters, decision variables, the
hydropower production functions (FPHs), and all relevant operational
constraints. Optionally, it includes the demand balance and the
cost-minimization objective.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which the hydropower problem will be added.
  * **data** ([*HydraulicData*](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Input data object containing planning horizon, demand mapping,
    unit definitions, inflows, storage bounds, and productivity
    coefficients.
  * **include_objective** (*bool* *,* *optional*) – If True, add the system-wide demand balance and deficit-penalizing
    objective function (default is False).
* **Returns:**
  The updated Pyomo model with hydropower sets, parameters, variables,
  constraints, and optionally the objective.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_subproblem(m: ConcreteModel, data: [HydraulicData](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData), stage: int) → ConcreteModel

Assemble a hydropower dispatch problem in Pyomo.

This builder configures a Pyomo model for reservoir-based hydropower
optimization. It attaches sets, parameters, decision variables, the
hydropower production functions (FPHs), and all relevant operational
constraints. Optionally, it includes the demand balance and the
cost-minimization objective.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which the hydropower problem will be added.
  * **data** ([*HydraulicData*](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Input data object containing planning horizon, demand mapping,
    unit definitions, inflows, storage bounds, and productivity
    coefficients.
  * **include_objective** (*bool* *,* *optional*) – If True, add the system-wide demand balance and deficit-penalizing
    objective function (default is False).
* **Returns:**
  The updated Pyomo model with hydropower sets, parameters, variables,
  constraints, and optionally the objective.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.build_FPHs(m: ConcreteModel, data: [HydraulicData](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData))

Initialize hydropower production functions (FPH) for all units.

For each hydro unit h, this function selects and constructs a callable
FPH according to the unit’s declared mode (constant, simplified,
specific, or exact) and assigns it to m.hydro_FPH[h] with
the signature FPH(Q, V, S) => MW.

* **Parameters:**
  * **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Pyomo model into which the FPH callables will be attached.
  * **data** ([*HydraulicData*](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Configuration object containing unit maps and modes
* **Returns:**
  The model m is modified in place. A dictionary m.hydro_FPH is
  created, indexed by unit name, each entry being a callable of the form
  FPH(Q, V, S).
* **Return type:**
  None

### NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.build_hydro_dispatch(data: [HydraulicData](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData), include_objective: bool = True)

Assemble a complete Pyomo model for hydropower dispatch.

The resulting model includes:

- Set and parameter definitions (via hydraulyc_add_sets_and_params)
- Continuous decision variables (via hydralic_add_variables_g)
- Per-unit FPH callables (via build_FPHs)
- Operational constraints: generation equation, reservoir mass balance,
  Qmin/Qmax, volume bounds, terminal storage target
- Optional system-wide demand balance and cost-minimization objective

* **Parameters:**
  * **data** ([*HydraulicData*](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Input data with horizon, demand, unit map, and conversion constants.
  * **include_objective** (*bool* *,* *optional*) – If True, add the hydropower balance constraint and define the
    objective function. Default is True.
* **Returns:**
  A Pyomo ConcreteModel ready to be passed to a solver.
* **Return type:**
  pyomo.core.base.PyomoModel.ConcreteModel

### Notes

- Designed for hydropower-only settings. For mixed hydro-thermal
  systems, use an extended builder with a combined balance equation.
- The order of operations ensures FPH callables are available before
  generation constraints are added.

## NaivePyDECOMP.HydraulicGenerator.HydraulicObjectives module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Objective Function for Pure Hydropower Dispatch

### Description

This module defines the objective for reservoir-based **hydropower-only**
optimization models. The objective minimizes (i) the total cost of unmet
energy (deficit) and (ii) a small penalty on water spillage to discourage
gratuitous releases, thereby promoting more efficient water usage.

### Functions

set_objective_hydro(m)
: Attach a minimization objective to a Pyomo model that penalizes
  deficit and spillage over the planning horizon.

### Modeling Conventions and Units

- Time periods: integers `t = 1, …, horizon`.
- Deficit `D[t]`: MW (interpreted per-period, consistent with objective scaling).
- Spill `hydro_S[h,t]`: m^3/s.
- `Cdef`: $/MWh (ensure consistency with how deficit is modeled and aggregated).

### Notes

- Designed for **pure hydropower** systems (no thermal generation).
- The spillage penalty uses a fixed coefficient (0.3). Adjust as needed
  to break degeneracy or steer solutions away from unnecessary spill.
- Compatible with NaivePyDECOMP hydropower data and constraints.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## NaivePyDECOMP.HydraulicGenerator.HydraulicVars module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Hydropower Model Initialization: Sets, Parameters, and Variables

### Description

This module provides initialization routines for setting up the basic
sets, parameters, and continuous variables required by hydropower
optimization models in Pyomo. It accommodates multiple hydropower
generation modes, natural-inflow handling, and head-dependent power
relationships supplied elsewhere in the modeling stack.

### Functions

hydraulyc_add_sets_and_params(m, data)
: Initialize sets and model-level parameters/containers for hydropower units
  and system-wide demand.

hydralic_add_variables_g(m)
: Declare continuous decision variables for hydropower dispatch modeling.

### Modeling Conventions and Units

- Time periods are indexed as integers `t = 1, …, horizon`.
- Turbined/Spill discharges (Q, S): hm^3.
- Storage volume (V): hm^3.
- Demand and power (d, G): MWh.

### Notes

- The argument `data` is expected to be an instance of `HydraulicData`,
  where each unit is a `HydraulicUnit`.
- Some attributes attached to the model are plain Python containers
  (e.g., dictionaries) rather than Pyomo `Param` objects, by design.
- This module targets short-term planning models and is suitable for
  integration into MILP/MIQP hydropower (or hydrothermal) formulations.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.HydraulicGenerator.HydraulicVars.hydraulyc_add_sets_and_params(m, data)

Initialize hydropower sets and model-level parameters/containers.

Configures the Pyomo model `m` with time and hydropower unit sets,
system-level demand, and per-unit attributes such as flow limits,
storage bounds, initial/terminal storages, natural inflows, cascade
topology, and flags used by inflow aggregation. Values are sourced
from the `HydraulicData`/`HydraulicUnit` objects.

* **Parameters:**
  * **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Target Pyomo model to be populated with sets and parameters.
  * **data** ([*HydraulicData*](#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Input data object with planning horizon, demand mapping, and the
    dictionary of hydropower units.
* **Returns:**
  The same model `m` with initialized sets and parameters/containers.
* **Return type:**
  pyomo.core.base.PyomoModel.ConcreteModel

### Notes

- All plant-specific containers are indexed by the hydropower unit set
  `m.HG`.
- Time-varying arrays (e.g., `afluencia`) are assumed to be external,
  0-based Python lists that are accessed as `[t-1]` inside constraints.
- Some attributes (e.g., `m.hydro_Qmin`, `m.hydro_Vmax`) are plain
  Python dictionaries attached to the model for convenience; others
  (e.g., `m.d`) are Pyomo `Param` objects.
- The attribute `m.horizon` stores the number of periods for quick access.

## NaivePyDECOMP.HydraulicGenerator.SimplifiedConstantProductivityFPH module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Simplified Constant Productivity FPH Function

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Defines a simplified hydropower production function (FPH) for short-term
operation models. The generation is assumed to be proportional to turbine
discharge, scaled by a constant productivity coefficient.

The FPH is expressed as:

> FPH(Q) = P \* Q

where:
- Q : turbine discharge (hm^3)
- P : global productivity coefficient (dimensionless)

This formulation is particularly useful for approximate dispatch models,
sensitivity analyses, or didactic examples that do not require head-dependent
hydraulic modeling.

### Notes

- Unlike the more detailed constant-productivity model, this simplified
  function does not include the `zeta` scaling factor. If desired, the
  conversion constant can be absorbed directly into `P` to yield MW.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
