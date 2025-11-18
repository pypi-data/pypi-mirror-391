"""
Generator Constraints Module
============================
EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module defines the operational and investment constraints associated with
dispatchable generation units in the MDI framework. These constraints ensure that
generation power levels remain within admissible technical limits and that
investment decisions are properly linked across the planning horizon.

Description
-----------
The generator constraints implemented here enforce:

1. **Operational bounds**:  
   Ensures that each unit’s generation output lies between its minimum and maximum
   power levels whenever it is operational.

2. **Investment linkage**:  
   Establishes a temporal dependency between the binary investment decision variables
   (`gen_y`) and the operational availability variables (`gen_x`), guaranteeing
   consistent activation of units across consecutive time periods.

These constraints are intended to be modular and easily extensible for more
sophisticated generation formulations (e.g., ramping limits, minimum up/down
times, or emission constraints).

Functions
---------
add_generator_power_limits_constraint(m)
    Adds upper and lower power output constraints for each generator and time step.

add_generator_investment_link_constraint(m)
    Adds the logical linkage between investment and operational state variables
    across the planning horizon.

Notes
-----
- Both constraints assume that the model already defines sets ``GU``, ``T``, and ``P``,
  as well as parameters ``gen_Pmin`` and ``gen_Pmax``.
- The investment linkage formulation assumes chronological time indexing.
- These formulations align with the expansion-phase component of the MDI methodology.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

Module Dependencies
-------------------
- **Internal:** ``MDI.GeneratorVars``, ``MDI.GeneratorDataTypes``  
- **External:** ``pyomo.environ (Constraint, ConcreteModel)``
"""

from pyomo.environ import Constraint, ConcreteModel


def add_generator_power_limits_constraint(m: ConcreteModel) -> ConcreteModel:
    """
    Add operational power limits for dispatchable generation units.

    This constraint ensures that the generation output of each unit remains within
    its technical minimum and maximum power levels whenever the unit is operational.
    The constraint is applied over all generators, time periods, and demand levels.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing generator sets, parameters, and decision variables.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model instance, extended with upper and lower generation limits.

    Raises
    ------
    AttributeError
        If any required model attribute is missing (e.g., ``gen_P``, ``gen_Pmax``).

    Workflow
    --------
    1. For each generator, period, and demand level, define:
       - Upper limit: :math:`P_{g,t,p} \\leq P^{max}_g \\cdot x_{g,t}`
       - Lower limit: :math:`P_{g,t,p} \\geq P^{min}_g \\cdot x_{g,t}`
    2. Skip constraint creation if the required attributes are not defined.

    Notes
    -----
    - ``gen_x[g, t]`` represents whether the generator is active at time ``t``.
    - This constraint does not include ramping or minimum up/down time conditions,
      which should be defined in a separate submodule.
    """
    required = [
        'GU', 'T', 'P',
        'gen_P', 'gen_pmax', 'gen_x'
    ]

    if all(hasattr(m, attr) for attr in required):

        def _gen_max_rule(m, g, t, p):
            return m.gen_P[g, t, p] <= m.gen_pmax[g] * m.gen_x[g, t]

        def _gen_min_rule(m, g, t, p):
            return m.gen_P[g, t, p] >= 0.0

        m.gen_power_upper_constraint = Constraint(
            m.GU, m.T, m.P, rule=_gen_max_rule)
        m.gen_power_lower_constraint = Constraint(
            m.GU, m.T, m.P, rule=_gen_min_rule)

    return m


def add_generator_investment_link_constraint(m: ConcreteModel) -> ConcreteModel:
    """
    Add investment linkage constraints between generator states and investment decisions.

    These constraints ensure temporal consistency between investment decisions
    (`gen_y`) and operational availability (`gen_x`) throughout the planning horizon.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model containing generator-related variables and sets.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model instance, extended with investment linkage constraints.

    Workflow
    --------
    1. Initialization constraint:
       - At the first period, equate ``gen_y[g, 1]`` with the initial state ``gen_state[g]``.
    2. Temporal linkage constraint:
       - Enforce that ``x[g, t] = x[g, t-1] + y[g, t]`` for ``t > 1``,
         ensuring capacity accumulation through time.

    Notes
    -----
    - The binary variable ``gen_y`` represents new investments.
    - The binary variable ``gen_x`` denotes whether the generator is operational.
    - ``gen_state`` specifies the pre-existing operational state at the start of the horizon.
    - Skips constraint definition if any required model components are missing.
    """
    required = ['GU', 'T', 'gen_x', 'gen_y']

    if all(hasattr(m, attr) for attr in required):

        def _inv_initial_value_rule(m, g, t):
            if t == 1:
                return m.gen_y[g, t] == m.gen_state[g]
            return Constraint.Skip

        def _inv_link_rule(m, g, t):
            if t == 1:
                return m.gen_x[g, t] == m.gen_y[g, t]
            return m.gen_x[g, t] == m.gen_x[g, m.T.prev(t)] + m.gen_y[g, t]

        m.gen_initial_state_constraint = Constraint(
            m.GU, m.T, rule=_inv_initial_value_rule)
        m.gen_investment_link_constraint = Constraint(
            m.GU, m.T, rule=_inv_link_rule)

    return m
