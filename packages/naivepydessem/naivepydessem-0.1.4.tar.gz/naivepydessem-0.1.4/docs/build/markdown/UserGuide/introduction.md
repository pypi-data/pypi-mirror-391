# NaivePyDESSEM User Guide

## 1. Introduction

### Purpose and Scope

The **NaivePyDESSEM Project Suite** is a pedagogical framework designed to provide a transparent, modular, and fully reproducible environment for the study and experimentation of **power system operation and expansion planning**. The suite comprises three complementary packages — **NaivePyDESSEM**, **NaivePyDECOMP**, and **MDI** — which collectively simulate, analyze, and optimize short-term dispatch, medium-term operation, and data integration within the energy systems domain.

This User Guide is intended for researchers, graduate students, and professionals seeking to understand the internal logic, structure, and usage of the NaivePyDESSEM ecosystem. The document adopts a formal technical tone consistent with academic and professional documentation standards, offering detailed explanations of modeling principles, solver integration, data preparation, and output interpretation.

### Conceptual Foundations

The NaivePyDESSEM family mirrors the conceptual hierarchy established in the **CEPEL** models — *DESSEM* for short-term operation, *DECOMP* for medium-term optimization, and *NEWAVE* for long-term planning — while maintaining a simplified yet analytically rigorous structure suitable for academic research and classroom experimentation.

Each package is built atop the **Pyomo** optimization framework, leveraging its declarative modeling language to define decision variables, constraints, and objective functions for deterministic and stochastic optimization problems. The design emphasizes clarity of implementation, mathematical transparency, and reproducibility, allowing users to directly inspect, modify, and extend each model component.

### Target Audience

This guide addresses three primary user profiles:

1. **Students and Educators** – who require a didactic framework for demonstrating fundamental principles of energy systems operation and optimization.
2. **Researchers and Developers** – who seek a modular foundation for developing or benchmarking novel optimization methodologies, including stochastic, metaheuristic, or decomposition-based approaches.
3. **Industry Professionals** – who wish to experiment with open, interpretable models before transitioning to large-scale proprietary tools.

### System Requirements

To ensure optimal performance and reproducibility, the following environment is recommended:

* **Operating System:** Linux (preferred), macOS, or Windows 10/11.
* **Python Version:** 3.9 or higher.
* **Required Dependencies:** `pyomo`, `pandas`, `numpy`, `yaml`, `matplotlib`, and `mealpy` (for metaheuristic integration).
* **Optional Solvers:** `GLPK`, `CPLEX`, `Gurobi`, or `IPOPT`.

Installation can be performed via standard Python package management tools:

```bash
pip install naivepydessem
```

### Documentation Conventions

Throughout this guide, the following conventions are used:

* **Monospaced text** denotes command-line inputs or code fragments.
* *Italics* identify technical terms, functions, or variables introduced in the text.
* Boldface (\*\*) is used to highlight crucial terms or key conceptual distinctions.
* Mathematical expressions appear in inline LaTeX syntax when applicable.

Example:

> The **economic dispatch problem** seeks to minimize the total operational cost ( C = \\sum_{i} c_i P_i ) subject to power balance and generation limits.

### Versioning and Licensing

All packages within the NaivePyDESSEM ecosystem adhere to **semantic versioning (SemVer)** principles. Updates follow a structured pattern of incremental releases:

* `MAJOR` – structural redesign or interface-breaking changes.
* `MINOR` – feature additions or functional extensions.
* `PATCH` – bug fixes, documentation, or minor corrections.

The project is distributed under the **MIT License**, ensuring unrestricted use, modification, and distribution for educational and research purposes. Users are encouraged to cite the project in academic publications using the official bibliographic entry provided in the *References* section of this guide.

---

**Next Section:** [Conceptual Background →]()
