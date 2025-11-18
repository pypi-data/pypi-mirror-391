# NaivePyDESSEM — A Pedagogical and Modular Framework for Hydrothermal Economic Dispatch and Expansion Planning in Pyomo (DESSEM, DECOMP, and MDI-like Solvers)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/naivepydessem?period=total&units=INTERNATIONAL_SYSTEM&left_color=GRAY&right_color=GREEN&left_text=Downloads)](https://pepy.tech/projects/naivepydessem)
[![Docs](https://github.com/superflanker/NaivePyDESSEM/actions/workflows/docs.yml/badge.svg)](https://superflanker.github.io/NaivePyDESSEM/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-NaivePyDESSEM-181717?logo=github)](https://github.com/superflanker/NaivePyDESSEM)

**NaivePyDESSEM** is a pedagogical project that brings together **three complementary packages** for teaching and research in power system operation planning:

- **NaivePyDESSEM** — inspired by DESSEM, it models the **short-term** (daily/hourly) operation with detailed individual plant representation.  
- **NaivePyDECOMP** — inspired by DECOMP, it models the **medium-term** (weekly/monthly) operation with deterministic dual dynamic programming (PDDD).  
- **MDI** — Generation Expansion Planning inspired by **MDI** methodology.

Both are implemented in **Pyomo**, with modular architecture and integrated documentation via Sphinx.

---

## 🔎 Overview

**NaivePyDESSEM** is a pedagogical and modular project that consolidates **three complementary packages** designed for teaching, research, and experimentation in **operation and expansion planning of electric power systems**.  
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

The **NaivePyDESSEM** package provides a transparent and instructive framework for the **short-term hydrothermal operation problem**, reproducing the fundamental structure of CEPEL’s *DESSEM*.  
It enables the formulation, solution, and analysis of **mixed-integer linear and quadratic optimization models**, allowing detailed representation of individual generating units and system-level constraints.

### Core Functionalities

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

## 📗 NaivePyDECOMP Package

### Purpose

The **NaivePyDECOMP** package mirrors the *DECOMP* model, addressing **medium-term operation planning** through *Deterministic Dual Dynamic Programming (DDDP)* and linear optimization.  
It provides a modular structure for decomposing long-horizon energy scheduling problems and facilitates analytical exploration of temporal and spatial coupling.

### Core Functionalities

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

## 📙 MDI Package

### Purpose

The **MDI** package implements a simplified but methodologically coherent framework for **long-term generation expansion planning**, drawing on the *Investment Decision Model (MDI)* used in Brazilian *PDE* studies.  
It integrates investment and operational decisions into a unified **mixed-integer linear optimization problem**.

### Core Functionalities

- **Investment Planning:**  
  Formulates a multi-period optimization problem minimizing investment and operational costs under uncertainty.  
  Incorporates candidate projects for thermal, hydro, renewable, and storage technologies, as well as transmission reinforcements.

- **Specialized Submodules:**  
  Subpackages `MDI.Generator`, `MDI.Storage`, `MDI.ConnectionBar` and `MDI.TransmissionLine` define project-level variables, constraints, and cost components.  
  The `Builder` module consolidates these into a system-wide energy balance, while `YAMLLoader` manages structured scenario data.

- **Solution and Analysis:**  
  Supports a variety of *Pyomo* solvers (`GLPK`, `CBC`, `HIGHS`, `CPLEX`) and provides post-solution tools (`Reporting`, `DataFrames`, `PlotSeries`) for sensitivity and scenario analysis.

- **Educational Design:**  
  Preserves the key structural and economic principles of real-world expansion models while maintaining tractability for academic exercises.

---

## 📂 Project Structure

```text
├── src
│   ├── MDI
│   │   ├── cli
│   │   │   ├── __init__.py
│   │   │   ├── cli.py
│   │   │   └── plot_cli.py
│   │   ├── ConnectionBar
│   │   │   ├── __init__.py
│   │   │   ├── ConnectionBarBuilder.py
│   │   │   ├── ConnectionBarConstraints.py
│   │   │   ├── ConnectionBarDataTypes.py
│   │   │   ├── ConnectionBarEquations.py
│   │   │   └── ConnectionBarVars.py
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
│   │   ├── TransmissionLine
│   │   │   ├── __init__.py
│   │   │   ├── TransmissionLineBuilder.py
│   │   │   ├── TransmissionLineConstraints.py
│   │   │   ├── TransmissionLineDataTypes.py
│   │   │   ├── TransmissionLineEquations.py
│   │   │   └── TransmissionLineVars.py
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
│   │   ├── ConnectionBar
│   │   │   ├── __init__.py
│   │   │   ├── ConnectionBarBuilder.py
│   │   │   ├── ConnectionBarConstraints.py
│   │   │   ├── ConnectionBarDataTypes.py
│   │   │   ├── ConnectionBarEquations.py
│   │   │   └── ConnectionBarVars.py
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
│   │   ├── TransmissionLine
│   │   │   ├── __init__.py
│   │   │   ├── TransmissionLineBuilder.py
│   │   │   ├── TransmissionLineConstraints.py
│   │   │   ├── TransmissionLineDataTypes.py
│   │   │   ├── TransmissionLineEquations.py
│   │   │   └── TransmissionLineVars.py
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
│   │   ├── ConnectionBar
│   │   │   ├── __init__.py
│   │   │   ├── ConnectionBarBuilder.py
│   │   │   ├── ConnectionBarConstraints.py
│   │   │   ├── ConnectionBarDataTypes.py
│   │   │   ├── ConnectionBarEquations.py
│   │   │   └── ConnectionBarVars.py
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
│   │   ├── TransmissionLine
│   │   │   ├── __init__.py
│   │   │   ├── TransmissionLineBuilder.py
│   │   │   ├── TransmissionLineConstraints.py
│   │   │   ├── TransmissionLineDataTypes.py
│   │   │   ├── TransmissionLineEquations.py
│   │   │   └── TransmissionLineVars.py
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

| Package      | Version Requirement | PyPI Link |
|--------------|---------------------|-----------|
| `colorama`   | `>=0.4.6`           | [colorama](https://pypi.org/project/colorama/) |
| `matplotlib` | `>=3.10.5`          | [matplotlib](https://pypi.org/project/matplotlib/) |
| `numpy`      | `>=2.2.6`           | [numpy](https://pypi.org/project/numpy/) |
| `pandas`     | `>=2.3.2`           | [pandas](https://pypi.org/project/pandas/) |
| `pyomo`      | `>=6.9.3`           | [pyomo](https://pypi.org/project/pyomo/) |

---

## 🛠  Installation

```bash
pip install naivepydessem
```

Optionally, install with some open-source solvers:

```bash
pip install naivepydessem[solvers]
```

You can install  from source:

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
- EPE. Plano Decenal de Expansão de Energia (PDE) — Metodologia MDI, 2023.

---

## 📚 Documentation

Full API and usage documentation is built with **Sphinx** and available here:  
👉 [NaivePyDessem Documentation](https://superflanker.github.io/NaivePyDESSEM/)


This project is hosted on GitHub at:

👉 [NaivePyDessem GitHub Repo](https://github.com/superflanker/NaivePyDESSEM)

---

## 🌐 Get Involved

You are cordially invited to explore the repository, review the examples, and adapt the framework to your own studies or applications.  
This project was designed with openness and reproducibility in mind — whether you are conducting academic research, developing optimization tools, or exploring hybrid energy models, your engagement is most welcome.

### 🤝 Contribute & Collaborate
- 🧩 **Report Issues:** [Open an Issue](https://github.com/superflanker/NaivePyDESSEM/issues)  
- 🍴 **Fork the Project:** [Create Your Own Branch](https://github.com/superflanker/NaivePyDESSEM/fork)  
- 🧠 **Cite This Work:** If used in research, please acknowledge it in your publication.

### ✉️ Contact
For collaboration, technical inquiries, or academic exchange:  
📨 **Augusto Mathias Adams** — augusto.adams@ufpr.br

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