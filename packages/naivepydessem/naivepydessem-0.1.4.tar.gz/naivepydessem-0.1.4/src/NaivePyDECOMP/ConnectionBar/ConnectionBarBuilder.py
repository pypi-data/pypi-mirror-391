"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Connection Bar — Model Builder

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides high-level routines for constructing and
assembling Pyomo models representing electrical connection bars
(buses) within DC power flow formulations. It integrates the
components defined in submodules:

    - :mod:`ConnectionBarDataTypes`
    - :mod:`ConnectionBarVars`
    - :mod:`ConnectionBarConstraints`

The builder functions create or extend a ``ConcreteModel`` with
sets, parameters, variables, and constraints associated with
each connection bar. The formulation supports hybrid systems
(hydro, thermal, renewable, and storage) as well as networked
multi-bar expansion studies (e.g., MDI, DECOMP, DESSEM).

Functions
---------
build_connection_bars(data, include_objective=True)
    Create and return a complete Pyomo model representing
    the connection-bar subsystem.

add_connection_bar_problem(m, data, include_objective=False)
    Attach all sets, parameters, variables, and constraints
    related to connection bars to an existing Pyomo model.

Notes
-----
- This module is the main interface between the connection-bar
  data structures and their corresponding Pyomo model elements.
- The resulting model includes:
    * Sets and parameters (bars, demands, and slack identification)
    * Variables (phase angles and deficits)
    * Constraints:
        - Slack-bar reference (θ = 0)
        - Angular limits (-π ≤ θ ≤ π)
        - Power balance per bar and time period
- The functions are designed for integration with higher-level
  system builders that include generators and transmission lines.
- The optional argument ``include_objective`` is reserved for
  compatibility with renewable-only formulations and may be
  deprecated in future versions.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""
import copy
from pyomo.environ import ConcreteModel, Objective, minimize
from .ConnectionBarVars import (
    connection_bar_add_sets_and_params,
    connection_bar_add_variables
)
from .ConnectionBarConstraints import (
    add_connection_bar_angle_limits_constraints,
    add_connection_bar_slack_constraints
)
from .ConnectionBarDataTypes import ConnectionBarData
from NaivePyDESSEM.ConnectionBar.ConnectionBarBuilder import (
    build_connection_bars,
    add_connection_bar_problem
)


def add_connection_bar_subproblem(m: ConcreteModel,
                                  data: ConnectionBarData,
                                  stage: int) -> ConcreteModel:
    """
    Add a connection-bar subproblem structure to an existing Pyomo model.

    This routine constructs the local connection-bar component corresponding
    to a single stage of the overall planning horizon. It initializes the
    sets, parameters, and decision variables related to nodal representation
    (bars), and attaches the associated angular and slack-bar constraints.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance to which the connection-bar subproblem will be
        added.
    data : ConnectionBarData
        Input data structure containing bar-level information such as
        demand profiles, slack status, and other nodal parameters.
    stage : int
        Index of the planning stage for which this subproblem is created.
        The function internally restricts the horizon to one stage to
        enable decomposition or stage-wise simulation.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model including the connection-bar subproblem for the
        specified stage, with initialized sets, parameters, variables, and
        angle-related constraints.

    Notes
    -----
    - Components added:
        * Bar sets and parameters (demand, slack status, etc.)
        * Decision variables: deficit ``D[b,t]`` and phase angle ``θ[b,t]``
        * Constraints:
            - Angular bounds (−π ≤ θ ≤ π)
            - Slack-bar reference (θ = 0)
    - The horizon is automatically restricted to a single stage for
      stage-wise decomposition or iterative expansion methods.
    - This subproblem formulation is compatible with integrated models
      combining multiple network or generation layers.

    References
    ----------
    [1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
    [2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
        Lecture Notes, EELT7030/UFPR, 2023.
    """
    # data copy
    subproblem_data = copy.deepcopy(data)
    subproblem_data.horizon = 1
    # demand
    for name in subproblem_data.units.keys():
        subproblem_data.units[name].demand = [data.units[name].demand[stage]]
    # sets & params
    connection_bar_add_sets_and_params(m, subproblem_data)
    # variables
    connection_bar_add_variables(m)
    # constraints
    add_connection_bar_angle_limits_constraints(m)
    add_connection_bar_slack_constraints(m)

    return m
