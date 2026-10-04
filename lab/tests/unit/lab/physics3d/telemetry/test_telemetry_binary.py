from __future__ import annotations

import math

from lab.physics3d.telemetry.binary import (
    BinaryDeltaReader,
    BinaryDeltaWriter,
    BinaryDenseReader,
    BinaryDenseWriter,
    BinaryEventReader,
    BinaryEventWriter,
    BinaryFrameSchemaReader,
    BinaryFrameSchemaWriter,
    BinaryPathRegistryReader,
    BinaryPathRegistryWriter,
    BinaryRecordIterator,
    BinaryStringTableReader,
    BinaryStringTableWriter,
    BinaryValueCodec,
    decode_uvarint,
    encode_uvarint,
)
from lab.physics3d.telemetry.compaction import canonical_json_bytes
from lab.physics3d.telemetry.structural import logical_view, structural_view


def test_uvarint_round_trip_boundaries():
    for value in (0, 1, 127, 128, 255, 16_384, 2**32, 2**63 - 1):
        encoded = encode_uvarint(value)
        decoded, offset = decode_uvarint(encoded)
        assert decoded == value
        assert offset == len(encoded)


def test_binary_value_codec_round_trip_preserves_signed_zero(tmp_path):
    strings_path = tmp_path / "strings.bin"
    with strings_path.open("wb") as handle:
        strings = BinaryStringTableWriter(handle)
        codec = BinaryValueCodec(strings)
        payload = codec.encode(
            {
                "zero": 0.0,
                "negative_zero": -0.0,
                "ids": ["sense.signal.abc", "sense.signal.abc"],
                "nested": [None, True, False, 17, -9],
            }
        )

    reader_strings = BinaryStringTableReader(strings_path)
    decoded, offset = BinaryValueCodec(reader_strings).decode(payload)

    assert offset == len(payload)
    assert canonical_json_bytes(decoded) == canonical_json_bytes(
        {
            "zero": 0.0,
            "negative_zero": -0.0,
            "ids": ["sense.signal.abc", "sense.signal.abc"],
            "nested": [None, True, False, 17, -9],
        }
    )
    assert math.copysign(1.0, decoded["negative_zero"]) < 0


def test_binary_dense_full_sparse_and_copy_round_trip(tmp_path):
    strings_path = tmp_path / "strings.bin"
    schemas_path = tmp_path / "schemas.bin"
    frames_path = tmp_path / "frames.bin"

    with (
        strings_path.open("wb") as strings_handle,
        schemas_path.open("wb") as schema_handle,
        frames_path.open("wb") as frame_handle,
    ):
        strings = BinaryStringTableWriter(strings_handle)
        schemas = BinaryFrameSchemaWriter(schema_handle, strings)
        writer = BinaryDenseWriter(frame_handle, schemas, strings)
        first = {"x": 1.0, "y": [2.0, 3.0]}
        second = {"x": 1.5, "y": [2.0, 3.0]}
        writer.append(1, "post.physical", first)
        writer.append(2, "post.physical", second)
        writer.append_copy(
            3,
            "pre.physical",
            second,
            source_channel="post.physical",
        )

    strings = BinaryStringTableReader(strings_path)
    schemas = BinaryFrameSchemaReader(schemas_path, strings)
    reader = BinaryDenseReader(schemas, strings)

    records = []
    with frames_path.open("rb") as handle:
        iterator = BinaryRecordIterator(handle, reader.decode_record)
        while True:
            item = iterator.next()
            if item is None:
                break
            records.append(item)
            reader.apply(item)

    assert len(records) == 3
    assert records[1]["m"] == 1
    assert records[2]["m"] == 2
    assert reader.values["post.physical"] == second
    assert reader.values["pre.physical"] == second


def test_binary_structural_delta_round_trip_claim_growth(tmp_path):
    strings_path = tmp_path / "strings.bin"
    paths_path = tmp_path / "paths.bin"
    state_path = tmp_path / "state.bin"

    first = [
        {
            "signal_id": "signal.a",
            "claims": [{"claim_id": "claim.1", "status": "candidate", "count": 1}],
        }
    ]
    second = [
        {
            "signal_id": "signal.a",
            "claims": [
                {"claim_id": "claim.1", "status": "supported", "count": 2},
                {"claim_id": "claim.2", "status": "candidate", "count": 1},
            ],
        }
    ]

    with (
        strings_path.open("wb") as strings_handle,
        paths_path.open("wb") as paths_handle,
        state_path.open("wb") as state_handle,
    ):
        strings = BinaryStringTableWriter(strings_handle)
        paths = BinaryPathRegistryWriter(paths_handle, strings)
        writer = BinaryDeltaWriter(
            state_handle,
            paths,
            strings,
            transform=structural_view,
        )
        writer.append(1, "runtime.signal_knowledge", first)
        writer.append(2, "runtime.signal_knowledge", second)

    strings = BinaryStringTableReader(strings_path)
    paths = BinaryPathRegistryReader(paths_path, strings)
    reader = BinaryDeltaReader(
        paths,
        strings,
        transform=structural_view,
        inverse=logical_view,
    )

    with state_path.open("rb") as handle:
        iterator = BinaryRecordIterator(handle, reader.decode_record)
        one = iterator.next()
        two = iterator.next()
        assert one is not None and two is not None
        reader.apply(one)
        _channel, restored = reader.apply(two)

    assert restored == second
    assert len(two["p"]) < 10


def test_binary_event_writer_batches_ephemeral_events(tmp_path):
    strings_path = tmp_path / "strings.bin"
    events_path = tmp_path / "events.bin"
    events = [
        {"kind": "one", "event_id": "e1"},
        {"kind": "two", "event_id": "e2"},
        {"kind": "three", "event_id": "e3"},
    ]

    with (
        strings_path.open("wb") as strings_handle,
        events_path.open("wb") as events_handle,
    ):
        strings = BinaryStringTableWriter(strings_handle)
        writer = BinaryEventWriter(events_handle, strings)
        hashes = writer.append(1, "runtime.knowledge_events", events)
        assert len(hashes) == 1

    strings = BinaryStringTableReader(strings_path)
    reader = BinaryEventReader(strings)
    with events_path.open("rb") as handle:
        iterator = BinaryRecordIterator(handle, reader.decode_record)
        record = iterator.next()
        assert record is not None
        assert iterator.next() is None
        reader.apply(record)

    assert reader.values["runtime.knowledge_events"] == events


def test_binary_dense_reader_rejects_wrong_full_leaf_count(tmp_path):
    strings_path = tmp_path / "strings.bin"
    schemas_path = tmp_path / "schemas.bin"
    frames_path = tmp_path / "frames.bin"

    with (
        strings_path.open("wb") as strings_handle,
        schemas_path.open("wb") as schema_handle,
        frames_path.open("wb") as frame_handle,
    ):
        strings = BinaryStringTableWriter(strings_handle)
        schemas = BinaryFrameSchemaWriter(schema_handle, strings)
        writer = BinaryDenseWriter(frame_handle, schemas, strings)
        writer.append(1, "dense", {"a": 1.0, "b": 2.0})

    strings = BinaryStringTableReader(strings_path)
    schemas = BinaryFrameSchemaReader(schemas_path, strings)
    reader = BinaryDenseReader(schemas, strings)
    with frames_path.open("rb") as handle:
        iterator = BinaryRecordIterator(handle, reader.decode_record)
        record = iterator.next()
    assert record is not None
    record["v"] = record["v"][:-1]

    import pytest

    with pytest.raises(ValueError, match="leaf count mismatch"):
        reader.apply(record)


def _reference_diff(left, right, path=""):
    """The delta algorithm as first written: eager paths, a copy per value."""
    from collections.abc import Mapping
    from copy import deepcopy

    from lab.physics3d.telemetry.binary import _escape, _exact_equal

    if type(left) is not type(right):
        return [{"op": "set", "path": path, "value": deepcopy(right)}]
    if isinstance(right, Mapping):
        operations = []
        for key in sorted(set(left) - set(right), key=str):
            operations.append({"op": "remove", "path": f"{path}/{_escape(key)}"})
        for key in sorted(right, key=str):
            child = f"{path}/{_escape(key)}"
            if key not in left:
                operations.append({"op": "set", "path": child, "value": deepcopy(right[key])})
            else:
                operations.extend(_reference_diff(left[key], right[key], child))
        return operations
    if isinstance(right, list):
        if len(left) != len(right):
            return [{"op": "set", "path": path, "value": deepcopy(right)}]
        operations = []
        for index, (before, after) in enumerate(zip(left, right, strict=True)):
            operations.extend(_reference_diff(before, after, f"{path}/{index}"))
        return operations
    if not _exact_equal(left, right):
        return [{"op": "set", "path": path, "value": deepcopy(right)}]
    return []


def test_delta_operations_match_the_reference_algorithm():
    import random

    from lab.physics3d.telemetry.binary import _diff
    from lab.physics3d.telemetry.structural import structural_view

    rng = random.Random(7)
    keys = ["a", "b/c", "d~e", "id", "10", "z"]

    def value(depth):
        roll = rng.random()
        if depth == 0 or roll < 0.35:
            return rng.choice([0, 1, 1.0, -0.0, 0.0, True, None, "x", "y/z", 2.5])
        if roll < 0.7:
            return {key: value(depth - 1) for key in rng.sample(keys, rng.randint(0, 4))}
        return [value(depth - 1) for _ in range(rng.randint(0, 3))]

    for _ in range(300):
        left, right = value(4), value(4)
        for before, after in ((left, right), (structural_view(left), structural_view(right))):
            assert _diff(before, after) == _reference_diff(before, after)
        assert _diff(left, left) == []


def test_delta_writer_keeps_no_alias_of_the_callers_state():
    from io import BytesIO

    from lab.physics3d.telemetry.binary import (
        BinaryDeltaWriter,
        BinaryPathRegistryWriter,
        BinaryStringTableWriter,
    )
    from lab.physics3d.telemetry.structural import structural_view

    strings = BinaryStringTableWriter(BytesIO())
    paths = BinaryPathRegistryWriter(BytesIO(), strings)
    for options in ({}, {"transform": structural_view, "transform_returns_owned": True}):
        writer = BinaryDeltaWriter(BytesIO(), paths, strings, **options)
        state = {"nested": {"values": [1, 2]}, "name": "n"}
        assert writer.append(1, "channel", state) is not None
        state["nested"]["values"][0] = 99
        info = writer.append(2, "channel", state)
        assert info is not None and info["operations"] == 1
        assert writer.append(3, "channel", state) is None
