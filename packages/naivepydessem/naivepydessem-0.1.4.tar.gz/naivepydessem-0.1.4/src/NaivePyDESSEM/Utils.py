"""
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


import re
import pandas as pd
import numpy as np


def binary_df_to_colored_latex(df: pd.DataFrame,
                               *,
                               caption: str = "Variáveis U, Y e W horárias",
                               label: str = "tab:bin_table",
                               one_color: str = "oncell",
                               zero_color: str = "white",
                               column_format: str = None,
                               floatfmt: str = "{:d}",
                               size_cmd: str = "\\small"
                               ) -> str:
    """
    Convert a binary (0/1) pandas DataFrame into a colored LaTeX table.

    Cells with value 1 are filled using ``\\cellcolor{one_color}``; zeros keep
    the background set by ``zero_color`` (default: white). Row labels are
    automatically wrapped in math mode (``$...$``). The returned string
    contains a complete LaTeX ``table`` environment with an inner ``tabular``.

    Parameters
    ----------
    df : pandas.DataFrame
        Binary matrix to render. The index holds row labels
        (e.g., ``'U_{UT_{1}}'``) and the columns are time steps
        (e.g., ``0..23``).
    caption : str, optional
        Caption to place under the table in LaTeX.
    label : str, optional
        LaTeX label used for ``\\ref{...}``.
    one_color : str, optional
        Name of a LaTeX color (defined in the document preamble) used to
        fill cells equal to 1. Example: ``"oncell"``.
    zero_color : str, optional
        Background color for cells equal to 0 (default: ``"white"``).
    column_format : str or None, optional
        Column specification for the ``tabular`` environment
        (e.g., ``"l*{24}{c}"``). If ``None``, a default is inferred from the
        number of columns.
    floatfmt : str, optional
        Format string used to render numeric entries (e.g., ``"{:d}"``).
    size_cmd : str, optional
        LaTeX size command applied inside the table
        (e.g., ``"\\small"``, ``"\\scriptsize"``).

    Returns
    -------
    str
        LaTeX code for the complete table, ready to paste into your document.

    Notes
    -----
    - Requires ``\\usepackage[table]{xcolor}`` (or a package providing
      ``\\cellcolor``). Also ensure the color given by ``one_color`` is defined
      in the preamble, e.g., ``\\definecolor{oncell}{RGB}{230,240,255}``.
    - The function expects a boolean/binary DataFrame. Values other than 0/1
      are rendered using ``floatfmt`` and will not be colored.
    - Row labels are emitted in math mode: ``$<label>$``.

    Examples
    --------
    >>> latex = binary_df_to_colored_latex(
    ...     df,
    ...     caption="Hourly U, Y and W variables",
    ...     label="tab:uyw",
    ...     one_color="oncell",
    ... )
    >>> print(latex[:30])
    \\begin{table}[ht]
    """

    arr = np.array(df.values, dtype=int)

    def _fmt_col(c):
        try:
            return str(int(c) + 1)
        except Exception:
            return str(c)

    cols = [_fmt_col(c) for c in df.columns]
    if column_format is None:
        column_format = "l" + "c" * len(cols)

    index_header = str(df.index.name) if df.index.name is not None else ""
    header_cells = ["\\textbf{" + index_header + "}"] + \
        [f"\\textbf{{{c}}}" for c in cols]
    header = " & ".join(header_cells) + " \\\\"

    def _mathwrap(s: str) -> str:
        s = str(s)
        return s if (s.startswith("$") and s.endswith("$")) else f"${s}$"

    body_lines = []
    for i in range(arr.shape[0]):
        row_label = _mathwrap(df.index[i])
        cells_tex = []
        for v in arr[i]:
            if v == 1:
                cells_tex.append(
                    f"\\cellcolor{{{one_color}}} \\textcolor{{{one_color}}}{{{floatfmt.format(v)}}}"
                )
            else:
                cells_tex.append(
                    f"\\cellcolor{{{zero_color}}} \\textcolor{{{zero_color}}}{{{floatfmt.format(v)}}}"
                )
        # >>> NOVO: prefixa a linha com o rótulo do índice
        body_lines.append(" & ".join([row_label] + cells_tex) + " \\\\")
    body = "\n".join(body_lines)

    # Monta tabela completa
    latex = []
    latex.append("\\begin{table}[!ht]")
    if size_cmd:
        latex.append(size_cmd)
    latex.append(r"\centering")
    latex.append(f"\\caption{{{caption}}}")
    latex.append(f"\\label{{{label}}}")
    latex.append(r"\resizebox{\textwidth}{!}{")
    latex.append(f"\\begin{{tabular}}{{{column_format}}}")
    latex.append(header)
    latex.append(body)
    latex.append("\\end{tabular}")
    latex.append(r"}")
    latex.append("\\end{table}")
    return "\n".join(latex)


def custom_df_to_latex(df: pd.DataFrame,
                       *,
                       caption: str = "Table",
                       label: str = "tab:table",
                       column_format: str | None = None,
                       size_cmd: str = "\\small",
                       bold_math_cmd: str = "\\mathbf") -> str:
    """
    Render a pandas DataFrame as a LaTeX table with bold header and bold first column.

    This function produces a complete LaTeX ``table`` environment (with
    ``tabular`` inside) using ``booktabs`` rules. The column headers are
    boldfaced. The first column (index) is also boldfaced. Any math-mode
    fragments inside **bolded** cells (i.e., header cells and first-column
    cells) are additionally set in bold math using the chosen command
    (default: ``\\boldsymbol``). Inline math is detected if delimited by
    ``$...$`` or ``\\(...\\)``. Non-math text in bolded cells is wrapped
    with ``\\textbf{...}``.

    Parameters
    ----------
    df : pandas.DataFrame
        Table to render. The DataFrame's index becomes the first (row-label)
        column. The index name (if any) is used for the top-left header cell.
    caption : str, optional
        Caption for the LaTeX table.
    label : str, optional
        LaTeX label used with ``\\ref{...}``.
    column_format : str or None, optional
        Column specification for the ``tabular`` environment. If ``None``,
        it defaults to left alignment for the first column and centered
        alignment for the remaining columns (i.e., ``"l" + "c"*ncols``).
    size_cmd : str, optional
        A LaTeX size command applied inside the table (e.g., ``"\\small"``,
        ``"\\scriptsize"``).
    bold_math_cmd : str, optional
        Command used to bold math fragments (e.g., ``"\\boldsymbol"`` or
        ``"\\bm"``). Ensure the corresponding package is loaded.

    Returns
    -------
    str
        LaTeX code for the complete table, ready to paste into a document.

    Notes
    -----
    - Requires ``\\usepackage{booktabs}`` and a package providing the chosen
      math-bold command (e.g., ``\\usepackage{amsmath}`` for ``\\boldsymbol``,
      or ``\\usepackage{bm}`` for ``\\bm``).
    - Math detection is applied **only** to bolded cells (header and first
      column). Other cells are emitted verbatim (no escaping is performed).
    - If a math fragment is *already* bold (e.g., contains ``\\boldsymbol{...}``
      or ``\\bm{...}`` or ``\\mathbf{...}``), it is left unchanged.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame([[1, 2], [3, 4]], index=[r"$x_1$", r"$x_2$"], columns=["t=1", "t=2"])
    >>> print(df_to_latex_bold_firstcol_header(df, caption="Example", label="tab:ex")[:60])
    \\begin{table}[!ht]
    """
    def _bold_math_fragments(text: str) -> str:
        """Bold every inline math fragment ($...$ or \(...\)) in text using bold_math_cmd."""
        s = str(text)

        def repl_dollar(m: re.Match) -> str:
            inner = m.group(1)
            if any(cmd in inner for cmd in (r"\boldsymbol{", r"\bm{", r"\mathbf{")):
                return f"${inner}$"
            return f"$%s{{{inner}}}$" % bold_math_cmd

        def repl_paren(m: re.Match) -> str:
            inner = m.group(1)
            if any(cmd in inner for cmd in (r"\boldsymbol{", r"\bm{", r"\mathbf{")):
                return r"\(" + inner + r"\)"
            return r"\(" + f"{bold_math_cmd}" + "{" + inner + r"}\)"

        s = re.sub(r"\$(.+?)\$", repl_dollar, s, flags=re.DOTALL)
        s = re.sub(r"\\\((.+?)\\\)", repl_paren, s, flags=re.DOTALL)
        return s

    def _bold_header_cell(s: str) -> str:
        """Bold a header cell, preserving and bolding math fragments."""
        s_bold_math = _bold_math_fragments(str(s))
        return r"\textbf{" + s_bold_math + "}"
    
    def _mathwrap(s: str) -> str:
        s = str(s)
        return s if (s.startswith("$") and s.endswith("$")) else f"${s}$"
    
    ncols = len(df.columns)
    if column_format is None:
        column_format = "c" * ncols  # todas centradas; ajuste para 'l'/'r' se quiser

    header_cells = [_bold_header_cell(_mathwrap(col)) for col in df.columns]

    def _fmt_cell(v):
        if isinstance(v, (int, float, np.integer, np.floating)):
            return f"{v:0.2f}"
        return str(v)

    body_lines = []
    for _, row in df.iterrows():
        row_cells = [_fmt_cell(v) for v in row.values]
        body_lines.append(" & ".join(row_cells) + r" \\")

    latex = []
    latex.append(r"\begin{table}[!ht]")
    if size_cmd:
        latex.append(size_cmd)
    latex.append(r"\centering")
    latex.append(f"\\caption{{{caption}}}")
    latex.append(f"\\label{{{label}}}")
    latex.append(r"\resizebox{\textwidth}{!}{")
    latex.append(f"\\begin{{tabular}}{{{column_format}}}")
    latex.append(r"\toprule")
    latex.append(" & ".join(header_cells) + r" \\")
    latex.append(r"\midrule")
    latex.extend(body_lines)
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"}")
    latex.append(r"\end{table}")
    return "\n".join(latex)
