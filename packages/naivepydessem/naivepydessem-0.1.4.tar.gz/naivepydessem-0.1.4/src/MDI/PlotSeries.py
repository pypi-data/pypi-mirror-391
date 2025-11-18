"""
PlotSeries Module
=================

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
from NaivePyDESSEM.PlotSeries import *