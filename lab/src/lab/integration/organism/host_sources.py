"""Host channels from ``modality.host``, presented to the organism in its own types."""

from __future__ import annotations

from modality.host.contracts import (
    HostDiscoveryProvider,
    HostReadingProvider,
    HostTickObserver,
)
from modality.host.records import Capability as ModalityCapability
from modality.host.records import CapabilityKind as ModalityCapabilityKind

from symbiont.host.contracts import Capability, CapabilityKind
from symbiont.host.readings import ReadingPrivacyClass, ReadingQuality, SensorReading, Unit


class HostSource:
    """One host channel as an organism discovery and reading provider.

    Records are converted field for field; the organism's types validate them.
    """

    def __init__(
        self,
        source: HostDiscoveryProvider | HostReadingProvider | HostTickObserver,
    ) -> None:
        self.source = source
        self.provider_id: str = source.provider_id

    def discover(self) -> tuple[Capability, ...]:
        if not isinstance(self.source, HostDiscoveryProvider):
            raise TypeError("host source does not satisfy the modality discovery contract")
        return tuple(
            Capability(
                capability_id=surface.capability_id,
                kind=CapabilityKind(surface.kind),
                source=surface.source,
                available=surface.available,
                detail=surface.detail,
            )
            for surface in self.source.discover()
        )

    def sample(self, capabilities: tuple[Capability, ...]) -> tuple[SensorReading, ...]:
        if not isinstance(self.source, HostReadingProvider):
            raise TypeError("host source does not satisfy the modality reading contract")
        modality_capabilities = tuple(
            ModalityCapability(
                capability_id=capability.capability_id,
                kind=ModalityCapabilityKind(capability.kind.value),
                source=capability.source,
                available=capability.available,
                detail=capability.detail,
            )
            for capability in capabilities
        )
        return tuple(
            SensorReading(
                capability_id=reading.capability_id,
                source=reading.source,
                value=reading.value,
                unit=Unit(reading.unit),
                monotonic_timestamp_ns=reading.monotonic_timestamp_ns,
                quality=ReadingQuality(reading.quality),
                privacy_class=ReadingPrivacyClass(reading.privacy_class),
            )
            for reading in self.source.sample(modality_capabilities)
        )

    def observe_tick(self, latency: float) -> None:
        if not isinstance(self.source, HostTickObserver):
            raise TypeError("host source does not satisfy the passive observer contract")
        self.source.observe_tick(latency)
