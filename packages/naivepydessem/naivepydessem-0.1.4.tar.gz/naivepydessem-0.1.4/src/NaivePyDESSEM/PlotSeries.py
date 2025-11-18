"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)


Plotting Utilities for Time Series in Power System Studies

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------

This module provides high-level plotting routines to visualize time-indexed
variables commonly encountered in short-term operation and planning studies
of hydrothermal systems. It offers both line plots and bar plots, supporting
grouped or stacked styles.

Functions
---------
plot_series(t, series_dict, title, ylabel, file)
    Plot one or more time series as line graphs, with LaTeX-compatible labels.

plot_series_bar(t, series_dict, title, ylabel, file, stacked=False, width=0.85)
    Plot multiple time series as bar charts, either grouped or stacked, with
    configurable bar width.

Conventions
-----------
- The time axis is discrete, typically representing hourly stages
  (e.g., t = 1, …, 24).
- Input series must be aligned with the time axis.
- Labels provided in series_dict are rendered in math mode
  to enable LaTeX-style notation in figures.
- Output files are saved with 600 dpi resolution and tight bounding boxes.

Notes
-----
- Figures are generated using Matplotlib and saved to the given file path
  (PNG, PDF, or other supported formats).
- The functions are designed for clarity in academic and technical reports,
  especially when documenting hydrothermal dispatch and unit-commitment results.
- Grid lines, legends, and axis labels are automatically formatted for
  readability.

Examples
--------
Render a simple time series plot:

>>> t = range(1, 5)
>>> data = {"U_{1}": [100, 120, 130, 140], "U_{2}": [90, 110, 125, 150]}
>>> plot_series(t, data, title="Hydropower Generation", ylabel="MW",
...             file="generation.png")

Render a stacked bar plot:

>>> data = {"Hydro": [200, 220, 210], "Thermal": [300, 280, 290]}
>>> t = [1, 2, 3]
>>> plot_series_bar(t, data, title="Generation Mix", ylabel="MW",
...                 file="mix.png", stacked=True)

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""


from typing import List, Dict, Sequence, Tuple, Optional, Union
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cycler
from pyomo.environ import value
import os


def get_distinct_colors(n: int, cmap_name: str = 'tab20') -> list[str]:
    """
    Generate a list of visually distinct colors.

    Parameters
    ----------
    n : int
        Number of colors to generate.
    cmap_name : str, optional
        Name of the Matplotlib colormap to use (default is 'tab10').

    Returns
    -------
    colors : list of str
        List of hex color strings usable in Matplotlib.
    """
    cmap = plt.get_cmap(cmap_name)
    colors = [cmap(i % cmap.N) for i in range(n)]
    return colors


def plot_series(t: Sequence,
                series_dict: Dict[str, Sequence[float]],
                title: str,
                ylabel: str,
                file: str,
                xlabel: str = "Estágio - T (h)") -> None:
    """
    Plot one or more time series as line graphs.

    This function generates a line plot for multiple time-indexed series
    and saves the resulting figure to a file. Each series is drawn with a
    distinct line style and included in the legend. The x-axis represents
    discrete time stages, while the y-axis corresponds to the variable of
    interest (e.g., power, flow, volume).

    Parameters
    ----------
    t : Sequence
        Ordered sequence of time stages to be used as the x-axis values.
    series_dict : Dict[str, Sequence[float]]
        Dictionary mapping labels to numeric sequences. Each sequence must
        have the same length as `t`. Labels may include LaTeX math ($...$).
    title : str
        Title of the plot, displayed at the top of the figure.
    ylabel : str
        Label for the y-axis.    
    xlabel : str
        Label for the x-axis.
    file : str
        Output file path where the figure will be saved (e.g., PNG, PDF).

    Returns
    -------
    None
        The function saves the generated plot to `file`.

    Notes
    -----
    - The figure is sized at 8 * 5 inches and saved at 600 dpi resolution.
    - A grid is shown to facilitate reading values.
    - The legend is automatically constructed from the provided labels.

    Examples
    --------
    >>> t = range(1, 5)
    >>> data = {"U_{1}": [100, 120, 130, 140], "U_{2}": [90, 110, 125, 150]}
    >>> plot_series(t, data, title="Hydropower Generation", ylabel="MW",
    ...             file="generation.png")
    # Saves a line plot with two curves to 'generation.png'.
    """
    def _mathwrap(s: str) -> str:
        s = str(s)
        return s if (s.startswith("$") and s.endswith("$")) else f"${s}$"
    colors = get_distinct_colors(len(series_dict))

    plt.figure(figsize=(8, 5))
    k = 0
    for label, values in series_dict.items():
        plt.plot(t, values, label=_mathwrap(
            label), linewidth=2, color=colors[k])
        k += 1
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(file, dpi=600)
    plt.close()


def plot_series_bar(
    t: Sequence,
    series_dict: Dict[str, Sequence[float]],
    title: str,
    ylabel: str,
    file: str,
    *,
    xlabel: str = "Estágio - T (h)",
    stacked: bool = False,
    width: float = 0.85
) -> None:
    """
    Plot multiple time series as bar charts, either grouped or stacked.

    This function generates a bar chart visualization for a set of time-indexed
    series and saves it to a file. The bars can be rendered side-by-side
    (grouped) or stacked to show composition. Each series is labeled and
    included in the legend. The x-axis corresponds to discrete time stages.

    Parameters
    ----------
    t : Sequence
        Ordered sequence of time stages to be used as x-axis labels.
    series_dict : Dict[str, Sequence[float]]
        Dictionary mapping series labels to their corresponding numeric values.
        All series must have the same length as `t`.
    title : str
        Title of the plot.
    ylabel : str
        Label for the y-axis    
    xlabel : str
        Label for the x-axis.
    file : str
        Output file path where the figure will be saved (e.g., PNG, PDF).
    stacked : bool, optional
        If True, plot stacked bars (suitable for compositional views such as
        generation mix). If False, plot grouped bars. Default is False.
    width : float, optional
        Width of the bars. For grouped mode, this value determines the total
        group width. Default is 0.85.

    Returns
    -------
    None
        The function saves the generated plot to `file`.

    Notes
    -----
    - The output figure is saved with 600 dpi resolution and tight bounding box.
    - When stacked mode is enabled or only a single series is provided,
      values are drawn cumulatively (top of each other).
    - Legend columns are adapted to the number of series.

    Examples
    --------
    >>> t = range(1, 5)
    >>> data = {"A": [1, 2, 3, 4], "B": [2, 3, 4, 5]}
    >>> plot_series_bar(t, data, title="Example", ylabel="MW", file="out.png")
    # Produces and saves a grouped bar chart to 'out.png'.

    >>> plot_series_bar(t, data, title="Stacked", ylabel="MW",
    ...                 file="out_stacked.png", stacked=True)
    # Produces and saves a stacked bar chart to 'out_stacked.png'.
    """
  
    def _mathwrap(s: str) -> str:
        s = str(s)
        return s if (s.startswith("$") and s.endswith("$")) else f"${s}$"

    colors = get_distinct_colors(len(series_dict))

    os.makedirs(os.path.dirname(file) or ".", exist_ok=True)

    labels = list(series_dict.keys())
    data = np.array([series_dict[k] for k in labels], dtype=float)  # (S, T)
    T = len(t)
    S = len(labels)

    fig, ax = plt.subplots(constrained_layout=True, figsize=(8, 5))
    x = np.arange(T)

    if stacked or S == 1:
        # único acumulador: cada barra é somada em sequência
        cum = np.zeros(T, dtype=float)
        for i, lab in enumerate(labels):
            y = data[i]
            ax.bar(
                x,
                y,
                bottom=cum,
                width=width,
                label=_mathwrap(lab),
                color=colors[i]
            )
            cum = cum + y
    else:
        group_width = min(0.95, width)
        bar_w = group_width / max(1, S)
        offsets = (np.arange(S) - (S - 1) / 2.0) * bar_w
        for i, lab in enumerate(labels):
            ax.bar(
                x + offsets[i],
                data[i],
                width=bar_w,
                label=_mathwrap(lab),
                color=colors[i]
            )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y")
    ax.set_xticks(x)
    ax.set_xticklabels([str(tt) for tt in t])

    # legenda fora do gráfico, abaixo da figura
    ncol = 1 if S <= 1 else min(4, S)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=min(4, S)  # até 4 colunas, ajusta automaticamente
    )
    
    fig.savefig(file, dpi=600, bbox_inches="tight")
    plt.close(fig)