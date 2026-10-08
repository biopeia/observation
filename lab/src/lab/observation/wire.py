"""Versioned JSON projection of semantic observations.

This module is a transport representation only. It does not define semantic
authority; it serializes the already-admitted SemanticObservation model.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from lab.observation.plane import PlaneMessage
from lab.observation.semantic import ActorRef, IdentityAssertion, SemanticObservation

SEMANTIC_WIRE_CONTRACT = "observation-semantic-wire-v1"


def _json_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {str(key): _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return _json_value(value.value)
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if type(value) in (str, int, float, bool) or value is None:
        return value
    return str(value)


def _actor(actor: ActorRef | None) -> dict[str, str] | None:
    if actor is None:
        return None
    return {"kind": actor.kind, "id": actor.identifier}


def _identity(assertion: IdentityAssertion) -> dict[str, Any]:
    identity = assertion.identity
    payload: dict[str, Any] = {
        "kind": identity.kind,
        "value": identity.value,
        "issuer": _actor(identity.issuer),
        "asserter": _actor(assertion.asserter),
    }
    if identity.scope is not None:
        payload["scope"] = identity.scope
    if identity.lifetime is not None:
        payload["lifetime"] = identity.lifetime
    return payload


def semantic_observation_payload(
    observation: SemanticObservation[object],
    *,
    sequence: int | None = None,
) -> dict[str, Any]:
    claim = observation.claim
    subject = claim.subject
    payload: dict[str, Any] = {
        "type": "semantic_observation",
        "wire_contract": SEMANTIC_WIRE_CONTRACT,
        "family": claim.family.qualified_name,
        "authority": claim.authority.value,
        "semantic_contract": {
            "id": claim.family.contract.contract_id,
            "revision": claim.family.contract.revision,
        },
        "subject": {
            "kind": subject.kind,
            "key": subject.key,
            "identities": [_identity(item) for item in subject.identities],
            "participants": [_identity(item) for item in subject.participants],
        },
        "epistemic_kind": claim.epistemic_kind,
        "value": _json_value(claim.value),
        "acquisition": {
            "method": observation.acquisition.method,
            "measurement_source": _actor(observation.acquisition.measurement_source),
        },
        "asserter": _actor(observation.asserter),
        "producer": _actor(observation.producer),
        "domain_time": [
            {"domain": item.domain.value, "kind": item.kind, "value": item.value}
            for item in observation.domain_time
        ],
        "context_time": [
            {"domain": item.domain.value, "kind": item.kind, "value": item.value}
            for item in observation.context_time
        ],
        "orchestration": (
            {
                "run": _identity(observation.orchestration.run_identity),
            }
            if observation.orchestration is not None
            else None
        ),
        "conditions": [
            {
                "dimension": item.dimension.value,
                "origin": item.origin.value,
                "kind": item.kind,
                "detail": item.detail,
            }
            for item in observation.conditions
        ],
    }
    if sequence is not None:
        payload["sequence"] = int(sequence)
    if observation.lineage.parents or observation.lineage.transformation is not None:
        payload["lineage"] = {
            "parents": [
                {"namespace": item.namespace, "reference": item.reference}
                for item in observation.lineage.parents
            ],
            "transformation": (
                {
                    "id": observation.lineage.transformation.transformation_id,
                    "revision": observation.lineage.transformation.revision,
                    "effective_configuration": dict(
                        observation.lineage.transformation.effective_configuration
                    ),
                }
                if observation.lineage.transformation is not None
                else None
            ),
        }
    return payload


def plane_message_payload(message: PlaneMessage) -> dict[str, Any]:
    return semantic_observation_payload(message.observation, sequence=message.sequence)


__all__ = [
    "SEMANTIC_WIRE_CONTRACT",
    "plane_message_payload",
    "semantic_observation_payload",
]
