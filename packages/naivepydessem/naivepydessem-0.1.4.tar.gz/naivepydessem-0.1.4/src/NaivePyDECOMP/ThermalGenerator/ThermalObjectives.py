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

Usage
-----
- Call *set_objective_thermo_miqp(m)* for the quadratic-cost UC model.
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


def set_objective_thermo(m):
    """
    Define the medium-term thermal objective.

    Minimizes the total operating cost over the planning horizon, composed of:
    - Linear thermal generation cost: Cg[g] * G[g,t]
    - Deficit penalty: Cdef * Def[t]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model with:

        - Sets: m.TG (thermal units), m.T (stages)
        - Variables:
            m.thermal_G[g,t] (MW), m.Def[t] (MW)
        - Parameters:
            m.thermal_C[g] (US$/MWh), m.Cdef (deficit penalty)

    Returns
    -------
    pyomo.environ.ConcreteModel
        Model with objective m.OBJ set to minimize total cost.

    Examples
    --------
    >>> _ = set_objective_decomp(m)
    >>> m.OBJ.pprint()
    """
    def _obj(m):
        thermal_cost = sum(m.thermal_Cost[g] * m.thermal_G[g, t] for g in m.TG for t in m.T)
        deficit_cost = m.Cdef * sum(m.Def[t] for t in m.T)
        return thermal_cost + deficit_cost

    m.OBJ = Objective(rule=_obj, sense=minimize)
    return m
