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

Use this module as part of the pre-solve interface of NaivePyDESSEM to
provide clarity and visual feedback about the simulation setup.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConcreteModel, value
from typing import Any, Tuple, Dict
from colorama import Fore, Style


def print_welcome_banner():
    """
    Print a formatted welcome banner with project information and author credit.

    Uses colored and bold text to enhance readability in the terminal.
    """

    print(f"{Fore.CYAN}{Style.BRIGHT}" + "=" * 70)
    print(f"{Fore.YELLOW}{Style.BRIGHT}EELT 7030 — Operation and Expansion Planning of Electric Power Systems")
    print(f"{Fore.YELLOW}Federal University of Paraná (UFPR)\n")
    print(f"{Fore.GREEN}{Style.BRIGHT}NaivePyDESSEM: {Style.NORMAL}Mixed Economical Dispatch Solver based on {Fore.MAGENTA}PyOMO{Style.RESET_ALL}")
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
    if 'bars' in case.keys():
        units.append('Connection Bar Units')
    if 'lines' in case.keys():
        units.append('Line Transmission Units')

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
    format_connection_bar_model(case)
    format_line_transmission_model(case)


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
            vmeta = u.get("Vmeta", 0.0)
            mode = u.get("mode", "---")
            compute_total_inflow = u.get("compute_total_inflow", False)
            upstreams = ", ".join(u.get("upstreams", []))
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Qmin, {Fore.BLUE} Value: {Fore.CYAN}{qmin} m³/s")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Qmax, {Fore.BLUE} Value: {Fore.CYAN}{qmax} m³/s")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Vmin, {Fore.BLUE} Value: {Fore.CYAN}{vmin} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Vmax, {Fore.BLUE} Value: {Fore.CYAN}{vmax} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Vini, {Fore.BLUE} Value: {Fore.CYAN}{vini} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Vmeta, {Fore.BLUE} Value: {Fore.CYAN}{vmeta} hm³")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Mode, {Fore.BLUE} Value: {Fore.CYAN}{mode}")
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
            pmin = u.get("Pmin", 0.0)
            pmax = u.get("Pmax", 0.0)
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Pmin, {Fore.BLUE} Value: {Fore.CYAN}{pmin} MW")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Pmax, {Fore.BLUE} Value: {Fore.CYAN}{pmax} MW")


def format_renewable_model(case: Dict) -> None:
    """
    Print formatted information for each renewable generation unit.

    Parameters
    ----------
    case : dict
        Dictionary containing 'renewable' section with unit definitions.
    """
    renewable = case.get('renewable', {})
    renewable_units = renewable.get('units', {})
    if len(renewable_units) > 0:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "=" * 70)
        print(f"{Fore.YELLOW}Renewable Units\n")

        for name, u in renewable_units.items():
            print(f"{Fore.BLUE}{Style.BRIGHT}{name}")


def format_storage_model(case: Dict) -> None:
    """
    Print formatted information for each storage unit.

    Parameters
    ----------
    case : dict
        Dictionary containing 'storage' section with unit definitions.
    """
    storage = case.get('storage', {})
    storage_units = storage.get('units', {})
    if len(storage_units) > 0:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "=" * 70)
        print(f"{Fore.YELLOW}Storage Units\n")

        for name, u in storage_units.items():
            print(f"{Fore.BLUE}{Style.BRIGHT}{name}")
            emin = u.get("Emin", 0.0)
            emax = u.get("Emax", 0.0)
            eini = u.get("Eini", 0.0)
            pch_max = u.get("Pch_max", 0.0)
            pdis_max = u.get("Pdis_max", 0.0)
            eta_c = u.get("eta_c", 0.0)
            eta_d = u.get("eta_d", 0.0)

            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Emin, {Fore.BLUE} Value: {Fore.CYAN}{emin} MWh")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Emax, {Fore.BLUE} Value: {Fore.CYAN}{emax} MWh")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Eini, {Fore.BLUE} Value: {Fore.CYAN}{eini} MWh")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Pch_max, {Fore.BLUE} Value: {Fore.CYAN}{pch_max} MWh")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Pdis_max, {Fore.BLUE} Value: {Fore.CYAN}{pdis_max} MWh")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}eta_c, {Fore.BLUE} Value: {Fore.CYAN}{eta_c}")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}eta_d, {Fore.BLUE} Value: {Fore.CYAN}{eta_d}")


def format_connection_bar_model(case: Dict) -> None:
    """
    Print formatted information for each connection bar unit.

    Parameters
    ----------
    case : dict
        Dictionary containing 'bars' section with unit definitions.
    """
    connection_bars = case.get('bars', {})
    connection_bars_units = connection_bars.get('units', {})
    if len(connection_bars_units) > 0:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "=" * 70)
        print(f"{Fore.YELLOW}Connection Bar Units\n")

        for name, u in connection_bars_units.items():
            print(f"{Fore.BLUE}{Style.BRIGHT}{name}")
            slack = u.get("slack", False)
            cdef = u.get("Cdef", 0.0)
            slack_text = "Yes" if slack else "No"
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Slack Bar?, {Fore.BLUE} Value: {Fore.CYAN}{slack_text}")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Deficit Cost, {Fore.BLUE} Value: \$ {Fore.CYAN}{cdef}")


def format_line_transmission_model(case: Dict) -> None:
    """
    Print formatted information for each transmission line unit.

    Parameters
    ----------
    case : dict
        Dictionary containing 'lines' section with unit definitions.
    """
    transmission_lines = case.get('lines', {})
    transmission_lines_units = transmission_lines.get('units', {})
    if len(transmission_lines_units) > 0:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}" + "=" * 70)
        print(f"{Fore.YELLOW}Transmission Line Units\n")

        for name, u in transmission_lines_units.items():
            print(f"{Fore.BLUE}{Style.BRIGHT}{name}")
            model = u.get("model", False)
            b = u.get("b", 0.0)
            pmax = u.get("pmax", 0.0)
            endpoints = ",".join(u.get("endpoints"))
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Model, {Fore.BLUE} Value: {Fore.CYAN}{model}")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Line Susceptance , {Fore.BLUE} Value: {Fore.CYAN}{b} p.u")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Max Power , {Fore.BLUE} Value: {Fore.CYAN}{pmax} MW")
            print(
                f"      {Fore.BLUE}  Parameter: {Fore.CYAN}Endpoints , {Fore.BLUE} Value: {Fore.CYAN}{endpoints}")
