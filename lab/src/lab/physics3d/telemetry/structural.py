"""Keyed structural path-delta codec for telemetry v4.1."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from lab.physics3d.telemetry.compaction import canonical_json_bytes

_ID_CANDIDATES = (
    "node_id",
    "primitive_id",
    "actuator_id",
    "percept_id",
    "signal_id",
    "concept_id",
    "record_id",
    "capability_id",
    "sensor_id",
    "effector_id",
    "claim_id",
    "id",
)


def _identity_token(value: Any) -> str:
    if value is None:
        return "n:"
    if isinstance(value, bool):
        return f"b:{int(value)}"
    if isinstance(value, int):
        return f"i:{value}"
    if isinstance(value, float):
        return f"f:{value!r}"
    return f"s:{value}"


def _key_tokens_for_list(
    items: list[Any],
) -> tuple[str, list[str]] | None:
    if not items or not all(isinstance(item, Mapping) for item in items):
        return None
    for candidate in _ID_CANDIDATES:
        if all(candidate in item for item in items):
            tokens = [_identity_token(item[candidate]) for item in items]
            if len(tokens) == len(set(tokens)):
                return candidate, tokens
    edge_fields = ("source_id", "target_id", "kind", "delay_ticks")
    if all(all(field in item for field in edge_fields) for item in items):
        tokens = [
            "edge:" + canonical_json_bytes([item[field] for field in edge_fields]).decode("utf-8")
            for item in items
        ]
        if len(tokens) == len(set(tokens)):
            return "edge", tokens
    return None


_IMMUTABLE_LEAVES = (str, int, float, bool, type(None))


def structural_view(value: Any) -> Any:
    """Collision-free AST optimized for keyed temporal deltas."""
    if isinstance(value, Mapping):
        return {"@m": {str(key): structural_view(value[key]) for key in sorted(value, key=str)}}
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list):
        keyed = _key_tokens_for_list(value)
        if keyed is None:
            return {"@l": [structural_view(item) for item in value]}
        label, tokens = keyed
        return {
            "@k": {
                "n": label,
                "o": list(tokens),
                "i": {
                    token: structural_view(dict(item))
                    for item, token in zip(value, tokens, strict=True)
                },
            }
        }
    # Immutable scalars cannot alias the caller's state; only other leaves
    # need a private copy.
    return {"@v": value if type(value) in _IMMUTABLE_LEAVES else deepcopy(value)}


def logical_view(value: Any) -> Any:
    if not isinstance(value, Mapping) or len(value) != 1:
        raise ValueError("invalid structural AST node")
    tag, payload = next(iter(value.items()))
    if tag == "@v":
        return deepcopy(payload)
    if tag == "@m":
        if not isinstance(payload, Mapping):
            raise ValueError("invalid structural mapping node")
        return {str(key): logical_view(child) for key, child in payload.items()}
    if tag == "@l":
        if not isinstance(payload, list):
            raise ValueError("invalid structural list node")
        return [logical_view(item) for item in payload]
    if tag == "@k":
        if not isinstance(payload, Mapping):
            raise ValueError("invalid keyed structural node")
        order = payload.get("o")
        items = payload.get("i")
        if not isinstance(order, list) or not isinstance(items, Mapping):
            raise ValueError("invalid keyed structural payload")
        result = []
        for raw_token in order:
            token = str(raw_token)
            if token not in items:
                raise ValueError(f"keyed structural item missing: {token!r}")
            result.append(logical_view(items[token]))
        return result
    raise ValueError(f"unknown structural AST tag: {tag!r}")


__all__ = ["logical_view", "structural_view"]
