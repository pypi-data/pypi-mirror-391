"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Utility: Welcome Message and Model Summary Printer

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This utility provides formatted, color-enhanced terminal output using the
`colorama` library to display a welcome banner, solver configuration,
and model characteristics. It is intended to improve the user experience
by offering clear diagnostics and summaries prior to model solving.

Features include:
- Welcome banner with project and author information.
- Display of solver name and strategy.
- Pretty-printed summary of subsystems included in the dispatch problem.
- Parameter visualization for hydraulic, thermal, renewable, and storage units.

Use this module as part of the pre-solve interface of NaivePyDECOMP to
provide clarity and visual feedback about the simulation setup.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConcreteModel, value
from typing import Any, Tuple, Dict
from colorama import Fore, Style
from NaivePyDESSEM.ModelFormatters import (
    format_renewable_model,
    format_storage_model,
    format_connection_bar_model,
    format_line_transmission_model
)


def print_welcome_banner():
    """
    Print a formatted welcome banner with project information and author credit.

    Uses colored and bold text to enhance readability in the terminal.
    """

    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
    print(f"{Fore.YELLOW}{Style.BRIGHT}EELT 7030 — Operation and Expansion Planning of Electric Power Systems")
    print(f"{Fore.YELLOW}Federal University of Paraná (UFPR)\n")
    print(f"{Fore.GREEN}{Style.BRIGHT}NaivePyDECOMP: {Style.NORMAL}Mixed Medium Term Economical Dispatch Solver based on {Fore.MAGENTA}PyOMO{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Author: {Fore.WHITE}{Style.BRIGHT}Augusto Mathias Adams {Fore.BLUE}<augusto.adams@ufpr.br>")


def print_welcome_message(model: ConcreteModel, case: Dict) -> None:
    """
    Display the full welcome message and solver configuration.

    This includes the banner, solver details, and an overview of
    the model components based on the input dictionary.

    Parameters
    ----------
    model : ConcreteModel
        The Pyomo model instance.
    case : dict
        Configuration dictionary loaded from YAML or JSON input.
    """

    print_welcome_banner()
    solver_str = case['meta']['Solver']
    options = case['meta'].get('Solver_Options', {})
    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
    print(
        f"  Solving case: {Fore.YELLOW}{case['meta'].get('name', 'Unnamed')}")
    print(f"  Solver:       {Fore.GREEN}{solver_str}")
    if solver_str == 'mindtpy':
        print(f"{Fore.RED} MindtPy called with options: ")
        for option, option_value in options.items():
            print(
                f" {Fore.BLUE}  Option: {Fore.CYAN}{option}, {Fore.BLUE} Value: {Fore.CYAN}{option_value}")
    format_models(case)


def model_properties(case: Dict) -> None:
    """
    Print a concise list of subsystems included in the case (hydro, thermal, etc.).

    Parameters
    ----------
    case : dict
        Parsed input configuration containing subsystem definitions.
    """

    print(f"{Fore.YELLOW}{Style.BRIGHT}Model Properties")

    units = []
    if 'hydro' in case.keys():
        units.append("Hydraulic Units")
    if 'thermal' in case.keys():
        units.append("Thermal Units")
    if 'renewable' in case.keys():
        units.append("Renewable Units")
    if 'storage' in case.keys():
        units.append('Storage Units')

    units = ", ".join(units)

    print(f" {Fore.BLUE}  Model Units: {Fore.CYAN}{units}")


def format_models(case: Dict) -> None:
    """
    Dispatch model formatting routines to subsystem-specific formatters.

    Parameters
    ----------
    case : dict
        Input data dictionary containing unit-level information.
    """

    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
    model_properties(case)
    format_hydro_model(case)
    format_thermal_model(case)
    format_renewable_model(case)
    format_storage_model(case)


def format_hydro_model(case: Dict) -> None:
    """
    Print formatted information for each hydropower unit.

    Parameters
    ----------
    case : dict
        Dictionary containing 'hydro' section with unit definitions.
    """
    hydro = case.get('hydro', {})
    hydro_units = hydro.get('units', {})
    if len(hydro_units) > 0:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "=" * 70)
        print(f"{Fore.YELLOW}Hydraulic Units\n")

        for name, u in hydro_units.items():
            print(f"{Fore.BLUE}{Style.BRIGHT}{name}")
            qmin = u.get("Qmin", 0.0)
            qmax = u.get("Qmax", 0.0)
            vmin = u.get("Vmin", 0.0)
            vmax = u.get("Vmax", 0.0)
            vini = u.get("Vini", 0.0)
            compute_total_inflow = u.get("compute_total_inflow", False)
            upstreams = ", ".join(u.get("upstreams", []))
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Qmin, {Fore.BLUE} Value: {Fore.CYAN}{qmin} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Qmax, {Fore.BLUE} Value: {Fore.CYAN}{qmax} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Vmin, {Fore.BLUE} Value: {Fore.CYAN}{vmin} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Vmax, {Fore.BLUE} Value: {Fore.CYAN}{vmax} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Vini, {Fore.BLUE} Value: {Fore.CYAN}{vini} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Compute Total Inflow, {Fore.BLUE} Value: {Fore.CYAN}{compute_total_inflow}")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Upstreams, {Fore.BLUE} Value: {Fore.CYAN}{upstreams}")


def format_thermal_model(case: Dict) -> None:
    """
    Print formatted information for each thermal generation unit.

    Parameters
    ----------
    case : dict
        Dictionary containing 'thermal' section with unit definitions.
    """
    thermal = case.get('thermal', {})
    thermal_units = thermal.get('units', {})
    if len(thermal_units) > 0:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "=" * 70)
        print(f"{Fore.YELLOW}Thermal Units\n")

        for name, u in thermal_units.items():
            print(f"{Fore.BLUE}{Style.BRIGHT}{name}")
            gmin = u.get("Gmin", 0.0)
            gmax = u.get("Gmax", 0.0)
            cost = u.get("Cost", 0.0)
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Gmin, {Fore.BLUE} Value: {Fore.CYAN}{gmin} MWmed")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Gmax, {Fore.BLUE} Value: {Fore.CYAN}{gmax} MWmed")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Cost, {Fore.BLUE} Value: {Fore.CYAN}{cost} $/MWh")
