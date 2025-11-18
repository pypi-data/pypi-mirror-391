"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Semi-Exact Hydroelectric Generation Function (FPH) with Net Head

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines a hydropower production function (FPH) that incorporates the net
hydraulic head via upstream and downstream water levels combined with a
constant specific productivity efficiency.

The FPH is given by

    FPH(Q, V, S) = zeta * PE * [ h_mont(V) - h_jus(Q + S) ] * Q,

where:
- Q     : turbine discharge (m^3/s)
- V     : reservoir volume (hm^3)
- S     : spill discharge (m^3/s)
- PE    : specific productivity efficiency (dimensionless)
- zeta  : head–flow–power conversion constant (e.g., 9.81 / 1000 to yield MW)

This formulation approximates the physical power output of a hydro unit
while simplifying losses and other complex hydraulic interactions.

Notes
-----
- Unit consistency is essential for meaningful results (Q in m^3/s, head in m,
  output in MW when using ``zeta = 9.81/1000``).
- The downstream head depends on the total discharge ``Q + S``, capturing
  tailwater variations with flow.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023 
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""
from typing import Callable


def fph_pe_factory(PE: float, 
                   zeta: float, 
                   hmont_func: Callable, 
                   hjus_func: Callable) -> Callable:
    """
    Factory for a semi-exact hydropower generation function with net head.

    Builds a callable implementing

        FPH(Q, V, S) = zeta * PE * ( h_mont(V) - h_jus(Q + S) ) * Q.

    Parameters
    ----------
    PE : float
        Specific productivity efficiency (dimensionless).
    zeta : float
        Head–flow–power conversion constant (e.g., 9.81 / 1000 to express power in MW).
    hmont_func : Callable
        Function ``h_mont(V)`` mapping reservoir volume (hm^3) to upstream head (m).
    hjus_func : Callable
        Function ``h_jus(Q + S)`` mapping total discharge (m^3/s) to downstream head (m).

    Returns
    -------
    Callable
        Function ``FPH(Q, V, S)`` returning generation in MW.

    Examples
    --------
    >>> from ExactFPH import polynomial_factory
    >>> f = fph_pe_factory(0.92, 9.81 / 1000,
    ...                    polynomial_factory([400]),
    ...                    polynomial_factory([300]))
    >>> f(100, 2500, 0)
    92.0

    Notes
    -----
    - Ensure that ``hmont_func`` and ``hjus_func`` are calibrated so that
      head values (m) and flows (m^3/s) combine consistently with ``zeta``.
    - The returned callable is suitable for embedding in Pyomo expressions.
    """
    def fph(Q, V, S):
        return zeta * PE * (hmont_func(V) - hjus_func(Q + S) ) * Q
    return fph
