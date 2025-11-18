"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Thermal Unit Commitment — Objectives

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Objective functions for thermal unit-commitment (UC) models in Pyomo.
Two major formulations are supported:

1) Mixed-Integer Quadratic Programming (MIQP)
   Cost structure per unit and period:

       a * u + b * p + c * p^2 + SC * y + Cdef * D
   
   capturing fixed commitment cost, linear/quadratic variable cost,
   hot start-up cost, and deficit penalty.

2) Mixed-Integer Linear Programming (MILP) with Piecewise Linear (PWL) cost
   Variable cost represented by linear segments (Piecewise/SOS2).
   Objective includes:

       a * u  +  Cvar[g,t]  +  SC * y  +  Cdef * D

Usage
-----
- Call *set_objective_thermo_miqp(m)* for the quadratic-cost UC model.
- Call *set_objective_thermo_pwl(m)* for the piecewise-linear-cost UC model.
  Both functions attach a Pyomo *Objective* set for minimization.

Notes
-----
- Ensure unit consistency for costs (e.g., $/h vs $/MWh) and for power/energy.
- The functions assume that all referenced sets, variables and parameters
  have been previously added to the model.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import Objective, minimize


def set_objective_thermo_miqp(m):
    """
    Define a mixed-integer quadratic programming (MIQP) objective.

    Minimizes the total operating cost over the planning horizon, composed of:
    - Quadratic variable generation cost: *a * u + b * p + c * p^2*
    - Start-up cost: *SC * y*
    - Deficit penalty: *Cdef * D*

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model with:

        - Sets: *m.TG* (thermal units), *m.T* (time periods)
        - Variables:
            *m.thermal_p[g,t]* (MW), *m.thermal_u[g,t]* (binary),
            *m.thermal_y[g,t]* (binary), *m.D[t]* (MW)
        - Parameters:
            *m.thermal_a[g]*, *m.thermal_b[g]*, *m.thermal_c[g]* (cost coeffs),
            *m.thermal_SC[g]* (start-up cost), *m.Cdef* (deficit cost)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with quadratic objective *m.OBJ* set to minimize total cost.

    Examples
    --------
    >>> # Assuming sets, variables, and parameters are already defined:
    >>> _ = set_objective_thermo_miqp(m)
    >>> m.OBJ.pprint()  # doctest: +ELLIPSIS

    Notes
    -----
    - Prefer MIQP when accurate heat-rate curves are important and the solver
      handles convex quadratic objectives efficiently.
    - Ensure convexity: typically *m.thermal_c[g] >= 0* for all *g*.
    - Check scaling of cost coefficients to avoid numerical issues.
    """
    def _obj(m):
        quad = sum(m.thermal_c[g]*(m.thermal_p[g, t]**2) + m.thermal_b[g]*m.thermal_p[g, t] + m.thermal_a[g]*m.thermal_u[g, t]
                   for g in m.TG for t in m.T)
        starts = sum(m.thermal_SC[g]*m.thermal_y[g, t]
                     for g in m.TG for t in m.T)
        deficit = m.Cdef*sum(m.D[t] for t in m.T)
        return quad + starts + deficit
    m.OBJ = Objective(rule=_obj, sense=minimize)
    return m


def set_objective_thermo_pwl(m):
    """
    Define a piecewise linear (PWL) objective (MILP).

    Minimizes the total operating cost over the planning horizon, composed of:

    - Piecewise linear variable generation cost: *Cvar[g,t]*
    - Fixed commitment cost: *a * u*
    - Start-up cost: *SC * y*
    - Deficit penalty: *Cdef * D*

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model with:

        - Sets: *m.TG* (thermal units), *m.T* (time periods)
        - Variables:
            *m.thermal_Cvar[g,t]* (PWL cost), *m.thermal_u[g,t]* (binary),
            *m.thermal_y[g,t]* (binary), *m.D[t]* (MW)
        - Parameters:
            *m.thermal_a[g]* (fixed cost), *m.thermal_SC[g]* (start-up cost),
            *m.Cdef* (deficit cost)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with linear objective *m.OBJ* set to minimize total cost.

    Examples
    --------
    >>> # Assuming PWL cost variables/constraints are defined:
    >>> _ = set_objective_thermo_pwl(m)
    >>> m.OBJ.pprint()  # doctest: +ELLIPSIS

    Notes
    -----
    - Prefer PWL when MILP solvers perform better on large instances or when
      granular control of approximation accuracy is desired.
    - Ensure the PWL construction (breakpoints/SOS2) matches unit operating ranges.
    - Keep cost units consistent across all terms to maintain a well-scaled model.
    """
    def _obj(m):
        varcost = sum(m.thermal_Cvar[g, t] for g in m.TG for t in m.T)
        fixed = sum(m.thermal_a[g]*m.thermal_u[g, t]
                    for g in m.TG for t in m.T)
        starts = sum(m.thermal_SC[g]*m.thermal_y[g, t]
                     for g in m.TG for t in m.T)
        deficit = m.Cdef*sum(m.D[t] for t in m.T)
        return varcost + fixed + starts + deficit
    m.OBJ = Objective(rule=_obj, sense=minimize)
    return m

