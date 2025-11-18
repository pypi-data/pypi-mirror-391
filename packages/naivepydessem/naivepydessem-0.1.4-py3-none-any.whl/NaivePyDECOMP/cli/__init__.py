"""
NaivePyDECOMP – CLI Subpackage
==============================

EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This subpackage contains the command-line interface (CLI) utilities for
the **NaivePyDECOMP** project. It enables interactive and scripted execution
of core workflows such as solving dispatch models and visualizing results,
without requiring direct code interaction.

Modules
-------
cli.py
    Solver CLI entry point. Loads a YAML case file, builds and solves the model,
    and exports dispatch results to a spreadsheet.

plot_cli.py
    Interactive and scriptable plotting/export interface. Allows users to load
    dispatch data from files, select categories, and export LaTeX tables or
    visual plots (bar or line).

Features
--------
- Modular CLI design for pedagogical workflows.
- Integration with Colorama for enhanced terminal output.
- Supports interactive prompts and fully scriptable modes.
- Compatible with *.csv*, *.xlsx*, and *.parquet* formats.
- Export options include LaTeX tables (with styling) and high-quality plots.

Example Usage
-------------
Solve a dispatch case and export results to CSV:

    $ python -m NaivePyDECOMP.CLI.cli_solve case.yaml --out_dir results --out_file output.csv

Export selected results as LaTeX table and plots:

    $ python -m NaivePyDECOMP.CLI.cli_plot results/output.csv --mode table -c G Q V --out_dir latex --out_file table.tex

Notes
-----
- The CLI scripts are intended for instructional use in energy systems modeling.
- Users can extend or modify CLI logic to accommodate other workflows or backends.

See Also
--------
NaivePyDECOMP.Solver.solve : Model construction and solving routine.
NaivePyDECOMP.DataFrames : Functions for assembling dispatch outputs.
NaivePyDECOMP.Utils : Formatting, LaTeX, and input helpers.
"""
