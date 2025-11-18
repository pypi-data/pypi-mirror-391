# NaivePyDESSEM.HydraulicGenerator package

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

ConstantProductivityFPH
: Simple FPH based on constant productivity.

SimplifiedConstantProductivityFPH
: Didactic constant productivity model (simplified).

PEFPH
: Semi-exact FPH with net head representation.

ExactFPH
: Full DESSEM-style FPH with head- and flow-dependent terms.

### Notes

- Multiple FPH modes are supported (constant, simplified, specific, exact).
- Reservoir mass balance constraints ensure intertemporal consistency.
- Designed for interoperability with Thermal, Renewable, and Storage packages
  in hybrid models.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

## Submodules

## NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Constant Productivity FPH Function

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides a simplified hydroelectric production function (FPH)
for use in short-term operation and dispatch models. The generation is
assumed to be proportional to the turbine discharge, scaled by a constant
productivity factor.

The formulation is expressed as:

> FPH(Q) = zeta \* P \* Q

where:
- Q     : turbine discharge (m^3/s)
- P     : global productivity coefficient (dimensionless)
- zeta  : unit conversion constant (e.g., 9.81 / 1000 to convert to MW)

This approximation is particularly useful in didactic or preliminary
planning contexts where detailed head-dependent modeling is unnecessary.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH.constant_productivity_fph(P: float, zeta: float) → Callable

Factory for a constant-productivity hydroelectric generation function.

Constructs a callable object representing the simplified FPH
relationship:

> FPH(Q) = zeta \* P \* Q
* **Parameters:**
  * **P** (*float*) – Constant productivity coefficient (dimensionless).
  * **zeta** (*float*) – Conversion constant (e.g., 9.81 / 1000 to scale to MW).
* **Returns:**
  A function of the form `f(Q) = zeta * P * Q`, which accepts
  the turbine discharge (Q) in m^3/s and returns the generation
  in MW.
* **Return type:**
  Callable

### Examples

```pycon
>>> f = constant_productivity_fph(0.9, 9.81 / 1000)
>>> f(100)
0.8829
```

## NaivePyDESSEM.HydraulicGenerator.ExactFPH module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Hydropower Dispatch with Exact FPH Model

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Implements an exact-form hydropower production function (FPH) aligned with
the DESSEM methodology. The model uses polynomial (or polynomial-like)
approximations for four building blocks:

- Specific productivity,       rho(Q, h_liq)
- Upstream water head,         h_mont(V)
- Downstream water head,       h_jus(Q + S)
- Hydraulic losses,            h_perdas(Q)

The electrical power is computed as

> FPH(Q, V, S) = rho(Q, h_liq) \* Q \* h_liq,

where the net head is

> h_liq = h_mont(V) - h_jus(Q + S) - h_perdas(Q).

Variables and units:
- Q : turbine discharge (m^3/s)
- V : reservoir volume (hm^3)
- S : spill discharge (m^3/s)
- FPH : electrical power (MW), assuming consistent scaling inside rho

### Notes

- The exact physical fidelity depends on the quality and calibration of the
  polynomials/surrogates provided to the factories.
- Unit consistency is essential: typical conversions use zeta = 9.81/1000
  within rho (or within head-to-power mapping) to yield MW.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.HydraulicGenerator.ExactFPH.fph_factory(rho_func: Callable, hmont_func: Callable, hjus_func: Callable, hperdas_func: Callable) → Callable

Compose the exact hydropower generation function (FPH) from components.

The assembled function computes

> FPH(Q, V, S) = rho(Q, h_liq) \* Q \* h_liq,

with net head

> h_liq = h_mont(V) - h_jus(Q + S) - h_perdas(Q).
* **Parameters:**
  * **rho_func** (*Callable*) – Specific productivity surface `rho(Q, h_liq)`; e.g., from
    [`rho_colina_factory()`](#NaivePyDESSEM.HydraulicGenerator.ExactFPH.rho_colina_factory).
  * **hmont_func** (*Callable*) – Upstream head function `h_mont(V)` mapping reservoir volume to head.
  * **hjus_func** (*Callable*) – Downstream head function `h_jus(Q + S)` mapping total discharge to
    tailwater level.
  * **hperdas_func** (*Callable*) – Hydraulic-loss function `h_perdas(Q)` mapping discharge to losses.
* **Returns:**
  Function `FPH(Q, V, S)` returning generation in MW (given consistent
  units and scaling inside the components).
* **Return type:**
  Callable

### Examples

```pycon
>>> rho = rho_colina_factory([0.88, 0.01, 0.002, 1e-4, -5e-5, -2e-5])
>>> h_mont   = polynomial_factory([400])                  # constant upstream head
>>> h_jus    = polynomial_factory([300])                  # constant downstream head
>>> h_perdas = polynomial_factory([0.0, 0.0, 1e-5])       # losses ~ 1e-5 * Q^2
>>> fph = fph_factory(rho, h_mont, h_jus, h_perdas)
>>> _ = fph(Q=100, V=1000, S=0)  
```

### Notes

- Ensure that `rho_func` and the head functions use consistent units
  so that the product yields MW.
- The returned function is suitable for use inside Pyomo expressions.

### NaivePyDESSEM.HydraulicGenerator.ExactFPH.polynomial_factory(coefs: List[float]) → Callable

Create a univariate polynomial function from coefficients.

The resulting polynomial is

> f(x) = c_0 + c_1 x + c_2 x² + … + c_n xⁿ,

with coefficients given in increasing order of degree.

* **Parameters:**
  **coefs** (*List* *[**float* *]*) – Polynomial coefficients [c_0, c_1, …, c_n] in ascending degree.
* **Returns:**
  Function `f(x)` that evaluates the polynomial at a scalar `x`.
* **Return type:**
  Callable

### Examples

```pycon
>>> f = polynomial_factory([2, 3, 0.5])  # 2 + 3x + 0.5 x^2
>>> f(2)
10.0
>>> f(0)
2.0
```

### NaivePyDESSEM.HydraulicGenerator.ExactFPH.rho_colina_factory(coefs: List[float], zeta: float = 0.009810000000000001) → Callable

Build a colina-type specific productivity surface rho(Q, h_liq).

The parametric surface follows

> rho(Q, h_liq) = zeta \* (rho0
> : + rho1 \* Q
>   + rho2 \* h_liq
>   + rho3 \* Q \* h_liq
>   + rho4 \* Q^2
>   + rho5 \* h_liq^2)
* **Parameters:**
  * **coefs** (*List* *[**float* *]*) – Six coefficients [rho0, rho1, rho2, rho3, rho4, rho5] for the bilinear/
    quadratic surface fitted to efficiency/productivity data.
  * **zeta** (*float* *,* *optional*) – Unit conversion/scaling constant (default 9.81/1000), typically chosen
    so that the final FPH is expressed in MW.
* **Returns:**
  Function `rho(Q, h_liq)` returning specific productivity consistent
  with the downstream power computation.
* **Return type:**
  Callable

### Examples

```pycon
>>> rho = rho_colina_factory([0.88, 0.01, 0.002, 1e-4, -5e-5, -2e-5])
>>> rho(Q=300, hliq=120)  
...
```

### Notes

- Raises `ValueError` if the coefficient list length is not 6.

## NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints module

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
- add_hydro_volume_meta_constraint(m)
- add_hydro_volume_max_constraint(m)
- add_hydro_volume_mim_constraint(m)
- add_hydro_balance_constraint(m)

#### Model Requirements

Sets
: m.HG : hydropower units
  m.T  : time periods

Variables
: m.hydro_V[h,t] : storage volume (hm^3)
  m.hydro_Q[h,t] : turbined discharge (m^3/s)
  m.hydro_S[h,t] : spill discharge (m^3/s)
  m.hydro_G[h,t] : hydropower generation (MW)
  m.D[t]         : deficit (MW), if used

Parameters
: m.hydro_zeta_vol : flow-to-volume converter per period (e.g., 3600/1e6)
  m.hydro_Vini[h]  : initial storage (hm^3)
  m.hydro_Vmeta[h] : terminal storage target (hm^3)
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

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_balance_constraint(m)

Add hydropower-only system balance constraints.

For each time period t:
: sum_h m.hydro_G[h,t] + m.D[t] == m.d[t].

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Model with variables m.hydro_G[h,t], m.D[t] and parameter m.d[t],
  and sets m.HG, m.T.
* **Returns:**
  Constraint block m.hydro_balance_constraint enforcing balance per period.
* **Return type:**
  pyomo.core.base.constraint.Constraint

### Notes

This is intended for pure hydropower settings. If thermal generation is present,
a combined (hydro + thermal) balance should be used instead.

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_generation_constraint(m)

Add hydropower generation constraints using plant-specific FPH callables.

For each hydropower unit and time period, this constraint enforces

m.hydro_G[h, t] == m.hydro_FPH[h](m.hydro_Q[h, t], m.hydro_V[h, t], m.hydro_S[h, t])

The callable m.hydro_FPH[h] may represent:

- Constant productivity
- Specific productivity with fixed head
- Exact head-dependent model (possibly nonlinear)
- Simplified approximations

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Pyomo model containing hydraulic variables and callables
* **Returns:**
  The updated model with constraint block m.hydro_generation_constraint.
* **Return type:**
  pyomo.core.base.PyomoModel.ConcreteModel

### Notes

Ensure unit consistency across the callable and model variables so that
the right-hand side yields MW.

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_qmax_constraint(m)

Add maximum turbined flow constraint.

Ensures that, for each hydro unit and period,
m.hydro_Q[h,t] <= m.hydro_Qmax[h].

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with variables/parameters:
  m.hydro_Q[h,t], m.hydro_Qmax[h]; sets m.HG, m.T.
* **Returns:**
  Model with constraint block m.hydro_qmax_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_qmin_constraint(m)

Add minimum turbined flow constraint.

Ensures that, for each hydro unit and period,
m.hydro_Q[h,t] >= m.hydro_Qmin[h].

* **Parameters:**
  **m** (*pyomo.environ.ConcreteModel*) – Model with variables/parameters:
  m.hydro_Q[h,t], m.hydro_Qmin[h]; sets m.HG, m.T.
* **Returns:**
  Model with constraint block m.hydro_qmin_constraint.
* **Return type:**
  pyomo.environ.ConcreteModel

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_continuity_constraint(m)

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
  [`hydro_total_inflow_expr()`](#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.hydro_total_inflow_expr).
* **Returns:**
  Constraint block m.hydro_volume_balance_constraint added to the model.
* **Return type:**
  pyomo.core.expr.relational.EqualityExpression

### Notes

m.hydro_zeta_vol converts flow (m^3/s) into volume (hm^3) over one period
(e.g., 3600 / 1e6 for hourly steps).

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_max_constraint(m)

Add maximum storage constraints.

For all (h, t):
: m.hydro_V[h,t] <= m.hydro_Vmax[h].

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Model with variable m.hydro_V and parameter m.hydro_Vmax.
* **Returns:**
  Constraint block m.hydro_volume_maximal_constraint added to the model.
* **Return type:**
  pyomo.core.expr.relational.InequalityExpression

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_meta_constraint(m)

Add terminal storage target constraints.

Enforces a minimum end-of-horizon storage for each plant:
: m.hydro_V[h, m.horizon] >= m.hydro_Vmeta[h].

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Model with variable m.hydro_V, parameter m.hydro_Vmeta,
  and an integer m.horizon indicating the last period.
* **Returns:**
  Constraint block m.hydro_volume_meta_constraint added to the model.
* **Return type:**
  pyomo.core.expr.relational.InequalityExpression

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_mim_constraint(m)

Add minimum storage constraints.

For all (h, t):
: m.hydro_V[h,t] >= m.hydro_Vmin[h].

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Model with variable m.hydro_V and parameter m.hydro_Vmin.
* **Returns:**
  Constraint block m.hydro_volume_minimal_constraint added to the model.
* **Return type:**
  pyomo.core.expr.relational.InequalityExpression

### Notes

The function name includes mim for historical reasons; the constraint
enforces a **minimum** volume at each time period.

### NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.hydro_total_inflow_expr(m, h, t)

Compute instantaneous total inflow without travel time.

The returned expression equals the sum of:

1. natural inflow to plant h at period t, plus
2. releases (turbined flow + spill) from all immediate upstream plants
   during the **same** period t (no routing delay).

* **Parameters:**
  * **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Pyomo model providing variables m.hydro_Q, m.hydro_S and
    parameters/containers m.hydro_afluencia, m.hydro_upstreams,
    and the boolean flag m.hydro_compute_total_inflow[h].
  * **h** (*hashable*) – Plant identifier (element of m.HG).
  * **t** (*int*) – Time period (element of m.T). External arrays are 0-based,
    hence access via t-1.
* **Returns:**
  Pyomo expression for the total inflow to plant h at time t.
* **Return type:**
  pyomo.core.expr.numeric_expr.ExpressionBase

### Notes

This function assumes **no travel time** between cascaded plants. If
routing is relevant, replace this expression with a routed inflow model.

## NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes module

### Hydraulic System Data Classes for Reservoir Optimization

This module defines data classes for modeling structural and operational
characteristics of hydroelectric systems in short-term dispatch and
unit-commitment studies. The classes are designed to serve as a clean
interface between problem data and Pyomo-based optimization models.

#### Overview

Two classes are provided:

- `HydraulicUnit`: describes a single hydro plant, including storage bounds,
  turbined-flow limits, initial/terminal volumes, natural inflows, cascade
  topology, and optional coefficients for alternative FPH (hydropower
  production function) modes.
- `HydraulicData`: encapsulates system-wide information such as planning
  horizon, hourly demand, plant map, and conversion/penalty constants.

#### Conventions and Units

- Time is discretized in periods `t = 1, …, horizon` (integers).
- Discharges (Q, S) are in m^3/s.
- Storage volumes (V) are in hm^3.
- Demand is in MW.
- `zeta` typically equals 9.81/1000 to convert head \* flow to MW.
- `zeta_vol` converts flow (m^3/s) into volume (hm^3) over one period
  (e.g., 3600/1e6 for hourly steps).

### Notes

- Cascade routing: this data layer assumes **no travel time**. If routing
  delays are relevant, they should be handled in the modeling layer.
- The field `mode` is a selector for FPH modeling choices (e.g., constant,
  specific, exact, simplified). The interpretation belongs to the modeling
  code that consumes these data.
- Optional vectors (`a`, `b`, `rho`, `losses`) can parameterize
  alternative FPH formulations; their semantics depend on the chosen mode.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### *class* NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData(horizon: int, demand: Dict[int, float], units: Dict[str, [HydraulicUnit](#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)], zeta: float = 0.009810000000000001, zeta_vol: float = 0.0036, Cdef: float = 1000.0)

Bases: `object`

System-wide hydropower data for planning and dispatch.

* **Parameters:**
  * **horizon** (*int*) – Number of time periods in the planning horizon.
  * **demand** (*Dict* *[**int* *,* *float* *]*) – Mapping from period `t` (1-based) to system demand (MW).
  * **units** (*Dict* *[**str* *,* [*HydraulicUnit*](#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit) *]*) – Map from plant name to its `HydraulicUnit` data structure.
  * **zeta** (*float* *,* *optional*) – Conversion constant for head–flow to power (typ. 9.81/1000). Default
    is `9.81/1000`; ensure consistency with the FPH used.
  * **zeta_vol** (*float* *,* *optional*) – Flow-to-volume conversion over one period (hm^3 per (m^3/s)).
    Default is `3600/1e6` for hourly steps.
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

#### units *: Dict[str, [HydraulicUnit](#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)]*

#### zeta *: float* *= 0.009810000000000001*

#### zeta_vol *: float* *= 0.0036*

### *class* NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit(name: str, Qmin: float, Qmax: float, Vmin: float, Vmax: float, Vmeta: float, Vini: float, afluencia: List[float], upstreams: List[str] | None = None, a: List[float] | None = None, b: List[float] | None = None, rho: List[float] | None = None, losses: List[float] | None = None, pe: float | None = None, p: float | None = None, mode: str = 'constant', compute_total_inflow: bool = True)

Bases: `object`

Hydropower plant data container.

* **Parameters:**
  * **name** (*str*) – Unique identifier of the hydro plant.
  * **Qmin** (*float*) – Minimum allowed turbined flow (m^3/s).
  * **Qmax** (*float*) – Maximum allowed turbined flow (m^3/s).
  * **Vmin** (*float*) – Minimum storage volume (hm^3).
  * **Vmax** (*float*) – Maximum storage volume (hm^3).
  * **Vmeta** (*float*) – Terminal target storage at the end of the horizon (hm^3).
  * **Vini** (*float*) – Initial storage volume at the beginning of the horizon (hm^3).
  * **afluencia** (*List* *[**float* *]*) – Natural inflow time series (m^3/s); external, 0-based list aligned
    with model periods (accessed as `afluencia[t-1]`).
  * **upstreams** (*List* *[**str* *]* *,* *optional*) – List of immediate upstream plant names that feed this unit.
    Defaults to `None` (treated as no upstreams).
  * **a** (*List* *[**float* *]* *,* *optional*) – Optional coefficient vector associated with an FPH/head submodel
    (semantics defined by the chosen `mode`).
  * **b** (*List* *[**float* *]* *,* *optional*) – Optional coefficient vector associated with an FPH/head submodel
    (semantics defined by the chosen `mode`).
  * **rho** (*List* *[**float* *]* *,* *optional*) – Optional weights/coefficients for specific productivity surfaces
    (e.g., colina-type fits), depending on the `mode`.
  * **losses** (*List* *[**float* *]* *,* *optional*) – Optional coefficients for hydraulic-loss approximations.
  * **pe** (*float* *,* *optional*) – Specific productivity coefficient (dimensionless multiplier used in
    simplified models).
  * **p** (*float* *,* *optional*) – Global productivity coefficient (used in constant/simplified models;
    unit interpretation depends on how head is handled in the FPH).
  * **mode** (*str* *,* *optional*) – Generation-mode selector. Valid options include
    {“constant”, “specific”, “exact”, “simplified”}.
    Default is “constant”.
  * **compute_total_inflow** (*bool* *,* *optional*) – If `True`, total inflow will include upstream releases in addition
    to exogenous natural inflow in expressions that support it.
    Default is `True`.

### Notes

- The presence and interpretation of the optional vectors (`a`, `b`,
  `rho`, `losses`) are **model-dependent** and only take effect if
  the consuming code uses them for the selected `mode`.

#### Qmax *: float*

#### Qmin *: float*

#### Vini *: float*

#### Vmax *: float*

#### Vmeta *: float*

#### Vmin *: float*

#### a *: List[float] | None* *= None*

#### afluencia *: List[float]*

#### b *: List[float] | None* *= None*

#### compute_total_inflow *: bool* *= True*

#### losses *: List[float] | None* *= None*

#### mode *: str* *= 'constant'*

#### name *: str*

#### p *: float | None* *= None*

#### pe *: float | None* *= None*

#### rho *: List[float] | None* *= None*

#### upstreams *: List[str]* *= None*

## NaivePyDESSEM.HydraulicGenerator.HydraulicEquations module

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

### NaivePyDESSEM.HydraulicGenerator.HydraulicEquations.add_hydraulic_balance_expression(m: ConcreteModel, t: Any, balance_array: List[Any]) → List[Any]

Append hydroelectric generation terms at time t to the power balance expression list.

This function constructs a symbolic expression representing the total hydroelectric
power generation at a given time step t, summed over all hydro units defined
in the model. The resulting expression can be integrated into modular power
balance constraints.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing hydro generation variables.
  * **t** (*int*) – Time index at which the hydro contribution is evaluated.
  * **balance_array** (*list* *of* *expressions*) – List of symbolic expressions representing components of the power balance.
* **Returns:**
  The updated list including the hydro generation term at time t.
* **Return type:**
  list of expressions

### Notes

- The model is expected to contain:
  ‘HG’ (set of hydro units), ‘T’ (time set), and ‘hydro_G’ (generation variable).
- The function returns the input list unchanged if any component is missing.
- This function is designed for integration into hybrid dispatch frameworks
  that include thermal, hydraulic, and renewable sources.

### NaivePyDESSEM.HydraulicGenerator.HydraulicEquations.add_hydraulic_cost_expression(m: ConcreteModel, cost_array: List[Any]) → List[Any]

Append hydroelectric generation cost terms to the total cost expression list.

This function serves as a placeholder for incorporating cost components
associated with hydroelectric operation into the objective function.
Although hydro generation typically has negligible marginal cost,
certain formulations may include opportunity costs, spill penalties,
or environmental constraints as cost terms.

* **Parameters:**
  * **m** (*ConcreteModel*) – Pyomo model instance containing hydroelectric generation variables.
  * **cost_array** (*list* *of* *expressions*) – List of symbolic expressions used in constructing the total system cost.
* **Returns:**
  The input list, optionally extended with hydro-related cost expressions.
* **Return type:**
  list of expressions

### Notes

- In many cases, this function may return the original list unchanged.
- It may be extended to include penalties for deviation from targets,
  reservoir violations, or environmental compensation.

## NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder module

### Hydropower Dispatch Model Builder

This module defines the construction logic for assembling a **hydropower-only**
optimization model in Pyomo. It integrates the full sequence of:

- Set and parameter initialization,
- Decision variable declaration,
- Piecewise or analytical hydropower production modeling (FPH),
- Operational constraints,
- Objective function (optional).

#### Supported generation modes (per unit)

- Constant productivity
- Specific productivity with fixed head
- Exact head-dependent generation with nonlinear losses
- Simplified constant productivity (didactic)

#### Functions

build_FPHs(m, data)
: Initialize the hydropower production function (FPH) callable for each unit.

build_hydro_dispatch(data, include_objective=True)
: Assemble a complete Pyomo model for hydropower dispatch optimization.

#### Modeling Conventions and Units

- Time periods are indexed as integers t = 1, …, horizon.
- Turbined and spill discharges (Q, S): m^3/s.
- Storage volume (V): hm^3.
- Power (G) and demand (d): MW.
- Typical power conversion constant: zeta = 9.81/1000 (when used within FPH).
- Volume conversion per period: zeta_vol = 3600/1e6 for hourly steps.

### Notes

- This builder targets **pure hydropower** systems. To include thermal units,
  couple with a combined system balance elsewhere.
- The callable stored in m.hydro_FPH[h] must accept the signature
  FPH(Q, V, S) → MW and be consistent with model units.
- Exact and specific modes rely on coefficient vectors that parameterize
  head or loss polynomials supplied via data.units[h].

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_problem(m: ConcreteModel, data: [HydraulicData](#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData), include_objective: bool = False) → ConcreteModel

Assemble a hydropower dispatch problem in Pyomo.

This builder configures a Pyomo model for reservoir-based hydropower
optimization. It attaches sets, parameters, decision variables, the
hydropower production functions (FPHs), and all relevant operational
constraints. Optionally, it includes the demand balance and the
cost-minimization objective.

* **Parameters:**
  * **m** (*pyomo.environ.ConcreteModel*) – Pyomo model to which the hydropower problem will be added.
  * **data** ([*HydraulicData*](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Input data object containing planning horizon, demand mapping,
    unit definitions, inflows, storage bounds, and productivity
    coefficients.
  * **include_objective** (*bool* *,* *optional*) – If True, add the system-wide demand balance and deficit-penalizing
    objective function (default is False).
* **Returns:**
  The updated Pyomo model with hydropower sets, parameters, variables,
  constraints, and optionally the objective.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- Constraints added:
  : * Hydropower generation equation (FPH-based)
    * Minimum/maximum turbined flow
    * Reservoir volume balance (continuity)
    * Minimum/maximum storage limits
    * Terminal storage requirement
- If include_objective=True, the system-wide balance constraint and
  the hydropower objective (deficit + spill penalty) are attached.
- This builder targets **pure hydropower** systems; for mixed
  hydrothermal systems, a combined balance and objective should be
  used instead.

### Examples

```pycon
>>> from pyomo.environ import ConcreteModel
>>> m = ConcreteModel()
>>> m = add_hydro_problem(m, data, include_objective=True)
>>> type(m)
<class 'pyomo.core.base.PyomoModel.ConcreteModel'>
```

### NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.build_FPHs(m: ConcreteModel, data: [HydraulicData](#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData))

Initialize hydropower production functions (FPH) for all units.

For each hydro unit h, this function selects and constructs a callable
FPH according to the unit’s declared mode (constant, simplified,
specific, or exact) and assigns it to m.hydro_FPH[h] with
the signature FPH(Q, V, S) => MW.

* **Parameters:**
  * **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Pyomo model into which the FPH callables will be attached.
  * **data** ([*HydraulicData*](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Configuration object containing unit maos and modes
* **Returns:**
  The model m is modified in place. A dictionary m.hydro_FPH is
  created, indexed by unit name, each entry being a callable of the form
  FPH(Q, V, S).
* **Return type:**
  None

### Notes

- **constant**: uses constant_productivity_fph(unit.p, data.zeta).
- **simplified**: uses simplified_constant_productivity_fph(unit.p).
- **specific**: uses fph_pe_factory(unit.pe, data.zeta, h_mont(.), h_jus(.)),
  where h_mont and h_jus are built via polynomial_factory(unit.a)
  and polynomial_factory(unit.b).
- **exact**: uses
  fph_factory(rho(.), h_mont(.), h_jus(.), h_perdas(.)), where
  rho = rho_colina_factory(unit.rho, data.zeta) and the three head/loss
  components are built via polynomial_factory with the respective
  coefficient lists.
- Units with an unknown/unsupported mode raise ValueError.

### NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.build_hydro_dispatch(data: [HydraulicData](#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData), include_objective: bool = True)

Assemble a complete Pyomo model for hydropower dispatch.

The resulting model includes:

- Set and parameter definitions (via hydraulyc_add_sets_and_params)
- Continuous decision variables (via hydralic_add_variables_g)
- Per-unit FPH callables (via build_FPHs)
- Operational constraints: generation equation, reservoir mass balance,
  Qmin/Qmax, volume bounds, terminal storage target
- Optional system-wide demand balance and cost-minimization objective

* **Parameters:**
  * **data** ([*HydraulicData*](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Input data with horizon, demand, unit map, and conversion constants.
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

## NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives module

### Objective Function for Pure Hydropower Dispatch

This module defines the objective for reservoir-based **hydropower-only**
optimization models. The objective minimizes (i) the total cost of unmet
energy (deficit) and (ii) a small penalty on water spillage to discourage
gratuitous releases, thereby promoting more efficient water usage.

#### Functions

set_objective_hydro(m)
: Attach a minimization objective to a Pyomo model that penalizes
  deficit and spillage over the planning horizon.

#### Modeling Conventions and Units

- Time periods: integers `t = 1, …, horizon`.
- Deficit `D[t]`: MW (interpreted per-period, consistent with objective scaling).
- Spill `hydro_S[h,t]`: m^3/s.
- `Cdef`: $/MWh (ensure consistency with how deficit is modeled and aggregated).

### Notes

- Designed for **pure hydropower** systems (no thermal generation).
- The spillage penalty uses a fixed coefficient (0.3). Adjust as needed
  to break degeneracy or steer solutions away from unnecessary spill.
- Compatible with NaivePyDESSEM hydropower data and constraints.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives.set_objective_hydro(m)

Add the linear objective function for hydropower-only dispatch.

The objective minimizes:
: - A deficit penalty: `Cdef * D[t]` summed over all periods;
  - A small spill penalty: `0.3 * hydro_S[h,t]` summed over plants and periods.

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Pyomo model containing:
  - `m.D[t]`          : deficit at time `t` (MW),
  - `m.hydro_S[h,t]`  : spill discharge (m^3/s),
  - `m.T`             : time set,
  - `m.HG`            : hydropower unit set,
  - `m.Cdef`          : cost of unmet demand ( $/MWh ).
* **Returns:**
  The same model with objective `m.OBJ` attached.
* **Return type:**
  pyomo.environ.ConcreteModel

### Notes

- The spill-penalty coefficient is fixed at `0.3` here as a mild
  regularizer; tune it to match your study’s units and priorities.
- If thermal units are present, use a combined objective instead.

## NaivePyDESSEM.HydraulicGenerator.HydraulicVars module

### Hydropower Model Initialization: Sets, Parameters, and Variables

This module provides initialization routines for setting up the basic
sets, parameters, and continuous variables required by hydropower
optimization models in Pyomo. It accommodates multiple hydropower
generation modes, natural-inflow handling, and head-dependent power
relationships supplied elsewhere in the modeling stack.

#### Functions

hydraulyc_add_sets_and_params(m, data)
: Initialize sets and model-level parameters/containers for hydropower units
  and system-wide demand.

hydralic_add_variables_g(m)
: Declare continuous decision variables for hydropower dispatch modeling.

#### Modeling Conventions and Units

- Time periods are indexed as integers `t = 1, …, horizon`.
- Turbined/Spill discharges (Q, S): m^3/s.
- Storage volume (V): hm^3.
- Demand and power (d, G): MW.
- Typical period conversion for volume: `zeta_vol = 3600/1e6` (hourly steps).
- Typical head–flow–power conversion: `zeta = 9.81/1000` (when used inside FPH).

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

### NaivePyDESSEM.HydraulicGenerator.HydraulicVars.hydralic_add_variables_g(m)

Declare continuous decision variables for hydropower dispatch.

The following Pyomo variables are added to model `m`:
- `hydro_Q[h,t]` : turbined discharge (m^3/s)
- `hydro_V[h,t]` : storage volume (hm^3)
- `hydro_S[h,t]` : spill discharge (m^3/s)
- `hydro_G[h,t]` : hydropower generation (MW)
- `D[t]`         : system deficit (MW)

All variables are nonnegative and defined over the hydropower units and
the planning horizon.

* **Parameters:**
  **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Pyomo model to which the decision variables will be attached.
* **Returns:**
  The same model `m` with variables declared.
* **Return type:**
  pyomo.core.base.PyomoModel.ConcreteModel

### Notes

- Assumes that sets `m.HG` and `m.T` have been initialized previously.
- Both `D` and `hydro_D` are provided to ease integration with
  different objective/balance formulations; keep only the one you use.

### NaivePyDESSEM.HydraulicGenerator.HydraulicVars.hydraulyc_add_sets_and_params(m, data)

Initialize hydropower sets and model-level parameters/containers.

Configures the Pyomo model `m` with time and hydropower unit sets,
system-level demand, and per-unit attributes such as flow limits,
storage bounds, initial/terminal storages, natural inflows, cascade
topology, and flags used by inflow aggregation. Values are sourced
from the `HydraulicData`/`HydraulicUnit` objects.

* **Parameters:**
  * **m** (*pyomo.core.base.PyomoModel.ConcreteModel*) – Target Pyomo model to be populated with sets and parameters.
  * **data** ([*HydraulicData*](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)) – Input data object with planning horizon, demand mapping, and the
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
  (e.g., `m.d`, `m.hydro_zeta`) are Pyomo `Param` objects.
- The attribute `m.horizon` stores the number of periods for quick access.

## NaivePyDESSEM.HydraulicGenerator.PEFPH module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Semi-Exact Hydroelectric Generation Function (FPH) with Net Head

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

Defines a hydropower production function (FPH) that incorporates the net
hydraulic head via upstream and downstream water levels combined with a
constant specific productivity efficiency.

The FPH is given by

> FPH(Q, V, S) = zeta \* PE \* [ h_mont(V) - h_jus(Q + S) ] \* Q,

where:
- Q     : turbine discharge (m^3/s)
- V     : reservoir volume (hm^3)
- S     : spill discharge (m^3/s)
- PE    : specific productivity efficiency (dimensionless)
- zeta  : head–flow–power conversion constant (e.g., 9.81 / 1000 to yield MW)

This formulation approximates the physical power output of a hydro unit
while simplifying losses and other complex hydraulic interactions.

### Notes

- Unit consistency is essential for meaningful results (Q in m^3/s, head in m,
  output in MW when using `zeta = 9.81/1000`).
- The downstream head depends on the total discharge `Q + S`, capturing
  tailwater variations with flow.

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDESSEM.HydraulicGenerator.PEFPH.fph_pe_factory(PE: float, zeta: float, hmont_func: Callable, hjus_func: Callable) → Callable

Factory for a semi-exact hydropower generation function with net head.

Builds a callable implementing

> FPH(Q, V, S) = zeta \* PE \* ( h_mont(V) - h_jus(Q + S) ) \* Q.
* **Parameters:**
  * **PE** (*float*) – Specific productivity efficiency (dimensionless).
  * **zeta** (*float*) – Head–flow–power conversion constant (e.g., 9.81 / 1000 to express power in MW).
  * **hmont_func** (*Callable*) – Function `h_mont(V)` mapping reservoir volume (hm^3) to upstream head (m).
  * **hjus_func** (*Callable*) – Function `h_jus(Q + S)` mapping total discharge (m^3/s) to downstream head (m).
* **Returns:**
  Function `FPH(Q, V, S)` returning generation in MW.
* **Return type:**
  Callable

### Examples

```pycon
>>> from ExactFPH import polynomial_factory
>>> f = fph_pe_factory(0.92, 9.81 / 1000,
...                    polynomial_factory([400]),
...                    polynomial_factory([300]))
>>> f(100, 2500, 0)
92.0
```

### Notes

- Ensure that `hmont_func` and `hjus_func` are calibrated so that
  head values (m) and flows (m^3/s) combine consistently with `zeta`.
- The returned callable is suitable for embedding in Pyomo expressions.

## NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH module

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
- Q : turbine discharge (m^3/s)
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

### NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH.simplified_constant_productivity_fph(P: float) → Callable

Factory for a simplified constant-productivity hydropower function.

Builds a callable implementing:

> FPH(Q) = P \* Q
* **Parameters:**
  **P** (*float*) – Constant productivity coefficient (dimensionless). If power output
  should be in MW, incorporate the appropriate conversion constant
  (e.g., 9.81 / 1000) into `P`.
* **Returns:**
  Function `f(Q, V, S)` returning generation as `P * Q`. The
  arguments `V` and `S` are accepted for signature compatibility
  but ignored in the calculation.
* **Return type:**
  Callable

### Examples

```pycon
>>> f = simplified_constant_productivity_fph(0.9)
>>> f(100, 2500, 0)
90.0
```

### Notes

- The returned callable is compatible with Pyomo expressions since it
  accepts three arguments (Q, V, S), even though only `Q` is used.
- Use this version when a head-independent linear mapping is sufficient.
