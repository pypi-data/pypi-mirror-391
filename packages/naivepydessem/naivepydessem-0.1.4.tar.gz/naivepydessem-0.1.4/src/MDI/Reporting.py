"""
EELT 7030 — Operation and Expansion Planning of Electric Power Systems  
Federal University of Paraná (UFPR)

Utility: Post-Solve Dispatch Summary and Cost Reports

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
This module contains functions to summarize dispatch results after solving
a Pyomo-based optimization problem. It prints total generation, cost breakdowns,
and unit-level summaries for hydropower, thermal, renewable, and storage technologies.

Features:
- Total cost, demand, deficit and thermal cost components.
- Per-unit dispatch summaries with color-enhanced output (via `colorama`).
- Compatible with modular NaivePyDESSEM subsystem architecture.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023  
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

from pyomo.environ import ConcreteModel, value
from typing import Any, Tuple, Dict
from colorama import Fore, Style
from .Formatters import format_brl
from .ModelCheck import *


def __compute_total_generation(model: ConcreteModel) -> float:
    """
    Compute total system generation across all technologies.

    Parameters
    ----------
    model : ConcreteModel
        Solved Pyomo model instance.

    Returns
    -------
    float
        Total generated energy [MWh] across hydro, thermal, renewable, and storage.
    """
    total_generation = 0.0

    if has_generator_model(model):
        total_generation += sum(
            value(model.level_hours[p] * model.gen_P[g, t, p])
            for g in model.GU for t in model.T for p in model.P
        )

    if has_storage_model(model):
        total_generation += sum(value(
            model.level_hours[p] * (
                model.storage_dis[s, t, p] - model.storage_ch[s, t, p]
            ))
            for s in model.SU for t in model.T for p in model.P
        )

    return total_generation


def __compute_investment_cost(model: ConcreteModel) -> float:
    """
    Compute total investment cost.

    Parameters
    ----------
    model : ConcreteModel
        Solved Pyomo model.

    Returns
    -------
    float
        Total investment[$] for building units (geerators and storages).
    """
    total_investment = 0.0
    if has_generator_model(model):
        if model.parcel_investment:
            total_investment += sum(model.discounts[t] * value(model.gen_c_inv[g] * model.gen_x[g, t])
                                    for g in model.GU for t in model.T)
        else:
            total_investment += sum(value(model.discounts[t] * model.gen_c_inv[g] * model.gen_y[g, t])
                                    for g in model.GU for t in model.T)
    if has_storage_model(model):
        if model.parcel_investment:
            total_investment += sum(value(
                model.discounts[t] * model.storage_c_inv[s] * model.storage_x[s, t]) for s in model.SU for t in model.T)
        else:
            total_investment += sum(value(
                model.discounts[t] * model.storage_c_inv[s] * model.storage_y[s, t]) for s in model.SU for t in model.T)
    
    if has_transmission_line_model(model):
        if model.parcel_investment:
            total_investment += sum(value(
                model.discounts[t] * model.lines_c_inv[l] * model.lines_x[l, t]
                )
                for l in model.LT for t in model.T) 
        else:
            total_investment += sum(value(
                model.discounts[t] * model.lines_c_inv[l] * model.lines_y[l, t]
                )
                for l in model.LT for t in model.T)
            
    return total_investment


def __compute_operational_cost(model: ConcreteModel) -> float:
    """
    Compute total operational cost.

    Parameters
    ----------
    model : ConcreteModel
        Solved Pyomo model.

    Returns
    -------
    float
        Total cost[$] for operating units (geerators and storages).
    """
    total_op_cost = 0.0
    if has_generator_model(model):
        total_op_cost += sum(
            value(model.discounts[t] * model.level_hours[p] *
                  model.gen_c_op[g] * model.gen_P[g, t, p]
                  )
            for g in model.GU for t in model.T for p in model.P
        )
    if has_storage_model(model):
        total_op_cost += sum(
            value(model.discounts[t] * model.level_hours[p] * model.storage_c_op[s] * (
                model.storage_ch[s, t, p] + model.storage_dis[s, t, p]
            ))
            for s in model.SU for t in model.T for p in model.P
        )
    if has_transmission_line_model(model):
        total_op_cost += sum(
            value(model.discounts[t] * model.level_hours[p] * model.lines_c_op[l] * model.lines_flow[l, t, p]
                  )
            for l in model.LT for t in model.T for p in model.P
        )
    if has_connection_bar_model(model):

        total_op_cost += sum(
            value(model.discounts[t] * model.level_hours[p] * model.Cdef[b] * model.D[b, t, p]
                  )
            for b in model.CB for t in model.T for p in model.P)

    return total_op_cost


def dispatch_summary(model: ConcreteModel) -> None:
    """
    Print a complete dispatch and cost summary including:
    - Total generation and demand.
    - Deficit and its monetary cost.
    - Thermal cost breakdown (start-up, generation).
    - Overall total cost from the model objective.

    Parameters
    ----------
    model : ConcreteModel
        Solved Pyomo model instance.
    """
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}==================== EXPANSION SUMMARY ===================={Style.RESET_ALL}")
    total_generation = __compute_total_generation(model)
    print(f"  {Fore.CYAN}Total Generation{Style.RESET_ALL}: {Fore.RED}{total_generation:.2f} MWh")
    demand = sum(value(model.level_hours[p] * model.d[b, t, p])
                 for b in model.CB for t in model.T for p in model.P)
    print(
        f"  {Fore.CYAN}Total Demand{Style.RESET_ALL}: {Fore.RED}{demand:.2f} MWh")

    print(
        f"  {Fore.CYAN}Total Investment Cost{Style.RESET_ALL}: {Fore.RED} $ {format_brl(__compute_investment_cost(model))}")

    print(
        f"  {Fore.CYAN}Total Operational Cost{Style.RESET_ALL}: {Fore.RED} $ {format_brl(__compute_operational_cost(model))}")


def generator_dispatch_summary(model: ConcreteModel) -> None:
    """
    Print unit-level generator units generation summary in MWh.

    Parameters
    ----------
    model : ConcreteModel
        Solved Pyomo model with generator subsystem.
    """
    if has_generator_model(model):
        print(f"{Fore.YELLOW}Generator Units Generation:{Style.RESET_ALL}")
        for g in model.GU:
            # Identify line state
            if value(model.gen_x[g, 1]) >= 0.5:
                state = "Existing"
                entry_time = 1
            else:
                state = "Candidate"
                # find first t where y[l,t] = 1
                entry_time = next(
                    (t for t in model.T if hasattr(model, "gen_y") and value(model.gen_y[g, t]) > 0.5),
                    None
                )
            dispatch = sum(value(
                model.level_hours[p] * model.gen_P[g, t, p]) for t in model.T for p in model.P)
            print(
                f"  {Fore.BLUE}{g} ({state}){Style.RESET_ALL}: {Fore.RED}{dispatch:.2f} MWh")
            if entry_time:
                print(f"  {Fore.BLUE}Entry Period (t*):{Style.RESET_ALL} {Fore.MAGENTA}{entry_time}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.BLUE}Entry Period (t*):{Style.RESET_ALL} {Fore.MAGENTA}— never built —{Style.RESET_ALL}")


def storage_dispatch_summary(model: ConcreteModel) -> None:
    """
    Print unit-level storage discharge summary in MWh.

    Parameters
    ----------
    model : ConcreteModel
        Solved Pyomo model with storage subsystem.
    """
    if has_storage_model(model):
        print(f"\n{Fore.YELLOW}Storage Discharge Summary: {Style.RESET_ALL}")
        for s in model.SU:
            # Identify line state
            if value(model.storage_x[s, 1]) >= 0.5:
                state = "Existing"
                entry_time = 1
            else:
                state = "Candidate"
                # find first t where y[l,t] = 1
                entry_time = next(
                    (t for t in model.T if hasattr(model, "storage_y") and value(model.storage_y[s, t]) > 0.5),
                    None
                )
            dispatch = sum(value(
                model.storage_dis[s, t, p] * model.level_hours[p]) for t in model.T for p in model.P)
            print(
                f"  {Fore.MAGENTA}Storage {s} ({state}) - Discharge{Style.RESET_ALL}: {Fore.RED}{dispatch:.2f} MWh")
            dispatch = sum(value(
                model.storage_ch[s, t, p] * model.level_hours[p]) for t in model.T for p in model.P)
            print(
                f"  {Fore.MAGENTA}{s} - Charge{Style.RESET_ALL}: {Fore.RED}{dispatch:.2f} MWh")
            dispatch = sum(
                value((model.storage_dis[s, t, p] - model.storage_ch[s, t, p]) * model.level_hours[p]) for t in model.T for p in model.P)
            print(
                f"  {Fore.MAGENTA}{s} - Delta{Style.RESET_ALL}: {Fore.RED}{dispatch:.2f} MWh")
            if entry_time:
                print(f"  {Fore.BLUE}Entry Period (t*):{Style.RESET_ALL} {Fore.MAGENTA}{entry_time}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.BLUE}Entry Period (t*):{Style.RESET_ALL} {Fore.MAGENTA}— never built —{Style.RESET_ALL}")


def connection_bar_dispatch_summary(model: ConcreteModel) -> None:
    """
    Print a unit-level dispatch summary for each connection bar in MWh.

    Parameters
    ----------
    model : pyomo.environ.ConcreteModel
        A solved Pyomo model containing a valid connection-bar subsystem,
        verified via :func:`has_connection_bar_model`.

    Returns
    -------
    None
        Prints formatted results directly to the console.

    """
    if has_connection_bar_model(model):
        if not model.unique_bar:
            print(f"\n{Fore.YELLOW}Connection Bar Summary Dispatch:{Style.RESET_ALL}")

            for b in model.CB:
                total_demand = sum(value(model.d[b, t, p] * model.level_hours[p]) for t in model.T for p in model.P)
                total_deficit = sum(value(model.D[b, t, p] * model.level_hours[p]) for t in model.T for p in model.P)
                served = total_demand - total_deficit
                avg_angle = 0.0
                if not model.unique_bar:
                    avg_angle = sum(value(model.theta[b, t, p])
                                    for t in model.T for p in model.P) / (len(model.T) + len(model.P))

                print(f"\n{Fore.CYAN}Bar {b}:{Style.RESET_ALL}")
                print(
                    f"  {Fore.BLUE}Demand:{Style.RESET_ALL}   {Fore.RED}{total_demand:.2f} MWh{Style.RESET_ALL}")
                print(
                    f"  {Fore.GREEN}Served:{Style.RESET_ALL}   {Fore.RED}{served:.2f} MWh{Style.RESET_ALL}")
                print(
                    f"  {Fore.MAGENTA}Deficit:{Style.RESET_ALL}  {Fore.RED}{total_deficit:.2f} MWh{Style.RESET_ALL}")
                print(
                    f"  {Fore.YELLOW}Avg θ:{Style.RESET_ALL}     {Fore.RED}{avg_angle:.4f} rad{Style.RESET_ALL}")


def transmission_line_dispatch_summary(model: ConcreteModel) -> None:
    """
    Print a unit-level dispatch summary for each transmission line in MWh.

    Parameters
    ----------
    model : pyomo.environ.ConcreteModel
        A solved Pyomo model containing a valid transmission line subsystem,
        verified via :func:`has_transmission_line_model`.

    Returns
    -------
    None
        Prints formatted results directly to the console.

    """
    if has_transmission_line_model(model):

        print(f"\n{Fore.YELLOW}Transmission Line Summary Dispatch:{Style.RESET_ALL}")

        for l in model.LT:
             # Identify line state
            if value(model.lines_x[l, 1]) >= 0.5:
                state = "Existing"
                entry_time = 1
            else:
                state = "Candidate"
                # find first t where y[l,t] = 1
                entry_time = next(
                    (t for t in model.T if hasattr(model, "lines_y") and value(model.lines_y[l, t]) > 0.5),
                    None
                )
            total_flow = sum(abs(value(model.lines_flow[l, t, p]) * model.level_hours[p]) for t in model.T for p in model.P)
            print(f"\n{Fore.CYAN}Line {l} ({state}):{Style.RESET_ALL}")
            print(
                f"  {Fore.BLUE}Power Flow: {Style.RESET_ALL}   {Fore.RED}{total_flow:.2f} MWh{Style.RESET_ALL}")
            if entry_time:
                print(f"  {Fore.BLUE}Entry Period (t*):{Style.RESET_ALL} {Fore.MAGENTA}{entry_time}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.BLUE}Entry Period (t*):{Style.RESET_ALL} {Fore.MAGENTA}— never built —{Style.RESET_ALL}")
