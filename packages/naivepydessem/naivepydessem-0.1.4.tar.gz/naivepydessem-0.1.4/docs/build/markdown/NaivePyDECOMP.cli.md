# NaivePyDECOMP.cli package

## Module contents

### NaivePyDECOMP – CLI Subpackage

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Description

This subpackage contains the command-line interface (CLI) utilities for
the **NaivePyDECOMP** project. It enables interactive and scripted execution
of core workflows such as solving dispatch models and visualizing results,
without requiring direct code interaction.

#### Modules

cli.py
: Solver CLI entry point. Loads a YAML case file, builds and solves the model,
  and exports dispatch results to a spreadsheet.

plot_cli.py
: Interactive and scriptable plotting/export interface. Allows users to load
  dispatch data from files, select categories, and export LaTeX tables or
  visual plots (bar or line).

#### Features

- Modular CLI design for pedagogical workflows.
- Integration with Colorama for enhanced terminal output.
- Supports interactive prompts and fully scriptable modes.
- Compatible with  *.csv*,  *.xlsx*, and  *.parquet* formats.
- Export options include LaTeX tables (with styling) and high-quality plots.

#### Example Usage

Solve a dispatch case and export results to CSV:

> $ python -m NaivePyDECOMP.CLI.cli_solve case.yaml –out_dir results –out_file output.csv

Export selected results as LaTeX table and plots:

> $ python -m NaivePyDECOMP.CLI.cli_plot results/output.csv –mode table -c G Q V –out_dir latex –out_file table.tex

### Notes

- The CLI scripts are intended for instructional use in energy systems modeling.
- Users can extend or modify CLI logic to accommodate other workflows or backends.

#### SEE ALSO
[`NaivePyDECOMP.Solver.solve`](NaivePyDECOMP.md#NaivePyDECOMP.Solver.solve)
: Model construction and solving routine.

[`NaivePyDECOMP.DataFrames`](NaivePyDECOMP.md#module-NaivePyDECOMP.DataFrames)
: Functions for assembling dispatch outputs.

[`NaivePyDECOMP.Utils`](NaivePyDECOMP.md#module-NaivePyDECOMP.Utils)
: Formatting, LaTeX, and input helpers.

## Submodules

## NaivePyDECOMP.cli.cli module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Solver cli for NaivePyDECOMP framework

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This script provides a command-line interface (CLI) for solving power system
dispatch problems using the NaivePyDECOMP framework. It loads a structured
YAML configuration file containing the model horizon, demand, and definitions
of thermal, hydro, renewable, and storage units.

Once the Pyomo model is built and solved via the specified solver (e.g., GLPK,
CBC, MindtPy), the resulting dispatch decisions are exported to a tabular
DataFrame and saved to disk in a user-defined format (CSV, Excel, or Parquet).

### Features

- Model construction and solver execution based on *NaivePyDECOMP.Solver*
- Tabular export using *NaivePyDECOMP.DataFrames.build_dispatch_dataframe*
- Interactive or scriptable invocation
- Colorized console output via *colorama* for enhanced readability

### Dependencies

- argparse
- os
- pandas
- colorama
- pyomo.environ
- NaivePyDECOMP.Solver
- NaivePyDECOMP.DataFrames

### Usage

$ python cli.py case.yaml –out_dir results –out_file dispatch.xlsx

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.cli.cli.main()

Command-line interface for solving and exporting dispatch results.

This function serves as the main entry point for the NaivePyDECOMP solver CLI.
It loads an input YAML file describing a power system dispatch problem, builds
and solves the corresponding Pyomo model, and exports the resulting dispatch
data to a structured file format (CSV, Excel, or Parquet).

The output includes generation, storage, and control decisions across all time
steps, organized into a tabular format suitable for post-processing or plotting.

* **Returns:**
  The function performs file I/O and prints summary information to the console.
* **Return type:**
  None

### Notes

- The input YAML file must include sections for at least one of: hydro, thermal,
  renewable, or storage units, along with metadata and demand series.
- The output DataFrame is rounded to zero for absolute values below 1e-3 for clarity.
- Supported file extensions:  *.csv*,  *.xlsx*,  *.xls*,  *.parquet*.

### Examples

$ python cli.py case.yaml –out_dir results –out_file dispatch.xlsx

### NaivePyDECOMP.cli.cli.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

Uses colored and bold text to enhance readability in the terminal.

### NaivePyDECOMP.cli.cli.save_dataframe(df, path)

Save a DataFrame to disk in the format specified by the file extension.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to be saved.
  * **path** (*str*) – The output file path (must end with .csv, .xlsx, or .parquet).
* **Raises:**
  **ValueError** – If the file extension is not supported.

## NaivePyDECOMP.cli.pddd_cli module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Solver cli for NaivePyDECOMP PDDD framework

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This script provides a command-line interface (CLI) for solving power system
dispatch problems using the NaivePyDECOMP framework. It loads a structured
YAML configuration file containing the model horizon, demand, and definitions
of thermal, hydro, renewable, and storage units.

Once the Pyomo model is built and solved via the specified solver (e.g., GLPK,
CBC, MindtPy), the resulting dispatch decisions are exported to a tabular
DataFrame and saved to disk in a user-defined format (CSV, Excel, or Parquet).

### Features

- Model construction and solver execution based on *NaivePyDECOMP.Solver*
- Tabular export using *NaivePyDECOMP.DataFrames.build_dispatch_dataframe*
- Interactive or scriptable invocation
- Colorized console output via *colorama* for enhanced readability

### Dependencies

- argparse
- os
- pandas
- colorama
- pyomo.environ
- NaivePyDECOMP.Solver
- NaivePyDECOMP.DataFrames

### Usage

$ python cli.py case.yaml –out_dir results –out_file dispatch.xlsx

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.cli.pddd_cli.main()

Command-line interface for solving and exporting dispatch results.

This function serves as the main entry point for the NaivePyDECOMP solver CLI.
It loads an input YAML file describing a power system dispatch problem, builds
and solves the corresponding Pyomo model, and exports the resulting dispatch
data to a structured file format (CSV, Excel, or Parquet).

The output includes generation, storage, and control decisions across all time
steps, organized into a tabular format suitable for post-processing or plotting.

* **Returns:**
  The function performs file I/O and prints summary information to the console.
* **Return type:**
  None

### Notes

- The input YAML file must include sections for at least one of: hydro, thermal,
  renewable, or storage units, along with metadata and demand series.
- The output DataFrame is rounded to zero for absolute values below 1e-3 for clarity.
- Supported file extensions:  *.csv*,  *.xlsx*,  *.xls*,  *.parquet*.

### Examples

$ python cli.py case.yaml –out_dir results –out_file dispatch.xlsx

### NaivePyDECOMP.cli.pddd_cli.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

Uses colored and bold text to enhance readability in the terminal.

### NaivePyDECOMP.cli.pddd_cli.save_dataframe(df, path)

Save a DataFrame to disk in the format specified by the file extension.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame to be saved.
  * **path** (*str*) – The output file path (must end with .csv, .xlsx, or .parquet).
* **Raises:**
  **ValueError** – If the file extension is not supported.

## NaivePyDECOMP.cli.plot_cli module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: CLI — Visualization and Export Interface

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides a command-line interface (CLI) for inspecting and exporting
the results of a solved NaivePyDECOMP dispatch model.

The CLI supports both interactive and non-interactive use, allowing users to:

- Export generation and control data as LaTeX tables.
- Generate bar and line plots from selected result categories.
- Save control variables (U, Y, W) as visually annotated LaTeX matrices.

### Features

- Supports CSV, Excel, and Parquet input formats.
- Category-based selection of variables (e.g., G, Q, V, S, BAT, cost).
- Automated LaTeX formatting and colored control tables.
- Customizable plot styling, labeling, and output paths.

### Categories

- ‘G’     : Generation (thermal, renewable, battery)
- ‘Q’     : Turbine flow [hydro]
- ‘V’     : Volume [hydro]
- ‘S’     : Spillage [hydro]
- ‘BAT’   : Battery-specific (charge/discharge/SoC)
- ‘cost’  : Cost components per stage (var, start, deficit)

### Dependencies

- pandas
- matplotlib
- colorama
- argparse
- NaivePyDECOMP utilities: plotting, formatting, LaTeX export

### Usage

Run via command line:
: $ python plot_cli.py results.csv –mode table –category G cost –out-dir tables

Or interactively:
: $ python plot_cli.py results.parquet

### Quick examples

# 1) Non-interactive: stacked bar plot for Generation + Spillage
python plot_results_cli.py results/day1.parquet –mode plot –category G S –plot-style bar –stacked –title “Generation & Spillage” –ylabel MW –out-dir plots –out-file gen_spill.png

# 2) Non-interactive: LaTeX table for Volume and Costs
python plot_results_cli.py results/day1.csv –mode table –category V cost –title “Reservoir Volume and Cost Variables” –label tab:vol_cost –out-dir tables –out-file vol_cost.tex

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### NaivePyDECOMP.cli.plot_cli.handle_plot(df: DataFrame, categories: list[str], \*, plot_style: str | None = None, stacked: str | None = None, title: str | None = None, ylabel: str | None = None, out_dir: str | None = None, out_file: str | None = None)

Generate and export plots for selected variable categories.

Supports both line and bar charts, including stacked bar plots. If not
fully specified via arguments, the function prompts the user for relevant
plot metadata and output settings.

* **Parameters:**
  * **df** (*pd.DataFrame*) – DataFrame containing simulation results.
  * **categories** (*list* *of* *str*) – List of category identifiers to include in the plot.
  * **plot_style** (*str* *,* *optional*) – Plot type (“line” or “bar”). Prompted if not provided.
  * **stacked** (*bool* *,* *optional*) – Whether to stack bars (applies only to bar plots).
  * **title** (*str* *,* *optional*) – Title of the plot. Prompted if not provided.
  * **ylabel** (*str* *,* *optional*) – Label for the Y-axis. Prompted if not provided.
  * **out_dir** (*str* *,* *optional*) – Directory to save the plot. Prompted if not provided.
  * **out_file** (*str* *,* *optional*) – File name for the saved image. Prompted if not provided.
* **Returns:**
  Saves the plot to disk and prints the file location.
* **Return type:**
  None

### NaivePyDECOMP.cli.plot_cli.handle_table(df: DataFrame, categories: list[str], \*, out_dir: str | None = None, out_file: str | None = None, caption: str | None = None, label: str | None = None)

Export selected variables as a LaTeX table.

Filters the DataFrame based on one or more variable categories, formats it into
LaTeX using custom styling, and saves the result to a file.

* **Parameters:**
  * **df** (*pd.DataFrame*) – DataFrame with simulation results.
  * **categories** (*list* *of* *str*) – One or more category identifiers to include.
  * **out_dir** (*str* *,* *optional*) – Output directory path. Prompted if not provided.
  * **out_file** (*str* *,* *optional*) – Output .tex file name. Prompted if not provided.
  * **caption** (*str* *or* *None* *,* *optional*) – Caption for the LaTeX table.
  * **label** (*str* *or* *None* *,* *optional*) – LaTeX label for the table.
* **Returns:**
  Writes the LaTeX table to the specified file.
* **Return type:**
  None

### NaivePyDECOMP.cli.plot_cli.load_dataframe(path: str) → DataFrame

Load a pandas DataFrame from a supported file format.

Supports CSV, Excel (.xlsx, .xls), and Parquet formats. The file extension is used
to determine the appropriate loader.

* **Parameters:**
  **path** (*str*) – Full path to the data file.
* **Returns:**
  The loaded DataFrame.
* **Return type:**
  pd.DataFrame
* **Raises:**
  **ValueError** – If the file format is not supported.

### NaivePyDECOMP.cli.plot_cli.main()

Command-line interface (CLI) entry point for visualization and export.

This function enables both interactive and scripted execution modes for exporting
results from NaivePyDECOMP simulations. It supports the generation of:

- LaTeX tables for generation, flow, spillage, storage, cost, and control variables.
- Binary control matrix tables with color-coded LaTeX formatting (U/Y/W).
- Time-series plots (line or bar, stacked or grouped) for selected variable categories.

The CLI can be invoked directly via command line with arguments, or interactively
with user prompts when arguments are omitted.

* **Returns:**
  Results are saved to disk in the specified format. No value is returned.
* **Return type:**
  None

### Examples

Command-line usage:

> $ python plot_cli.py results.csv –mode table -c G cost –out-dir out –out-file results.tex

Interactive usage:

> $ python plot_cli.py results.csv
> > Generate table, plot, or CTRL matrix? (table/plot/ctrl)
> > Enter category(ies) separated by spaces (e.g., G S V):
> > …

### Notes

- Categories are case-insensitive. Recognized categories include:
  “G”, “Q”, “S”, “V”, “BAT”, “cost”, “CTRL”.
- For LaTeX export, output directory and file name are required.
- For plotting, time column ‘T’ is used if available; otherwise, index is used.

### NaivePyDECOMP.cli.plot_cli.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

Uses colored and bold text to enhance readability in the terminal.

### NaivePyDECOMP.cli.plot_cli.prompt(msg: str) → str

Prompt the user for input with a highlighted message.

If the message ends with “[optional]”, the user may press Enter to return an empty string.

* **Parameters:**
  **msg** (*str*) – The message displayed to the user.
* **Returns:**
  The user response, stripped of leading and trailing whitespace.
* **Return type:**
  str

### NaivePyDECOMP.cli.plot_cli.select_columns_multi(df: DataFrame, categories: list[str]) → DataFrame

Filter and concatenate DataFrame columns across multiple categories.

Avoids column duplication by tracking previously added columns. Used to
assemble a view of variables spanning multiple categories (e.g., flow and volume).

* **Parameters:**
  * **df** (*pd.DataFrame*) – The input DataFrame containing simulation results.
  * **categories** (*list* *of* *str*) – List of category identifiers (e.g., [“G”, “S”, “V”, “cost”]).
* **Returns:**
  A DataFrame composed of all selected columns, in order of appearance.
* **Return type:**
  pd.DataFrame
* **Raises:**
  **ValueError** – If no categories are provided.

### NaivePyDECOMP.cli.plot_cli.select_variable_columns(df: DataFrame, category: str) → DataFrame

Filter DataFrame columns based on a single category.

The function selects columns corresponding to predefined variable categories
such as generation, flow, storage, control actions, and cost.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The input DataFrame containing simulation results.
  * **category** (*str*) – One of: {“G”, “Q”, “S”, “V”, “BAT”, “cost”, “CTRL”}.
* **Returns:**
  A filtered view of the DataFrame containing only relevant columns.
* **Return type:**
  pd.DataFrame
* **Raises:**
  **ValueError** – If the category is unrecognized.
