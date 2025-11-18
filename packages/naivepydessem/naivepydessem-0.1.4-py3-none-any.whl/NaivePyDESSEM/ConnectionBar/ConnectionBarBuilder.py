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

from .ConnectionBarVars import (
    connection_bar_add_sets_and_params,
    connection_bar_add_variables
)
from .ConnectionBarConstraints import (
    add_connection_bar_angle_limits_constraints,
    add_connection_bar_slack_constraints
)
from .ConnectionBarDataTypes import ConnectionBarData
from pyomo.environ import ConcreteModel


def build_connection_bars(data: ConnectionBarData,
                          include_objective: bool = True) -> ConcreteModel:
    """
    Build a complete Pyomo model representing the connection-bar subsystem.

    Creates a new :class:`~pyomo.environ.ConcreteModel` and populates it with
    all components associated with connection bars (sets, parameters,
    variables, and constraints). It serves as the main entry point for
    standalone tests or integration into larger system models.

    Parameters
    ----------
    data : ConnectionBarData
        Structured data containing the planning horizon, bar demands,
        slack-bar configuration, and deficit penalty cost.
    include_objective : bool, optional
        Reserved argument for backward compatibility with renewable-only
        dispatch models (default is ``True``). Currently unused.

    Returns
    -------
    pyomo.environ.ConcreteModel
        A fully initialized Pyomo model containing connection-bar elements.

    Notes
    -----
    - The created model includes:
        * Time set ``m.T`` and bar set ``m.BAR``
        * Demand and deficit penalty parameters
        * Phase-angle (``θ_b``) and deficit (``D[b,t]``) variables
        * Slack-bar, angular-limit, and balance constraints
    - Intended for modular integration with generation and transmission
      builders in network expansion formulations.
    """
    m = ConcreteModel()
    m = add_connection_bar_problem(m=m,
                                   data=data,
                                   include_objective=include_objective)
    return m


def add_connection_bar_problem(m: ConcreteModel,
                               data: ConnectionBarData,
                               include_objective: bool = False) -> ConcreteModel:
    """
    Attach connection-bar components and constraints to a Pyomo model.

    Populates an existing :class:`~pyomo.environ.ConcreteModel` with all
    connection-bar-related elements, including sets, parameters, variables,
    and the fundamental constraints for DC power flow consistency.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model instance to which connection-bar elements will be added.
    data : ConnectionBarData
        Input data containing:
            - Planning horizon (``horizon``)
            - Bar-level demand profiles
            - Slack-bar configuration
            - Deficit cost (``Cdef``)
    include_objective : bool, optional
        Reserved parameter for compatibility with legacy renewable-only
        builders. Currently unused (default ``False``).

    Returns
    -------
    pyomo.environ.ConcreteModel
        The updated model containing all connection-bar components.

    Notes
    -----
    - Functions called:
        * :func:`connection_bar_add_sets_and_params`
        * :func:`connection_bar_add_variables`
        * :func:`add_connection_bar_slack_constraints`
        * :func:`add_connection_bar_angle_limits_constraints`
    - The sequence ensures that:
        1. Sets and parameters are initialized.
        2. Variables are declared with appropriate bounds.
        3. The slack bar is fixed (θ = 0).
        4. Non-slack bars are bounded between ±π.
    - The routine can be reused within multi-bar or multi-region models,
      such as those in DECOMP and MDI formulations.
    """
    connection_bar_add_sets_and_params(m, data)
    connection_bar_add_variables(m)
    add_connection_bar_slack_constraints(m)
    add_connection_bar_angle_limits_constraints(m)
    return m
