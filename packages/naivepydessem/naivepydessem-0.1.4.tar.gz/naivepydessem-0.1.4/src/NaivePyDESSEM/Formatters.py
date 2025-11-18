"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Utility: Format Numbers in Brazilian Currency Style

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides a helper function to format numerical values in the 
Brazilian currency style: periods as thousand separators and commas for 
decimals (e.g., 1234567.89 → '1.234.567,89').

It is intended for producing human-readable cost reports or summaries in 
energy dispatch problems solved by NaivePyDESSEM.

Examples
--------
>>> format_brl(1234567.89)
'1.234.567,89'

>>> format_brl(42.5)
'42,50'

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""


def format_brl(value: float) -> str:
    """
    Format a floating-point number as a Brazilian-style currency string.

    This function converts a numeric value into a string formatted with
    periods as thousand separators and a comma as the decimal mark,
    following the standard Brazilian notation (e.g., R$ 1.234,56).

    Parameters
    ----------
    value : float
        The numeric value to format.

    Returns
    -------
    str
        The formatted string representing the value in BRL-style.

    Examples
    --------
    >>> format_brl(1234567.89)
    '1.234.567,89'

    >>> format_brl(42)
    '42,00'

    Notes
    -----
    - No currency symbol (e.g., 'R$') is included in the output.
    - Internally, uses Python formatting and string replacement.
    """

    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
