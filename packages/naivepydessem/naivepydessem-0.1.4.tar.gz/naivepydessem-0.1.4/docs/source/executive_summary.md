
# Executive Summary / Sumário Executivo

## English Version 🇬🇧

**NaivePyDESSEM** is an educational and modular framework designed for teaching and research in **hydrothermal operation and expansion planning** of electric power systems.  
Developed as part of the graduate course **EELT7030 – Planning of Operation and Expansion of Electric Power Systems** at the **Federal University of Paraná (UFPR)**, this initiative aims to bridge the gap between academic theory and computational practice.

The framework implements simplified versions of Brazil’s main optimization models — **DESSEM, DECOMP, and MDI** — using **Pyomo** as the modeling environment.  
It provides transparent access to mathematical formulations, datasets, and solver configurations, supporting both **didactic exploration** and **research replication**.

This documentation consolidates the theoretical foundation of the course, covering:
- The mathematical modeling of DESSEM, DECOMP, and MDI;
- The hierarchy of short-, medium-, and long-term operation planning;
- Key optimization paradigms (LP, MILP, MIQP, MINLP, etc.);
- Advanced topics such as uncertainty modeling, stochastic programming, and D-OPF formulations.

By unifying theory, models, and reproducible examples, **NaivePyDESSEM** aspires to serve as an **open reference for energy planning education worldwide**, fostering knowledge exchange between academia, research centers, and the power industry.

---

## Versão em Português 🇧🇷

O **NaivePyDESSEM** é um framework educacional e modular voltado ao ensino e à pesquisa em **planejamento da operação e expansão hidrotérmica** de sistemas elétricos de potência.  
Desenvolvido no contexto da disciplina **EELT7030 – Planejamento da Operação e Expansão de Sistemas Elétricos de Potência** da **Universidade Federal do Paraná (UFPR)**, o projeto busca conectar a teoria acadêmica à prática computacional.

O framework implementa versões didáticas dos principais modelos de otimização do setor elétrico brasileiro — **DESSEM, DECOMP e MDI** — utilizando o ambiente **Pyomo** para formulação e resolução.  
Oferece acesso transparente às formulações matemáticas, conjuntos de dados e configurações de solver, permitindo a **exploração didática** e a **reprodução de experimentos de pesquisa**.

Esta documentação reúne os fundamentos teóricos da disciplina, abrangendo:
- A modelagem matemática dos modelos DESSEM, DECOMP e MDI;
- A hierarquia do planejamento de operação de curto, médio e longo prazo;
- Os principais paradigmas de otimização (LP, MILP, MIQP, MINLP, etc.);
- Tópicos avançados como incertezas, programação estocástica e formulações D-OPF.

Ao unificar teoria, modelos e exemplos reprodutíveis, o **NaivePyDESSEM** busca consolidar-se como uma **referência aberta e global para o ensino de planejamento energético**, promovendo o intercâmbio de conhecimento entre universidades, centros de pesquisa e o setor elétrico.

---

## Institutional Credits / Créditos Institucionais

Developed within the  
**Federal University of Paraná (UFPR)** – *Post-Graduate Program in Electrical Engineering (PPGEE)*  
**Department of Electrical Engineering (DELT)** 

Supervised by faculty of the professor Dr. Clodomiro Unsihuay Vila, Phd,  
in collaboration with a student of the course **EELT7030**, Augusto Mathias Adams.

Desenvolvido no âmbito da  
**Universidade Federal do Paraná (UFPR)** – *Programa de Pós-Graduação em Engenharia Elétrica (PPGEE)*  
**Departamento de Engenharia Elétrica (DELT)**

Com orientação docente do professor Dr. Clodomiro Unsihuay Vila, Phd,  
em colaboração com o discente da disciplina **EELT7030**, Augusto Mathias Adams.

---

## License / Licença

This project is licensed under the **GNU General Public License, version 3 (GPL-3.0)**.  
You may freely use, modify, and distribute this work, provided that all copies and derivative works remain under the same license.  
No warranty of any kind is provided. For more information, see: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

Este projeto está licenciado sob a **Licença Pública Geral GNU, versão 3 (GPL-3.0)**.  
É permitido o uso, modificação e redistribuição deste trabalho, desde que todas as cópias e obras derivadas mantenham a mesma licença.  
Nenhuma garantia é fornecida. Para mais informações, consulte: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

