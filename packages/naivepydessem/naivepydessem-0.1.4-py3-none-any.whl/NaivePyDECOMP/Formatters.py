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
energy dispatch problems solved by NaivePyDECOMP.

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
from NaivePyDESSEM.Formatters import format_brl