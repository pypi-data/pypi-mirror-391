"""
Dataframes Module
=================
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Summary
-------
The **Dataframes** module provides structured routines for converting
optimization results from **Pyomo** models into analytical **pandas DataFrames**.
It enables direct visualization and statistical evaluation of dispatch,
cost, and marginal values from the **MDI (Modular Decision Infrastructure)** framework.

Description
-----------
This module acts as a post-processing interface between the optimization
model and external data analysis tools. It extracts primal and dual
values from the **Pyomo ConcreteModel**, computes derived indicators
(e.g., marginal operation cost), and organizes the results into tabular
form suitable for export to spreadsheets, CSV, or visualization software.

Each function contributes a layer of semantic enrichment to the resulting
dataset, corresponding to a subsystem (generation, storage, cost structure).

Functions
---------
add_generator_dispatch_to_dataframe(df, model)
    Extracts generator dispatch, commitment, and investment variables
    from the model and appends them to the provided DataFrame.

add_storage_dispatch_to_dataframe(df, model)
    Extracts storage charge/discharge behavior, state of charge, and
    investment decisions from the model and appends them to the DataFrame.

add_cost_to_dataframe(df, model)
    Computes total operating and investment costs, as well as marginal
    prices such as CMO (Custo Marginal de Operação) and CME (Custo Marginal
    de Expansão). Adds these metrics as new columns to the DataFrame.

build_dispatch_dataframe(model)
    High-level routine that sequentially aggregates generator, storage,
    and cost data into a single unified DataFrame.

Notes
-----
- Requires **pandas ≥ 2.0.0** and **Pyomo ≥ 6.6.0**.
- All numerical values are retrieved through `pyomo.environ.value()`.
- Dual values must be available (i.e., model must have been solved
  with a solver that supports dual variable extraction).
- The notation `CMO` and `CME` corresponds respectively to:
  - *Custo Marginal de Operação* — derived from balance constraints.
  - *Custo Marginal de Expansão* — derived from adequacy constraints.
- Column naming conventions are consistent with the MDI’s export structure
  for integration with visualization dashboards and academic reports.

References
----------
[1] CEPEL, DESSEM. Manual de Metodologia, 2023
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030/UFPR, 2023.
"""

import pandas as pd
from pyomo.environ import ConcreteModel, value
from .ModelCheck import *

from copy import deepcopy
from pyomo.environ import ConcreteModel, SolverFactory, value


def add_generator_dispatch_to_dataframe(df: pd.DataFrame,
                                        model: ConcreteModel) -> pd.DataFrame:
    """
    Append generator dispatch results to a pandas DataFrame.

    This function extracts the generation from a Pyomo model and 
    appends them to the given DataFrame, one column per unit and variable.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to which the results will be appended. It may be empty.
    model : ConcreteModel
        A Pyomo model instance containing generator variables.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame including generator dispatch results.
    """

    if has_generator_model(model):
        T = list(model.T)
        G = list(model.GU)
        P = list(model.P)

        for g in G:
            for p in P:
                ps = r'{' + p + r'}'
                df[f'G_{{{{g_{g}}}{{p_{ps}}}}}'] = [
                    value(model.gen_P[g, t, p]) for t in T]
                df = df.copy()
            df[f'Y_{{g_{g}}}'] = [value(model.gen_y[g, t]) for t in T]
            df[f'X_{{g_{g}}}'] = [value(model.gen_x[g, t]) for t in T]
            df = df.copy() # avoid fragmented DataFrame Warning
    return df


def add_storage_dispatch_to_dataframe(df: pd.DataFrame,
                                      model: ConcreteModel) -> pd.DataFrame:
    """
    Append storage dispatch results to a pandas DataFrame.

    This function extracts charging, discharging, net output,
    and state of charge (SoC) values from the Pyomo model and
    adds them as columns to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to which the results will be appended.
    model : ConcreteModel
        A Pyomo model instance containing storage unit variables.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame including storage dispatch results.
    """

    if has_storage_model(model):
        T = list(model.T)
        S = list(model.SU)
        P = list(model.P)
        for s in S:
            for p in P:
                ps = r'{' + p + r'}'
                df[f'D_{{{{s_{s}}}{{p_{ps}}}}}'] = [
                    value(model.storage_dis[s, t, p] * model.level_hours[p]) for t in T]
                df[f'C_{{{{s_{s}}}{{p_{ps}}}}}'] = [
                    -value(model.storage_ch[s, t, p] * model.level_hours[p]) for t in T]
                df[f'G_{{{{s_{s}}}{{p_{ps}}}}}'] = [
                    value(model.storage_dis[s, t, p] - model.storage_ch[s, t, p]) for t in T]
                df[f'E_{{{{s_{s}}}{{p_{ps}}}}}'] = [
                    value(model.storage_E[s, t, p]) for t in T]
                df = df.copy()
            df[f'Y_{{b_{s}}}'] = [value(model.storage_y[s, t]) for t in T]
            df[f'X_{{b_{s}}}'] = [value(model.storage_x[s, t]) for t in T]
            df = df.copy() # avoid fragmented DataFrame Warning
    return df


def add_transmission_line_dispatch_to_dataframe(df: pd.DataFrame,
                                                model: ConcreteModel) -> pd.DataFrame:
    """
    Append transmission lines flow results to a pandas DataFrame.

    This function extracts transmission lines flow values from the Pyomo model and
    adds them as columns to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to which the results will be appended.
    model : ConcreteModel
        A Pyomo model instance containing transmission lines unit variables.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame including transmission lines flow dispatch results.
    """
    if has_transmission_line_model(model):
        T = list(model.T)
        L = list(model.LT)
        P = list(model.P)
        for l in L:
            i, j = model.lines_endpoints[l]
            for p in P:
                ps = r'{' + p + r'}'
                df[f'F_{{{{LT_{l}}}{{p_{ps}}}}}'] = [
                    value(model.lines_flow[l, t, p]) for t in T]
                df[f'\\Delta_{{\\Theta_{{LT_{l}}}{{p_{ps}}}}}'] = [
                    value(model.theta[i, t, p] - model.theta[j, t, p]) for t in model.T]

                # --- Economic indicators derived from duals ---
                
                # CMO per Transmission Line
                df[f'CMOT_{{{{LT_{l}}}{{p_{ps}}}}}'] = [abs(
                    value(model.dual[model.LinesFlowMaxLimitConstraint[l, t, p]]
                          - model.dual[model.LinesFlowMinLimitConstraint[l, t, p]])) for t in T
                ]

                # CME: CMO + CME_e = \lambda_+ plus \lambda_-
                df[f'CMET_{{{{LT_{l}}}{{p_{ps}}}}}'] = [abs(
                    value(model.dual[model.LinesFlowMaxLimitConstraint[l, t, p]]
                          + model.dual[model.LinesFlowMinLimitConstraint[l, t, p]])) for t in T
                ]

                # CONGESTION RENT
                df[f'CRT_{{{{LT_{l}}}{{p_{ps}}}}}'] = [
                    value((model.dual[model.LinesFlowMaxLimitConstraint[l, t, p]]
                           + model.dual[model.LinesFlowMinLimitConstraint[l, t, p]]) * model.lines_flow[l, t, p]) for t in T
                ]

                # UTILIZATION
                df[f'UR_{{{{LT_{l}}}{{p_{ps}}}}}'] = [
                    value(model.lines_flow[l, t, p]/model.lines_pmax[l]) for t in T
                ]

                df = df.copy() # avoid fragmented DataFrame Warning
            df[f'Y_{{l_{l}}}'] = [value(model.lines_y[l, t]) for t in T]
            df[f'X_{{l_{l}}}'] = [value(model.lines_x[l, t]) for t in T]
            df = df.copy() # avoid fragmented DataFrame Warning
    return df


def add_connection_bar_dispatch_to_dataframe(df: pd.DataFrame,
                                             model: ConcreteModel) -> pd.DataFrame:
    """
    Append connection bar voltage angles and marginal costs (CMO, CME)
    to a pandas DataFrame.

    This function extracts the following quantities from the Pyomo model:
      - Voltage angle θ[b, t, p] for each bar, period, and load level.
      - Marginal Operation Cost (CMO) per bar and period.
      - Marginal Expansion Cost (CME) per bar and period.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to which the results will be appended.
    model : pyomo.environ.ConcreteModel

    Returns
    -------
    pd.DataFrame
        Updated DataFrame including θ, CMO, and CME per bar.
    """

    if has_connection_bar_model(model):
        if not model.unique_bar:
            T = list(model.T)
            B = list(model.CB)
            P = list(model.P)

            for b in B:
                for p in P:
                    ps = r'{' + p + r'}'

                    # θ (phase angle)
                    df[f'\Theta_{{{{CB_{b}}}{{p_{ps}}}}}'] = [
                        value(model.theta[b, t, p]) for t in T
                    ]

                    # CMO: dual of balance constraint for bar b
                    df[f'CMOBar_{{{{CB_{b}}}{{p_{ps}}}}}'] = [
                        value(model.dual[model.Balance[b, t, p]]) for t in T
                    ]

                    # CME: CMO + dual adequacy (system-level effect)
                    df[f'CMEBar_{{{{CB_{b}}}{{p_{ps}}}}}'] = [
                        value(model.dual[model.Balance[b, t, p]]) +
                        value(model.dual[model.Adequacy[t, p]]) for t in T
                    ]
                    df = df.copy() # avoid fragmented DataFrame Warning
    return df


def add_cost_to_dataframe(df: pd.DataFrame,
                          model: ConcreteModel) -> pd.DataFrame:
    """
    Append cost components and total demand/deficit to the DataFrame.

    This function computes and appends the variable generation cost,
    startup cost, deficit cost, and total cost per time period.
    It also includes total generation, demand, and deficit series.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to which cost components will be appended.
    model : ConcreteModel
        A Pyomo model instance with thermal and system-wide cost variables.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame including cost components and energy balance data.
    """

    def compute_average_CMO(model: ConcreteModel) -> dict:
        """
        Compute the time-weighted average marginal operation cost (CMO).

        This function calculates, for each time period `t`, the average
        value of the dual variables associated with the *power balance*
        constraints. The result represents the marginal cost of supplying
        one additional MWh of energy in period `t`, averaged across all
        load levels (`p`) and connection bars (`b`).

        Parameters
        ----------
        model : pyomo.environ.ConcreteModel
            Solved pyomo model

        Returns
        -------
        dict
            Dictionary indexed by `t`, with values in **R$/MWh**, representing
            the time-weighted average marginal operation cost (CMO).

        """
        avg_CMO = {}
        total_hours = sum(model.level_hours[p] for p in model.P)

        for t in model.T:
            weighted_sum = sum(
                value(model.dual[model.Balance[b, t, p]]) *
                model.level_hours[p]
                for b in model.CB for p in model.P
            )
            avg_CMO[t] = weighted_sum / total_hours

        return avg_CMO

    def compute_average_CME(model: ConcreteModel) -> dict:
        """
        Compute the time-weighted average marginal expansion cost (CME).

        The CME is obtained by summing the average CMO and the marginal value
        of the *adequacy constraint*, which enforces long-term system capacity.
        It reflects the total marginal cost of energy supply, combining
        short-term operational effects (CMO) and long-term adequacy effects (CME).

        Parameters
        ----------
        model : pyomo.environ.ConcreteModel
            Solved Pyomo model

        Returns
        -------
        dict
            Dictionary indexed by `t`, with values in **R$/MWh**, representing
            the time-weighted average marginal expansion cost (CME).
        """
        avg_CME = {}
        avg_CMO = compute_average_CMO(model)
        total_hours = sum(model.level_hours[p] for p in model.P)

        for t in model.T:
            weighted_sum = sum(
                value(model.dual[model.Adequacy[t, p]]) for p in model.P)
            avg_CME[t] = avg_CMO[t] + weighted_sum / total_hours

        return avg_CME

    T = list(model.T)

    P = list(model.P)

    generator_generation = {p: [0.0] * len(T) for p in P}

    storage_generation = {p: [0.0] * len(T) for p in P}

    if has_generator_model(model):
        for p in P:
            generator_generation[p] = [sum(value(model.gen_P[g, t, p])
                                           for g in model.GU) for t in model.T]

    if has_storage_model(model):
        for p in P:
            storage_generation[p] = [sum(value(model.storage_dis[s, t, p]
                                               - model.storage_ch[s, t, p])
                                         for s in model.SU) for t in model.T]
    # Totals per level

    for p in P:

        ps = r'{' + p + r'}'
        df[f'Ge_{{Total}}{ps}'] = [x + y for x, y in zip(generator_generation[p],
                                                         storage_generation[p])]

        df[f'Demand_{{Total}}{ps}'] = [sum(value(model.d[b, t, p])
                                           for b in model.CB) for t in T]
        
        df = df.copy() # avoid fragmented DataFrame Warning
        if has_connection_bar_model(model):
            for b in model.CB:
                df[f'DemandBar_{{{{CB_{b}}}{{p_{ps}}}}}'] = [
                    value(model.d[b, t, p]) for t in T]
                df[f'DeficitBar_{{{{CB_{b}}}{{p_{ps}}}}}'] = [
                    value(model.D[b, t, p]) for t in T]
                df = df.copy() # avoid fragmented DataFrame Warning

    cost_var, cost_inv = [], []
    for t in T:
        cost_var_t = 0
        cost_inv_t = 0
        if has_storage_model(model):
            cost_var_t += value(sum(
                # Custo de operação (por energia movimentada)
                model.discounts[t] * model.level_hours[p] * model.storage_c_op[s] * (
                    model.storage_ch[s, t, p] + model.storage_dis[s, t, p]
                )
                for s in model.SU for p in model.P)
            )
            if model.parcel_investment:
                cost_inv_t += value(model.discounts[t] * sum(model.storage_c_inv[s]
                                    * model.storage_x[s, t] for s in model.SU))
            else:
                cost_inv_t += value(sum(model.discounts[t] * model.storage_c_inv[s]
                                    * model.storage_y[s, t] for s in model.SU))
        if has_generator_model(model):
            cost_var_t += value(sum(
                model.discounts[t] * model.level_hours[p] *
                model.gen_c_op[g] * model.gen_P[g, t, p]
                for g in model.GU for p in model.P))

            if model.parcel_investment:
                cost_inv_t += value(model.discounts[t] * sum(model.gen_c_inv[g]
                                    * model.gen_x[g, t] for g in model.GU))
            else:
                cost_inv_t += value(model.discounts[t] * sum(model.gen_c_inv[g]
                                    * model.gen_y[g, t] for g in model.GU))

        if has_transmission_line_model(model):
            cost_var_t += value(sum(
                model.discounts[t] * model.level_hours[p] *
                model.lines_c_op[l] * model.lines_flow[l, t, p]
                for l in model.LT for p in model.P))

            if model.parcel_investment:
                cost_inv_t += value(model.discounts[t] * sum(model.lines_c_inv[l]
                                    * model.lines_x[l, t] for l in model.LT))
            else:
                cost_inv_t += value(model.discounts[t] * sum(model.lines_c_inv[l]
                                    * model.lines_y[l, t] for l in model.GU))

        cost_var.append(cost_var_t)
        cost_inv.append(cost_inv_t)
    df['Cost_{var}'] = cost_var
    df['Cost_{inv}'] = cost_inv
    df['CMO_{avg}'] = compute_average_CMO(model=model)
    df['CME_{avg}'] = compute_average_CME(model=model)
    df = df.copy() # avoid fragmented DataFrame Warning
    return df


def build_dispatch_dataframe(model: ConcreteModel) -> pd.DataFrame:
    """
    Build a full dispatch DataFrame with generation, cost, and balance data.

    This function aggregates the dispatch results from all subsystems
    (hydropower, thermal, renewable, storage) along with cost components
    into a single structured pandas DataFrame.

    Parameters
    ----------
    model : ConcreteModel
        A Pyomo model instance containing subsystem variables and time horizon.

    Returns
    -------
    pd.DataFrame
        A DataFrame with all relevant dispatch results and economic metrics.
    """

    df = pd.DataFrame()
    df = add_storage_dispatch_to_dataframe(df, model)
    df = add_generator_dispatch_to_dataframe(df, model)
    df = add_connection_bar_dispatch_to_dataframe(df, model)
    df = add_transmission_line_dispatch_to_dataframe(df, model)
    df = add_cost_to_dataframe(df, model)
    return df
