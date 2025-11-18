"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Builder

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Provides the high-level construction routine for assembling the
transmission line subsystem within DC power flow formulations.
This module integrates sets, variables, and constraints that
represent line flows, capacity limits, and their relationship
with nodal phase angles.

Functions
---------
build_transmission_lines(m)
    Create and attach all components of the transmission line
    subsystem to the given Pyomo model, including variables
    and constraints.

Notes
-----
- This module orchestrates the routines from:
    * :mod:`TransmissionLineVars`
    * :mod:`TransmissionLineConstraints`
- The formulation is consistent with the DC power flow approximation:
    ``F_ij,t = b_ij (θ_i,t − θ_j,t)``
- The resulting subsystem is compatible with both fixed-network
  (operational) and mixed-integer (expansion) models.
- Phase angles ``θ[b,t]`` must be declared before calling this builder.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from .TransmissionLineVars import (transmission_line_add_variables, 
                                   transmission_line_add_sets_and_params)
from .TransmissionLineConstraints import (
    add_transmission_line_flow_constraints,
    add_transmission_line_flow_limits_constraints,
)
from .TransmissionLineDataTypes import TransmissionLineData

from pyomo.environ import ConcreteModel

def build_transmission_lines(data: TransmissionLineData,
                             include_objective: bool = True) -> ConcreteModel:
    """
    Construct a standalone Pyomo model for the transmission-line subsystem.

    This high-level builder creates a new :class:`~pyomo.environ.ConcreteModel`
    instance and populates it with all sets, parameters, variables, and
    constraints required to represent transmission lines in DC power flow
    formulations. It serves as the main entry point for testing or integrating
    the transmission-line subsystem independently from other components
    (e.g., connection bars, generators, or storage).

    Parameters
    ----------
    data : TransmissionLineData
        Structured input data containing the planning horizon and the
        collection of transmission lines with their respective physical
        and economic attributes, including:
            - ``b`` : susceptance (1/x_ij)
            - ``pmax`` : maximum flow (MW)
            - ``endpoints`` : list of connected bars [i, j]
            - ``state`` : existing (1) or candidate (0)
            - ``model`` : modeling type ('dc' or 'transport')
    include_objective : bool, optional
        Reserved for future use (default ``True``). Currently, this flag
        has no effect, as transmission lines are typically passive network
        elements without an explicit objective term. It is retained for
        interface consistency with other subsystem builders.

    Returns
    -------
    pyomo.environ.ConcreteModel
        A new Pyomo model fully configured with the transmission-line
        subsystem, including:
            - Set of lines (``m.LT``)
            - Time set (``m.T``)
            - Line parameters (susceptance, capacity, endpoints)
            - Decision variables (``m.lines_flow[l,t]``)
            - Constraints:
                * DC flow definition (for ``model = 'dc'``)
                * Flow capacity limits (for all lines)

    Notes
    -----
    - The function internally calls :func:`add_transmission_line_problem`,
      which attaches the subsystem components to the newly created model.
    - The resulting model can be later coupled with other subsystems via
      shared variables such as bus angles (``θ[b,t]``) and power balances.
    - Both DC and transport models are supported within the same formulation,
      enabling hybrid operation and expansion studies.

    References
    ----------
    [1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
    [2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
        Lecture Notes, EELT7030/UFPR, 2023.
    """
    m = ConcreteModel()
    m.unique_bar = False # avoid the unique bar restriction just for testing
    return add_transmission_line_problem(m=m, 
                                         data=data, 
                                         include_objective=include_objective)

def add_transmission_line_problem(m: ConcreteModel,
                                  data: TransmissionLineData,
                                  include_objective: bool = False) -> ConcreteModel:
    """
    Attach the transmission-line subsystem to an existing Pyomo model.

    This function populates a given :class:`~pyomo.environ.ConcreteModel`
    with all sets, parameters, variables, and constraints related to
    transmission lines under the DC power flow approximation. It forms
    the network component of the system model, complementing the
    connection-bar formulation.

    Parameters
    ----------
    m : pyomo.environ.ConcreteModel
        Pyomo model to which the transmission-line subsystem will be added.
        The model must contain or be prepared to receive:
            - ``m.LT`` : set of transmission lines
            - ``m.T`` : set of time periods
            - ``m.lines_b[l]`` : susceptance (1/x_ij)
            - ``m.lines_pmax[l]`` : flow capacity limit (MW)
            - ``m.lines_endpoints[l]`` : list of connected bars [i, j]
            - ``m.theta[b,t]`` : phase angle variable (radians)
    data : TransmissionLineData
        Structured input containing the system horizon and the physical
        and operational parameters of each transmission line, including
        endpoints, susceptance, and capacity.
    include_objective : bool, optional, deprecated
        Reserved argument for interface compatibility (default ``False``).
        Currently unused, as transmission lines are passive network
        elements without a direct cost component in the objective.

    Returns
    -------
    pyomo.environ.ConcreteModel
        The same model, augmented with transmission-line sets, variables,
        and constraints.

    Notes
    -----
    - Steps performed:
        1. Initialize sets and parameters from :class:`TransmissionLineData`.
        2. Declare line flow decision variables (``lines_flow[l,t]``).
        3. Add DC flow definition constraints:
           ``F_ij,t = b_ij (θ_i,t − θ_j,t)``
        4. Add flow capacity limit constraints:
           ``−pmax_ij ≤ F_ij,t ≤ pmax_ij``.
    - The order of addition ensures that variables are defined before
      constraints that depend on them.
    - The formulation is compatible with both pure DC models and
      hybrid DC/transport formulations (lines marked with
      ``model: "transport"`` are automatically excluded from the DC flow
      constraint).

    References
    ----------
    [1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
    [2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
        Lecture Notes, EELT7030/UFPR, 2023.
    """
    if not m.unique_bar:
        transmission_line_add_sets_and_params(m, data)
        transmission_line_add_variables(m)
        add_transmission_line_flow_constraints(m)
        add_transmission_line_flow_limits_constraints(m)
    return m

