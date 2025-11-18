"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Module: CLI — Visualization and Export Interface

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module provides a command-line interface (CLI) for inspecting and exporting 
the results of a solved NaivePyDECOMP dispatch model.

The CLI supports both interactive and non-interactive use, allowing users to:

- Export generation and control data as LaTeX tables.
- Generate bar and line plots from selected result categories.
- Save control variables (U, Y, W) as visually annotated LaTeX matrices.

Features
--------
- Supports CSV, Excel, and Parquet input formats.
- Category-based selection of variables (e.g., G, Q, V, S, BAT, cost).
- Automated LaTeX formatting and colored control tables.
- Customizable plot styling, labeling, and output paths.

Categories
----------
- 'G'     : Generation (thermal, renewable, battery)
- 'Q'     : Turbine flow [hydro]
- 'V'     : Volume [hydro]
- 'S'     : Spillage [hydro]
- 'F'     : Transmission Line Power Flow [TransmissionLine]
- 'BAT'   : Battery-specific (charge/discharge/SoC)
- 'CB'    : Connection Bar Variables
- 'LT'    : Transmission Lines Variables
- 'cost'  : Cost components per stage (var, start, deficit)

Dependencies
------------
- pandas
- matplotlib
- colorama
- argparse
- NaivePyDECOMP utilities: plotting, formatting, LaTeX export

Usage
-----
Run via command line:
    $ python plot_cli.py results.csv --mode table --category G cost --out-dir tables

Or interactively:
    $ python plot_cli.py results.parquet

Quick examples
--------------
# 1) Non-interactive: stacked bar plot for Generation + Spillage
python plot_results_cli.py results/day1.parquet \
--mode plot --category G S --plot-style bar --stacked \
--title "Generation & Spillage" --ylabel MW \
--out-dir plots --out-file gen_spill.png


# 2) Non-interactive: LaTeX table for Volume and Costs
python plot_results_cli.py results/day1.csv \
--mode table --category V cost \
--title "Reservoir Volume and Cost Variables" --label tab:vol_cost \
--out-dir tables --out-file vol_cost.tex

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

import argparse
import os
import pandas as pd
from colorama import Fore, Style, init as colorama_init
from NaivePyDECOMP.PlotSeries import plot_series, plot_series_bar
from NaivePyDECOMP.Utils import binary_df_to_colored_latex, custom_df_to_latex


def print_welcome_banner():
    """
    Print a formatted welcome banner with project information and author credit.

    Uses colored and bold text to enhance readability in the terminal.
    """

    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
    print(f"{Fore.YELLOW}{Style.BRIGHT}EELT 7030 — Operation and Expansion Planning of Electric Power Systems")
    print(f"{Fore.YELLOW}Federal University of Paraná (UFPR)\n")
    print(f"{Fore.GREEN}{Style.BRIGHT}NaiveDECOMP-Plot: {Fore.CYAN}Reporting CLI For {Fore.MAGENTA}NaivePyDECOMP Simulations{Style.RESET_ALL}\n")
    print(f"{Fore.BLUE}{Style.BRIGHT}Author: {Fore.WHITE}Augusto Mathias Adams {Fore.BLUE}<augusto.adams@ufpr.br>")
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
   

def prompt(msg: str) -> str:
    """
    Prompt the user for input with a highlighted message.

    If the message ends with "[optional]", the user may press Enter to return an empty string.

    Parameters
    ----------
    msg : str
        The message displayed to the user.

    Returns
    -------
    str
        The user response, stripped of leading and trailing whitespace.
    """

    print(f"{Fore.YELLOW}{msg.strip()}{Style.RESET_ALL}")
    return input("> ").strip()


def load_dataframe(path: str) -> pd.DataFrame:
    """
    Load a pandas DataFrame from a supported file format.

    Supports CSV, Excel (.xlsx, .xls), and Parquet formats. The file extension is used
    to determine the appropriate loader.

    Parameters
    ----------
    path : str
        Full path to the data file.

    Returns
    -------
    pd.DataFrame
        The loaded DataFrame.

    Raises
    ------
    ValueError
        If the file format is not supported.
"""

    ext = os.path.splitext(path)[-1].lower()
    print(f"{Fore.CYAN}Loading file: {path}{Style.RESET_ALL}")
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    elif ext == ".parquet":
        return pd.read_parquet(path)
    else:
        raise ValueError(
            f"{Fore.RED}Unsupported file format: {ext}{Style.RESET_ALL}")


def select_variable_columns(df: pd.DataFrame,
                            category: str) -> pd.DataFrame:
    """
    Filter DataFrame columns based on a single category.

    The function selects columns corresponding to predefined variable categories
    such as generation, flow, storage, control actions, and cost.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing simulation results.
    category : str
        One of: {"G", "Q", "S", "V", "BAT", "CB", "LT", "cost", "CTRL"}.

    Returns
    -------
    pd.DataFrame
        A filtered view of the DataFrame containing only relevant columns.

    Raises
    ------
    ValueError
        If the category is unrecognized.
    """

    if category == "GT":
        return df.filter(regex=r"^(G_|Ge_|Deficit_|Demand_).*")
    elif category == "G":
        return df.filter(regex=r"^(G_|Deficit_).*")
    elif category == "Q":
        return df.filter(regex=r"^Q_.*")
    elif category == "S":
        return df.filter(regex=r"^S_.*")
    elif category == "V":
        return df.filter(regex=r"^V_.*")    
    elif category == "F":
        return df.filter(regex=r"^F_.*")    
    elif category == "CB":
        return df.filter(regex=r"^(\\Theta_|DemandBar_|DeficitBar_).*")
    elif category == "LT":
        return df.filter(regex=r"^(\\Delta_|F_).*")
    elif category == "BAT":
        return df.filter(regex=r"^(D_|C_|E_).*")
    elif category.lower() == "cost":
        return df.filter(regex=r"^(Cost_|CMO|CMA_|FC).*")
    elif category.lower() == "alpha":
        return df.filter(regex=r"^(FCF_\{1\})")    
    elif category.lower() == "alpha_table":
        return df.filter(regex=r"^(FCF_\{1\})")
    elif category.lower() == "zlim":
        return df.filter(regex=r"^(ZSUP|ZINF)")
    else:
        raise ValueError(
            f"{Fore.RED}Unrecognized category: {category}{Style.RESET_ALL}")


def select_columns_multi(df: pd.DataFrame,
                         categories: list[str]) -> pd.DataFrame:
    """
    Filter and concatenate DataFrame columns across multiple categories.

    Avoids column duplication by tracking previously added columns. Used to
    assemble a view of variables spanning multiple categories (e.g., flow and volume).

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing simulation results.
    categories : list of str
        List of category identifiers (e.g., ["G", "S", "V", "cost"]).

    Returns
    -------
    pd.DataFrame
        A DataFrame composed of all selected columns, in order of appearance.

    Raises
    ------
    ValueError
        If no categories are provided.
    """

    if not categories:
        raise ValueError(
            f"{Fore.RED}At least one category must be provided.{Style.RESET_ALL}")
    parts = []
    seen = set()
    for cat in categories:
        sub = select_variable_columns(df, cat)
        cols = [c for c in sub.columns if c not in seen]
        parts.append(sub[cols])
        seen.update(cols)
    return pd.concat(parts, axis=1) if parts else pd.DataFrame(index=df.index)

def handle_table(df: pd.DataFrame,
                 categories: list[str],
                 *,
                 out_dir: str = None,
                 out_file: str = None,
                 caption: str = None,
                 label: str = None):
    """
    Export selected variables as a LaTeX table.

    Filters the DataFrame based on one or more variable categories, formats it into
    LaTeX using custom styling, and saves the result to a file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with simulation results.
    categories : list of str
        One or more category identifiers to include.
    out_dir : str, optional
        Output directory path. Prompted if not provided.
    out_file : str, optional
        Output .tex file name. Prompted if not provided.
    caption : str or None, optional
        Caption for the LaTeX table.
    label : str or None, optional
        LaTeX label for the table.

    Returns
    -------
    None
        Writes the LaTeX table to the specified file.
    """

    out_dir = out_dir or prompt(
        "Enter the output directory for the LaTeX table")
    out_file = out_file or prompt("Enter the output .tex file name")
    caption = caption if caption is not None else prompt(
        "Enter the caption for the LaTeX table [optional]")
    label = label if label is not None else prompt(
        "Enter the label for the LaTeX table [optional]")
    os.makedirs(out_dir, exist_ok=True)
    subset = select_columns_multi(df, categories)
    subset.index = df.index
    kwargs = {}
    if caption:
        kwargs["caption"] = caption
    if label:
        kwargs["label"] = label
    tex = custom_df_to_latex(subset, **kwargs)
    path = os.path.join(out_dir, out_file)
    with open(path, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"{Fore.GREEN}✔ Table saved to:{Style.RESET_ALL} {Fore.CYAN}{path}{Style.RESET_ALL}")


def handle_plot(df: pd.DataFrame,
                categories: list[str],
                *,
                plot_style: str = None,
                stacked: str = None,
                title: str = None,
                ylabel: str = None,
                xlabel: str = None,
                out_dir: str = None,
                out_file: str = None):
    """
    Generate and export plots for selected variable categories.

    Supports both line and bar charts, including stacked bar plots. If not
    fully specified via arguments, the function prompts the user for relevant
    plot metadata and output settings.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing simulation results.
    categories : list of str
        List of category identifiers to include in the plot.
    plot_style : str, optional
        Plot type ("line" or "bar"). Prompted if not provided.
    stacked : bool, optional
        Whether to stack bars (applies only to bar plots).
    title : str, optional
        Title of the plot. Prompted if not provided.
    ylabel : str, optional
        Label for the Y-axis. Prompted if not provided.
    out_dir : str, optional
        Directory to save the plot. Prompted if not provided.
    out_file : str, optional
        File name for the saved image. Prompted if not provided.

    Returns
    -------
    None
        Saves the plot to disk and prints the file location.
    """
    plot_style = (plot_style or prompt("Line or bar plot? (line/bar)")).lower()
    title = title or prompt("Enter the title of the plot [optional]")
    ylabel = ylabel or prompt("Enter the y-axis label [optional]")
    xlabel = xlabel or prompt("Enter the x-axis label [optional]")
    out_dir = out_dir or prompt("Enter the output directory for the figure")
    out_file = out_file or prompt(
        "Enter the output file name (e.g., plot.png)")
    os.makedirs(out_dir, exist_ok=True)
    series = select_columns_multi(df, categories)
    t = df["T"] if "T" in df.columns else df.index
    title_use = title if title else ", ".join(categories)
    ylabel_use = ylabel if ylabel else ", ".join(categories)
    xlabel_use = xlabel if xlabel else ", ".join(categories)
    path = os.path.join(out_dir, out_file)
    if plot_style == "line":
        plot_series(t, series.to_dict(orient="list"),
                    title=title_use, ylabel=ylabel_use, xlabel="Estágio T", file=path)
    elif plot_style == "bar":
        stacked = (stacked if stacked is not None else prompt(
            "Stacked bars? (y/n)").lower() == "y")
        plot_series_bar(t, series.to_dict(orient="list"), title=title_use,
                        ylabel=ylabel_use, xlabel=xlabel_use, file=path, stacked=stacked)
    else:
        print(f"{Fore.RED}Unrecognized plot style.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✔ Figure saved to:{Style.RESET_ALL} {Fore.CYAN}{path}{Style.RESET_ALL}")


def main():
    """
    Command-line interface (CLI) entry point for visualization and export.

    This function enables both interactive and scripted execution modes for exporting
    results from NaivePyDECOMP simulations. It supports the generation of:

    - LaTeX tables for generation, flow, spillage, storage, cost, and control variables.
    - Binary control matrix tables with color-coded LaTeX formatting (U/Y/W).
    - Time-series plots (line or bar, stacked or grouped) for selected variable categories.

    The CLI can be invoked directly via command line with arguments, or interactively
    with user prompts when arguments are omitted.

    Returns
    -------
    None
        Results are saved to disk in the specified format. No value is returned.

    Examples
    --------
    Command-line usage:

        $ python plot_cli.py results.csv --mode table -c G cost --out-dir out --out-file results.tex

    Interactive usage:

        $ python plot_cli.py results.csv
        > Generate table, plot, or CTRL matrix? (table/plot/ctrl)
        > Enter category(ies) separated by spaces (e.g., G S V):
        > ...

    Notes
    -----
    - Categories are case-insensitive. Recognized categories include:
      "G", "Q", "S", "V", "BAT", "cost", "CTRL".
    - For LaTeX export, output directory and file name are required.
    - For plotting, time column 'T' is used if available; otherwise, index is used.
    """

    colorama_init(autoreset=True)
    print_welcome_banner()
    """Main CLI entry point (interactive and non-interactive)."""
    parser = argparse.ArgumentParser(
        description="CLI for visualization/export of NaivePyDECOMP results")
    parser.add_argument(
        "input_file", help="Input file (.csv, .xlsx, .parquet)")
    parser.add_argument("--mode", choices=["table", "plot", "ctrl"],
                        help="Export mode: LaTeX table, plot")
    parser.add_argument("--category", "-c", nargs="+",
                        help="One or more categories (e.g., G GG Q S V BAT cost alpha alpha_table zlim)")
    parser.add_argument(
        "--plot-style", choices=["line", "bar"], help="Plot style")
    parser.add_argument("--stacked", action="store_true",
                        help="Use stacked bars (bar plots only)")
    parser.add_argument("--title", help="Plot title or LaTeX caption")
    parser.add_argument("--ylabel", help="Y-axis label (plots)")
    parser.add_argument("--xlabel", help="X-axis label (plots)")
    parser.add_argument("--out-dir", help="Output directory")
    parser.add_argument(
        "--out-file", help="Output file name (plot image or .tex)")
    parser.add_argument("--label", help="LaTeX label (tables)")
    args = parser.parse_args()
    df = load_dataframe(args.input_file)
    print("Available categories: G (Generation), Q (Turbine flow), S (Spillage), V (Volume), CB (Connection Bars), \n LT (Transmission Lines), COST, BAT, alpha, zlim")
    mode = args.mode or prompt(
        "Generate table, plot, or CTRL matrix? (table/plot/ctrl)").lower()
    categories = [c.upper() for c in (
        args.category or prompt("Enter category(ies) separated by spaces (e.g., G S V):").split())]
    if mode == "table":
        handle_table(df, categories, out_dir=args.out_dir,
                     out_file=args.out_file, caption=args.title, label=args.label)
    elif mode == "plot":
        handle_plot(df, categories, plot_style=args.plot_style, stacked=args.stacked,
                    title=args.title, ylabel=args.ylabel, xlabel=args.xlabel, out_dir=args.out_dir, out_file=args.out_file)
    else:
        print("Unrecognized mode.")

if __name__ == "__main__":
    main()
