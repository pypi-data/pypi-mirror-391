# NaivePyDESSEM documentation

Official Documentation of NaivePyDESSEM Project — A Pedagogical and Modular Framework for Hydrothermal Economic Dispatch and Expansion Planning in Pyomo (DESSEM, DECOMP, and MDI-like Solvers)

## NaivePyDESSEM — A Pedagogical and Modular Framework for Hydrothermal Economic Dispatch and Expansion Planning in Pyomo (DESSEM, DECOMP, and MDI-like Solvers)

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

### 🔎 Overview

**NaivePyDESSEM** is a pedagogical and modular project that consolidates **three complementary packages** designed for teaching, research, and experimentation in **operation and expansion planning of electric power systems**.
The suite draws direct inspiration from the **CEPEL models DESSEM, DECOMP, and MDI**, reinterpreting their conceptual formulations within a transparent, open-source framework based on **Pyomo**.

This initiative seeks to replicate the key methodological elements of the Brazilian **short-term (DESSEM)**, **medium-term (DECOMP)**, and **long-term investment (MDI)** planning models, ensuring consistency with real-world methodologies while maintaining academic accessibility and pedagogical clarity.

---

### ⚙️ Framework Composition

- **NaivePyDESSEM** — A short-term (hourly/daily) **hydrothermal dispatch model**, implementing detailed unit-level formulations for hydro, thermal, renewable, and storage subsystems, analogous to CEPEL’s *DESSEM*.
- **NaivePyDECOMP** — A medium-term (weekly/monthly) **aggregated dispatch model**, incorporating *Deterministic Dual Dynamic Programming (DDDP)* and drawing structural parallels with *DECOMP*.
- **MDI** — A long-term **generation expansion planning model**, representing investment decisions under uncertainty, inspired by the *Investment Decision Model* (MDI) used in national *PDE* studies.

All packages share a common data interface and modeling philosophy, enabling **coherent analysis across temporal horizons** and **integrated experimentation** with energy balance problems.

---

### 🧩 Shared Characteristics

- Modular architecture with standardized builder, solver, and reporting modules.
- Command-line interfaces (CLI) for model execution, reporting, and visualization.
- YAML/JSON-based configuration files for data and scenario specification.
- Seamless interoperability between subsystems (hydro, thermal, renewable, and storage).
- Direct export of results to *Pandas DataFrames*, LaTeX tables, and graphical outputs.
- Full compatibility with **Pyomo**, **NumPy**, **Pandas**, **Matplotlib**, and **Colorama**.

---

### 📘 NaivePyDESSEM Package

#### Purpose

The **NaivePyDESSEM** package provides a transparent and instructive framework for the **short-term hydrothermal operation problem**, reproducing the fundamental structure of CEPEL’s *DESSEM*.
It enables the formulation, solution, and analysis of **mixed-integer linear and quadratic optimization models**, allowing detailed representation of individual generating units and system-level constraints.

#### Core Functionalities

- **Individual Unit Modeling:**
  Comprehensive representation of hydroelectric units (with reservoirs, flows, and variable productivity formulations) and thermal units (linear/quadratic costs, startup/shutdown dynamics, ramping, and minimum up/down times).
  Data classes such as `HydraulicGenerator`, `ThermalGenerator`, `RenewableGenerator`, and `Storage` define the physical and operational parameters.
- **Multi-Technology Dispatch:**
  Incorporates non-dispatchable renewable generation (wind and solar) and storage technologies (state-of-charge tracking, round-trip efficiency).
  Supports the inclusion or omission of subsystems through YAML configuration, enabling modular experimentation.
- **Automated Model Construction:**
  The `Builder` module parses YAML/JSON data via the `YAMLLoader` class and automatically assembles the *Pyomo* model with all constraints and the total cost minimization objective.
- **Post-Solution Analysis:**
  Results are exported to `Pandas DataFrames` and visualized through time-series plots using the `PlotSeries` module.
  The `Formatters` and `Reporting` utilities generate well-structured tabular and graphical summaries for comprehensive cost and dispatch analysis.
- **Command-Line Execution:**
  CLI commands (`pydessem-solve`, `pydessem-plot`) facilitate the execution and visualization of simulation results, ensuring accessibility for educational use.

---

### 📗 NaivePyDECOMP Package

#### Purpose

The **NaivePyDECOMP** package mirrors the *DECOMP* model, addressing **medium-term operation planning** through *Deterministic Dual Dynamic Programming (DDDP)* and linear optimization.
It provides a modular structure for decomposing long-horizon energy scheduling problems and facilitates analytical exploration of temporal and spatial coupling.

#### Core Functionalities

- **Medium-Term Dispatch:**
  Models aggregated hydro and thermal subsystems across extended time horizons.
  Hydroelectric plants are grouped into regional subsystems (REEs) with constant productivity, while thermal generation is modeled through aggregated cost and capacity parameters.
- **DDDP-Based Optimization:**
  Implements both **single-stage linear programming** and **multi-stage decomposition** via the `BuilderPDDD` and `SolverPDDD` modules.
  Enables the generation of future cost functions, convergence limits, and deterministic scenario analyses.
- **Shared Submodules:**
  Adopts a consistent modular structure with `Builder`, `ModelCheck`, `PlotSeries`, `Formatters`, and `Reporting` modules — ensuring interoperability with *NaivePyDESSEM*.
- **CLI and Configurability:**
  Commands such as `pydecomp-solve`, `pydecomp-pddd-solve`, and `pydecomp-plot` simplify experimentation.
  Input data are handled through YAML configuration validated by the `YAMLLoader`.

---

### 📙 MDI Package

#### Purpose

The **MDI** package implements a simplified but methodologically coherent framework for **long-term generation expansion planning**, drawing on the *Investment Decision Model (MDI)* used in Brazilian *PDE* studies.
It integrates investment and operational decisions into a unified **mixed-integer linear optimization problem**.

#### Core Functionalities

- **Investment Planning:**
  Formulates a multi-period optimization problem minimizing investment and operational costs under uncertainty.
  Incorporates candidate projects for thermal, hydro, renewable, and storage technologies, as well as transmission reinforcements.
- **Specialized Submodules:**
  Subpackages `MDI.Generator` and `MDI.Storage` define project-level variables, constraints, and cost components.
  The `Builder` module consolidates these into a system-wide energy balance, while `YAMLLoader` manages structured scenario data.
- **Solution and Analysis:**
  Supports a variety of *Pyomo* solvers (`GLPK`, `CPLEX`, `IPOPT`, `MindtPy`) and provides post-solution tools (`Reporting`, `DataFrames`, `PlotSeries`) for sensitivity and scenario analysis.
- **Educational Design:**
  Preserves the key structural and economic principles of real-world expansion models while maintaining tractability for academic exercises.

---

### 📂 Project Structure

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

### 🛠 Dependencies

The following Python packages are required to run **NaivePyDESSEM**:

| Package      | Version Requirement   | PyPI Link                                          |
|--------------|-----------------------|----------------------------------------------------|
| `colorama`   | `>=0.4.6`             | [colorama](https://pypi.org/project/colorama/)     |
| `matplotlib` | `>=3.10.5`            | [matplotlib](https://pypi.org/project/matplotlib/) |
| `numpy`      | `>=2.2.6`             | [numpy](https://pypi.org/project/numpy/)           |
| `pandas`     | `>=2.3.2`             | [pandas](https://pypi.org/project/pandas/)         |
| `pyomo`      | `>=6.9.3`             | [pyomo](https://pypi.org/project/pyomo/)           |

---

### 🛠  Installation

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

### ▶️ Usage

#### Solving a model

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

#### Plotting results

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

### 📄 References

This implementation is aligned with the pedagogical materials of UFPR (Federal University of Paraná) and official CEPEL/EPE documentation:

- Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica, Lecture Notes, EELT7030, UFPR, 2023.
- CEPEL. Manual de Metodologia do DESSEM, 2023.
- CEPEL. Modelo DECOMP — Manual de Referência Técnica, 2022.
- EPE. Plano Decenal de Expansão de Energia (PDE) — Metodologia MDI, 2023.

---

### 📚 Documentation

Full API and usage documentation is built with **Sphinx** and available here:
👉 [NaivePyDessem Documentation](https://superflanker.github.io/NaivePyDESSEM/)

---

### 📚 How to Cite

If you use **NaivePyDessem** in teaching or research, please cite:

```bibtex
@misc{adams2025naivepydessem,
  author       = {Augusto Mathias Adams},
  title        = {NaivePyDESSEM — A Pedagogical and Modular Framework for Hydrothermal Economic Dispatch and Expansion Planning in Pyomo (DESSEM, DECOMP, and MDI-like Solvers)},
  year         = {2025},
  howpublished = {\url{https://github.com/superflanker/NaivePyDESSEM}}
}
```

# Main modules (DESSEM/DECOMP/MDI):

* [DESSEM/DECOMP/MDI](modules.md)
  * [NaivePyDESSEM package](NaivePyDESSEM.md)
    * [Module contents](NaivePyDESSEM.md#module-NaivePyDESSEM)
      * [Author](NaivePyDESSEM.md#author)
      * [Description](NaivePyDESSEM.md#description)
      * [Submodules](NaivePyDESSEM.md#submodules)
    * [Subpackages](NaivePyDESSEM.md#subpackages)
      * [NaivePyDESSEM.HydraulicGenerator package](NaivePyDESSEM.HydraulicGenerator.md)
        * [Module contents](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator)
          * [Author](NaivePyDESSEM.HydraulicGenerator.md#author)
          * [Description](NaivePyDESSEM.HydraulicGenerator.md#description)
          * [Submodules](NaivePyDESSEM.HydraulicGenerator.md#submodules)
        * [Submodules](NaivePyDESSEM.HydraulicGenerator.md#id1)
        * [NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH)
          * [Author](NaivePyDESSEM.HydraulicGenerator.md#id2)
          * [Description](NaivePyDESSEM.HydraulicGenerator.md#id3)
          * [`constant_productivity_fph()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ConstantProductivityFPH.constant_productivity_fph)
        * [NaivePyDESSEM.HydraulicGenerator.ExactFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.ExactFPH)
          * [Author](NaivePyDESSEM.HydraulicGenerator.md#id4)
          * [Description](NaivePyDESSEM.HydraulicGenerator.md#id5)
          * [`fph_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ExactFPH.fph_factory)
          * [`polynomial_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ExactFPH.polynomial_factory)
          * [`rho_colina_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.ExactFPH.rho_colina_factory)
        * [NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints)
          * [Hydropower Constraints Module for Multi-Mode Generation Modeling](NaivePyDESSEM.HydraulicGenerator.md#hydropower-constraints-module-for-multi-mode-generation-modeling)
          * [`add_hydro_balance_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_balance_constraint)
          * [`add_hydro_generation_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_generation_constraint)
          * [`add_hydro_qmax_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_qmax_constraint)
          * [`add_hydro_qmin_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_qmin_constraint)
          * [`add_hydro_volume_continuity_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_continuity_constraint)
          * [`add_hydro_volume_max_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_max_constraint)
          * [`add_hydro_volume_meta_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_meta_constraint)
          * [`add_hydro_volume_mim_constraint()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_mim_constraint)
          * [`hydro_total_inflow_expr()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicConstraints.hydro_total_inflow_expr)
        * [NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes)
          * [Hydraulic System Data Classes for Reservoir Optimization](NaivePyDESSEM.HydraulicGenerator.md#hydraulic-system-data-classes-for-reservoir-optimization)
          * [`HydraulicData`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicData)
          * [`HydraulicUnit`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)
        * [NaivePyDESSEM.HydraulicGenerator.HydraulicEquations module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicEquations)
          * [Author](NaivePyDESSEM.HydraulicGenerator.md#id6)
          * [Description](NaivePyDESSEM.HydraulicGenerator.md#id7)
          * [Intended Use](NaivePyDESSEM.HydraulicGenerator.md#intended-use)
          * [`add_hydraulic_balance_expression()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicEquations.add_hydraulic_balance_expression)
          * [`add_hydraulic_cost_expression()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicEquations.add_hydraulic_cost_expression)
        * [NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder)
          * [Hydropower Dispatch Model Builder](NaivePyDESSEM.HydraulicGenerator.md#hydropower-dispatch-model-builder)
          * [`add_hydro_problem()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_problem)
          * [`build_FPHs()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.build_FPHs)
          * [`build_hydro_dispatch()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicGeneratorBuilder.build_hydro_dispatch)
        * [NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives)
          * [Objective Function for Pure Hydropower Dispatch](NaivePyDESSEM.HydraulicGenerator.md#objective-function-for-pure-hydropower-dispatch)
          * [`set_objective_hydro()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicObjectives.set_objective_hydro)
        * [NaivePyDESSEM.HydraulicGenerator.HydraulicVars module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.HydraulicVars)
          * [Hydropower Model Initialization: Sets, Parameters, and Variables](NaivePyDESSEM.HydraulicGenerator.md#hydropower-model-initialization-sets-parameters-and-variables)
          * [`hydralic_add_variables_g()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicVars.hydralic_add_variables_g)
          * [`hydraulyc_add_sets_and_params()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.HydraulicVars.hydraulyc_add_sets_and_params)
        * [NaivePyDESSEM.HydraulicGenerator.PEFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.PEFPH)
          * [Author](NaivePyDESSEM.HydraulicGenerator.md#id13)
          * [Description](NaivePyDESSEM.HydraulicGenerator.md#id14)
          * [`fph_pe_factory()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.PEFPH.fph_pe_factory)
        * [NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH module](NaivePyDESSEM.HydraulicGenerator.md#module-NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH)
          * [Author](NaivePyDESSEM.HydraulicGenerator.md#id15)
          * [Description](NaivePyDESSEM.HydraulicGenerator.md#id16)
          * [`simplified_constant_productivity_fph()`](NaivePyDESSEM.HydraulicGenerator.md#NaivePyDESSEM.HydraulicGenerator.SimplifiedConstantProductivityFPH.simplified_constant_productivity_fph)
      * [NaivePyDESSEM.RenewableGenerator package](NaivePyDESSEM.RenewableGenerator.md)
        * [Module contents](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator)
          * [Author](NaivePyDESSEM.RenewableGenerator.md#author)
          * [Description](NaivePyDESSEM.RenewableGenerator.md#description)
          * [Submodules](NaivePyDESSEM.RenewableGenerator.md#submodules)
        * [Submodules](NaivePyDESSEM.RenewableGenerator.md#id1)
        * [NaivePyDESSEM.RenewableGenerator.RenewableConstraints module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableConstraints)
          * [Author](NaivePyDESSEM.RenewableGenerator.md#id2)
          * [Description](NaivePyDESSEM.RenewableGenerator.md#id3)
          * [Functions](NaivePyDESSEM.RenewableGenerator.md#functions)
          * [`add_renewable_balance_constraint()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableConstraints.add_renewable_balance_constraint)
          * [`add_renewable_capacity_constraints()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableConstraints.add_renewable_capacity_constraints)
        * [NaivePyDESSEM.RenewableGenerator.RenewableDataTypes module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableDataTypes)
          * [Author](NaivePyDESSEM.RenewableGenerator.md#id4)
          * [Description](NaivePyDESSEM.RenewableGenerator.md#id5)
          * [Classes](NaivePyDESSEM.RenewableGenerator.md#classes)
          * [`RenewableData`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableData)
          * [`RenewableUnit`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableDataTypes.RenewableUnit)
        * [NaivePyDESSEM.RenewableGenerator.RenewableEquations module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableEquations)
          * [Author](NaivePyDESSEM.RenewableGenerator.md#id6)
          * [Description](NaivePyDESSEM.RenewableGenerator.md#id7)
          * [Intended Use](NaivePyDESSEM.RenewableGenerator.md#intended-use)
          * [`add_renewable_balance_expression()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableEquations.add_renewable_balance_expression)
          * [`add_renewable_cost_expression()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableEquations.add_renewable_cost_expression)
        * [NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder)
          * [Author](NaivePyDESSEM.RenewableGenerator.md#id8)
          * [Description](NaivePyDESSEM.RenewableGenerator.md#id9)
          * [Functions](NaivePyDESSEM.RenewableGenerator.md#id10)
          * [`add_renewable_problem()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder.add_renewable_problem)
          * [`build_renewables()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableGeneratorBuilder.build_renewables)
        * [NaivePyDESSEM.RenewableGenerator.RenewableObjectives module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableObjectives)
          * [Author](NaivePyDESSEM.RenewableGenerator.md#id11)
          * [Description](NaivePyDESSEM.RenewableGenerator.md#id12)
          * [Functions](NaivePyDESSEM.RenewableGenerator.md#id13)
          * [`set_objective_renewable()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableObjectives.set_objective_renewable)
        * [NaivePyDESSEM.RenewableGenerator.RenewableVars module](NaivePyDESSEM.RenewableGenerator.md#module-NaivePyDESSEM.RenewableGenerator.RenewableVars)
          * [Author](NaivePyDESSEM.RenewableGenerator.md#id14)
          * [Description](NaivePyDESSEM.RenewableGenerator.md#id15)
          * [Functions](NaivePyDESSEM.RenewableGenerator.md#id16)
          * [`renewable_add_sets_and_params()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableVars.renewable_add_sets_and_params)
          * [`renewable_add_variables()`](NaivePyDESSEM.RenewableGenerator.md#NaivePyDESSEM.RenewableGenerator.RenewableVars.renewable_add_variables)
      * [NaivePyDESSEM.Storage package](NaivePyDESSEM.Storage.md)
        * [Module contents](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage)
          * [Author](NaivePyDESSEM.Storage.md#author)
          * [Description](NaivePyDESSEM.Storage.md#description)
          * [Submodules](NaivePyDESSEM.Storage.md#submodules)
        * [Submodules](NaivePyDESSEM.Storage.md#id1)
        * [NaivePyDESSEM.Storage.StorageBuilder module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageBuilder)
          * [Author](NaivePyDESSEM.Storage.md#id2)
          * [Description](NaivePyDESSEM.Storage.md#id3)
          * [Functions](NaivePyDESSEM.Storage.md#functions)
          * [`add_storage_problem()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageBuilder.add_storage_problem)
          * [`build_storage()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageBuilder.build_storage)
        * [NaivePyDESSEM.Storage.StorageConstraints module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageConstraints)
          * [Author](NaivePyDESSEM.Storage.md#id4)
          * [Description](NaivePyDESSEM.Storage.md#id5)
          * [Functions](NaivePyDESSEM.Storage.md#id6)
          * [`add_storage_energy_balance_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_energy_balance_constraint)
          * [`add_storage_mutual_exclusion_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_mutual_exclusion_constraint)
          * [`add_storage_only_balance_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_only_balance_constraint)
          * [`add_storage_power_limits_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_power_limits_constraint)
          * [`add_storage_soc_bounds_constraint()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageConstraints.add_storage_soc_bounds_constraint)
        * [NaivePyDESSEM.Storage.StorageDataTypes module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageDataTypes)
          * [Author](NaivePyDESSEM.Storage.md#id7)
          * [Description](NaivePyDESSEM.Storage.md#id8)
          * [Classes](NaivePyDESSEM.Storage.md#classes)
          * [`StorageData`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageData)
          * [`StorageUnit`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageDataTypes.StorageUnit)
        * [NaivePyDESSEM.Storage.StorageEquations module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageEquations)
          * [Author](NaivePyDESSEM.Storage.md#id9)
          * [Description](NaivePyDESSEM.Storage.md#id10)
          * [Intended Use](NaivePyDESSEM.Storage.md#intended-use)
          * [`add_storage_balance_expression()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageEquations.add_storage_balance_expression)
          * [`add_storage_cost_expression()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageEquations.add_storage_cost_expression)
        * [NaivePyDESSEM.Storage.StorageObjective module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageObjective)
          * [Author](NaivePyDESSEM.Storage.md#id11)
          * [Description](NaivePyDESSEM.Storage.md#id12)
          * [Functions](NaivePyDESSEM.Storage.md#id13)
          * [`set_objective_storage()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageObjective.set_objective_storage)
        * [NaivePyDESSEM.Storage.StorageVars module](NaivePyDESSEM.Storage.md#module-NaivePyDESSEM.Storage.StorageVars)
          * [Author](NaivePyDESSEM.Storage.md#id14)
          * [Description](NaivePyDESSEM.Storage.md#id15)
          * [Functions](NaivePyDESSEM.Storage.md#id16)
          * [`storage_add_sets_and_params()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageVars.storage_add_sets_and_params)
          * [`storage_add_variables()`](NaivePyDESSEM.Storage.md#NaivePyDESSEM.Storage.StorageVars.storage_add_variables)
      * [NaivePyDESSEM.ThermalGenerator package](NaivePyDESSEM.ThermalGenerator.md)
        * [Module contents](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#author)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#description)
          * [Submodules](NaivePyDESSEM.ThermalGenerator.md#submodules)
        * [Submodules](NaivePyDESSEM.ThermalGenerator.md#id1)
        * [NaivePyDESSEM.ThermalGenerator.ThermalConstraints module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalConstraints)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#id2)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#id3)
          * [Constraint Families](NaivePyDESSEM.ThermalGenerator.md#constraint-families)
          * [Usage](NaivePyDESSEM.ThermalGenerator.md#usage)
          * [`thermal_add_balance_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_balance_constraint)
          * [`thermal_add_capacity_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_capacity_constraint)
          * [`thermal_add_min_up_down_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_min_up_down_constraint)
          * [`thermal_add_ramps_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_ramps_constraint)
          * [`thermal_add_reserve_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_reserve_constraint)
          * [`thermal_add_startup_shutdown_logic_constraint()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalConstraints.thermal_add_startup_shutdown_logic_constraint)
        * [NaivePyDESSEM.ThermalGenerator.ThermalDataTypes module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalDataTypes)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#id4)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#id5)
          * [Notation (per unit g and time t)](NaivePyDESSEM.ThermalGenerator.md#notation-per-unit-g-and-time-t)
          * [Typical objective (MIQP form)](NaivePyDESSEM.ThermalGenerator.md#typical-objective-miqp-form)
          * [Usage](NaivePyDESSEM.ThermalGenerator.md#id6)
          * [Intended pairing](NaivePyDESSEM.ThermalGenerator.md#intended-pairing)
          * [`ThermalData`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalData)
          * [`ThermalUnit`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalDataTypes.ThermalUnit)
        * [NaivePyDESSEM.ThermalGenerator.ThermalEquations module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalEquations)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#id7)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#id8)
          * [Intended Use](NaivePyDESSEM.ThermalGenerator.md#intended-use)
          * [`add_thermal_balance_expression()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalEquations.add_thermal_balance_expression)
          * [`add_thermal_cost_expression()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalEquations.add_thermal_cost_expression)
        * [NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#id9)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#id10)
          * [Builder Function](NaivePyDESSEM.ThermalGenerator.md#builder-function)
          * [Usage](NaivePyDESSEM.ThermalGenerator.md#id11)
          * [`add_thermal_problem()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_problem)
          * [`build_thermal_uc()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalGeneratorBuilder.build_thermal_uc)
        * [NaivePyDESSEM.ThermalGenerator.ThermalObjectives module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalObjectives)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#id12)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#id13)
          * [Usage](NaivePyDESSEM.ThermalGenerator.md#id14)
          * [`set_objective_thermo_miqp()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalObjectives.set_objective_thermo_miqp)
          * [`set_objective_thermo_pwl()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalObjectives.set_objective_thermo_pwl)
        * [NaivePyDESSEM.ThermalGenerator.ThermalPieceWise module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalPieceWise)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#id15)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#id16)
          * [Features](NaivePyDESSEM.ThermalGenerator.md#features)
          * [Requirements](NaivePyDESSEM.ThermalGenerator.md#requirements)
          * [Usage](NaivePyDESSEM.ThermalGenerator.md#id17)
          * [`thermal_add_piecewise_cost()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalPieceWise.thermal_add_piecewise_cost)
        * [NaivePyDESSEM.ThermalGenerator.ThermalVars module](NaivePyDESSEM.ThermalGenerator.md#module-NaivePyDESSEM.ThermalGenerator.ThermalVars)
          * [Author](NaivePyDESSEM.ThermalGenerator.md#id19)
          * [Description](NaivePyDESSEM.ThermalGenerator.md#id20)
          * [Features](NaivePyDESSEM.ThermalGenerator.md#id21)
          * [Variables](NaivePyDESSEM.ThermalGenerator.md#variables)
          * [Usage](NaivePyDESSEM.ThermalGenerator.md#id22)
          * [`thermal_add_sets_and_params()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalVars.thermal_add_sets_and_params)
          * [`thermal_add_variables_uc()`](NaivePyDESSEM.ThermalGenerator.md#NaivePyDESSEM.ThermalGenerator.ThermalVars.thermal_add_variables_uc)
      * [NaivePyDESSEM.cli package](NaivePyDESSEM.cli.md)
        * [Module contents](NaivePyDESSEM.cli.md#module-NaivePyDESSEM.cli)
          * [NaivePyDESSEM – CLI Subpackage](NaivePyDESSEM.cli.md#naivepydessem-cli-subpackage)
        * [Submodules](NaivePyDESSEM.cli.md#submodules)
        * [NaivePyDESSEM.cli.cli module](NaivePyDESSEM.cli.md#module-NaivePyDESSEM.cli.cli)
          * [Author](NaivePyDESSEM.cli.md#id1)
          * [Description](NaivePyDESSEM.cli.md#id2)
          * [Features](NaivePyDESSEM.cli.md#id3)
          * [Dependencies](NaivePyDESSEM.cli.md#dependencies)
          * [Usage](NaivePyDESSEM.cli.md#usage)
          * [`main()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.cli.main)
          * [`print_welcome_banner()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.cli.print_welcome_banner)
          * [`save_dataframe()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.cli.save_dataframe)
        * [NaivePyDESSEM.cli.plot_cli module](NaivePyDESSEM.cli.md#module-NaivePyDESSEM.cli.plot_cli)
          * [Author](NaivePyDESSEM.cli.md#id4)
          * [Description](NaivePyDESSEM.cli.md#id5)
          * [Features](NaivePyDESSEM.cli.md#id6)
          * [Categories](NaivePyDESSEM.cli.md#categories)
          * [Dependencies](NaivePyDESSEM.cli.md#id7)
          * [Usage](NaivePyDESSEM.cli.md#id8)
          * [Quick examples](NaivePyDESSEM.cli.md#quick-examples)
          * [`handle_control_variables()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.handle_control_variables)
          * [`handle_plot()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.handle_plot)
          * [`handle_table()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.handle_table)
          * [`load_dataframe()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.load_dataframe)
          * [`main()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.main)
          * [`print_welcome_banner()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.print_welcome_banner)
          * [`prompt()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.prompt)
          * [`select_columns_multi()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.select_columns_multi)
          * [`select_variable_columns()`](NaivePyDESSEM.cli.md#NaivePyDESSEM.cli.plot_cli.select_variable_columns)
    * [Submodules](NaivePyDESSEM.md#id1)
    * [NaivePyDESSEM.Builder module](NaivePyDESSEM.md#module-NaivePyDESSEM.Builder)
      * [Author](NaivePyDESSEM.md#id2)
      * [Description](NaivePyDESSEM.md#id3)
      * [Usage](NaivePyDESSEM.md#usage)
      * [`build_balance_and_objective_from_yaml()`](NaivePyDESSEM.md#NaivePyDESSEM.Builder.build_balance_and_objective_from_yaml)
      * [`build_model_from_file()`](NaivePyDESSEM.md#NaivePyDESSEM.Builder.build_model_from_file)
    * [NaivePyDESSEM.DataFrames module](NaivePyDESSEM.md#module-NaivePyDESSEM.DataFrames)
      * [Author](NaivePyDESSEM.md#id4)
      * [Description](NaivePyDESSEM.md#id5)
      * [`add_cost_to_dataframe()`](NaivePyDESSEM.md#NaivePyDESSEM.DataFrames.add_cost_to_dataframe)
      * [`add_hydro_dispatch_to_dataframe()`](NaivePyDESSEM.md#NaivePyDESSEM.DataFrames.add_hydro_dispatch_to_dataframe)
      * [`add_renewable_dispatch_to_dataframe()`](NaivePyDESSEM.md#NaivePyDESSEM.DataFrames.add_renewable_dispatch_to_dataframe)
      * [`add_storage_dispatch_to_dataframe()`](NaivePyDESSEM.md#NaivePyDESSEM.DataFrames.add_storage_dispatch_to_dataframe)
      * [`add_thermal_dispatch_to_dataframe()`](NaivePyDESSEM.md#NaivePyDESSEM.DataFrames.add_thermal_dispatch_to_dataframe)
      * [`build_dispatch_dataframe()`](NaivePyDESSEM.md#NaivePyDESSEM.DataFrames.build_dispatch_dataframe)
    * [NaivePyDESSEM.Formatters module](NaivePyDESSEM.md#module-NaivePyDESSEM.Formatters)
      * [Author](NaivePyDESSEM.md#id6)
      * [Description](NaivePyDESSEM.md#id7)
      * [`format_brl()`](NaivePyDESSEM.md#NaivePyDESSEM.Formatters.format_brl)
    * [NaivePyDESSEM.ModelCheck module](NaivePyDESSEM.md#module-NaivePyDESSEM.ModelCheck)
      * [Author](NaivePyDESSEM.md#id8)
      * [Description](NaivePyDESSEM.md#id9)
      * [Functions](NaivePyDESSEM.md#functions)
      * [Usage Example](NaivePyDESSEM.md#usage-example)
      * [`has_hydro_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelCheck.has_hydro_model)
      * [`has_renewable_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelCheck.has_renewable_model)
      * [`has_storage_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelCheck.has_storage_model)
      * [`has_thermal_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelCheck.has_thermal_model)
    * [NaivePyDESSEM.ModelFormatters module](NaivePyDESSEM.md#module-NaivePyDESSEM.ModelFormatters)
      * [Author](NaivePyDESSEM.md#id10)
      * [Description](NaivePyDESSEM.md#id11)
      * [`format_hydro_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.format_hydro_model)
      * [`format_models()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.format_models)
      * [`format_renewable_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.format_renewable_model)
      * [`format_storage_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.format_storage_model)
      * [`format_thermal_model()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.format_thermal_model)
      * [`model_properties()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.model_properties)
      * [`print_welcome_banner()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.print_welcome_banner)
      * [`print_welcome_message()`](NaivePyDESSEM.md#NaivePyDESSEM.ModelFormatters.print_welcome_message)
    * [NaivePyDESSEM.PlotSeries module](NaivePyDESSEM.md#module-NaivePyDESSEM.PlotSeries)
      * [Author](NaivePyDESSEM.md#id12)
      * [Description](NaivePyDESSEM.md#id13)
      * [Functions](NaivePyDESSEM.md#id14)
      * [Conventions](NaivePyDESSEM.md#conventions)
      * [`get_distinct_colors()`](NaivePyDESSEM.md#NaivePyDESSEM.PlotSeries.get_distinct_colors)
      * [`plot_series()`](NaivePyDESSEM.md#NaivePyDESSEM.PlotSeries.plot_series)
      * [`plot_series_bar()`](NaivePyDESSEM.md#NaivePyDESSEM.PlotSeries.plot_series_bar)
    * [NaivePyDESSEM.Reporting module](NaivePyDESSEM.md#module-NaivePyDESSEM.Reporting)
      * [Author](NaivePyDESSEM.md#id15)
      * [Description](NaivePyDESSEM.md#id16)
      * [`dispatch_summary()`](NaivePyDESSEM.md#NaivePyDESSEM.Reporting.dispatch_summary)
      * [`hydro_dispatch_summary()`](NaivePyDESSEM.md#NaivePyDESSEM.Reporting.hydro_dispatch_summary)
      * [`renewable_dispatch_summary()`](NaivePyDESSEM.md#NaivePyDESSEM.Reporting.renewable_dispatch_summary)
      * [`storage_dispatch_summary()`](NaivePyDESSEM.md#NaivePyDESSEM.Reporting.storage_dispatch_summary)
      * [`thermal_dispatch_summary()`](NaivePyDESSEM.md#NaivePyDESSEM.Reporting.thermal_dispatch_summary)
    * [NaivePyDESSEM.Solver module](NaivePyDESSEM.md#module-NaivePyDESSEM.Solver)
      * [Author](NaivePyDESSEM.md#id17)
      * [Description](NaivePyDESSEM.md#id18)
      * [`solve()`](NaivePyDESSEM.md#NaivePyDESSEM.Solver.solve)
    * [NaivePyDESSEM.Utils module](NaivePyDESSEM.md#module-NaivePyDESSEM.Utils)
      * [Author](NaivePyDESSEM.md#id19)
      * [Description](NaivePyDESSEM.md#id20)
      * [Functions](NaivePyDESSEM.md#id21)
      * [Parameters (Shared)](NaivePyDESSEM.md#parameters-shared)
      * [Additional Parameters](NaivePyDESSEM.md#additional-parameters)
      * [`binary_df_to_colored_latex()`](NaivePyDESSEM.md#NaivePyDESSEM.Utils.binary_df_to_colored_latex)
      * [`custom_df_to_latex()`](NaivePyDESSEM.md#NaivePyDESSEM.Utils.custom_df_to_latex)
    * [NaivePyDESSEM.YAMLLoader module](NaivePyDESSEM.md#module-NaivePyDESSEM.YAMLLoader)
      * [Author](NaivePyDESSEM.md#id22)
      * [Description](NaivePyDESSEM.md#id23)
      * [Functions](NaivePyDESSEM.md#id24)
      * [`key_replace()`](NaivePyDESSEM.md#NaivePyDESSEM.YAMLLoader.key_replace)
      * [`pre_process()`](NaivePyDESSEM.md#NaivePyDESSEM.YAMLLoader.pre_process)
      * [`yaml_loader()`](NaivePyDESSEM.md#NaivePyDESSEM.YAMLLoader.yaml_loader)
  * [NaivePyDECOMP package](NaivePyDECOMP.md)
    * [Module contents](NaivePyDECOMP.md#module-NaivePyDECOMP)
      * [Author](NaivePyDECOMP.md#author)
      * [Description](NaivePyDECOMP.md#description)
      * [Submodules](NaivePyDECOMP.md#submodules)
    * [Subpackages](NaivePyDECOMP.md#subpackages)
      * [NaivePyDECOMP.HydraulicGenerator package](NaivePyDECOMP.HydraulicGenerator.md)
        * [Module contents](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator)
          * [Author](NaivePyDECOMP.HydraulicGenerator.md#author)
          * [Description](NaivePyDECOMP.HydraulicGenerator.md#description)
          * [Submodules](NaivePyDECOMP.HydraulicGenerator.md#submodules)
        * [Submodules](NaivePyDECOMP.HydraulicGenerator.md#id1)
        * [NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints)
          * [Hydropower Constraints Module for Multi-Mode Generation Modeling](NaivePyDECOMP.HydraulicGenerator.md#hydropower-constraints-module-for-multi-mode-generation-modeling)
          * [`add_hydro_volume_continuity_constraint()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicConstraints.add_hydro_volume_continuity_constraint)
        * [NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes)
          * [Description](NaivePyDECOMP.HydraulicGenerator.md#id2)
          * [Overview](NaivePyDECOMP.HydraulicGenerator.md#overview)
          * [Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#conventions-and-units)
          * [`HydraulicData`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicData)
          * [`HydraulicUnit`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicDataTypes.HydraulicUnit)
        * [NaivePyDECOMP.HydraulicGenerator.HydraulicEquations module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicEquations)
          * [Author](NaivePyDECOMP.HydraulicGenerator.md#id3)
          * [Description](NaivePyDECOMP.HydraulicGenerator.md#id4)
          * [Intended Use](NaivePyDECOMP.HydraulicGenerator.md#intended-use)
        * [NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder)
          * [Description](NaivePyDECOMP.HydraulicGenerator.md#id5)
          * [Supported generation modes (per unit)](NaivePyDECOMP.HydraulicGenerator.md#supported-generation-modes-per-unit)
          * [Functions](NaivePyDECOMP.HydraulicGenerator.md#id6)
          * [Modeling Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#modeling-conventions-and-units)
          * [`add_hydro_problem()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_problem)
          * [`add_hydro_subproblem()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.add_hydro_subproblem)
          * [`build_FPHs()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.build_FPHs)
          * [`build_hydro_dispatch()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicGeneratorBuilder.build_hydro_dispatch)
        * [NaivePyDECOMP.HydraulicGenerator.HydraulicObjectives module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicObjectives)
          * [Description](NaivePyDECOMP.HydraulicGenerator.md#id7)
          * [Functions](NaivePyDECOMP.HydraulicGenerator.md#id8)
          * [Modeling Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#id9)
        * [NaivePyDECOMP.HydraulicGenerator.HydraulicVars module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.HydraulicVars)
          * [Description](NaivePyDECOMP.HydraulicGenerator.md#id10)
          * [Functions](NaivePyDECOMP.HydraulicGenerator.md#id11)
          * [Modeling Conventions and Units](NaivePyDECOMP.HydraulicGenerator.md#id12)
          * [`hydraulyc_add_sets_and_params()`](NaivePyDECOMP.HydraulicGenerator.md#NaivePyDECOMP.HydraulicGenerator.HydraulicVars.hydraulyc_add_sets_and_params)
        * [NaivePyDECOMP.HydraulicGenerator.SimplifiedConstantProductivityFPH module](NaivePyDECOMP.HydraulicGenerator.md#module-NaivePyDECOMP.HydraulicGenerator.SimplifiedConstantProductivityFPH)
          * [Author](NaivePyDECOMP.HydraulicGenerator.md#id13)
          * [Description](NaivePyDECOMP.HydraulicGenerator.md#id14)
      * [NaivePyDECOMP.RenewableGenerator package](NaivePyDECOMP.RenewableGenerator.md)
        * [Module contents](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator)
          * [Author](NaivePyDECOMP.RenewableGenerator.md#author)
          * [Description](NaivePyDECOMP.RenewableGenerator.md#description)
          * [Submodules](NaivePyDECOMP.RenewableGenerator.md#submodules)
        * [Submodules](NaivePyDECOMP.RenewableGenerator.md#id1)
        * [NaivePyDECOMP.RenewableGenerator.RenewableConstraints module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableConstraints)
          * [Author](NaivePyDECOMP.RenewableGenerator.md#id2)
          * [Description](NaivePyDECOMP.RenewableGenerator.md#id3)
          * [Functions](NaivePyDECOMP.RenewableGenerator.md#functions)
        * [NaivePyDECOMP.RenewableGenerator.RenewableDataTypes module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableDataTypes)
          * [Author](NaivePyDECOMP.RenewableGenerator.md#id4)
          * [Description](NaivePyDECOMP.RenewableGenerator.md#id5)
          * [Classes](NaivePyDECOMP.RenewableGenerator.md#classes)
        * [NaivePyDECOMP.RenewableGenerator.RenewableEquations module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableEquations)
          * [Author](NaivePyDECOMP.RenewableGenerator.md#id6)
          * [Description](NaivePyDECOMP.RenewableGenerator.md#id7)
          * [Intended Use](NaivePyDECOMP.RenewableGenerator.md#intended-use)
        * [NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder)
          * [Author](NaivePyDECOMP.RenewableGenerator.md#id8)
          * [Description](NaivePyDECOMP.RenewableGenerator.md#id9)
          * [Functions](NaivePyDECOMP.RenewableGenerator.md#id10)
          * [`add_renewable_subproblem()`](NaivePyDECOMP.RenewableGenerator.md#NaivePyDECOMP.RenewableGenerator.RenewableGeneratorBuilder.add_renewable_subproblem)
        * [NaivePyDECOMP.RenewableGenerator.RenewableObjectives module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableObjectives)
          * [Author](NaivePyDECOMP.RenewableGenerator.md#id11)
          * [Description](NaivePyDECOMP.RenewableGenerator.md#id12)
          * [Functions](NaivePyDECOMP.RenewableGenerator.md#id13)
        * [NaivePyDECOMP.RenewableGenerator.RenewableVars module](NaivePyDECOMP.RenewableGenerator.md#module-NaivePyDECOMP.RenewableGenerator.RenewableVars)
          * [Author](NaivePyDECOMP.RenewableGenerator.md#id14)
          * [Description](NaivePyDECOMP.RenewableGenerator.md#id15)
          * [Functions](NaivePyDECOMP.RenewableGenerator.md#id16)
      * [NaivePyDECOMP.Storage package](NaivePyDECOMP.Storage.md)
        * [Module contents](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage)
          * [Author](NaivePyDECOMP.Storage.md#author)
          * [Description](NaivePyDECOMP.Storage.md#description)
          * [Submodules](NaivePyDECOMP.Storage.md#submodules)
        * [Submodules](NaivePyDECOMP.Storage.md#id1)
        * [NaivePyDECOMP.Storage.StorageBuilder module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageBuilder)
          * [Author](NaivePyDECOMP.Storage.md#id2)
          * [Description](NaivePyDECOMP.Storage.md#id3)
          * [Functions](NaivePyDECOMP.Storage.md#functions)
          * [`add_storage_subproblem()`](NaivePyDECOMP.Storage.md#NaivePyDECOMP.Storage.StorageBuilder.add_storage_subproblem)
        * [NaivePyDECOMP.Storage.StorageConstraints module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageConstraints)
          * [Author](NaivePyDECOMP.Storage.md#id4)
          * [Description](NaivePyDECOMP.Storage.md#id5)
          * [Functions](NaivePyDECOMP.Storage.md#id6)
        * [NaivePyDECOMP.Storage.StorageDataTypes module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageDataTypes)
          * [Author](NaivePyDECOMP.Storage.md#id7)
          * [Description](NaivePyDECOMP.Storage.md#id8)
          * [Classes](NaivePyDECOMP.Storage.md#classes)
        * [NaivePyDECOMP.Storage.StorageEquations module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageEquations)
          * [Author](NaivePyDECOMP.Storage.md#id9)
          * [Description](NaivePyDECOMP.Storage.md#id10)
          * [Intended Use](NaivePyDECOMP.Storage.md#intended-use)
        * [NaivePyDECOMP.Storage.StorageObjective module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageObjective)
          * [Author](NaivePyDECOMP.Storage.md#id11)
          * [Description](NaivePyDECOMP.Storage.md#id12)
          * [Functions](NaivePyDECOMP.Storage.md#id13)
        * [NaivePyDECOMP.Storage.StorageVars module](NaivePyDECOMP.Storage.md#module-NaivePyDECOMP.Storage.StorageVars)
          * [Author](NaivePyDECOMP.Storage.md#id14)
          * [Description](NaivePyDECOMP.Storage.md#id15)
          * [Functions](NaivePyDECOMP.Storage.md#id16)
      * [NaivePyDECOMP.ThermalGenerator package](NaivePyDECOMP.ThermalGenerator.md)
        * [Module contents](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator)
          * [Author](NaivePyDECOMP.ThermalGenerator.md#author)
          * [Description](NaivePyDECOMP.ThermalGenerator.md#description)
          * [Submodules](NaivePyDECOMP.ThermalGenerator.md#submodules)
        * [Submodules](NaivePyDECOMP.ThermalGenerator.md#id1)
        * [NaivePyDECOMP.ThermalGenerator.ThermalConstraints module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalConstraints)
          * [Author](NaivePyDECOMP.ThermalGenerator.md#id2)
          * [Description](NaivePyDECOMP.ThermalGenerator.md#id3)
          * [Constraint Families](NaivePyDECOMP.ThermalGenerator.md#constraint-families)
          * [Usage](NaivePyDECOMP.ThermalGenerator.md#usage)
          * [`thermal_add_balance_constraint()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalConstraints.thermal_add_balance_constraint)
          * [`thermal_add_capacity_constraint()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalConstraints.thermal_add_capacity_constraint)
        * [NaivePyDECOMP.ThermalGenerator.ThermalDataTypes module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalDataTypes)
          * [Author](NaivePyDECOMP.ThermalGenerator.md#id4)
          * [Description](NaivePyDECOMP.ThermalGenerator.md#id5)
          * [Notation (per unit g and time t)](NaivePyDECOMP.ThermalGenerator.md#notation-per-unit-g-and-time-t)
          * [Typical objective (MIQP form)](NaivePyDECOMP.ThermalGenerator.md#typical-objective-miqp-form)
          * [Usage](NaivePyDECOMP.ThermalGenerator.md#id6)
          * [Intended pairing](NaivePyDECOMP.ThermalGenerator.md#intended-pairing)
          * [`ThermalData`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalData)
          * [`ThermalUnit`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalDataTypes.ThermalUnit)
        * [NaivePyDECOMP.ThermalGenerator.ThermalEquations module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalEquations)
          * [Author](NaivePyDECOMP.ThermalGenerator.md#id7)
          * [Description](NaivePyDECOMP.ThermalGenerator.md#id8)
          * [Intended Use](NaivePyDECOMP.ThermalGenerator.md#intended-use)
          * [`add_thermal_balance_expression()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalEquations.add_thermal_balance_expression)
          * [`add_thermal_cost_expression()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalEquations.add_thermal_cost_expression)
        * [NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder)
          * [Author](NaivePyDECOMP.ThermalGenerator.md#id9)
          * [Description](NaivePyDECOMP.ThermalGenerator.md#id10)
          * [Builder Function](NaivePyDECOMP.ThermalGenerator.md#builder-function)
          * [Usage](NaivePyDECOMP.ThermalGenerator.md#id11)
          * [`add_thermal_problem()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_problem)
          * [`add_thermal_subproblem()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.add_thermal_subproblem)
          * [`build_thermal_uc()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.build_thermal_uc)
          * [`thermo_update_model()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalGeneratorBuilder.thermo_update_model)
        * [NaivePyDECOMP.ThermalGenerator.ThermalObjectives module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalObjectives)
          * [Author](NaivePyDECOMP.ThermalGenerator.md#id12)
          * [Description](NaivePyDECOMP.ThermalGenerator.md#id13)
          * [Usage](NaivePyDECOMP.ThermalGenerator.md#id14)
          * [`set_objective_thermo()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalObjectives.set_objective_thermo)
        * [NaivePyDECOMP.ThermalGenerator.ThermalVars module](NaivePyDECOMP.ThermalGenerator.md#module-NaivePyDECOMP.ThermalGenerator.ThermalVars)
          * [Author](NaivePyDECOMP.ThermalGenerator.md#id15)
          * [Description](NaivePyDECOMP.ThermalGenerator.md#id16)
          * [Features](NaivePyDECOMP.ThermalGenerator.md#features)
          * [Variables](NaivePyDECOMP.ThermalGenerator.md#variables)
          * [Usage](NaivePyDECOMP.ThermalGenerator.md#id17)
          * [`thermal_add_sets_and_params()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalVars.thermal_add_sets_and_params)
          * [`thermal_add_variables_uc()`](NaivePyDECOMP.ThermalGenerator.md#NaivePyDECOMP.ThermalGenerator.ThermalVars.thermal_add_variables_uc)
      * [NaivePyDECOMP.cli package](NaivePyDECOMP.cli.md)
        * [Module contents](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli)
          * [NaivePyDECOMP – CLI Subpackage](NaivePyDECOMP.cli.md#naivepydecomp-cli-subpackage)
        * [Submodules](NaivePyDECOMP.cli.md#submodules)
        * [NaivePyDECOMP.cli.cli module](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli.cli)
          * [Author](NaivePyDECOMP.cli.md#id1)
          * [Description](NaivePyDECOMP.cli.md#id2)
          * [Features](NaivePyDECOMP.cli.md#id3)
          * [Dependencies](NaivePyDECOMP.cli.md#dependencies)
          * [Usage](NaivePyDECOMP.cli.md#usage)
          * [`main()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.cli.main)
          * [`print_welcome_banner()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.cli.print_welcome_banner)
          * [`save_dataframe()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.cli.save_dataframe)
        * [NaivePyDECOMP.cli.pddd_cli module](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli.pddd_cli)
          * [Author](NaivePyDECOMP.cli.md#id4)
          * [Description](NaivePyDECOMP.cli.md#id5)
          * [Features](NaivePyDECOMP.cli.md#id6)
          * [Dependencies](NaivePyDECOMP.cli.md#id7)
          * [Usage](NaivePyDECOMP.cli.md#id8)
          * [`main()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.pddd_cli.main)
          * [`print_welcome_banner()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.pddd_cli.print_welcome_banner)
          * [`save_dataframe()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.pddd_cli.save_dataframe)
        * [NaivePyDECOMP.cli.plot_cli module](NaivePyDECOMP.cli.md#module-NaivePyDECOMP.cli.plot_cli)
          * [Author](NaivePyDECOMP.cli.md#id9)
          * [Description](NaivePyDECOMP.cli.md#id10)
          * [Features](NaivePyDECOMP.cli.md#id11)
          * [Categories](NaivePyDECOMP.cli.md#categories)
          * [Dependencies](NaivePyDECOMP.cli.md#id12)
          * [Usage](NaivePyDECOMP.cli.md#id13)
          * [Quick examples](NaivePyDECOMP.cli.md#quick-examples)
          * [`handle_plot()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.handle_plot)
          * [`handle_table()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.handle_table)
          * [`load_dataframe()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.load_dataframe)
          * [`main()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.main)
          * [`print_welcome_banner()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.print_welcome_banner)
          * [`prompt()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.prompt)
          * [`select_columns_multi()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.select_columns_multi)
          * [`select_variable_columns()`](NaivePyDECOMP.cli.md#NaivePyDECOMP.cli.plot_cli.select_variable_columns)
    * [Submodules](NaivePyDECOMP.md#id1)
    * [NaivePyDECOMP.Builder module](NaivePyDECOMP.md#module-NaivePyDECOMP.Builder)
      * [Author](NaivePyDECOMP.md#id2)
      * [Description](NaivePyDECOMP.md#id3)
      * [Usage](NaivePyDECOMP.md#usage)
      * [`build_balance_and_objective_from_yaml()`](NaivePyDECOMP.md#NaivePyDECOMP.Builder.build_balance_and_objective_from_yaml)
      * [`build_model_from_data()`](NaivePyDECOMP.md#NaivePyDECOMP.Builder.build_model_from_data)
      * [`build_model_from_file()`](NaivePyDECOMP.md#NaivePyDECOMP.Builder.build_model_from_file)
    * [NaivePyDECOMP.BuilderPDDD module](NaivePyDECOMP.md#module-NaivePyDECOMP.BuilderPDDD)
      * [Author](NaivePyDECOMP.md#id4)
      * [Description](NaivePyDECOMP.md#id5)
      * [Usage](NaivePyDECOMP.md#id6)
      * [`build_pddd_balance_and_objective_from_yaml()`](NaivePyDECOMP.md#NaivePyDECOMP.BuilderPDDD.build_pddd_balance_and_objective_from_yaml)
      * [`build_pddd_data_from_file()`](NaivePyDECOMP.md#NaivePyDECOMP.BuilderPDDD.build_pddd_data_from_file)
    * [NaivePyDECOMP.DataFrames module](NaivePyDECOMP.md#module-NaivePyDECOMP.DataFrames)
      * [Author](NaivePyDECOMP.md#id7)
      * [Description](NaivePyDECOMP.md#id8)
      * [`add_cost_to_dataframe()`](NaivePyDECOMP.md#NaivePyDECOMP.DataFrames.add_cost_to_dataframe)
      * [`add_hydro_dispatch_to_dataframe()`](NaivePyDECOMP.md#NaivePyDECOMP.DataFrames.add_hydro_dispatch_to_dataframe)
      * [`add_thermal_dispatch_to_dataframe()`](NaivePyDECOMP.md#NaivePyDECOMP.DataFrames.add_thermal_dispatch_to_dataframe)
      * [`build_dispatch_dataframe()`](NaivePyDECOMP.md#NaivePyDECOMP.DataFrames.build_dispatch_dataframe)
    * [NaivePyDECOMP.Formatters module](NaivePyDECOMP.md#module-NaivePyDECOMP.Formatters)
      * [Author](NaivePyDECOMP.md#id9)
      * [Description](NaivePyDECOMP.md#id10)
    * [NaivePyDECOMP.ModelCheck module](NaivePyDECOMP.md#module-NaivePyDECOMP.ModelCheck)
      * [Author](NaivePyDECOMP.md#id11)
      * [Description](NaivePyDECOMP.md#id12)
      * [Functions](NaivePyDECOMP.md#functions)
      * [Usage Example](NaivePyDECOMP.md#usage-example)
      * [`has_thermal_model()`](NaivePyDECOMP.md#NaivePyDECOMP.ModelCheck.has_thermal_model)
    * [NaivePyDECOMP.ModelFormatters module](NaivePyDECOMP.md#module-NaivePyDECOMP.ModelFormatters)
      * [Author](NaivePyDECOMP.md#id13)
      * [Description](NaivePyDECOMP.md#id14)
      * [`format_hydro_model()`](NaivePyDECOMP.md#NaivePyDECOMP.ModelFormatters.format_hydro_model)
      * [`format_models()`](NaivePyDECOMP.md#NaivePyDECOMP.ModelFormatters.format_models)
      * [`format_thermal_model()`](NaivePyDECOMP.md#NaivePyDECOMP.ModelFormatters.format_thermal_model)
      * [`model_properties()`](NaivePyDECOMP.md#NaivePyDECOMP.ModelFormatters.model_properties)
      * [`print_welcome_banner()`](NaivePyDECOMP.md#NaivePyDECOMP.ModelFormatters.print_welcome_banner)
      * [`print_welcome_message()`](NaivePyDECOMP.md#NaivePyDECOMP.ModelFormatters.print_welcome_message)
    * [NaivePyDECOMP.PlotSeries module](NaivePyDECOMP.md#module-NaivePyDECOMP.PlotSeries)
      * [Author](NaivePyDECOMP.md#id15)
      * [Description](NaivePyDECOMP.md#id16)
      * [Functions](NaivePyDECOMP.md#id17)
      * [Conventions](NaivePyDECOMP.md#conventions)
    * [NaivePyDECOMP.PDDDMergeModels module](NaivePyDECOMP.md#module-NaivePyDECOMP.PDDDMergeModels)
      * [Author](NaivePyDECOMP.md#id18)
      * [Description](NaivePyDECOMP.md#id19)
      * [Main Functionality](NaivePyDECOMP.md#main-functionality)
      * [Intended Use](NaivePyDECOMP.md#intended-use)
      * [Dependencies](NaivePyDECOMP.md#dependencies)
      * [`generate_dummy_model()`](NaivePyDECOMP.md#NaivePyDECOMP.PDDDMergeModels.generate_dummy_model)
    * [NaivePyDECOMP.Reporting module](NaivePyDECOMP.md#module-NaivePyDECOMP.Reporting)
      * [Author](NaivePyDECOMP.md#id20)
      * [Description](NaivePyDECOMP.md#id21)
      * [`dispatch_summary()`](NaivePyDECOMP.md#NaivePyDECOMP.Reporting.dispatch_summary)
      * [`hydro_dispatch_summary()`](NaivePyDECOMP.md#NaivePyDECOMP.Reporting.hydro_dispatch_summary)
      * [`renewable_dispatch_summary()`](NaivePyDECOMP.md#NaivePyDECOMP.Reporting.renewable_dispatch_summary)
      * [`storage_dispatch_summary()`](NaivePyDECOMP.md#NaivePyDECOMP.Reporting.storage_dispatch_summary)
      * [`thermal_dispatch_summary()`](NaivePyDECOMP.md#NaivePyDECOMP.Reporting.thermal_dispatch_summary)
    * [NaivePyDECOMP.SolverPDDD module](NaivePyDECOMP.md#module-NaivePyDECOMP.SolverPDDD)
      * [Author](NaivePyDECOMP.md#id22)
      * [Description](NaivePyDECOMP.md#id23)
      * [`compute_fcf()`](NaivePyDECOMP.md#NaivePyDECOMP.SolverPDDD.compute_fcf)
      * [`fcf_from_cuts()`](NaivePyDECOMP.md#NaivePyDECOMP.SolverPDDD.fcf_from_cuts)
      * [`solve_pddd()`](NaivePyDECOMP.md#NaivePyDECOMP.SolverPDDD.solve_pddd)
      * [`solve_stage_pddd()`](NaivePyDECOMP.md#NaivePyDECOMP.SolverPDDD.solve_stage_pddd)
    * [NaivePyDECOMP.Solver module](NaivePyDECOMP.md#module-NaivePyDECOMP.Solver)
      * [Author](NaivePyDECOMP.md#id24)
      * [Description](NaivePyDECOMP.md#id25)
      * [`solve()`](NaivePyDECOMP.md#NaivePyDECOMP.Solver.solve)
    * [NaivePyDECOMP.Utils module](NaivePyDECOMP.md#module-NaivePyDECOMP.Utils)
      * [Author](NaivePyDECOMP.md#id26)
      * [Description](NaivePyDECOMP.md#id27)
      * [Functions](NaivePyDECOMP.md#id28)
      * [Parameters (Shared)](NaivePyDECOMP.md#parameters-shared)
      * [Additional Parameters](NaivePyDECOMP.md#additional-parameters)
    * [NaivePyDECOMP.YAMLLoader module](NaivePyDECOMP.md#module-NaivePyDECOMP.YAMLLoader)
      * [Author](NaivePyDECOMP.md#id29)
      * [Description](NaivePyDECOMP.md#id30)
      * [Functions](NaivePyDECOMP.md#id31)
  * [MDI package](MDI.md)
    * [Module contents](MDI.md#module-MDI)
      * [MDI — A Didactic Expansion Planning Framework for the NaivePyDESSEM Package](MDI.md#mdi-a-didactic-expansion-planning-framework-for-the-naivepydessem-package)
        * [Author](MDI.md#author)
        * [Summary](MDI.md#summary)
        * [Description](MDI.md#description)
        * [Submodules](MDI.md#submodules)
    * [Subpackages](MDI.md#subpackages)
      * [MDI.Generator package](MDI.Generator.md)
        * [Module contents](MDI.Generator.md#module-MDI.Generator)
          * [Generator Subpackage](MDI.Generator.md#generator-subpackage)
        * [Submodules](MDI.Generator.md#submodules)
        * [MDI.Generator.GeneratorBuilder module](MDI.Generator.md#module-MDI.Generator.GeneratorBuilder)
          * [Generator Builder Module](MDI.Generator.md#generator-builder-module)
          * [`add_generator_problem()`](MDI.Generator.md#MDI.Generator.GeneratorBuilder.add_generator_problem)
          * [`build_generators()`](MDI.Generator.md#MDI.Generator.GeneratorBuilder.build_generators)
        * [MDI.Generator.GeneratorConstraints module](MDI.Generator.md#module-MDI.Generator.GeneratorConstraints)
          * [Generator Constraints Module](MDI.Generator.md#generator-constraints-module)
          * [`add_generator_investment_link_constraint()`](MDI.Generator.md#MDI.Generator.GeneratorConstraints.add_generator_investment_link_constraint)
          * [`add_generator_power_limits_constraint()`](MDI.Generator.md#MDI.Generator.GeneratorConstraints.add_generator_power_limits_constraint)
        * [MDI.Generator.GeneratorDataTypes module](MDI.Generator.md#module-MDI.Generator.GeneratorDataTypes)
          * [Generator Data Types Module](MDI.Generator.md#generator-data-types-module)
          * [`GeneratorData`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorData)
          * [`GeneratorUnit`](MDI.Generator.md#MDI.Generator.GeneratorDataTypes.GeneratorUnit)
        * [MDI.Generator.GeneratorEquations module](MDI.Generator.md#module-MDI.Generator.GeneratorEquations)
          * [Generator Equations Module](MDI.Generator.md#generator-equations-module)
          * [`add_generator_balance_expression()`](MDI.Generator.md#MDI.Generator.GeneratorEquations.add_generator_balance_expression)
          * [`add_generator_capacity_expression()`](MDI.Generator.md#MDI.Generator.GeneratorEquations.add_generator_capacity_expression)
          * [`add_generator_cost_expression()`](MDI.Generator.md#MDI.Generator.GeneratorEquations.add_generator_cost_expression)
        * [MDI.Generator.GeneratorObjectives module](MDI.Generator.md#module-MDI.Generator.GeneratorObjectives)
          * [Generator Objectives Module](MDI.Generator.md#generator-objectives-module)
          * [`set_objective_generator()`](MDI.Generator.md#MDI.Generator.GeneratorObjectives.set_objective_generator)
        * [MDI.Generator.GeneratorVars module](MDI.Generator.md#module-MDI.Generator.GeneratorVars)
          * [Generator Variables and Parameters Module](MDI.Generator.md#generator-variables-and-parameters-module)
          * [`generator_add_sets_and_params()`](MDI.Generator.md#MDI.Generator.GeneratorVars.generator_add_sets_and_params)
          * [`generator_add_variables()`](MDI.Generator.md#MDI.Generator.GeneratorVars.generator_add_variables)
      * [MDI.Storage package](MDI.Storage.md)
        * [Module contents](MDI.Storage.md#module-MDI.Storage)
          * [Storage Subpackage](MDI.Storage.md#storage-subpackage)
        * [Submodules](MDI.Storage.md#submodules)
        * [MDI.Storage.StorageBuilder module](MDI.Storage.md#module-MDI.Storage.StorageBuilder)
          * [Storage Builder Module](MDI.Storage.md#storage-builder-module)
          * [`add_storage_problem()`](MDI.Storage.md#MDI.Storage.StorageBuilder.add_storage_problem)
          * [`build_storage()`](MDI.Storage.md#MDI.Storage.StorageBuilder.build_storage)
        * [MDI.Storage.StorageConstraints module](MDI.Storage.md#module-MDI.Storage.StorageConstraints)
          * [Storage Constraints Module](MDI.Storage.md#storage-constraints-module)
          * [`add_storage_energy_balance_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_energy_balance_constraint)
          * [`add_storage_investment_link_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_investment_link_constraint)
          * [`add_storage_power_limits_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_power_limits_constraint)
          * [`add_storage_soc_bounds_constraint()`](MDI.Storage.md#MDI.Storage.StorageConstraints.add_storage_soc_bounds_constraint)
        * [MDI.Storage.StorageDataTypes module](MDI.Storage.md#module-MDI.Storage.StorageDataTypes)
          * [Storage Data Types Module](MDI.Storage.md#storage-data-types-module)
          * [`StorageData`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageData)
          * [`StorageUnit`](MDI.Storage.md#MDI.Storage.StorageDataTypes.StorageUnit)
        * [MDI.Storage.StorageEquations module](MDI.Storage.md#module-MDI.Storage.StorageEquations)
          * [Storage Equations Module](MDI.Storage.md#storage-equations-module)
          * [`add_storage_balance_expression()`](MDI.Storage.md#MDI.Storage.StorageEquations.add_storage_balance_expression)
          * [`add_storage_capacity_expression()`](MDI.Storage.md#MDI.Storage.StorageEquations.add_storage_capacity_expression)
          * [`add_storage_cost_expression()`](MDI.Storage.md#MDI.Storage.StorageEquations.add_storage_cost_expression)
        * [MDI.Storage.StorageObjective module](MDI.Storage.md#module-MDI.Storage.StorageObjective)
          * [Storage Objective Function Module](MDI.Storage.md#storage-objective-function-module)
          * [`set_objective_storage()`](MDI.Storage.md#MDI.Storage.StorageObjective.set_objective_storage)
        * [MDI.Storage.StorageVars module](MDI.Storage.md#module-MDI.Storage.StorageVars)
          * [Storage Variables and Parameters Module](MDI.Storage.md#storage-variables-and-parameters-module)
          * [`storage_add_sets_and_params()`](MDI.Storage.md#MDI.Storage.StorageVars.storage_add_sets_and_params)
          * [`storage_add_variables()`](MDI.Storage.md#MDI.Storage.StorageVars.storage_add_variables)
      * [MDI.cli package](MDI.cli.md)
        * [Module contents](MDI.cli.md#module-MDI.cli)
          * [NaivePyDESSEM – CLI Subpackage](MDI.cli.md#naivepydessem-cli-subpackage)
        * [Submodules](MDI.cli.md#submodules)
        * [MDI.cli.cli module](MDI.cli.md#module-MDI.cli.cli)
          * [MDI Command-Line Interface (CLI)](MDI.cli.md#mdi-command-line-interface-cli)
          * [`main()`](MDI.cli.md#MDI.cli.cli.main)
          * [`print_welcome_banner()`](MDI.cli.md#MDI.cli.cli.print_welcome_banner)
          * [`save_dataframe()`](MDI.cli.md#MDI.cli.cli.save_dataframe)
        * [MDI.cli.plot_cli module](MDI.cli.md#module-MDI.cli.plot_cli)
          * [Author](MDI.cli.md#id3)
          * [Description](MDI.cli.md#id4)
          * [Features](MDI.cli.md#id5)
          * [Categories](MDI.cli.md#categories)
          * [Dependencies](MDI.cli.md#dependencies)
          * [Usage](MDI.cli.md#usage)
          * [Quick examples](MDI.cli.md#quick-examples)
          * [`handle_control_variables()`](MDI.cli.md#MDI.cli.plot_cli.handle_control_variables)
          * [`handle_plot()`](MDI.cli.md#MDI.cli.plot_cli.handle_plot)
          * [`handle_table()`](MDI.cli.md#MDI.cli.plot_cli.handle_table)
          * [`load_dataframe()`](MDI.cli.md#MDI.cli.plot_cli.load_dataframe)
          * [`main()`](MDI.cli.md#MDI.cli.plot_cli.main)
          * [`print_welcome_banner()`](MDI.cli.md#MDI.cli.plot_cli.print_welcome_banner)
          * [`prompt()`](MDI.cli.md#MDI.cli.plot_cli.prompt)
          * [`select_columns_multi()`](MDI.cli.md#MDI.cli.plot_cli.select_columns_multi)
          * [`select_variable_columns()`](MDI.cli.md#MDI.cli.plot_cli.select_variable_columns)
    * [Submodules](MDI.md#id1)
    * [MDI.Builder module](MDI.md#module-MDI.Builder)
      * [Builder Module](MDI.md#builder-module)
        * [Author](MDI.md#id2)
        * [Summary](MDI.md#id3)
        * [Description](MDI.md#id4)
        * [Functions](MDI.md#functions)
      * [`build_balance_and_objective_from_yaml()`](MDI.md#MDI.Builder.build_balance_and_objective_from_yaml)
      * [`build_model_from_file()`](MDI.md#MDI.Builder.build_model_from_file)
    * [MDI.DataFrames module](MDI.md#module-MDI.DataFrames)
      * [Dataframes Module](MDI.md#dataframes-module)
        * [Author](MDI.md#id5)
        * [Summary](MDI.md#id6)
        * [Description](MDI.md#id7)
        * [Functions](MDI.md#id8)
      * [`add_cost_to_dataframe()`](MDI.md#MDI.DataFrames.add_cost_to_dataframe)
      * [`add_generator_dispatch_to_dataframe()`](MDI.md#MDI.DataFrames.add_generator_dispatch_to_dataframe)
      * [`add_storage_dispatch_to_dataframe()`](MDI.md#MDI.DataFrames.add_storage_dispatch_to_dataframe)
      * [`build_dispatch_dataframe()`](MDI.md#MDI.DataFrames.build_dispatch_dataframe)
      * [`compute_CME_by_period()`](MDI.md#MDI.DataFrames.compute_CME_by_period)
    * [MDI.Formatters module](MDI.md#module-MDI.Formatters)
      * [Author](MDI.md#id9)
      * [Description](MDI.md#id10)
    * [MDI.ModelCheck module](MDI.md#module-MDI.ModelCheck)
      * [ModelCheck Module](MDI.md#modelcheck-module)
        * [Author](MDI.md#id11)
        * [Summary](MDI.md#id12)
        * [Description](MDI.md#id13)
        * [Functions](MDI.md#id14)
        * [Usage Example](MDI.md#usage-example)
      * [`has_generator_model()`](MDI.md#MDI.ModelCheck.has_generator_model)
      * [`has_storage_model()`](MDI.md#MDI.ModelCheck.has_storage_model)
    * [MDI.ModelFormatters module](MDI.md#module-MDI.ModelFormatters)
      * [Author](MDI.md#id15)
      * [Description](MDI.md#id16)
      * [`format_generator_model()`](MDI.md#MDI.ModelFormatters.format_generator_model)
      * [`format_models()`](MDI.md#MDI.ModelFormatters.format_models)
      * [`format_storage_model()`](MDI.md#MDI.ModelFormatters.format_storage_model)
      * [`model_properties()`](MDI.md#MDI.ModelFormatters.model_properties)
      * [`print_welcome_banner()`](MDI.md#MDI.ModelFormatters.print_welcome_banner)
      * [`print_welcome_message()`](MDI.md#MDI.ModelFormatters.print_welcome_message)
    * [MDI.PlotSeries module](MDI.md#module-MDI.PlotSeries)
      * [PlotSeries Module](MDI.md#plotseries-module)
        * [Author](MDI.md#id17)
        * [Description](MDI.md#id18)
        * [Functions](MDI.md#id19)
        * [Conventions](MDI.md#conventions)
    * [MDI.Reporting module](MDI.md#module-MDI.Reporting)
      * [Author](MDI.md#id20)
      * [Description](MDI.md#id21)
      * [`dispatch_summary()`](MDI.md#MDI.Reporting.dispatch_summary)
      * [`generator_dispatch_summary()`](MDI.md#MDI.Reporting.generator_dispatch_summary)
      * [`storage_dispatch_summary()`](MDI.md#MDI.Reporting.storage_dispatch_summary)
    * [MDI.Solver module](MDI.md#module-MDI.Solver)
      * [Author](MDI.md#id22)
      * [Description](MDI.md#id23)
      * [`solve()`](MDI.md#MDI.Solver.solve)
    * [MDI.Utils module](MDI.md#module-MDI.Utils)
      * [Utils Module](MDI.md#utils-module)
        * [Author](MDI.md#id24)
        * [Description](MDI.md#id25)
        * [Functions](MDI.md#id26)
        * [Parameters (Shared)](MDI.md#parameters-shared)
        * [Additional Parameters](MDI.md#additional-parameters)
    * [MDI.YAMLLoader module](MDI.md#module-MDI.YAMLLoader)
      * [YAMLLoader Module](MDI.md#yamlloader-module)
        * [Author](MDI.md#id27)
        * [Summary](MDI.md#id28)
        * [Description](MDI.md#id29)
        * [Functions](MDI.md#id30)

# Indexes

* [Index](genindex.md)
* [Module Index](py-modindex.md)
