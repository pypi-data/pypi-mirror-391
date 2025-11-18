"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Solver cli for NaivePyDECOMP PDDD framework

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This script provides a command-line interface (CLI) for solving power system
dispatch problems using the NaivePyDECOMP framework. It loads a structured
YAML configuration file containing the model horizon, demand, and definitions
of thermal, hydro, renewable, and storage units.

Once the Pyomo model is built and solved via the specified solver (e.g., GLPK,
CBC, MindtPy), the resulting dispatch decisions are exported to a tabular
DataFrame and saved to disk in a user-defined format (CSV, Excel, or Parquet).

Features
--------
- Model construction and solver execution based on *NaivePyDECOMP.Solver*
- Tabular export using *NaivePyDECOMP.DataFrames.build_dispatch_dataframe*
- Interactive or scriptable invocation
- Colorized console output via *colorama* for enhanced readability

Dependencies
------------
- argparse
- os
- pandas
- colorama
- pyomo.environ
- NaivePyDECOMP.Solver
- NaivePyDECOMP.DataFrames

Usage
-----
$ python cli.py case.yaml --out_dir results --out_file dispatch.xlsx

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""


import argparse
import os
from colorama import Fore, Style, init as colorama_init
from NaivePyDECOMP.SolverPDDD import solve_pddd
from NaivePyDECOMP.DataFrames import build_dispatch_dataframe
import pandas as pd


def print_welcome_banner():
    """
    Print a formatted welcome banner with project information and author credit.

    Uses colored and bold text to enhance readability in the terminal.
    """

    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
    print(f"{Fore.YELLOW}{Style.BRIGHT}EELT 7030 — Operation and Expansion Planning of Electric Power Systems")
    print(f"{Fore.YELLOW}Federal University of Paraná (UFPR)\n")
    print(f"{Fore.GREEN}{Style.BRIGHT}NaivePyDECOMP-PDDD: {Fore.CYAN}PDDD Solver CLI based on {Fore.MAGENTA}PyOMO{Style.RESET_ALL}\n")
    print(f"{Fore.BLUE}Author: {Fore.WHITE}{Style.BRIGHT}Augusto Mathias Adams {Fore.BLUE}<augusto.adams@ufpr.br>")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
   

def save_dataframe(df, path):
    """
    Save a DataFrame to disk in the format specified by the file extension.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be saved.
    path : str
        The output file path (must end with .csv, .xlsx, or .parquet).

    Raises
    ------
    ValueError
        If the file extension is not supported.
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
    Command-line interface for solving and exporting dispatch results.

    This function serves as the main entry point for the NaivePyDECOMP solver CLI.
    It loads an input YAML file describing a power system dispatch problem, builds
    and solves the corresponding Pyomo model, and exports the resulting dispatch
    data to a structured file format (CSV, Excel, or Parquet).

    The output includes generation, storage, and control decisions across all time
    steps, organized into a tabular format suitable for post-processing or plotting.

    Returns
    -------
    None
        The function performs file I/O and prints summary information to the console.

    Notes
    -----
    - The input YAML file must include sections for at least one of: hydro, thermal,
      renewable, or storage units, along with metadata and demand series.
    - The output DataFrame is rounded to zero for absolute values below 1e-3 for clarity.
    - Supported file extensions: *.csv*, *.xlsx*, *.xls*, *.parquet*.

    Examples
    --------
    $ python cli.py case.yaml --out_dir results --out_file dispatch.xlsx
    """

    colorama_init(autoreset=True)

    parser = argparse.ArgumentParser(
        description=f"{Fore.GREEN}{Style.BRIGHT}NaivePyDECOMP-PDDD CLI: {Style.NORMAL}Solver CLI based on {Fore.MAGENTA}PyOMO{Style.RESET_ALL}"
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

    model, _, alpha_values, z_limits = solve_pddd(args.yaml)
    df = build_dispatch_dataframe(model)
    df[abs(df) < 1e-3] = 0.0
    save_dataframe(df, output_path)

    root, ext = os.path.splitext(args.out_file)
    alpha_filename = f"{root}_alpha{ext}"

    alpha_output_path = os.path.join(args.out_dir, alpha_filename)
    df = pd.DataFrame(alpha_values)
    save_dataframe(df, alpha_output_path)

    z_limits_filename = f"{root}_zlimits{ext}"
    
    z_limits_output_path = os.path.join(args.out_dir, z_limits_filename)
    df = pd.DataFrame(z_limits)
    save_dataframe(df, z_limits_output_path)

    print(f"{Fore.CYAN}Results saved to:{Style.RESET_ALL} {output_path}")
    print(f"{Fore.CYAN}Alpha Results saved to:{Style.RESET_ALL} {alpha_output_path}")
    print(f"{Fore.CYAN}Z Limits Results saved to:{Style.RESET_ALL} {z_limits_output_path}")


if __name__ == '__main__':
    main()
