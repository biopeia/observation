"""Organism-owned sensory transduction layer.

The host discovers observable sources; this package owns how an individual
Symbiont turns those sources into percepts.  Keeping the boundary explicit
prevents provider/platform semantics from becoming cognitive semantics.
"""

from .evidence import EvidenceCount, SampleCount
from .limits import SensoryLimits
from .modalities import DEFAULT_MODALITIES, SensoryModality
from .predictive_credit import PairwisePredictiveEvidence, SensorySelectionEngine
from .sensor import MaturityState, SensorState
from .system import SensorySystem
from .transduction import TransductionKind

__all__ = [
    "DEFAULT_MODALITIES",
    "EvidenceCount",
    "MaturityState",
    "PairwisePredictiveEvidence",
    "SampleCount",
    "SensoryLimits",
    "SensoryModality",
    "SensorySelectionEngine",
    "SensorySystem",
    "SensorState",
    "TransductionKind",
]
