"""
Objective Function for Pure Hydropower Dispatch
===============================================

This module defines the objective for reservoir-based **hydropower-only**
optimization models. The objective minimizes (i) the total cost of unmet
energy (deficit) and (ii) a small penalty on water spillage to discourage
gratuitous releases, thereby promoting more efficient water usage.

Functions
---------
set_objective_hydro(m)
    Attach a minimization objective to a Pyomo model that penalizes
    deficit and spillage over the planning horizon.

Modeling Conventions and Units
------------------------------
- Time periods: integers ``t = 1, …, horizon``.
- Deficit ``D[t]``: MW (interpreted per-period, consistent with objective scaling).
- Spill ``hydro_S[h,t]``: m^3/s.
- ``Cdef``: $/MWh (ensure consistency with how deficit is modeled and aggregated).

Notes
-----
- Designed for **pure hydropower** systems (no thermal generation).
- The spillage penalty uses a fixed coefficient (0.3). Adjust as needed
  to break degeneracy or steer solutions away from unnecessary spill.
- Compatible with NaivePyDESSEM hydropower data and constraints.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023 
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""

from pyomo.environ import Objective, minimize


def set_objective_hydro(m):
    """
    Add the linear objective function for hydropower-only dispatch.

    The objective minimizes:
        - A deficit penalty: ``Cdef * D[t]`` summed over all periods;
        - A small spill penalty: ``0.3 * hydro_S[h,t]`` summed over plants and periods.

    Parameters
    ----------
    m : pyomo.core.base.PyomoModel.ConcreteModel
        Pyomo model containing:
        - ``m.D[t]``          : deficit at time ``t`` (MW),
        - ``m.hydro_S[h,t]``  : spill discharge (m^3/s),
        - ``m.T``             : time set,
        - ``m.HG``            : hydropower unit set,
        - ``m.Cdef``          : cost of unmet demand ( $/MWh ).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with objective ``m.OBJ`` attached.

    Notes
    -----
    - The spill-penalty coefficient is fixed at ``0.3`` here as a mild
      regularizer; tune it to match your study’s units and priorities.
    - If thermal units are present, use a combined objective instead.
    """
    def _obj_rule(m):
        return sum(m.Cdef * m.D[t] for t in m.T) + \
            0.3 * sum(m.hydro_S[h, t] for h in m.HG for t in m.T)

    m.OBJ = Objective(expr=_obj_rule(m), sense=minimize)
    return m
