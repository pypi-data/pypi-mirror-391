"""
EELT7030 — Operation and Expansion Planning of Electric Power Systems
Federal University of Paraná (UFPR)

Module: Transmission Line — Data Structures

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Description
-----------
Defines lightweight data classes for representing transmission lines
in DC power flow formulations. Each line connects two connection bars
(endpoints), has a specified susceptance and maximum power limit.

These structures serve as standardized inputs for Pyomo-based
optimization models, supporting both operational (DCOPF) and
expansion (MDI) formulations.

Classes
-------
TransmissionLineUnit
    Encapsulates the physical andproperties of a single
    transmission line or circuit, including endpoints and flow limits.

TransmissionLineData
    Aggregates multiple line units along with global configuration
    parameters such as planning horizon and reference data.

Notes
-----
- The line susceptance ``b`` is defined as the inverse of the series
  reactance ``x_ij`` in per-unit.
- The endpoints are represented as a list ``[bar_i, bar_j]``.
- The ``state`` attribute allows distinguishing between existing (1)
  and candidate (0) lines for expansion studies.

References
----------
[1] CEPEL, DECOMP / DESSEM. Manuais de Metodologia, 2023.
[2] Unsihuay Vila, C. Introdução aos Sistemas de Energia Elétrica,
    Lecture Notes, EELT7030/UFPR, 2023.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TransmissionLineUnit:
    """
    Data container for an individual transmission line or circuit.

    Parameters
    ----------
    name : str
        Unique identifier for the line (e.g., ``'LINE_120'``).
    b : float
        Line susceptance (1/x_ij), expressed in per-unit on the system base.
    pmax : float
        Maximum allowable active power flow (MW) through the line.
    endpoints : list of str
        Names of the two connection bars linked by the line,
        given as ``[bar_i, bar_j]``.

    """
    name: str
    model: str
    b: float
    pmax: float
    endpoints: List[str]


@dataclass
class TransmissionLineData:
    """
    Aggregated data structure for transmission lines.

    Parameters
    ----------
    horizon : int
        Number of planning periods in the study horizon.
    units : dict
        Mapping of line identifiers to their respective
        :class:`TransmissionLineUnit` instances.

    Notes
    -----
    - This class is typically used to initialize Pyomo sets and parameters.
    - Each line in ``units`` is assumed to have unique endpoints and
      electrical parameters.
    """
    horizon: int
    units: Dict[str, TransmissionLineUnit]
