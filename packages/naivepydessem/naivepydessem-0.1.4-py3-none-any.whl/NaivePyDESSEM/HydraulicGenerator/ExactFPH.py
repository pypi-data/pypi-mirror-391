"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Hydropower Dispatch with Exact FPH Model

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Implements an exact-form hydropower production function (FPH) aligned with
the DESSEM methodology. The model uses polynomial (or polynomial-like) 
approximations for four building blocks:

- Specific productivity,       rho(Q, h_liq)
- Upstream water head,         h_mont(V)
- Downstream water head,       h_jus(Q + S)
- Hydraulic losses,            h_perdas(Q)

The electrical power is computed as

    FPH(Q, V, S) = rho(Q, h_liq) * Q * h_liq,

where the net head is

    h_liq = h_mont(V) - h_jus(Q + S) - h_perdas(Q).

Variables and units:
- Q : turbine discharge (m^3/s)
- V : reservoir volume (hm^3)
- S : spill discharge (m^3/s)
- FPH : electrical power (MW), assuming consistent scaling inside `rho`

Notes
-----
- The exact physical fidelity depends on the quality and calibration of the
  polynomials/surrogates provided to the factories.
- Unit consistency is essential: typical conversions use zeta = 9.81/1000
  within `rho` (or within head-to-power mapping) to yield MW.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023. 
"""

from typing import List, Callable


def polynomial_factory(coefs: List[float]) -> Callable:
    """
    Create a univariate polynomial function from coefficients.

    The resulting polynomial is

        f(x) = c_0 + c_1 x + c_2 x² + ... + c_n xⁿ,

    with coefficients given in increasing order of degree.

    Parameters
    ----------
    coefs : List[float]
        Polynomial coefficients [c_0, c_1, ..., c_n] in ascending degree.

    Returns
    -------
    Callable
        Function ``f(x)`` that evaluates the polynomial at a scalar ``x``.

    Examples
    --------
    >>> f = polynomial_factory([2, 3, 0.5])  # 2 + 3x + 0.5 x^2
    >>> f(2)
    10.0
    >>> f(0)
    2.0
    """
    def polynomial(x):
        return sum(c * x**i for i, c in enumerate(coefs))
    return polynomial


def rho_colina_factory(coefs: List[float],
                       zeta: float = 9.81 / 1000) -> Callable:
    """
    Build a colina-type specific productivity surface rho(Q, h_liq).

    The parametric surface follows

        rho(Q, h_liq) = zeta * (rho0
                                + rho1 * Q
                                + rho2 * h_liq
                                + rho3 * Q * h_liq
                                + rho4 * Q^2
                                + rho5 * h_liq^2)

    Parameters
    ----------
    coefs : List[float]
        Six coefficients [rho0, rho1, rho2, rho3, rho4, rho5] for the bilinear/
        quadratic surface fitted to efficiency/productivity data.
    zeta : float, optional
        Unit conversion/scaling constant (default 9.81/1000), typically chosen
        so that the final FPH is expressed in MW.

    Returns
    -------
    Callable
        Function ``rho(Q, h_liq)`` returning specific productivity consistent
        with the downstream power computation.

    Examples
    --------
    >>> rho = rho_colina_factory([0.88, 0.01, 0.002, 1e-4, -5e-5, -2e-5])
    >>> rho(Q=300, hliq=120)  # doctest: +ELLIPSIS
    ...

    Notes
    -----
    - Raises ``ValueError`` if the coefficient list length is not 6.
    """
    if len(coefs) != 6:
        raise ValueError(
            "Expected 6 coefficients for rho(Q, hliq) polynomial surface.")

    def rho(Q: float, hliq: float) -> float:
        return zeta * (
            coefs[0] +
            coefs[1] * Q +
            coefs[2] * hliq +
            coefs[3] * Q * hliq +
            coefs[4] * Q**2 +
            coefs[5] * hliq**2
        )

    return rho


def fph_factory(rho_func: Callable, 
                hmont_func: Callable,
                hjus_func: Callable, 
                hperdas_func: Callable) -> Callable:
    """
    Compose the exact hydropower generation function (FPH) from components.

    The assembled function computes

        FPH(Q, V, S) = rho(Q, h_liq) * Q * h_liq,

    with net head

        h_liq = h_mont(V) - h_jus(Q + S) - h_perdas(Q).

    Parameters
    ----------
    rho_func : Callable
        Specific productivity surface ``rho(Q, h_liq)``; e.g., from
        :func:`rho_colina_factory`.
    hmont_func : Callable
        Upstream head function ``h_mont(V)`` mapping reservoir volume to head.
    hjus_func : Callable
        Downstream head function ``h_jus(Q + S)`` mapping total discharge to
        tailwater level.
    hperdas_func : Callable
        Hydraulic-loss function ``h_perdas(Q)`` mapping discharge to losses.

    Returns
    -------
    Callable
        Function ``FPH(Q, V, S)`` returning generation in MW (given consistent
        units and scaling inside the components).

    Examples
    --------
    >>> rho = rho_colina_factory([0.88, 0.01, 0.002, 1e-4, -5e-5, -2e-5])
    >>> h_mont   = polynomial_factory([400])                  # constant upstream head
    >>> h_jus    = polynomial_factory([300])                  # constant downstream head
    >>> h_perdas = polynomial_factory([0.0, 0.0, 1e-5])       # losses ~ 1e-5 * Q^2
    >>> fph = fph_factory(rho, h_mont, h_jus, h_perdas)
    >>> _ = fph(Q=100, V=1000, S=0)  # doctest: +ELLIPSIS

    Notes
    -----
    - Ensure that ``rho_func`` and the head functions use consistent units
      so that the product yields MW.
    - The returned function is suitable for use inside Pyomo expressions.
    """
    def fph(Q, V, S):
        hliq = hmont_func(V) - hjus_func(Q + S) - hperdas_func(Q)
        return rho_func(Q, hliq) * Q * hliq
    return fph
