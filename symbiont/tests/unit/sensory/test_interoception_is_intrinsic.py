"""Interoception is the organism's own: only its mode decides whether it exists."""

from __future__ import annotations

import pytest

from symbiont.core.orchestration.runtime import OrganismRuntime
from symbiont.host.sources import HostSenseSources
from symbiont.sensory.interoception import InteroceptionProvider, ShamInteroceptionProvider

# no host at all, a host that is not asked for, a host that is unavailable
HOSTS = [
    pytest.param({}, id="no-sources"),
    pytest.param({"discover_senses": False}, id="discovery-off"),
    pytest.param(
        {"host_sense_sources": HostSenseSources(availability="unavailable")}, id="unavailable"
    ),
    pytest.param(
        {"host_sense_sources": HostSenseSources(availability="available")}, id="available"
    ),
]


@pytest.mark.parametrize("host", HOSTS)
@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("enabled", InteroceptionProvider),
        ("sham", ShamInteroceptionProvider),
        ("absent", type(None)),
    ],
)
def test_only_the_mode_decides(host, mode, expected) -> None:
    runtime = OrganismRuntime(bootstrap_semantic_senses=False, interoception_mode=mode, **host)
    assert type(runtime._interoception_provider) is expected


def test_a_minimal_organism_with_interoception_senses_its_own_state() -> None:
    runtime = OrganismRuntime(bootstrap_semantic_senses=False, interoception_mode="enabled")
    runtime.tick()
    discovered = {
        capability.capability_id
        for capability in runtime._lifecycle._discovery.discover().capabilities
    }
    assert set(InteroceptionProvider.ORGANISM_CAPABILITY_IDS) <= discovered
