"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Renewable Unit Commitment — Objective Function

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines the objective function for renewable-only dispatch models in Pyomo.
The objective minimizes the total cost of unmet demand (deficit) over the
planning horizon. It uses the deficit penalty parameter ``Cdef`` to quantify
the economic impact of unserved energy.

Functions
---------
set_objective_renewable(m)
    Attach a minimization objective to the model, penalizing unmet demand.

Notes
-----
- This objective is designed for renewable-only systems, where generation
  is fully determined by availability and no explicit fuel costs exist.
- The deficit variable ``D[t]`` ensures feasibility when renewable
  generation cannot meet the demand ``d[t]``.
- The penalty coefficient ``Cdef`` should be chosen high enough to
  discourage deficits under normal conditions.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import Objective, minimize


def set_objective_renewable(m):
    """
    Define the objective function for renewable-only dispatch models.

    The objective minimizes the total penalty associated with unmet demand
    (deficit) across the planning horizon. This is expressed as:

        minimize  sum_t Cdef * D[t]

    where:
    - ``D[t]`` is the deficit variable (MW) at time period ``t``.
    - ``Cdef`` is the penalty coefficient for unserved energy (e.g., $/MWh).

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model with:
        - Set: ``m.T`` (time periods)
        - Variable: ``m.D[t]`` (deficit at time ``t``)
        - Parameter: ``m.Cdef`` (deficit penalty cost)

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model with objective function ``m.OBJ`` attached, set for
        minimization.

    Notes
    -----
    - This formulation is intended for renewable-only systems, where
      generation costs are absent and the only economic penalty comes
      from unmet demand.
    - Ensure that the penalty ``Cdef`` is set to a sufficiently high value
      so that the optimizer prioritizes meeting demand whenever possible.
    - The objective does not account for renewable curtailment or spill
      penalties. If such penalties are desired, they must be added explicitly.

    Examples
    --------
    >>> from pyomo.environ import ConcreteModel
    >>> m = ConcreteModel()
    >>> m.T = [1, 2, 3]
    >>> m.D = {t: 0 for t in m.T}  # deficit variables (mocked here)
    >>> m.Cdef = 1000.0
    >>> _ = set_objective_renewable(m)
    >>> m.OBJ.pprint()  # doctest: +ELLIPSIS
    """
    def _obj_rule(m):
        return sum(m.Cdef * m.D[t] for t in m.T)

    m.OBJ = Objective(expr=_obj_rule(m), sense=minimize)
    return m
