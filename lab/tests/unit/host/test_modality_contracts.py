from __future__ import annotations

import pytest

from lab.integration.organism.host_sources import HostSource
from modality.host.stdlib import StandardLibraryProvider
from modality.host.stdlib_readings import StandardLibraryReadingProvider
from symbiont.host.readings import SensorReading


def test_host_adapter_converts_discovered_organism_capabilities_back_to_modality() -> None:
    discovery = HostSource(StandardLibraryProvider())
    sampling = HostSource(StandardLibraryReadingProvider())

    capabilities = discovery.discover()
    readings = sampling.sample(capabilities)

    assert capabilities
    assert all(isinstance(reading, SensorReading) for reading in readings)
    assert {reading.capability_id for reading in readings} <= {
        capability.capability_id for capability in capabilities
    }


def test_host_adapter_rejects_use_outside_provider_contract() -> None:
    discovery = HostSource(StandardLibraryProvider())
    sampling = HostSource(StandardLibraryReadingProvider())

    with pytest.raises(TypeError, match="modality reading contract"):
        discovery.sample(())
    with pytest.raises(TypeError, match="modality discovery contract"):
        sampling.discover()
