# MDI.cli package

## Module contents

### NaivePyDESSEM – CLI Subpackage

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Description

This subpackage contains the command-line interface (CLI) utilities for
the **NaivePyDESSEM** project. It enables interactive and scripted execution
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

> $ python -m NaivePyDESSEM.CLI.cli_solve case.yaml –out_dir results –out_file output.csv

Export selected results as LaTeX table and plots:

> $ python -m NaivePyDESSEM.CLI.cli_plot results/output.csv –mode table -c G Q V –out_dir latex –out_file table.tex

### Notes

- The CLI scripts are intended for instructional use in energy systems modeling.
- Users can extend or modify CLI logic to accommodate other workflows or backends.

#### SEE ALSO
[`NaivePyDESSEM.Solver.solve`](NaivePyDESSEM.md#NaivePyDESSEM.Solver.solve)
: Model construction and solving routine.

[`NaivePyDESSEM.DataFrames`](NaivePyDESSEM.md#module-NaivePyDESSEM.DataFrames)
: Functions for assembling dispatch outputs.

[`NaivePyDESSEM.Utils`](NaivePyDESSEM.md#module-NaivePyDESSEM.Utils)
: Formatting, LaTeX, and input helpers.

## Submodules

## MDI.cli.cli module

### MDI Command-Line Interface (CLI)

EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

#### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

#### Summary

This module provides a command-line interface (CLI) for executing the
MDI (Modular Didactic Infrastructure) optimization framework, which
is based on the NaivePyDESSEM package and implemented using Pyomo.

It enables users to load YAML model definitions, execute the solver,
and export results in various tabular formats. The CLI offers convenient
command-line options for input specification, output management, and
result visualization.

#### Description

The CLI is intended primarily for educational and experimental use in
energy system operation and expansion planning. It automates the execution
of the MDI.Solver module, the construction of dataframes from model
outputs, and the export of dispatch and cost results.

The module also provides formatted console outputs with color-coded
information using the colorama package to improve readability during
interactive execution.

#### Functions

print_welcome_banner()
: Displays a formatted welcome banner with course and author information.

save_dataframe(df, path)
: Saves a given Pandas DataFrame to a file in one of the supported formats
  (.csv, .xlsx, .xls, .parquet).

main()
: Parses command-line arguments, executes the solver, and exports results
  to the specified directory and file.

### Notes

- The CLI uses the argparse module for argument parsing.
- Colorized console output is handled via colorama.
- The script is typically invoked directly from the terminal, e.g.:
  > ``bash
  > python -m MDI.cli input_case.yaml --out_dir results --out_file output.csv
  > ``
- Compatible with all major operating systems (Windows, macOS, Linux).

### References

[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*,

> Lecture Notes, EELT7030/UFPR, 2023.

### MDI.cli.cli.main()

Execute the command-line interface for the MDI framework.

Parses command-line arguments, initializes the solver, builds
the dispatch results DataFrame, and exports results to the
specified output file.

### Workflow

1. Initialize color output with colorama_init().
2. Parse arguments: input YAML, output directory, and output file.
3. Solve the optimization model using MDI.Solver.solve().
4. Build results with MDI.DataFrames.build_dispatch_dataframe().
5. Save results via save_dataframe() in the requested format.

### Command-Line Arguments

yaml
: Path to the YAML input file containing model data and configuration.

–out_dir
: Path to the directory where output files will be stored.

–out_file
: Output file name with extension (.csv, .xlsx, or .parquet).

### Notes

- The function automatically creates the output directory if it does not exist.
- Small numerical artifacts (< 1e-3) are rounded to zero for clarity.
- The first few rows of the resulting DataFrame are printed to the console.

### MDI.cli.cli.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

The banner includes colorized and bold text for better readability
in terminal environments. It provides visual emphasis on the
course title, project name, and author identification.

### Notes

- Uses colorama.Fore and colorama.Style for ANSI color formatting.
- Automatically resets color after printing via colorama.init(autoreset=True).

### MDI.cli.cli.save_dataframe(df, path)

Save a Pandas DataFrame to a file in one of the supported formats.

* **Parameters:**
  * **df** (*pandas.DataFrame*) – The DataFrame to be exported.
  * **path** (*str*) – Path (including filename and extension) where the DataFrame
    should be saved. The extension determines the output format.
* **Raises:**
  **ValueError** – If the file extension is not among the supported types
      (.csv, .xlsx, .xls, .parquet).

### Notes

- The function automatically determines the export format based
  on the file extension.
- Supported formats: CSV, Excel, and Parquet.
- The index is omitted (index=False) in all exports.

## MDI.cli.plot_cli module

EELT 7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: CLI — Visualization and Export Interface

### Author

Augusto Mathias Adams <[augusto.adams@ufpr.br](mailto:augusto.adams@ufpr.br)>

### Description

This module provides a command-line interface (CLI) for inspecting and exporting
the results of a solved NaivePyDESSEM dispatch model.

The CLI supports both interactive and non-interactive use, allowing users to:

- Export generation and control data as LaTeX tables.
- Generate bar and line plots from selected result categories.
- Save control variables (U, Y, W) as visually annotated LaTeX matrices.

### Features

- Supports CSV, Excel, and Parquet input formats.
- Category-based selection of variables (e.g., G, Q, V, S, BAT, cost, CTRL).
- Automated LaTeX formatting and colored control tables.
- Customizable plot styling, labeling, and output paths.

### Categories

- ‘G’     : Generation (thermal, renewable, battery)
- ‘BAT’   : Battery-specific (charge/discharge/SoC)
- ‘cost’  : Cost components per stage
- ‘CTRL’  : Control variables (Y, X)

### Dependencies

- pandas
- matplotlib
- colorama
- argparse
- NaivePyDESSEM utilities: plotting, formatting, LaTeX export

### Usage

Run via command line:
: $ python plot_cli.py results.csv –mode table –category G cost –out-dir tables

Or interactively:
: $ python plot_cli.py results.parquet

### Quick examples

# 1) Non-interactive: stacked bar plot for Generation + Spillage
python plot_results_cli.py results/day1.parquet –mode plot –category G  –plot-style bar –stacked –title “Generation” –ylabel MW –out-dir plots –out-file gen_spill.png

# 2) Non-interactive: LaTeX table for Volume and Costs
python plot_results_cli.py results/day1.csv –mode table –category V cost –title “Reservoir Volume and Cost Variables” –label tab:vol_cost –out-dir tables –out-file vol_cost.tex

# 3) Non-interactive: CTRL matrix (U/Y/W) with custom caption/label
python plot_results_cli.py results/day1.xlsx –mode ctrl –title “Unit Commitment Status” –label tab:uyw –out-dir tables –out-file uyw.tex

### References

[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.

### MDI.cli.plot_cli.handle_control_variables(df: DataFrame, \*, out_dir: str | None = None, out_file: str | None = None, caption: str | None = None, label: str | None = None) → None

Generate and export a colored LaTeX table for binary control variables.

This function prompts the user (if necessary) for export parameters and produces
a LaTeX table that visualizes control variables (U, Y, W) using a binary
color-coded scheme.

* **Parameters:**
  * **df** (*pd.DataFrame*) – The DataFrame containing control variable columns.
  * **out_dir** (*str* *,* *optional*) – Output directory path. Prompted if not provided.
  * **out_file** (*str* *,* *optional*) – Output .tex file name. Prompted if not provided.
  * **caption** (*str* *or* *None* *,* *optional*) – Caption text for the LaTeX table. Prompted if None.
  * **label** (*str* *or* *None* *,* *optional*) – LaTeX label for referencing the table. Prompted if None.
* **Returns:**
  The function saves the LaTeX file to disk and prints the location.
* **Return type:**
  None

### MDI.cli.plot_cli.handle_plot(df: DataFrame, categories: list[str], \*, plot_style: str | None = None, stacked: str | None = None, title: str | None = None, ylabel: str | None = None, out_dir: str | None = None, out_file: str | None = None, level: str | None = None)

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

### MDI.cli.plot_cli.handle_table(df: DataFrame, categories: list[str], \*, out_dir: str | None = None, out_file: str | None = None, caption: str | None = None, label: str | None = None)

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

### MDI.cli.plot_cli.load_dataframe(path: str) → DataFrame

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

### MDI.cli.plot_cli.main()

Command-line interface (CLI) entry point for visualization and export.

This function enables both interactive and scripted execution modes for exporting
results from NaivePyDESSEM simulations. It supports the generation of:

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

> $ python plot_xli.py results.csv –mode table -c G cost –out-dir out –out-file results.tex

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

### MDI.cli.plot_cli.print_welcome_banner()

Print a formatted welcome banner with project information and author credit.

Uses colored and bold text to enhance readability in the terminal.

### MDI.cli.plot_cli.prompt(msg: str) → str

Prompt the user for input with a highlighted message.

If the message ends with “[optional]”, the user may press Enter to return an empty string.

* **Parameters:**
  **msg** (*str*) – The message displayed to the user.
* **Returns:**
  The user response, stripped of leading and trailing whitespace.
* **Return type:**
  str

### MDI.cli.plot_cli.select_columns_multi(df: DataFrame, categories: list[str], level: str | None = None) → DataFrame

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

### MDI.cli.plot_cli.select_variable_columns(df: DataFrame, category: str, level: str | None = None) → DataFrame

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
