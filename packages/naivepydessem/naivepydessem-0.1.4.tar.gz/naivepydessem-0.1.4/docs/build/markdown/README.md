# NaivePyDESSEM — A Pedagogical and Modular Framework for Hydrothermal Economic Dispatch and Expansion Planning in Pyomo (DESSEM, DECOMP, and MDI-like Solvers)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CI](https://github.com/superflanker/NaivePyDESSEM/actions/workflows/ci.yml/badge.svg)](https://github.com/superflanker/NaivePyDESSEM/actions/workflows/ci.yml)
[![Docs](https://github.com/superflanker/NaivePyDESSEM/actions/workflows/docs.yml/badge.svg)](https://superflanker.github.io/NaivePyDESSEM/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-NaivePyDESSEM-181717?logo=github)](https://github.com/superflanker/NaivePyDESSEM)

**NaivePyDESSEM** is a pedagogical project that brings together **three complementary packages** for teaching and research in power system operation planning:

- **NaivePyDESSEM** — inspired by DESSEM, it models the **short-term** (daily/hourly) operation with detailed individual plant representation.
- **NaivePyDECOMP** — inspired by DECOMP, it models the **medium-term** (weekly/monthly) operation with deterministic dual dynamic programming (PDDD).
- **MDI** — Generation Expansion Planning inspired by **MDI** methodology.

Both are implemented in **Pyomo**, with modular architecture and integrated documentation via Sphinx.

---

## 🔎 Overview

**NaivePyDESSEM** is a pedagogical and modular project that consolidates **three complementary packages** designed for teaching, research, and experimentation in **operation and expansion planning of electric power systems**.<br />
\\\\
The suite draws direct inspiration from the **CEPEL models DESSEM, DECOMP, and MDI**, reinterpreting their conceptual formulations within a transparent, open-source framework based on **Pyomo**.

This initiative seeks to replicate the key methodological elements of the Brazilian **short-term (DESSEM)**, **medium-term (DECOMP)**, and **long-term investment (MDI)** planning models, ensuring consistency with real-world methodologies while maintaining academic accessibility and pedagogical clarity.

---

## ⚙️ Framework Composition

- **NaivePyDESSEM** — A short-term (hourly/daily) **hydrothermal dispatch model**, implementing detailed unit-level formulations for hydro, thermal, renewable, and storage subsystems, analogous to CEPEL’s *DESSEM*.
- **NaivePyDECOMP** — A medium-term (weekly/monthly) **aggregated dispatch model**, incorporating *Deterministic Dual Dynamic Programming (DDDP)* and drawing structural parallels with *DECOMP*.
- **MDI** — A long-term **generation expansion planning model**, representing investment decisions under uncertainty, inspired by the *Investment Decision Model* (MDI) used in national *PDE* studies.

All packages share a common data interface and modeling philosophy, enabling **coherent analysis across temporal horizons** and **integrated experimentation** with energy balance problems.

---

## 🧩 Shared Characteristics

- Modular architecture with standardized builder, solver, and reporting modules.
- Command-line interfaces (CLI) for model execution, reporting, and visualization.
- YAML/JSON-based configuration files for data and scenario specification.
- Seamless interoperability between subsystems (hydro, thermal, renewable, and storage).
- Direct export of results to *Pandas DataFrames*, LaTeX tables, and graphical outputs.
- Full compatibility with **Pyomo**, **NumPy**, **Pandas**, **Matplotlib**, and **Colorama**.

---

## 📘 NaivePyDESSEM Package

### Purpose

The **NaivePyDESSEM** package provides a transparent and instructive framework for the **short-term hydrothermal operation problem**, reproducing the fundamental structure of CEPEL’s *DESSEM*.<br />
\\\\
It enables the formulation, solution, and analysis of **mixed-integer linear and quadratic optimization models**, allowing detailed representation of individual generating units and system-level constraints.

### Core Functionalities

- **Individual Unit Modeling:**<br />
  \\\\
  Comprehensive representation of hydroelectric units (with reservoirs, flows, and variable productivity formulations) and thermal units (linear/quadratic costs, startup/shutdown dynamics, ramping, and minimum up/down times).<br />
  \\\\
  Data classes such as `HydraulicGenerator`, `ThermalGenerator`, `RenewableGenerator`, and `Storage` define the physical and operational parameters.
- **Multi-Technology Dispatch:**<br />
  \\\\
  Incorporates non-dispatchable renewable generation (wind and solar) and storage technologies (state-of-charge tracking, round-trip efficiency).<br />
  \\\\
  Supports the inclusion or omission of subsystems through YAML configuration, enabling modular experimentation.
- **Automated Model Construction:**<br />
  \\\\
  The `Builder` module parses YAML/JSON data via the `YAMLLoader` class and automatically assembles the *Pyomo* model with all constraints and the total cost minimization objective.
- **Post-Solution Analysis:**<br />
  \\\\
  Results are exported to `Pandas DataFrames` and visualized through time-series plots using the `PlotSeries` module.<br />
  \\\\
  The `Formatters` and `Reporting` utilities generate well-structured tabular and graphical summaries for comprehensive cost and dispatch analysis.
- **Command-Line Execution:**<br />
  \\\\
  CLI commands (`pydessem-solve`, `pydessem-plot`) facilitate the execution and visualization of simulation results, ensuring accessibility for educational use.

---

## 📗 NaivePyDECOMP Package

### Purpose

The **NaivePyDECOMP** package mirrors the *DECOMP* model, addressing **medium-term operation planning** through *Deterministic Dual Dynamic Programming (DDDP)* and linear optimization.<br />
\\\\
It provides a modular structure for decomposing long-horizon energy scheduling problems and facilitates analytical exploration of temporal and spatial coupling.

### Core Functionalities

- **Medium-Term Dispatch:**<br />
  \\\\
  Models aggregated hydro and thermal subsystems across extended time horizons.<br />
  \\\\
  Hydroelectric plants are grouped into regional subsystems (REEs) with constant productivity, while thermal generation is modeled through aggregated cost and capacity parameters.
- **DDDP-Based Optimization:**<br />
  \\\\
  Implements both **single-stage linear programming** and **multi-stage decomposition** via the `BuilderPDDD` and `SolverPDDD` modules.<br />
  \\\\
  Enables the generation of future cost functions, convergence limits, and deterministic scenario analyses.
- **Shared Submodules:**<br />
  \\\\
  Adopts a consistent modular structure with `Builder`, `ModelCheck`, `PlotSeries`, `Formatters`, and `Reporting` modules — ensuring interoperability with *NaivePyDESSEM*.
- **CLI and Configurability:**<br />
  \\\\
  Commands such as `pydecomp-solve`, `pydecomp-pddd-solve`, and `pydecomp-plot` simplify experimentation.<br />
  \\\\
  Input data are handled through YAML configuration validated by the `YAMLLoader`.

---

## 📙 MDI Package

### Purpose

The **MDI** package implements a simplified but methodologically coherent framework for **long-term generation expansion planning**, drawing on the *Investment Decision Model (MDI)* used in Brazilian *PDE* studies.<br />
\\\\
It integrates investment and operational decisions into a unified **mixed-integer linear optimization problem**.

### Core Functionalities

- **Investment Planning:**<br />
  \\\\
  Formulates a multi-period optimization problem minimizing investment and operational costs under uncertainty.<br />
  \\\\
  Incorporates candidate projects for thermal, hydro, renewable, and storage technologies, as well as transmission reinforcements.
- **Specialized Submodules:**<br />
  \\\\
  Subpackages `MDI.Generator` and `MDI.Storage` define project-level variables, constraints, and cost components.<br />
  \\\\
  The `Builder` module consolidates these into a system-wide energy balance, while `YAMLLoader` manages structured scenario data.
- **Solution and Analysis:**<br />
  \\\\
  Supports a variety of *Pyomo* solvers (`GLPK`, `CPLEX`, `IPOPT`, `MindtPy`) and provides post-solution tools (`Reporting`, `DataFrames`, `PlotSeries`) for sensitivity and scenario analysis.
- **Educational Design:**<br />
  \\\\
  Preserves the key structural and economic principles of real-world expansion models while maintaining tractability for academic exercises.

---

## 📂 Project Structure

```text
├── examples
│   ├── DECOMP
│   │   ├── trabalho02_caso01.yaml
│   │   ├── trabalho02_caso02.yaml
│   │   ├── trabalho02_caso03.yaml
│   │   └── trabalho02_caso04.yaml
│   ├── DESSEM
│   │   ├── exemplo_despacho_hibrido.yaml
│   │   ├── trabalho01_caso01_1.yaml
│   │   ├── trabalho01_caso01_2.yaml
│   │   ├── trabalho01_caso01_3.yaml
│   │   ├── trabalho01_caso02.yaml
│   │   ├── trabalho01_caso03.yaml
│   │   ├── trabalho01_caso04.yaml
│   │   └── trabalho01_caso05.yaml
│   └── MDI
│       ├── trabalho03_ex01.yaml
│       ├── trabalho03_ex01_anualizado.yaml
│       ├── trabalho03_ex01_anualizado_alternativo.yaml
│       ├── trabalho03_ex02.yaml
│       └── trabalho03_ex02_anualizado.yaml
├── relatorios
│   ├── DECOMP
│   │   ├── caso01
│   │   │   ├── imagens
│   │   │   │   ├── custo_futuro_caso01_pddd.png
│   │   │   │   ├── custos_geracao_caso01_pddd.png
│   │   │   │   ├── custos_geracao_caso01_single_pl.png
│   │   │   │   ├── geracao_caso01_pddd.png
│   │   │   │   ├── geracao_caso01_single_pl.png
│   │   │   │   ├── limites_convergencia_caso01_pddd.png
│   │   │   │   ├── vazao_turbinada_caso01_pddd.png
│   │   │   │   ├── vazao_turbinada_caso01_single_pl.png
│   │   │   │   ├── volume_armazenado_caso01_pddd.png
│   │   │   │   └── volume_armazenado_caso01_single_pl.png
│   │   │   └── tabelas
│   │   │       ├── custos_caso01_pddd.tex
│   │   │       ├── custos_caso01_single_pl.tex
│   │   │       ├── parametros_hidraulicos_caso01_pddd.tex
│   │   │       ├── parametros_hidraulicos_caso01_single_pl.tex
│   │   │       ├── tabela_geracao_caso01_pddd.tex
│   │   │       └── tabela_geracao_caso01_single_pl.tex
│   │   ├── caso02
│   │   │   ├── imagens
│   │   │   │   ├── custo_futuro_caso02_pddd.png
│   │   │   │   ├── custos_geracao_caso02_pddd.png
│   │   │   │   ├── custos_geracao_caso02_single_pl.png
│   │   │   │   ├── geracao_caso02_pddd.png
│   │   │   │   ├── geracao_caso02_single_pl.png
│   │   │   │   ├── limites_convergencia_caso02_pddd.png
│   │   │   │   ├── vazao_turbinada_caso02_pddd.png
│   │   │   │   ├── vazao_turbinada_caso02_single_pl.png
│   │   │   │   ├── volume_armazenado_caso02_pddd.png
│   │   │   │   └── volume_armazenado_caso02_single_pl.png
│   │   │   └── tabelas
│   │   │       ├── custos_caso02_pddd.tex
│   │   │       ├── custos_caso02_single_pl.tex
│   │   │       ├── parametros_hidraulicos_caso02_pddd.tex
│   │   │       ├── parametros_hidraulicos_caso02_single_pl.tex
│   │   │       ├── tabela_geracao_caso02_pddd.tex
│   │   │       └── tabela_geracao_caso02_single_pl.tex
│   │   ├── caso03
│   │   │   ├── imagens
│   │   │   │   ├── carga_descarga_baterias_caso03_pddd.png
│   │   │   │   ├── carga_descarga_baterias_caso03_single_pl.png
│   │   │   │   ├── custo_futuro_caso03_pddd.png
│   │   │   │   ├── custos_geracao_caso03_pddd.png
│   │   │   │   ├── custos_geracao_caso03_single_pl.png
│   │   │   │   ├── geracao_caso03_pddd.png
│   │   │   │   ├── geracao_caso03_single_pl.png
│   │   │   │   ├── limites_convergencia_caso03_pddd.png
│   │   │   │   ├── vazao_turbinada_caso03_pddd.png
│   │   │   │   ├── vazao_turbinada_caso03_single_pl.png
│   │   │   │   ├── volume_armazenado_caso03_pddd.png
│   │   │   │   └── volume_armazenado_caso03_single_pl.png
│   │   │   └── tabelas
│   │   │       ├── carga_descarga_baterias_caso03_pddd.tex
│   │   │       ├── carga_descarga_baterias_caso03_single_pl.tex
│   │   │       ├── custos_caso03_pddd.tex
│   │   │       ├── custos_caso03_single_pl.tex
│   │   │       ├── parametros_hidraulicos_caso03_pddd.tex
│   │   │       ├── parametros_hidraulicos_caso03_single_pl.tex
│   │   │       ├── tabela_geracao_caso03_pddd.tex
│   │   │       └── tabela_geracao_caso03_single_pl.tex
│   │   ├── caso04
│   │   │   ├── imagens
│   │   │   │   ├── carga_descarga_baterias_caso04_pddd.png
│   │   │   │   ├── carga_descarga_baterias_caso04_single_pl.png
│   │   │   │   ├── custo_futuro_caso04_pddd.png
│   │   │   │   ├── custos_geracao_caso04_pddd.png
│   │   │   │   ├── custos_geracao_caso04_single_pl.png
│   │   │   │   ├── geracao_caso04_pddd.png
│   │   │   │   ├── geracao_caso04_single_pl.png
│   │   │   │   ├── limites_convergencia_caso04_pddd.png
│   │   │   │   ├── vazao_turbinada_caso04_pddd.png
│   │   │   │   ├── vazao_turbinada_caso04_single_pl.png
│   │   │   │   ├── volume_armazenado_caso04_pddd.png
│   │   │   │   └── volume_armazenado_caso04_single_pl.png
│   │   │   └── tabelas
│   │   │       ├── carga_descarga_baterias_caso04_pddd.tex
│   │   │       ├── carga_descarga_baterias_caso04_single_pl.tex
│   │   │       ├── custos_caso04_pddd.tex
│   │   │       ├── custos_caso04_single_pl.tex
│   │   │       ├── parametros_hidraulicos_caso04_pddd.tex
│   │   │       ├── parametros_hidraulicos_caso04_single_pl.tex
│   │   │       ├── tabela_geracao_caso04_pddd.tex
│   │   │       └── tabela_geracao_caso04_single_pl.tex
│   │   └── arquivos.txt
│   ├── DESSEM
│   │   └── caso_345
│   │       ├── imagens
│   │       │   ├── carga_descarga_baterias_caso04.png
│   │       │   ├── carga_descarga_baterias_caso05.png
│   │       │   ├── custos_geracao_caso03.png
│   │       │   ├── custos_geracao_caso04.png
│   │       │   ├── custos_geracao_caso05.png
│   │       │   ├── geracao_caso03.png
│   │       │   ├── geracao_caso04.png
│   │       │   ├── geracao_caso05.png
│   │       │   ├── geracao_desempilhada_caso04.png
│   │       │   ├── geracao_desempilhada_caso05.png
│   │       │   ├── vazao_turbinada_caso03.png
│   │       │   ├── vazao_turbinada_caso04.png
│   │       │   ├── vazao_turbinada_caso05.png
│   │       │   ├── volume_armazenado_caso03.png
│   │       │   ├── volume_armazenado_caso04.png
│   │       │   └── volume_armazenado_caso05.png
│   │       ├── controle_termicas_caso03.tex
│   │       ├── controle_termicas_caso04.tex
│   │       ├── controle_termicas_caso05.tex
│   │       ├── custos_caso03.tex
│   │       ├── custos_caso04.tex
│   │       ├── custos_caso05.tex
│   │       ├── parametros_hidraulicos_caso03.tex
│   │       ├── parametros_hidraulicos_caso04.tex
│   │       ├── parametros_hidraulicos_caso05.tex
│   │       ├── tabela_geracao_caso03.tex
│   │       ├── tabela_geracao_caso04.tex
│   │       └── tabela_geracao_caso05.tex
│   └── MDI
│       ├── ex01
│       │   ├── imagens
│       │   │   ├── carga_descarga_baterias_ex01.png
│       │   │   ├── carga_descarga_baterias_ex01_anualizado.png
│       │   │   ├── custos_geracao_ex01.png
│       │   │   ├── custos_geracao_ex01_anualizado.png
│       │   │   ├── geracao_ex01.png
│       │   │   ├── geracao_ex01_anualizado.png
│       │   │   ├── geracao_ex01_anualizado_fora.png
│       │   │   ├── geracao_ex01_anualizado_ponta.png
│       │   │   ├── geracao_ex01_fora.png
│       │   │   └── geracao_ex01_ponta.png
│       │   └── tabelas
│       │       ├── decisoes_ex01.tex
│       │       ├── decisoes_ex01_anualizado.tex
│       │       ├── tabela_custos_ex01.tex
│       │       ├── tabela_custos_ex01_anualizado.tex
│       │       ├── tabela_geracao_ex01.tex
│       │       └── tabela_geracao_ex01_anualizado.tex
│       └── ex02
│           ├── imagens
│           │   ├── carga_descarga_baterias_ex02.png
│           │   ├── carga_descarga_baterias_ex02_anualizado.png
│           │   ├── custos_geracao_ex02.png
│           │   ├── custos_geracao_ex02_anualizado.png
│           │   ├── geracao_ex02.png
│           │   ├── geracao_ex02_anualizado.png
│           │   ├── geracao_ex02_anualizado_fora.png
│           │   ├── geracao_ex02_anualizado_ponta.png
│           │   ├── geracao_ex02_fora.png
│           │   └── geracao_ex02_ponta.png
│           └── tabelas
│               ├── decisoes_ex02.tex
│               ├── decisoes_ex02_anualizado.tex
│               ├── tabela_custos_ex02.tex
│               ├── tabela_custos_ex02_anualizado.tex
│               ├── tabela_geracao_ex02.tex
│               └── tabela_geracao_ex02_anualizado.tex
├── resultados
│   ├── DECOMP
│   │   ├── despacho_caso01_pddd.csv
│   │   ├── despacho_caso01_pddd_alpha.csv
│   │   ├── despacho_caso01_pddd_zlimits.csv
│   │   ├── despacho_caso01_single_pl.csv
│   │   ├── despacho_caso02_pddd.csv
│   │   ├── despacho_caso02_pddd_alpha.csv
│   │   ├── despacho_caso02_pddd_zlimits.csv
│   │   ├── despacho_caso02_single_pl.csv
│   │   ├── despacho_caso03_pddd.csv
│   │   ├── despacho_caso03_pddd_alpha.csv
│   │   ├── despacho_caso03_pddd_zlimits.csv
│   │   ├── despacho_caso03_single_pl.csv
│   │   ├── despacho_caso04.csv
│   │   ├── despacho_caso04_pddd.csv
│   │   ├── despacho_caso04_pddd_alpha.csv
│   │   ├── despacho_caso04_pddd_zlimits.csv
│   │   └── despacho_caso04_single_pl.csv
│   ├── DESSEM
│   │   ├── despacho_caso01_1.csv
│   │   ├── despacho_caso01_2.csv
│   │   ├── despacho_caso01_3.csv
│   │   ├── despacho_caso02.csv
│   │   ├── despacho_caso03.csv
│   │   ├── despacho_caso04.csv
│   │   └── despacho_caso05.csv
│   └── MDI
│       ├── planejamento_expansao_ex01.csv
│       ├── planejamento_expansao_ex01_anualizado.csv
│       ├── planejamento_expansao_ex01_anualizado_alternativo.csv
│       ├── planejamento_expansao_ex02.csv
│       └── planejamento_expansao_ex02_anualizado.csv
├── src
│   ├── MDI
│   │   ├── cli
│   │   │   ├── __init__.py
│   │   │   ├── cli.py
│   │   │   └── plot_cli.py
│   │   ├── Generator
│   │   │   ├── __init__.py
│   │   │   ├── GeneratorBuilder.py
│   │   │   ├── GeneratorConstraints.py
│   │   │   ├── GeneratorDataTypes.py
│   │   │   ├── GeneratorEquations.py
│   │   │   ├── GeneratorObjectives.py
│   │   │   └── GeneratorVars.py
│   │   ├── Storage
│   │   │   ├── __init__.py
│   │   │   ├── StorageBuilder.py
│   │   │   ├── StorageConstraints.py
│   │   │   ├── StorageDataTypes.py
│   │   │   ├── StorageEquations.py
│   │   │   ├── StorageObjective.py
│   │   │   └── StorageVars.py
│   │   ├── __init__.py
│   │   ├── Builder.py
│   │   ├── DataFrames.py
│   │   ├── Formatters.py
│   │   ├── ModelCheck.py
│   │   ├── ModelFormatters.py
│   │   ├── PlotSeries.py
│   │   ├── Reporting.py
│   │   ├── Solver.py
│   │   ├── Utils.py
│   │   └── YAMLLoader.py
│   ├── NaivePyDECOMP
│   │   ├── cli
│   │   │   ├── __init__.py
│   │   │   ├── cli.py
│   │   │   ├── pddd_cli.py
│   │   │   └── plot_cli.py
│   │   ├── HydraulicGenerator
│   │   │   ├── __init__.py
│   │   │   ├── HydraulicConstraints.py
│   │   │   ├── HydraulicDataTypes.py
│   │   │   ├── HydraulicEquations.py
│   │   │   ├── HydraulicGeneratorBuilder.py
│   │   │   ├── HydraulicObjectives.py
│   │   │   ├── HydraulicVars.py
│   │   │   └── SimplifiedConstantProductivityFPH.py
│   │   ├── RenewableGenerator
│   │   │   ├── __init__.py
│   │   │   ├── RenewableConstraints.py
│   │   │   ├── RenewableDataTypes.py
│   │   │   ├── RenewableEquations.py
│   │   │   ├── RenewableGeneratorBuilder.py
│   │   │   ├── RenewableObjectives.py
│   │   │   └── RenewableVars.py
│   │   ├── Storage
│   │   │   ├── __init__.py
│   │   │   ├── StorageBuilder.py
│   │   │   ├── StorageConstraints.py
│   │   │   ├── StorageDataTypes.py
│   │   │   ├── StorageEquations.py
│   │   │   ├── StorageObjective.py
│   │   │   └── StorageVars.py
│   │   ├── ThermalGenerator
│   │   │   ├── __init__.py
│   │   │   ├── ThermalConstraints.py
│   │   │   ├── ThermalDataTypes.py
│   │   │   ├── ThermalEquations.py
│   │   │   ├── ThermalGeneratorBuilder.py
│   │   │   ├── ThermalObjectives.py
│   │   │   └── ThermalVars.py
│   │   ├── __init__.py
│   │   ├── Builder.py
│   │   ├── BuilderPDDD.py
│   │   ├── DataFrames.py
│   │   ├── Formatters.py
│   │   ├── ModelCheck.py
│   │   ├── ModelFormatters.py
│   │   ├── PDDDMergeModels.py
│   │   ├── PlotSeries.py
│   │   ├── Reporting.py
│   │   ├── Solver.py
│   │   ├── SolverPDDD.py
│   │   ├── Utils.py
│   │   └── YAMLLoader.py
│   ├── NaivePyDESSEM
│   │   ├── cli
│   │   │   ├── __init__.py
│   │   │   ├── cli.py
│   │   │   └── plot_cli.py
│   │   ├── HydraulicGenerator
│   │   │   ├── __init__.py
│   │   │   ├── ConstantProductivityFPH.py
│   │   │   ├── ExactFPH.py
│   │   │   ├── HydraulicConstraints.py
│   │   │   ├── HydraulicDataTypes.py
│   │   │   ├── HydraulicEquations.py
│   │   │   ├── HydraulicGeneratorBuilder.py
│   │   │   ├── HydraulicObjectives.py
│   │   │   ├── HydraulicVars.py
│   │   │   ├── PEFPH.py
│   │   │   └── SimplifiedConstantProductivityFPH.py
│   │   ├── RenewableGenerator
│   │   │   ├── __init__.py
│   │   │   ├── RenewableConstraints.py
│   │   │   ├── RenewableDataTypes.py
│   │   │   ├── RenewableEquations.py
│   │   │   ├── RenewableGeneratorBuilder.py
│   │   │   ├── RenewableObjectives.py
│   │   │   └── RenewableVars.py
│   │   ├── Storage
│   │   │   ├── __init__.py
│   │   │   ├── StorageBuilder.py
│   │   │   ├── StorageConstraints.py
│   │   │   ├── StorageDataTypes.py
│   │   │   ├── StorageEquations.py
│   │   │   ├── StorageObjective.py
│   │   │   └── StorageVars.py
│   │   ├── ThermalGenerator
│   │   │   ├── __init__.py
│   │   │   ├── ThermalConstraints.py
│   │   │   ├── ThermalDataTypes.py
│   │   │   ├── ThermalEquations.py
│   │   │   ├── ThermalGeneratorBuilder.py
│   │   │   ├── ThermalObjectives.py
│   │   │   ├── ThermalPieceWise.py
│   │   │   └── ThermalVars.py
│   │   ├── __init__.py
│   │   ├── Builder.py
│   │   ├── DataFrames.py
│   │   ├── Formatters.py
│   │   ├── ModelCheck.py
│   │   ├── ModelFormatters.py
│   │   ├── PlotSeries.py
│   │   ├── Reporting.py
│   │   ├── Solver.py
│   │   ├── Utils.py
│   │   └── YAMLLoader.py
│   └── naivepydessem.egg-info
│       ├── dependency_links.txt
│       ├── entry_points.txt
│       ├── PKG-INFO
│       ├── requires.txt
│       ├── SOURCES.txt
│       └── top_level.txt
├── tests
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── README.md
├── requirements.txt
└── setup.cfg
```

---

## 🛠 Dependencies

The following Python packages are required to run **NaivePyDESSEM**:

| Package      | Version Requirement   | PyPI Link                                          |
|--------------|-----------------------|----------------------------------------------------|
| `colorama`   | `>=0.4.6`             | [colorama](https://pypi.org/project/colorama/)     |
| `matplotlib` | `>=3.10.5`            | [matplotlib](https://pypi.org/project/matplotlib/) |
| `numpy`      | `>=2.2.6`             | [numpy](https://pypi.org/project/numpy/)           |
| `pandas`     | `>=2.3.2`             | [pandas](https://pypi.org/project/pandas/)         |
| `pyomo`      | `>=6.9.3`             | [pyomo](https://pypi.org/project/pyomo/)           |

---

## 🛠  Installation

```bash
pip install naivepydessem
```

Or from source:

```bash
git clone https://github.com/superflanker/NaivePyDESSEM.git
cd NaivePyDESSEM
pip install -e .
```

Similarly, using git ssh clone url:

```bash
git clone git@github.com:superflanker/NaivePyDESSEM.git
cd NaivePyDESSEM
pip install -e .
```

---

## ▶️ Usage

### Solving a model

**DESSEM-like dispatch (short-term)**

```bash
pydessem-solve path/to/case.yaml --out_dir results/ --out_file dispatch.csv
```

**DECOMP-like dispatch (medium-term)**

Single-LP:

```bash
pydecomp-solve path/to/case.yaml --out_dir results/ --out_file dispatch.csv
```

Using PDDD:

```bash
pydecomp-pddsolve path/to/case.yaml --out_dir results/ --out_file dispatch.csv
```

**MDI Like Generation Expansion Planning**

```bash
mdi-solve path/to/case.yaml --out_dir results/ --out_file dispatch.csv
```

---

### Plotting results

```bash
pydessem-plot results/dispatch.csv --mode plot --category G V --plot-style line
```

```bash
pydecomp-plot results/dispatch.csv --mode plot --category G V --plot-style line
```

```bash
mdi-plot results/dispatch.csv --mode plot --category G --plot-style line
```

---

## 📄 References

This implementation is aligned with the pedagogical materials of UFPR (Federal University of Paraná) and official CEPEL/EPE documentation:

- Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030, UFPR, 2023.
- CEPEL. Manual de Metodologia do DESSEM, 2023.
- CEPEL. Modelo DECOMP — Manual de Referência Técnica, 2022.
- EPE. Plano Decenal de Expansão de Energia (PDE) — Metodologia MDI, 2023.

---

## 📚 Documentation

Full API and usage documentation is built with **Sphinx** and available here:<br />
\\\\
👉 [NaivePyDessem Documentation](https://superflanker.github.io/NaivePyDESSEM/)

---

## 📚 How to Cite

If you use **NaivePyDessem** in teaching or research, please cite:

```bibtex
@misc{adams2025naivepydessem,
  author       = {Augusto Mathias Adams},
  title        = {NaivePyDESSEM — A Pedagogical and Modular Framework for Hydrothermal Economic Dispatch and Expansion Planning in Pyomo (DESSEM, DECOMP, and MDI-like Solvers)},
  year         = {2025},
  howpublished = {\url{https://github.com/superflanker/NaivePyDESSEM}}
}
```
