"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Constant Productivity FPH Function

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides a simplified hydroelectric production function (FPH)
for use in short-term operation and dispatch models. The generation is
assumed to be proportional to the turbine discharge, scaled by a constant
productivity factor.

The formulation is expressed as:

    FPH(Q) = zeta * P * Q

where:
- Q     : turbine discharge (m^3/s)
- P     : global productivity coefficient (dimensionless)
- zeta  : unit conversion constant (e.g., 9.81 / 1000 to convert to MW)

This approximation is particularly useful in didactic or preliminary
planning contexts where detailed head-dependent modeling is unnecessary.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""

from typing import Callable


def constant_productivity_fph(P: float, zeta: float) -> Callable:
    """
    Factory for a constant-productivity hydroelectric generation function.

    Constructs a callable object representing the simplified FPH
    relationship:

        FPH(Q) = zeta * P * Q

    Parameters
    ----------
    P : float
        Constant productivity coefficient (dimensionless).
    zeta : float
        Conversion constant (e.g., 9.81 / 1000 to scale to MW).

    Returns
    -------
    Callable
        A function of the form ``f(Q) = zeta * P * Q``, which accepts
        the turbine discharge (Q) in m^3/s and returns the generation
        in MW.

    Examples
    --------
    >>> f = constant_productivity_fph(0.9, 9.81 / 1000)
    >>> f(100)
    0.8829
    """
    def fph(Q):
        return zeta * P * Q
    return fph
