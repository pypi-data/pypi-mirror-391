# NaivePyDESSEM.ThermalGenerator package

## Module contents

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Package: Thermal Generation Modeling (ThermalGenerator)

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

The **ThermalGenerator** package provides a modular framework for modeling
thermal generation units in Pyomo-based unit commitment and dispatch models.
It includes data structures, sets, parameters, variables, constraints,
objectives, and builder functions for both quadratic (MIQP) and piecewise-linear
(MILP) cost formulations.

### Submodules

ThermalDataTypes
: Dataclasses defining thermal unit parameters and system-wide data.

ThermalVars
: Initialization routines for Pyomo sets, parameters, and variables.

ThermalConstraints
: Constraint builders (balance, capacity, reserve, ramping, min up/down).

ThermalObjectives
: Objective function definitions (quadratic and piecewise-linear).

ThermalPiecewiseCost
: Utilities for building piecewise-linear cost functions.

ThermalBuilder
: High-level routines to assemble complete thermal generation models.

### Notes

- Supports MIQP and MILP formulations, enabling flexibility in solver choice.
- Reserve, emissions, and startup/shutdown costs can be included as needed.
- Designed for interoperability with Hydro, Renewable, and Storage packages
  to support hybrid hydrothermal-renewable models.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## Submodules

## NaivePyDESSEM.ThermalGenerator.ThermalConstraints module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Constraints

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Constraint builders for thermal unit commitment (UC) formulations in Pyomo.
Each function attaches a specific block of constraints to a
ConcreteModel, enabling modular construction of MILP/MIQP/MINLP UC
models. The naming convention uses the thermal_\* prefix for variables,
parameters, and constraint blocks attached to the model.

### Constraint Families

1. Balance (system-wide):
   - sum_g thermal_p[g,t] + D[t] = d[t]
2. Capacity (per unit and period):
   - Lower bound: thermal_Pmin[g] \* thermal_u[g,t] <= thermal_p[g,t]
   - Upper bound (no reserve): thermal_p[g,t] <= thermal_Pmax[g] \* thermal_u[g,t]
   - Upper bound (with reserve): thermal_p[g,t] + thermal_r[g,t] <= thermal_Pmax[g] \* thermal_u[g,t]
3. Spinning reserve:
   sum_g thermal_r[g,t] >= thermal_Rreq[t]
4. Commitment logic:
   - Mutual exclusivity: thermal_y[g,t] + thermal_w[g,t] <= 1
   - State transition:
     - t=1: thermal_u[g,1] - thermal_u0[g] = thermal_y[g,1] - thermal_w[g,1]
     - t>1: thermal_u[g,t] - thermal_u[g,t-1] = thermal_y[g,t] - thermal_w[g,t]
5. Ramping (with start/shut effects):
   - Up: thermal_p[g,t] - thermal_p[g,t-1] <= thermal_RU[g] + thermal_Pmax[g] \* thermal_y[g,t]
   - Down: thermal_p[g,t-1] - thermal_p[g,t] <= thermal_RD[g] + thermal_Pmax[g] \* thermal_w[g,t]
     At t=1, use thermal_p0[g] in place of the previous-period power.)
6. Minimum up/down time:
   - Up: SUM_{t=t-Tu+1}^{t} thermal_y[g,t] <= thermal_u[g,t]
   - Down: SUM_{t=t-Td+1}^{t} thermal_w[g,t] <= 1 - thermal_u[g,t]

### Usage

Combine these builders with:

- set/parameter/variable definitions for thermal UC, and
- an appropriate objective (quadratic or piecewise linear).

By composing the blocks, one can construct MIQP (quadratic costs) or
MILP (piecewise linear costs) UC formulations, optionally with reserve constraints.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_balance_constraint(m)

Add the system-wide energy balance constraint.

For each period t, the total thermal generation plus the deficit
must match the demand:

> sum_g thermal_p[g,t] + D[t] == d[t]
* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Pyomo model with thermal parameters and variables
* **Returns:**
  The updated model with constraint block
  m.thermal_balance_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> # Assume m has sets/vars/params defined; then:
>>> _ = thermal_add_balance_constraint(m)
>>> m.thermal_balance_constraint.pprint()  
```

### NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_capacity_constraint(m, include_reserve: bool = False)

Add generation capacity limits for all units and periods.

Enforces unit-wise lower and upper bounds linked to the on/off status.
When include_reserve is True, the upper bound also accounts for
spinning reserve provision.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Model containing thermal parameters and variables
  * **include_reserve** (*bool* *,* *optional*) – If True, apply thermal_p + thermal_r <= Pmax \* u as the upper
    bound. Default is False.
* **Returns:**
  The updated model with constraint blocks
  m.thermal_cap_lower_constraint and
  m.thermal_cap_upper_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> # Upper bound includes reserve if requested:
>>> _ = thermal_add_capacity_constraint(m, include_reserve=True)
```

### NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_min_up_down_constraint(m)

Add minimum up-time and down-time constraints with initial state consideration.

These constraints ensure logical consistency of operating sequences:

- **Minimum up-time**: if a unit is started, it must remain ON for at least
  thermal_t_up[g] periods. If the unit has already been ON before the
  optimization window (according to thermal_init_status[g] > 0),
  the remaining required ON time is reduced accordingly.
- **Minimum down-time**: if a unit is shut down, it must remain OFF for at least
  thermal_t_dn[g] periods. If the unit has already been OFF before the
  optimization window (according to thermal_init_status[g] < 0),
  the remaining required OFF time is reduced accordingly.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with thermal paraeters and variables
* **Returns:**
  Model with added constraint blocks:
  - m.thermal_min_up_constraint
  - m.thermal_min_dn_constraint
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> _ = thermal_add_min_up_down_constraint(m)
```

### NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_ramps_constraint(m)

Add ramp-up and ramp-down constraints.

Limits the change in generation between consecutive periods according
to thermal_RU[g] and thermal_RD[g], with allowances when a unit
starts up or shuts down. At t=1, the previous-period generation is
given by thermal_p0[g].

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with thermal paraeters and variables
* **Returns:**
  The updated model with constraint blocks
  m.thermal_ramp_up_constraint and m.thermal_ramp_dn_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> _ = thermal_add_ramps_constraint(m)
```

### NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_reserve_constraint(m)

Add spinning reserve requirement constraints.

For each period t, total spinning reserve must satisfy:

> sum_g thermal_r[g,t] >= thermal_Rreq[t].

### Notes

This constraint assumes that reserve variables and requirements are
present, and that capacity limits were added with
include_reserve=True.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with thermal parameters and variables
* **Returns:**
  The updated model with constraint block
  m.thermal_reserve_req_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> _ = thermal_add_reserve_constraint(m)
>>> m.thermal_reserve_req_constraint.pprint()  
```

### NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_startup_shutdown_logic_constraint(m)

Add startup/shutdown logical consistency constraints.

Imposes:

- Mutual exclusivity of start and shut in the same period:
  thermal_y[g,t] + thermal_w[g,t] <= 1.
- State transition linking on/off status to start/shut variables:
  - t=1: thermal_u[g,1] - thermal_u0[g] = thermal_y[g,1] - thermal_w[g,1]
  - t>1: thermal_u[g,t] - thermal_u[g,t-1] = thermal_y[g,t] - thermal_w[g,t]

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with thermal paraeters and variables
* **Returns:**
  The updated model with constraint blocks
  m.thermal_f_ss_constraint and m.thermal_logic_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> _ = thermal_add_startup_shutdown_logic_constraint(m)
```

## NaivePyDESSEM.ThermalGenerator.ThermalDataTypes module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Data Structures and Problem Skeleton

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module defines the canonical data structures for short-term thermal
unit commitment (UC) and economic dispatch problems. It is designed to be
paired with Pyomo model builders that assemble:

- Mixed-Integer Quadratic Programs (MIQP) with quadratic variable cost
  a \* u + b \* p + c \* p² and start-up cost SC \* y.
- Mixed-Integer Linear Programs (MILP) using piecewise-linear (PWL) cost
  curves via SOS2/convex-combination.
- Optional spinning reserve coupling and global emissions/fuel caps.

### Notation (per unit g and time t)

Decision variables (model side):

> u_{g,t} in {0,1}   : on/off state
> y_{g,t}, w_{g,t}  : start-up / shut-down flags (binary)
> p_{g,t} >= 0       : electrical output (MW)
> r_{g,t} >= 0       : spinning reserve (MW, optional)
> D_t >= 0           : demand deficit (MW, optional)

Core parameters (this module):

> Pmin_g, Pmax_g    : power bounds (MW)
> RU_g, RD_g        : ramp-up / ramp-down limits (MW/Δt)
> a_g, b_g, c_g     : cost coefficients for a \* u + b \* p + c \* p²
> SC_g              : hot start cost
> t_up_g, t_down_g  : minimum up/down times (periods)
> u0_g, p0_g        : initial state and output
> pw_breaks, pw_costs : PWL points for variable cost C(p)
> γ_g               : emissions factor (tCO₂/MWh), optional

### Typical objective (MIQP form)

Minimize over t,g:

> sum ( a_g u_{g,t} + b_g p_{g,t} + c_g p_{g,t}^2 + SC_g y_{g,t} ) + C_def sum(D_t)

subject to balance, capacity, ramping, min up/down, and (optionally)
reserve and emissions constraints.

### Usage

- *ThermalUnit*: describes a single thermal unit, including technical
  limits, cost curve, start-up, ramping, and optional PWL and emissions.
- *ThermalData*: wraps the system horizon, hourly demand, the unit map,
  and optional reserve/emissions settings to feed a Pyomo builder.

### Intended pairing

This module is agnostic to the specific Pyomo modeling choices. It is
compatible with builders that: (i) set MIQP objectives directly from
(a,b,c); or (ii) construct MILP PWL costs from (pw_breaks, pw_costs),
keeping a \* u and SC \* y in the linear objective.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### *class* NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData(horizon: int, demand: Dict[int, float], units: Dict[str, [ThermalUnit](#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit)], Cdef: float = 1000.0, Rreq: Dict[int, float] | None = None, has_history: bool = False)

Bases: `object`

System-wide data container for thermal unit commitment problems.

* **Parameters:**
  * **horizon** (*int*) – Number of time periods in the planning horizon.
  * **demand** (*Dict* *[**int* *,* *float* *]*) – Mapping of each period `t` to system demand (MW).
  * **units** (*Dict* *[**str* *,* [*ThermalUnit*](#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit) *]*) – Dictionary mapping unit identifiers to their `ThermalUnit` objects.
  * **Cdef** (*float* *,* *optional*) – Deficit penalty cost ($/MWh), default is 1000.0.
  * **Rreq** (*Dict* *[**int* *,* *float* *]* *,* *optional*) – Mapping of each period `t` to spinning reserve requirement (MW).
    Defaults to `None`.
  * **has_history** (*bool* *,* *optional*) – Consider previous states or not. Default is false

### Notes

- This class serves as a structured input for Pyomo-based UC models.
- `Rreq` is optional; if not provided, reserve constraints must be disabled.
- `Cdef` penalizes unmet demand in the optimization objective.

#### Cdef *: float* *= 1000.0*

#### Rreq *: Dict[int, float] | None* *= None*

#### demand *: Dict[int, float]*

#### has_history *: bool* *= False*

#### horizon *: int*

#### units *: Dict[str, [ThermalUnit](#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit)]*

### *class* NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit(name: str, Pmin: float, Pmax: float, RU: float, RD: float, a: float = 0.0, b: float = 0.0, c: float = 0.0, SC: float = 0.0, t_up: int = 1, t_down: int = 1, init_status_h: int = -1, u0: int = 0, p0: float = 0.0, pw_breaks: List[float] | None = None, pw_costs: List[float] | None = None, gamma: float = 0.0)

Bases: `object`

Data container for a thermal generating unit with unit commitment attributes.

* **Parameters:**
  * **name** (*str*) – Unique identifier of the thermal unit.
  * **Pmin** (*float*) – Minimum operating power output (MW).
  * **Pmax** (*float*) – Maximum operating power output (MW).
  * **RU** (*float*) – Ramp-up limit (MW per period).
  * **RD** (*float*) – Ramp-down limit (MW per period).
  * **a** (*float* *,* *optional*) – Fixed cost coefficient ($/h), default is 0.0.
  * **b** (*float* *,* *optional*) – Linear generation cost coefficient ($/MWh), default is 0.0.
  * **c** (*float* *,* *optional*) – Quadratic generation cost coefficient ($/MWh²), default is 0.0.
  * **SC** (*float* *,* *optional*) – Hot start-up cost ($), default is 0.0.
  * **t_up** (*int* *,* *optional*) – Minimum up-time (hours/periods), default is 1.
  * **t_down** (*int* *,* *optional*) – Minimum down-time (hours/periods), default is 1.
  * **init_status_h** (*int* *,* *optional*) – Value to compute initial t_min_up/t_min_down
  * **u0** (*int* *,* *optional*) – Initial commitment status at t=0 (1=ON, 0=OFF), default is 0.
  * **p0** (*float* *,* *optional*) – Initial generation level at t=0 (MW), default is 0.0.
  * **pw_breaks** (*List* *[**float* *]* *,* *optional*) – Breakpoints for piecewise-linear cost approximation.
  * **pw_costs** (*List* *[**float* *]* *,* *optional*) – Cost values corresponding to the piecewise breakpoints.
  * **gamma** (*float* *,* *optional*) – Emission factor or auxiliary cost coefficient (unit-dependent),
    default is 0.0.

### Notes

- The quadratic cost curve is typically defined as:
  `C(p) = a * u + b * p + c * p² + SC * y`,
  where `u` is the commitment status and `y` the startup indicator.
- Piecewise approximations use `pw_breaks` and `pw_costs` for MILP models.

#### Pmax *: float*

#### Pmin *: float*

#### RD *: float*

#### RU *: float*

#### SC *: float* *= 0.0*

#### a *: float* *= 0.0*

#### b *: float* *= 0.0*

#### c *: float* *= 0.0*

#### gamma *: float* *= 0.0*

#### init_status_h *: int* *= -1*

#### name *: str*

#### p0 *: float* *= 0.0*

#### pw_breaks *: List[float] | None* *= None*

#### pw_costs *: List[float] | None* *= None*

#### t_down *: int* *= 1*

#### t_up *: int* *= 1*

#### u0 *: int* *= 0*

## NaivePyDESSEM.ThermalGenerator.ThermalEquations module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Model Expression Utilities for Pyomo Optimization

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides helper functions to construct symbolic expressions
related to thermal power generation in Pyomo models. These expressions
can be incrementally assembled and used in constraints (e.g., power balance)
or in the objective function (e.g., cost minimization).

Functions are designed to be modular and composable, allowing the user to
build lists of partial expressions from multiple sources (e.g., thermal,
hydro, renewable, storage) and sum them later into complete constraints
or cost functions.

All functions operate safely: they first verify the presence of required
model components (e.g., sets, variables, parameters) before contributing
expressions. If components are missing, the expressions are skipped
silently, enabling flexible model composition.

### Intended Use

- To support modular construction of the objective function, especially
  when not all energy sources are known in advance.
- To build power balance equations at each time step by aggregating
  contributions from thermal and other sources.

### Examples

```pycon
>>> cost_terms = []
>>> add_thermal_cost_expression(model, cost_terms)
>>> model.TotalCost = Objective(expr=sum(cost_terms), sense=minimize)
```

```pycon
>>> balance_terms = []
>>> add_thermal_balance_expression(model, t=5, balance_terms)
>>> model.BalanceConstraint[5] = Constraint(expr=sum(balance_terms) == model.Demand[5])
```

### Notes

- All expressions returned are Pyomo symbolic expressions.
- This module assumes the model follows the naming convention:
  ‘thermal_p’, ‘thermal_u’, ‘thermal_y’, ‘thermal_SC’, etc.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.ThermalGenerator.ThermalEquations.add_thermal_balance_expression(m: ConcreteModel, t: Any, balance_array: List[Any]) → List[Any]

Append the thermal generation expression at a given time step t
to the balance equation expression list.

This is intended for use in constructing hybrid or modular power
balance constraints where multiple sources (thermal, hydro, solar, etc.)
contribute to the total injected power at each time step.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model containing the thermal variables.
  * **t** (*int*) – Time index for which the expression should be generated.
  * **balance_array** (*list* *of* *expressions*) – List of symbolic expressions to which the thermal component is appended.
* **Returns:**
  The updated list including the thermal power contribution at time t.
* **Return type:**
  list of expressions

### NaivePyDESSEM.ThermalGenerator.ThermalEquations.add_thermal_cost_expression(m: ConcreteModel, cost_array: List[Any]) → List[Any]

Append thermal generation cost terms to the total cost expression list,
if the required model components are present.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing thermal data.
  * **cost_array** (*list* *of* *expressions*) – List of symbolic expressions to be used in the objective function.
* **Returns:**
  The updated list including thermal cost terms if available.
* **Return type:**
  list of expressions

## NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Model Builder

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides a high-level builder function for thermal UC models.
It orchestrates the composition of Pyomo model objects by combining:

- Sets and parameters (*thermal_components.thermal_add_sets_and_params*)
- Variables (*thermal_components.thermal_add_variables_uc*)
- Constraint families (*thermal_constraints*)
- Objective functions (*thermal_objectives*)
- Optional features:
  : * Reserve provision and requirement constraints
    * Emissions/fuel caps
    * Piecewise-linear (PWL) variable cost representation

### Builder Function

*build_thermal_uc(data, objective, include_reserve, include_objective)*

Parameters:

- data            : ThermalData object with horizon, demand, and unit info
- objective       : “miqp” (quadratic) or “pwl” (piecewise linear)
- include_reserve : bool, add reserve variables/constraints if True
- include_objective : bool, add objective function

Returns:

- A fully assembled Pyomo ConcreteModel ready to be solved by MILP/MIQP solvers
  (e.g., Gurobi, CPLEX, SCIP) or MINLP solvers (via MindtPy with glpk/Ipopt).

### Usage

This is the main entry point to generate UC test cases from ThermalData
instances. It ensures consistency across modules and allows easy switching
between formulations.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_problem(m: ConcreteModel, data: [ThermalData](#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData), objective: str = 'miqp', include_reserve: bool = False, include_objective: bool = False) → ConcreteModel

Assemble a thermal unit-commitment (UC) problem in Pyomo.

This builder configures a thermal UC optimization model by attaching sets,
parameters, decision variables, and standard operational constraints. It
supports both MIQP (quadratic cost) and PWL (piecewise linear cost)
formulations, with optional reserve requirements and objective definition.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which the thermal UC problem will be added.
  * **data** ([*ThermalData*](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)) – Input data structure containing unit characteristics, cost parameters,
    horizon length, demand, reserve requirements, and initial conditions.
  * **objective** (*str* *,* *optional*) – Cost modeling approach. Options:
    - “miqp” : quadratic production cost (default),
    - “pwl”  : piecewise linear production cost.
  * **include_reserve** (*bool* *,* *optional*) – If True, include spinning reserve variables and constraints
    (default False).
  * **include_objective** (*bool* *,* *optional*) – If True, attach the cost-minimization objective function
    appropriate for the chosen cost type (default False).
* **Returns:**
  The updated model with thermal UC constraints and, if enabled,
  the objective function.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- Core constraints include: balance, capacity, startup/shutdown logic,
  ramping, and minimum up/down times.
- When include_reserve=True, a reserve requirement constraint is added.
- When objective=”pwl” and include_objective=True, piecewise cost
  variables and constraints are attached along with the linear objective.
- When objective=”miqp” and include_objective=True, a quadratic
  cost objective is set.
- This routine assumes that *thermal_add_sets_and_params* and
  *thermal_add_variables_uc* are available and correctly configured.

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> m = add_thermal_problem(m, data, objective="miqp",
...                         include_reserve=True,
...                         include_objective=True)
>>> type(m)
<class 'pyomo.core.base.PyomoModel.ConcreteModel'>
```

### NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder.build_thermal_uc(data: [ThermalData](#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData), objective: str = 'miqp', include_reserve: bool = False, include_objective: bool = True) → ConcreteModel

Builds a modular thermal Unit Commitment (UC) Pyomo model.

This function integrates all sets, parameters, variables,
constraints, and objectives required for the thermal UC problem.
The model may be constructed with either a quadratic cost
function (MIQP) or a piecewise linear cost approximation (PWL).
Optional constraints for spinning reserve and global emissions
caps are also supported.

* **Parameters:**
  * **data** (*object*) – 

    Data container providing unit and system information.
    Must include:
    - demand profile
    - unit technical parameters (min/max power, ramps,
      minimum up/down times, costs, etc.)
  * **objective** ( *{"miqp"* *,*  *"pwl"}* *,* *optional*) – 

    Type of objective function to use:
    - ”miqp”: quadratic cost coefficients (a, b, c).
    - ”pwl”
      : Default is “miqp”.
  * **include_reserve** (*bool* *,* *optional*) – Whether to include spinning reserve variables and
    reserve requirement constraints (default False).
* **Returns:**
  A fully constructed Pyomo model ready for solving
  with a MILP/MIQP solver.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> from pyomo.opt import SolverFactory
>>> from NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder import build_thermal_uc
>>> model = build_thermal_uc(
...     data,
...     objective="pwl",
...     include_reserve=True,
...     include_emissions=True
... )
>>> opt = SolverFactory("gurobi")
>>> results = opt.solve(model)
>>> print(results.solver.termination_condition)
optimal
```

### Notes

- Reserve constraints require that reserve variables r[g, t]
  are declared during variable creation.
- The piecewise linear objective uses SOS2 variables or
  McCormick envelopes for convexification.

## NaivePyDESSEM.ThermalGenerator.ThermalObjectives module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Objectives

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Objective functions for thermal unit-commitment (UC) models in Pyomo.
Two major formulations are supported:

1. Mixed-Integer Quadratic Programming (MIQP)
   Cost structure per unit and period:
   > a \* u + b \* p + c \* p^2 + SC \* y + Cdef \* D

   capturing fixed commitment cost, linear/quadratic variable cost,
   hot start-up cost, and deficit penalty.
2. Mixed-Integer Linear Programming (MILP) with Piecewise Linear (PWL) cost
   Variable cost represented by linear segments (Piecewise/SOS2).
   Objective includes:
   > a \* u  +  Cvar[g,t]  +  SC \* y  +  Cdef \* D

### Usage

- Call *set_objective_thermo_miqp(m)* for the quadratic-cost UC model.
- Call *set_objective_thermo_pwl(m)* for the piecewise-linear-cost UC model.
  Both functions attach a Pyomo *Objective* set for minimization.

### Notes

- Ensure unit consistency for costs (e.g., $/h vs $/MWh) and for power/energy.
- The functions assume that all referenced sets, variables and parameters
  have been previously added to the model.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.ThermalGenerator.ThermalObjectives.set_objective_thermo_miqp(m)

Define a mixed-integer quadratic programming (MIQP) objective.

Minimizes the total operating cost over the planning horizon, composed of:
- Quadratic variable generation cost: *a \* u + b \* p + c \* p^2*
- Start-up cost: *SC \* y*
- Deficit penalty: *Cdef \* D*

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – 

  Pyomo model with:
  - Sets: *m.TG* (thermal units), *m.T* (time periods)
  - Variables:
    : *m.thermal_p[g,t]* (MW), *m.thermal_u[g,t]* (binary),
      *m.thermal_y[g,t]* (binary), *m.D[t]* (MW)
  - Parameters:
    : *m.thermal_a[g]*, *m.thermal_b[g]*, *m.thermal_c[g]* (cost coeffs),
      *m.thermal_SC[g]* (start-up cost), *m.Cdef* (deficit cost)
* **Returns:**
  The same model with quadratic objective *m.OBJ* set to minimize total cost.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> # Assuming sets, variables, and parameters are already defined:
>>> _ = set_objective_thermo_miqp(m)
>>> m.OBJ.pprint()  
```

### Notes

- Prefer MIQP when accurate heat-rate curves are important and the solver
  handles convex quadratic objectives efficiently.
- Ensure convexity: typically *m.thermal_c[g] >= 0* for all *g*.
- Check scaling of cost coefficients to avoid numerical issues.

### NaivePyDESSEM.ThermalGenerator.ThermalObjectives.set_objective_thermo_pwl(m)

Define a piecewise linear (PWL) objective (MILP).

Minimizes the total operating cost over the planning horizon, composed of:

- Piecewise linear variable generation cost: *Cvar[g,t]*
- Fixed commitment cost: *a \* u*
- Start-up cost: *SC \* y*
- Deficit penalty: *Cdef \* D*

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – 

  Pyomo model with:
  - Sets: *m.TG* (thermal units), *m.T* (time periods)
  - Variables:
    : *m.thermal_Cvar[g,t]* (PWL cost), *m.thermal_u[g,t]* (binary),
      *m.thermal_y[g,t]* (binary), *m.D[t]* (MW)
  - Parameters:
    : *m.thermal_a[g]* (fixed cost), *m.thermal_SC[g]* (start-up cost),
      *m.Cdef* (deficit cost)
* **Returns:**
  The same model with linear objective *m.OBJ* set to minimize total cost.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> # Assuming PWL cost variables/constraints are defined:
>>> _ = set_objective_thermo_pwl(m)
>>> m.OBJ.pprint()  
```

### Notes

- Prefer PWL when MILP solvers perform better on large instances or when
  granular control of approximation accuracy is desired.
- Ensure the PWL construction (breakpoints/SOS2) matches unit operating ranges.
- Keep cost units consistent across all terms to maintain a well-scaled model.

## NaivePyDESSEM.ThermalGenerator.ThermalPieceWise module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Piecewise Linear Cost Module

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module defines utilities to construct piecewise-linear (PWL) cost
functions for thermal unit commitment (UC) models in Pyomo. It enables
the replacement of quadratic variable costs with linear approximations
compatible with MILP solvers.

### Features

- Builds Cvar[g,t] = f(p[g,t]) using Pyomo’s *Piecewise* component.
- Supports convex-combination (SOS2) representation.
- Enforces equality Cvar[g,t] = C_PWL(p[g,t]).
- Allows unit-specific breakpoints (pw_breaks[g]) and cost values
  (pw_costs[g]) for accurate curve fitting.

### Requirements

- A Pyomo model with:
  > * m.p[g,t]   : generation variable (MW)
  > * m.Cvar[g,t]: PWL cost variable (R$/h)
  > * m.pw_breaks[g], m.pw_costs[g] defined as lists of (x, f(x))
  >   points per unit g.

### Usage

Call *thermal_add_piecewise_cost(m)* after sets, parameters, and variables have
been added. For each unit g ∈ G and time t ∈ T, a PWL relation is built.

### Example

pw_breaks = [0, 150, 300, 455]
pw_costs  = [0, 2500, 6000, 10000]

Cvar[g,t] is constrained such that:

> Cvar[g,t] = Piecewise(p[g,t]; pw_breaks, pw_costs)

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.ThermalGenerator.ThermalPieceWise.thermal_add_piecewise_cost(m)

Add piecewise-linear generation cost expression Cvar[g,t] = C_PWL_g(p[g,t]).

For each thermal unit g and time period t, this function constructs a
piecewise-linear (PWL) cost expression using predefined breakpoints
and cost values. The implementation uses the ‘CC’ (convex combination)
method with equality enforcement.

### Requirements

m
: The Pyomo model must include:
  <br/>
  > - m.Cvar[g, t] : cost variable
  > - m.p[g, t] : power generation variable
  > - m.thermal_pw_breaks[g] : list of breakpoints (strictly increasing)
  > - m.thermal_pw_costs[g] : list of corresponding cost values

* **raises ValueError:**
  If a unit g has undefined or mismatched pw_breaks and pw_costs.
* **returns:**
  The modified model with one Piecewise component per unit.
* **rtype:**
  ConcreteModel

### Notes

- Each unit g must define a consistent pair of lists: pw_breaks[g] and
  pw_costs[g], with identical length.
- Internally, the function uses pyomo.environ.Piecewise with:
  : - Index set: model.T
    - Representation: ‘CC’ (convex combination with SOS2 variables)
    - Constraint type: ‘EQ’ (enforces equality between cost and function value)
- Each unit g receives a component named ‘pw_{g}’.

### Examples

```pycon
>>> model = thermal_add_piecewise_cost(model)
>>> model.pw_G1.pprint()
Piecewise component for thermal unit G1 over time.
```

## NaivePyDESSEM.ThermalGenerator.ThermalVars module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Sets, Parameters and Variables

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides the Pyomo set/parameter declarations and variable
definitions for thermal unit commitment (UC) models. It is intended to
be combined with constraint and objective builder modules.

### Features

- Time horizon (T) and thermal unit set (G)
- Demand profile d[t] and deficit penalty Cdef
- Unit-level parameters:
  : * Pmin, Pmax  : capacity bounds
    * RU, RD      : ramp-up / ramp-down limits
    * a, b, c     : cost coefficients for MIQP (a \* u + b \* p + c \* p²)
    * SC          : start-up (hot) cost
    * t_up, t_dn  : minimum up/down times
    * u0, p0      : initial commitment state and output
- Optional system-wide parameters:
  : * Rreq[t]     : spinning reserve requirement
    * gamma[g]    : emissions factor
    * CO2Cap      : global emission/fuel cap
- Optional piecewise data:
  : * pw_breaks[g], pw_costs[g] : piecewise linear cost curve points

### Variables

- p[g,t] : generation (MW)
- D[t]   : deficit (MW)
- r[g,t] : reserve (MW, optional)
- Cvar[g,t] : variable cost in PWL formulations (optional)
- u[g,t] : on/off state (binary)
- y[g,t] : start-up indicator (binary)
- w[g,t] : shut-down indicator (binary)

### Usage

Call *thermal_add_sets_and_params(m, data)* to populate a Pyomo model with
sets and parameters from a ThermalData object.

Call *thermal_add_variables_uc(m, include_reserve=True/False, use_pwl=True/False)*
to attach decision variables for UC formulations (MIQP or MILP-PWL).

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.ThermalGenerator.ThermalVars.thermal_add_sets_and_params(m: ConcreteModel, data: [ThermalData](#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData)) → ConcreteModel

Initializes sets and parameters for the thermal Unit Commitment (UC) model.

This function maps unit-level data (technical parameters, costs,
initial conditions, optional reserve and emissions information,
and piecewise cost segments) into Pyomo sets and parameters.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to be enriched with sets and parameters.
  * **data** ([*ThermalData*](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)) – 

    Data container with attributes:
    - horizon : int
      > Number of time periods.
    - demand : dict
      > Demand profile indexed by time.
    - Cdef : float
      > Cost of deficit ($/MWh).
    - units : dict
      > Dictionary keyed by unit id, each with attributes
      > Pmin, Pmax, RU, RD, a, b, c, SC, t_up, t_down, u0, p0,
      > gamma (optional), pw_breaks (optional), pw_costs (optional).
    - Rreq : dict, optional
      > Reserve requirement per period.
* **Returns:**
  The updated model with sets **m.T, m.TG** and all unit/system parameters.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> m = thermal_add_sets_and_params(m, data)
>>> list(m.TG)
['UT1', 'UT2', 'UT3']
>>> m.d[1]
500.0
```

### NaivePyDESSEM.ThermalGenerator.ThermalVars.thermal_add_variables_uc(m, include_reserve: bool = False, use_pwl: bool = False)

Declares decision variables for the thermal Unit Commitment (UC) model.

Variables include continuous generation and deficit levels,
binary commitment/start/stop indicators, and optionally,
reserve and piecewise cost variables.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Model where variables will be added.
  * **include_reserve** (*bool* *,* *optional*) – If True, reserve variables **m.r[g, t]** are created (default False).
  * **use_pwl** (*bool* *,* *optional*) – If True, piecewise linear cost variables **m.Cvar[g, t]**
    are created (default False).
* **Returns:**
  The updated model with added decision variables:
  - Continuous:
  > * **m.p[g, t]** : generation [MW].
  > * **m.D[t]** : deficit [MW].
  > * **m.r[g, t]** : reserve [MW], optional.
  > * **m.Cvar[g, t]** : piecewise cost variable, optional.
  - Binary:
    * **m.u[g, t]** : commitment (on/off).
    * **m.y[g, t]** : startup indicator.
    * **m.w[g, t]** : shutdown indicator.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> m = thermal_add_sets_and_params(m, data)
>>> m = thermal_add_variables_uc(m, include_reserve=True, use_pwl=True)
>>> m.p['UT1', 1].pprint()
Variable p[UT1,1]
Domain: NonNegativeReals
```

### Notes

**Reserve modeling (\*\*include_reserve=True**)\*\*

- **Advantages**: Captures spinning reserve obligations; ensures reliability
  under contingencies; critical for adequacy/security studies.
- **Trade-offs**: Increases model size with additional variables
  **m.r[g, t]** and constraints; may slow down MILP/MIQP solution.
- **Guidance**: Use if reserve margins are central to the study; omit in
  purely economic dispatch tests for simplicity.

**Piecewise costs (\*\*use_pwl=True**)\*\*4

- **Advantages**: Converts quadratic costs to MILP form; exploits strong
  LP relaxations; often faster and more scalable on large systems.
- **Trade-offs**: Approximation error unless sufficient breakpoints are
  used; adds SOS2 or convex-combination variables, increasing model size.
- **Guidance**: Use when quadratic costs cannot be handled efficiently
  by the chosen solver, or when MILP-only solvers are required.
