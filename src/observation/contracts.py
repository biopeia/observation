"""Observer-only contracts exposed to presentation transports.

Nothing in this module is consumed by the organism runtime. These structures
exist solely to make the boundary between scientific evidence and UI projection
explicit and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

PRESENTATION_PROJECTION = "observer-presentation-v1"
COMPLETED_FRAME_CONTRACT = "completed-render-frame-v1"
OBSERVATION_IDENTITY_CONTRACT = "observation-identity-v1"


@dataclass(frozen=True)
class ObservedFrame:
    """Transitional inherited projection assembled from a rendered tick.

    This inherited migration-stage structure is not a stable Biopeia semantic
    or compatibility contract. Its fields are retained only as an explicitly
    transitional projection and must not be treated as a target schema.
    """

    tick: int
    source: str
    run_id: str
    organism_id: str | None
    body: Mapping[str, Any] | None
    cognition: Mapping[str, Any] | None
    vitals: Mapping[str, Any] | None
    mind: Mapping[str, Any]
    instance_id: str | None = None
    body_id: str | None = None
    embodiment_id: str | None = None
    topology_revision: int | None = None

    def as_event(self) -> dict[str, Any]:
        event: dict[str, Any] = {
            "type": "observed_frame",
            "source": self.source,
            "run_id": self.run_id,
            "tick": int(self.tick),
            "organism_id": self.organism_id,
            "body": dict(self.body) if self.body is not None else None,
            "cognition": dict(self.cognition) if self.cognition is not None else None,
            "vitals": dict(self.vitals) if self.vitals is not None else None,
            "mind": dict(self.mind),
            "provenance": {
                "owner": "observer",
                "projection": PRESENTATION_PROJECTION,
                "contract": COMPLETED_FRAME_CONTRACT,
                "identity_contract": OBSERVATION_IDENTITY_CONTRACT,
                "feeds_back": False,
            },
        }
        for key, value in (
            ("instance_id", self.instance_id),
            ("body_id", self.body_id),
            ("embodiment_id", self.embodiment_id),
            ("topology_revision", self.topology_revision),
        ):
            if value is not None:
                event[key] = value
        return event


__all__ = [
    "COMPLETED_FRAME_CONTRACT",
    "OBSERVATION_IDENTITY_CONTRACT",
    "ObservedFrame",
    "PRESENTATION_PROJECTION",
]
