"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Energy Storage — Objective Function

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines the objective function for storage-only dispatch models in Pyomo.
The formulation minimizes the total penalty cost associated with unmet
demand (deficit) over the planning horizon, using the parameter ``Cdef``.

Functions
---------
set_objective_storage(m)
    Attach a minimization objective to the model that penalizes unmet
    demand through ``Cdef * D[t]``.

Notes
-----
- This objective is tailored for storage-only systems without explicit
  operating or cycling costs.
- The penalty coefficient ``Cdef`` should be chosen sufficiently high
  to discourage deficits under normal operating conditions.
- For hybrid models (hydro, thermal, renewable, storage), a combined
  system-wide objective should be defined at a higher level.
  
References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConcreteModel, Objective, minimize
def set_objective_storage(m: ConcreteModel) -> ConcreteModel:
    """
    Attach a deficit-penalizing objective for storage-only models.

    Objective
    ---------
    Minimize the total cost of unmet demand across the horizon:

        minimize  sum_t Cdef * D[t]

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Model with set ``m.T``, variable ``m.D[t]`` and parameter ``m.Cdef``.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with objective ``m.OBJ`` attached.
    """
    def _obj_rule(m):
        return sum(m.Cdef * m.D[t] for t in m.T)
    m.OBJ = Objective(rule=_obj_rule, sense=minimize)
    return m
