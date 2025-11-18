# NaivePyDECOMP.ThermalGenerator package

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

## NaivePyDECOMP.ThermalGenerator.ThermalConstraints module

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
   - Upper bound: thermal_p[g,t] <= thermal_Pmax[g] \* thermal_u[g,t]

### Usage

Combine these builders with:

- set/parameter/variable definitions for thermal UC, and
- an appropriate objective (quadratic or piecewise linear).

By composing the blocks, one can construct MIQP (quadratic costs) or
MILP (piecewise linear costs) UC formulations, optionally with reserve constraints.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.ThermalGenerator.ThermalConstraints.thermal_add_balance_constraint(m)

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

### NaivePyDECOMP.ThermalGenerator.ThermalConstraints.thermal_add_capacity_constraint(m, include_reserve: bool = False)

Add generation capacity limits for all units and periods.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model containing thermal parameters and variables
* **Returns:**
  The updated model with constraint blocks
  m.thermal_cap_lower_constraint and
  m.thermal_cap_upper_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> _ = thermal_add_capacity_constraint(m)
```

## NaivePyDECOMP.ThermalGenerator.ThermalDataTypes module

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

### *class* NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData(horizon: int, demand: Dict[int, float], units: Dict[str, [ThermalUnit](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit)], Cdef: float = 1000.0)

Bases: `object`

System-wide data container for thermal unit commitment problems.

* **Parameters:**
  * **horizon** (*int*) – Number of time periods in the planning horizon.
  * **demand** (*Dict* *[**int* *,* *float* *]*) – Mapping of each period `t` to system demand (MW).
  * **units** (*Dict* *[**str* *,* [*ThermalUnit*](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit) *]*) – Dictionary mapping unit identifiers to their `ThermalUnit` objects.
  * **Cdef** (*float* *,* *optional*) – Deficit penalty cost ($/MWh), default is 1000.0.

#### Cdef *: float* *= 1000.0*

#### demand *: Dict[int, float]*

#### horizon *: int*

#### units *: Dict[str, [ThermalUnit](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit)]*

### *class* NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit(name: str, Gmin: float, Gmax: float, Cost: float)

Bases: `object`

Data container for a thermal generating unit with unit commitment attributes.

* **Parameters:**
  * **name** (*str*) – Unique identifier of the thermal unit.
  * **Gmin** (*float*) – Minimum operating power output (MWh).
  * **Gmax** (*float*) – Maximum operating power output (MWh).
  * **Cost** (*float*) – Operation cost per MWh

#### Cost *: float*

#### Gmax *: float*

#### Gmin *: float*

#### name *: str*

## NaivePyDECOMP.ThermalGenerator.ThermalEquations module

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
  ‘thermal_p’, ‘thermal_Cost’, etc.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.ThermalGenerator.ThermalEquations.add_thermal_balance_expression(m: ConcreteModel, t: Any, balance_array: List[Any]) → List[Any]

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

### NaivePyDECOMP.ThermalGenerator.ThermalEquations.add_thermal_cost_expression(m: ConcreteModel, cost_array: List[Any]) → List[Any]

Append thermal generation cost terms to the total cost expression list,
if the required model components are present.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing thermal data.
  * **cost_array** (*list* *of* *expressions*) – List of symbolic expressions to be used in the objective function.
* **Returns:**
  The updated list including thermal cost terms if available.
* **Return type:**
  list of expressions

## NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder module

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

### NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_problem(m: ConcreteModel, data: [ThermalData](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData), include_objective: bool = False) → ConcreteModel

Assemble a thermal unit-commitment (UC) problem in Pyomo.

This builder configures a thermal UC optimization model by attaching sets,
parameters, decision variables, and standard operational constraints. It
supports both MIQP (quadratic cost) and PWL (piecewise linear cost)
formulations, with optional reserve requirements and objective definition.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which the thermal UC problem will be added.
  * **data** ([*ThermalData*](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)) – Input data structure containing unit characteristics, cost parameters,
    horizon length, demand, reserve requirements, and initial conditions.
  * **include_objective** (*bool* *,* *optional*) – If True, attach the cost-minimization objective function
    appropriate for the chosen cost type (default False).
* **Returns:**
  The updated model with thermal UC constraints and, if enabled,
  the objective function.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> m = add_thermal_problem(m, data, objective="miqp",
...                         include_objective=True)
>>> type(m)
<class 'pyomo.core.base.PyomoModel.ConcreteModel'>
```

### NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_subproblem(m: ConcreteModel, data: [ThermalData](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData), stage: int) → ConcreteModel

Assemble a thermal unit-commitment (UC) subproblem in Pyomo.

This builder configures a thermal UC optimization model by attaching sets,
parameters, decision variables, and standard operational constraints. It
supports both MIQP (quadratic cost) and PWL (piecewise linear cost)
formulations, with optional reserve requirements and objective definition.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which the thermal UC problem will be added.
  * **data** ([*ThermalData*](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)) – Input data structure containing unit characteristics, cost parameters,
    horizon length, demand, reserve requirements, and initial conditions.
  * **stage** (*int*) – the stage subproblem, informed for data copying
* **Returns:**
  The updated model with thermal UC constraints and, if enabled,
  the objective function.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> m = add_thermal_problem(m, data, objective="miqp",
...                         include_objective=True)
>>> type(m)
<class 'pyomo.core.base.PyomoModel.ConcreteModel'>
```

### NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.build_thermal_uc(data: [ThermalData](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData), include_objective: bool = True) → ConcreteModel

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
  * **include_objective** (*optional* *,* *bool*) – hj
* **Returns:**
  A fully constructed Pyomo model ready for solving
  with a MILP/MIQP solver.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> from pyomo.opt import SolverFactory
>>> from NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder import build_thermal_uc
>>> model = build_thermal_uc(
...     data
... )
>>> opt = SolverFactory("gurobi")
>>> results = opt.solve(model)
>>> print(results.solver.termination_condition)
optimal
```

### NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.thermo_update_model(m: ConcreteModel, data: Dict) → ConcreteModel

## NaivePyDECOMP.ThermalGenerator.ThermalObjectives module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Objectives

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Objective functions for thermal unit-commitment (UC) models in Pyomo.

### Usage

- Call *set_objective_thermo_miqp(m)* for the quadratic-cost UC model.
  Both functions attach a Pyomo *Objective* set for minimization.

### Notes

- Ensure unit consistency for costs (e.g., $/h vs $/MWh) and for power/energy.
- The functions assume that all referenced sets, variables and parameters
  have been previously added to the model.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.ThermalGenerator.ThermalObjectives.set_objective_thermo(m)

Define the medium-term thermal objective.

Minimizes the total operating cost over the planning horizon, composed of:
- Linear thermal generation cost: Cg[g] \* G[g,t]
- Deficit penalty: Cdef \* Def[t]

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – 

  Pyomo model with:
  - Sets: m.TG (thermal units), m.T (stages)
  - Variables:
    : m.thermal_G[g,t] (MW), m.Def[t] (MW)
  - Parameters:
    : m.thermal_C[g] (US$/MWh), m.Cdef (deficit penalty)
* **Returns:**
  Model with objective m.OBJ set to minimize total cost.
* **Return type:**
  pyomo.environ.ConcreteModel

### Examples

```pycon
>>> _ = set_objective_decomp(m)
>>> m.OBJ.pprint()
```

## NaivePyDECOMP.ThermalGenerator.ThermalVars module

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

### NaivePyDECOMP.ThermalGenerator.ThermalVars.thermal_add_sets_and_params(m: ConcreteModel, data: [ThermalData](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)) → ConcreteModel

Initializes sets and parameters for the thermal Unit Commitment (UC) model.

This function maps unit-level data (technical parameters, costs,
initial conditions, optional reserve and emissions information,
and piecewise cost segments) into Pyomo sets and parameters.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to be enriched with sets and parameters.
  * **data** ([*ThermalData*](#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)) – 

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

### NaivePyDECOMP.ThermalGenerator.ThermalVars.thermal_add_variables_uc(m)

Declares decision variables for the thermal Unit Commitment (UC) model.

Variables include continuous generation and deficit levels,
binary commitment/start/stop indicators, and optionally,
reserve and piecewise cost variables.

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model where variables will be added.
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
