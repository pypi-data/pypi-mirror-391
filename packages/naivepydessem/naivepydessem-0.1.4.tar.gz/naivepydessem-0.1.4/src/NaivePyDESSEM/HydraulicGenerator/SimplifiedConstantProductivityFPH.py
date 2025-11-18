"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Simplified Constant Productivity FPH Function

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines a simplified hydropower production function (FPH) for short-term
operation models. The generation is assumed to be proportional to turbine
discharge, scaled by a constant productivity coefficient.

The FPH is expressed as:

    FPH(Q) = P * Q

where:
- Q : turbine discharge (m^3/s)
- P : global productivity coefficient (dimensionless)

This formulation is particularly useful for approximate dispatch models,
sensitivity analyses, or didactic examples that do not require head-dependent
hydraulic modeling.

Notes
-----
- Unlike the more detailed constant-productivity model, this simplified
  function does not include the ``zeta`` scaling factor. If desired, the
  conversion constant can be absorbed directly into ``P`` to yield MW.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023 
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""
from typing import Callable


def simplified_constant_productivity_fph(P: float) -> Callable:
    """
    Factory for a simplified constant-productivity hydropower function.

    Builds a callable implementing:

        FPH(Q) = P * Q

    Parameters
    ----------
    P : float
        Constant productivity coefficient (dimensionless). If power output
        should be in MW, incorporate the appropriate conversion constant
        (e.g., 9.81 / 1000) into ``P``.

    Returns
    -------
    Callable
        Function ``f(Q, V, S)`` returning generation as ``P * Q``. The
        arguments ``V`` and ``S`` are accepted for signature compatibility
        but ignored in the calculation.

    Examples
    --------
    >>> f = simplified_constant_productivity_fph(0.9)
    >>> f(100, 2500, 0)
    90.0

    Notes
    -----
    - The returned callable is compatible with Pyomo expressions since it
      accepts three arguments (Q, V, S), even though only ``Q`` is used.
    - Use this version when a head-independent linear mapping is sufficient.
    """
    def fph(Q, V, S):
        return P * Q
    return fph
