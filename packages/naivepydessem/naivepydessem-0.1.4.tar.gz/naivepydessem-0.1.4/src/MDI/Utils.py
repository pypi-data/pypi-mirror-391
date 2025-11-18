"""
Utils Module
============

EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

LaTeX Table Utilities for Pandas DataFrames

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides helpers to render pandas DataFrames as LaTeX tables with
custom styling aimed at scientific and engineering reports. It includes:

- ``binary_df_to_colored_latex``: Renders a binary matrix (0/1) as a colored
  LaTeX table, highlighting ones and zeros with configurable colors and
  producing a complete ``table`` environment.

- ``custom_df_to_latex``: Renders a generic (non-binary) DataFrame as a LaTeX
  table with bold headers (and bold math within headers), using ``booktabs``
  rules and producing a complete ``table`` environment.

Both functions omit the DataFrame index from the LaTeX output by design,
emitting only the column headers and data cells.

Functions
---------
binary_df_to_colored_latex  
    Render a binary (0/1) DataFrame as a colored LaTeX table. Cells equal to 1  
    are filled with ``one_color``; cells equal to 0 use ``zero_color``.  
    Non-binary values, if present, are formatted with ``floatfmt`` and not  
    color-filled. The index is not included in the output.

custom_df_to_latex  
    Render a generic DataFrame as a LaTeX table using ``booktabs`` rules with a  
    bold header row. Inline math fragments in header cells  are additionally set 
    in bold math using ``bold_math_cmd``.  
    The index is not included in the output.

Parameters (Shared)
-------------------
df : pandas.DataFrame  
    The input table to render. Only the DataFrame **columns** are emitted;  
    the index is always omitted from the LaTeX output.

caption : str, optional  
    Caption text for the LaTeX ``table`` environment.

label : str, optional  
    Label for cross-referencing with ``\\ref{...}``.

column_format : str or None, optional  
    Column specification for the LaTeX ``tabular`` environment. If ``None``,  
    a default is inferred based on the number of columns (all centered).

size_cmd : str, optional  
    LaTeX size command applied inside the table (e.g., ``\\small``, ``\\scriptsize``).

Additional Parameters
---------------------
one_color : str, optional  
    (For ``binary_df_to_colored_latex``) LaTeX color name for cells with value 1.

zero_color : str, optional  
    (For ``binary_df_to_colored_latex``) LaTeX background color name for cells  
    with value 0.

floatfmt : str, optional  
    (For ``binary_df_to_colored_latex``) Format string for numeric entries that  
    are not 0/1 (e.g., ``"{:d}"`` or ``"{:.0f}"``).

bold_math_cmd : str, optional  
    (For ``custom_df_to_latex``) Command for bolding inline math in header cells,  
    e.g., ``\\mathbf``, ``\\boldsymbol``, or ``\\bm``. Ensure the corresponding  
    LaTeX package is loaded.

Returns
-------
str  
    A complete LaTeX ``table`` environment (including an inner ``tabular`` and  
    a ``\\resizebox{\\textwidth}{!}{...}`` wrapper) ready to paste into a  
    LaTeX document.

Requirements
------------
- Python packages: ``pandas``, ``numpy``, ``re`` (standard library).
- LaTeX packages:
  - For both functions: ``graphicx`` (for ``\\resizebox``), ``booktabs`` (for ``custom_df_to_latex``).
  - For coloring: ``xcolor`` with the ``table`` option (provides ``\\cellcolor``).  
    Colors such as ``oncell`` and ``white`` must be defined in the preamble.
  - For bold math: ``amsmath``, ``bm``, or any package compatible with ``bold_math_cmd``.

Notes
-----
- Both functions assume the DataFrame columns represent displayable headers.  
  If numeric, they are commonly used as time periods. Pre-formatting is advised.
- ``binary_df_to_colored_latex`` coerces values to integers for coloring.  
  Non-binary values are rendered using ``floatfmt`` but receive no coloring.
- ``custom_df_to_latex`` skips escaping in data cells, assuming LaTeX-safe input.

Examples
--------
Render a binary status matrix with colored cells:

>>> import pandas as pd  
>>> df = pd.DataFrame([[1, 0, 1], [0, 0, 1]])  
>>> tex = binary_df_to_colored_latex(  
...     df,  
...     caption="Hourly U, Y, and W variables",  
...     label="tab:uyw",  
...     one_color="oncell",  
...     zero_color="white",  
...     floatfmt="{:d}"  
... )  
>>> print(tex.splitlines()[0])  
\\begin{table}[!ht]

Render a numeric table with bold headers and math-aware bolding:

>>> df2 = pd.DataFrame(  
...     [[1.0, 2.0], [3.5, 4.25]],  
...     columns=[r"$t=1$", r"\\(t=2\\)"]  
... )  
>>> tex2 = custom_df_to_latex(  
...     df2,  
...     caption="Example Table",  
...     label="tab:example",  
...     bold_math_cmd="\\mathbf"  
... )  
>>> "\\toprule" in tex2  
True

See Also
--------
pandas.DataFrame.to_latex : Built-in (less specialized) LaTeX export.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from NaivePyDESSEM.Utils import *