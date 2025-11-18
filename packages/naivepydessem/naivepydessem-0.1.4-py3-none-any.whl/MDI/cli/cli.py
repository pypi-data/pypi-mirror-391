"""
MDI Command-Line Interface (CLI)
================================

EELT7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
This module provides a command-line interface (CLI) for executing the
MDI (Modular Didactic Infrastructure) optimization framework, which
is based on the NaivePyDESSEM package and implemented using Pyomo.

It enables users to load YAML model definitions, execute the solver,
and export results in various tabular formats. The CLI offers convenient
command-line options for input specification, output management, and
result visualization.

Description
-----------
The CLI is intended primarily for educational and experimental use in
energy system operation and expansion planning. It automates the execution
of the `MDI.Solver` module, the construction of dataframes from model
outputs, and the export of dispatch and cost results.

The module also provides formatted console outputs with color-coded
information using the `colorama` package to improve readability during
interactive execution.

Functions
---------
print_welcome_banner()
    Displays a formatted welcome banner with course and author information.

save_dataframe(df, path)
    Saves a given Pandas DataFrame to a file in one of the supported formats
    (.csv, .xlsx, .xls, .parquet).

main()
    Parses command-line arguments, executes the solver, and exports results
    to the specified directory and file.

Notes
-----
- The CLI uses the `argparse` module for argument parsing.
- Colorized console output is handled via `colorama`.
- The script is typically invoked directly from the terminal, e.g.:

    ```bash
    python -m MDI.cli input_case.yaml --out_dir results --out_file output.csv
    ```

- Compatible with all major operating systems (Windows, macOS, Linux).

References
----------
[1] CEPEL. *DESSEM — Manual de Metodologia*, 2023.  
[2] Unsihuay Vila, C. *Introdução aos Sistemas de Energia Elétrica*,  
    Lecture Notes, EELT7030/UFPR, 2023.
"""

import argparse
import os
from colorama import Fore, Style, init as colorama_init
from MDI.Solver import solve
from MDI.DataFrames import build_dispatch_dataframe
import pandas as pd


def print_welcome_banner():
    """
    Print a formatted welcome banner with project information and author credit.

    The banner includes colorized and bold text for better readability
    in terminal environments. It provides visual emphasis on the
    course title, project name, and author identification.

    Notes
    -----
    - Uses `colorama.Fore` and `colorama.Style` for ANSI color formatting.
    - Automatically resets color after printing via `colorama.init(autoreset=True)`.
    """
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
    print(f"{Fore.YELLOW}{Style.BRIGHT}EELT 7030 — Operation and Expansion Planning of Electric Power Systems")
    print(f"{Fore.YELLOW}Federal University of Paraná (UFPR)\n")
    print(f"{Fore.GREEN}{Style.BRIGHT}MDI: {Fore.CYAN}Gen/Trans Expansion Planning Solver CLI based on {Fore.MAGENTA}PyOMO{Style.RESET_ALL}\n")
    print(f"{Fore.BLUE}Author: {Fore.WHITE}{Style.BRIGHT}Augusto Mathias Adams {Fore.BLUE}<augusto.adams@ufpr.br>")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)


def save_dataframe(df, path):
    """
    Save a Pandas DataFrame to a file in one of the supported formats.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to be exported.
    path : str
        Path (including filename and extension) where the DataFrame
        should be saved. The extension determines the output format.

    Raises
    ------
    ValueError
        If the file extension is not among the supported types
        (.csv, .xlsx, .xls, .parquet).

    Notes
    -----
    - The function automatically determines the export format based
      on the file extension.
    - Supported formats: CSV, Excel, and Parquet.
    - The index is omitted (`index=False`) in all exports.
    """
    ext = os.path.splitext(path)[-1].lower()
    if ext == '.csv':
        df.to_csv(path, index=False)
    elif ext in ['.xlsx', '.xls']:
        df.to_excel(path, index=False)
    elif ext == '.parquet':
        df.to_parquet(path, index=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def main():
    """
    Execute the command-line interface for the MDI framework.

    Parses command-line arguments, initializes the solver, builds
    the dispatch results DataFrame, and exports results to the
    specified output file.

    Workflow
    --------
    1. Initialize color output with `colorama_init()`.
    2. Parse arguments: input YAML, output directory, and output file.
    3. Solve the optimization model using `MDI.Solver.solve()`.
    4. Build results with `MDI.DataFrames.build_dispatch_dataframe()`.
    5. Save results via `save_dataframe()` in the requested format.

    Command-Line Arguments
    ----------------------
    yaml : str
        Path to the YAML input file containing model data and configuration.
    --out_dir : str
        Path to the directory where output files will be stored.
    --out_file : str
        Output file name with extension (.csv, .xlsx, or .parquet).

    Notes
    -----
    - The function automatically creates the output directory if it does not exist.
    - Small numerical artifacts (< 1e-3) are rounded to zero for clarity.
    - The first few rows of the resulting DataFrame are printed to the console.
    """
    colorama_init(autoreset=True)

    parser = argparse.ArgumentParser(
        description=f"{Fore.GREEN}{Style.BRIGHT}MDI CLI: {Style.NORMAL}Generation Expansion Planning CLI based on {Fore.MAGENTA}PyOMO{Style.RESET_ALL}"
    )
    print_welcome_banner()
    parser.add_argument("yaml", help="YAML input file")
    parser.add_argument("--out_dir", required=True,
                        help="Output directory for results")
    parser.add_argument("--out_file", required=True,
                        help="Output file name with extension (.csv, .xlsx, .parquet)")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    output_path = os.path.join(args.out_dir, args.out_file)

    model, data = solve(args.yaml)
    df = build_dispatch_dataframe(model)
    df[abs(df) < 1e-3] = 0.0
    df.fillna(0.0, inplace=True)
    save_dataframe(df, output_path)

    print(f"{Fore.CYAN}Results saved to:{Style.RESET_ALL} {output_path}")


if __name__ == '__main__':
    main()
