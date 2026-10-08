"""Transport-independent semantic observation model.

This module implements the common in-memory concepts approved by
Observation Semantic Model v1. It deliberately does not define wire fields,
serialization, events, delivery, replay, endpoints, or transport.

The Lab hosts this representation for the operational Observation Plane.
Source domains remain independent distributions and do not import this module;
their observation boundaries may expose domain-owned values that the Lab
adapts structurally without transferring semantic authority.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, TypeVar

T = TypeVar("T")

_TOKEN = re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)*$")
_FAMILY_SEGMENT = re.compile(r"^[a-z][a-z0-9_]*$")


def _token(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized or not _TOKEN.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a non-empty semantic token: {value!r}")
    return normalized


def _text(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


class AuthorityDomain(StrEnum):
    """Semantic authority domains frozen for Observation Architecture v1."""

    SYMBIONT = "symbiont"
    EMBODIMENT = "embodiment"
    MODALITY = "modality"
    ENVIRONMENT = "environment"
    LAB = "lab"


class IdentityLinkState(StrEnum):
    """State of an explicit identity relationship assertion."""

    ASSERTED = "asserted"
    CONFLICT = "conflict"
    UNRESOLVED = "unresolved"


class ConditionDimension(StrEnum):
    """Interpretive condition dimension."""

    AVAILABILITY = "availability"
    COMPLETENESS = "completeness"


class ConditionOrigin(StrEnum):
    """Where an availability/completeness condition originates."""

    SOURCE = "source"
    PLANE = "plane"


@dataclass(frozen=True, slots=True)
class ActorRef:
    """A producer, asserter, measurement source, issuer, or other actor."""

    kind: str
    identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", _token(self.kind, field_name="actor kind"))
        object.__setattr__(
            self,
            "identifier",
            _text(self.identifier, field_name="actor identifier"),
        )


@dataclass(frozen=True, slots=True)
class SemanticContractRef:
    """Reference to the semantic definition under which a claim is interpreted."""

    contract_id: str
    revision: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _token(self.contract_id, field_name="semantic contract id"),
        )
        object.__setattr__(
            self,
            "revision",
            _text(self.revision, field_name="semantic contract revision"),
        )


@dataclass(frozen=True, slots=True)
class SemanticFamily:
    """Transport-independent semantic family identity."""

    authority: AuthorityDomain
    path: tuple[str, ...]
    contract: SemanticContractRef

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("semantic family path must contain at least one segment")
        normalized = tuple(segment.strip() for segment in self.path)
        if any(not _FAMILY_SEGMENT.fullmatch(segment) for segment in normalized):
            raise ValueError(f"invalid semantic family path: {self.path!r}")
        object.__setattr__(self, "path", normalized)

    @property
    def qualified_name(self) -> str:
        return ".".join((self.authority.value, *self.path))


@dataclass(frozen=True, slots=True)
class IdentityRef:
    """Identifier assertion target with explicit namespace/issuer semantics."""

    kind: str
    value: str
    issuer: ActorRef
    scope: str | None = None
    lifetime: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", _token(self.kind, field_name="identity kind"))
        object.__setattr__(self, "value", _text(self.value, field_name="identity value"))
        if self.scope is not None:
            object.__setattr__(self, "scope", _text(self.scope, field_name="identity scope"))
        if self.lifetime is not None:
            object.__setattr__(
                self,
                "lifetime",
                _text(self.lifetime, field_name="identity lifetime"),
            )


@dataclass(frozen=True, slots=True)
class IdentityAssertion:
    """An actor asserting an identifier without becoming its issuer or authority."""

    identity: IdentityRef
    asserter: ActorRef


@dataclass(frozen=True, slots=True)
class IdentityLink:
    """Explicit relationship between two independently asserted identities."""

    left: IdentityRef
    right: IdentityRef
    relation: str
    asserter: ActorRef
    state: IdentityLinkState = IdentityLinkState.ASSERTED

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "relation",
            _token(self.relation, field_name="identity link relation"),
        )


@dataclass(frozen=True, slots=True)
class SubjectScope:
    """Entity, relation, location, process, or source-scoped claim subject."""

    kind: str
    key: str | None = None
    identities: tuple[IdentityAssertion, ...] = ()
    participants: tuple[IdentityAssertion, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", _token(self.kind, field_name="subject/scope kind"))
        if self.key is not None:
            object.__setattr__(self, "key", _text(self.key, field_name="subject/scope key"))
        if self.key is None and not self.identities and not self.participants:
            raise ValueError(
                "subject/scope must provide a key, identity assertion, or participant"
            )


@dataclass(frozen=True, slots=True)
class DomainTimeRef:
    """Typed source-domain time/revision reference, never delivery sequence."""

    domain: AuthorityDomain
    kind: str
    value: int | float | str

    def __post_init__(self) -> None:
        kind = _token(self.kind, field_name="domain time kind")
        if kind in {"observation_sequence", "transport_sequence", "delivery_sequence"}:
            raise ValueError(f"{kind!r} is delivery metadata, not domain time")
        if isinstance(self.value, str):
            object.__setattr__(
                self,
                "value",
                _text(self.value, field_name="domain time value"),
            )
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True, slots=True)
class AcquisitionBasis:
    """How a source assertion was acquired, without defining its meaning."""

    method: str
    measurement_source: ActorRef | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "method",
            _token(self.method, field_name="acquisition method"),
        )


@dataclass(frozen=True, slots=True)
class TransformationRef:
    """Meaningful derivation/transformation identity and revision."""

    transformation_id: str
    revision: str
    effective_configuration: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "transformation_id",
            _token(self.transformation_id, field_name="transformation id"),
        )
        object.__setattr__(
            self,
            "revision",
            _text(self.revision, field_name="transformation revision"),
        )
        for key, value in self.effective_configuration:
            _token(key, field_name="configuration key")
            _text(value, field_name="configuration value")


@dataclass(frozen=True, slots=True)
class LineageSourceRef:
    """Transport-independent reference to a material source claim/assertion."""

    namespace: str
    reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "namespace",
            _token(self.namespace, field_name="lineage namespace"),
        )
        object.__setattr__(
            self,
            "reference",
            _text(self.reference, field_name="lineage reference"),
        )


@dataclass(frozen=True, slots=True)
class Lineage:
    """Interpretively sufficient derivation lineage, not execution genealogy."""

    parents: tuple[LineageSourceRef, ...] = ()
    transformation: TransformationRef | None = None

    def __post_init__(self) -> None:
        if self.transformation is not None and not self.parents:
            raise ValueError("a transformation lineage requires at least one parent")


@dataclass(frozen=True, slots=True)
class ObservationCondition:
    """Availability/completeness qualifier with explicit origin."""

    dimension: ConditionDimension
    origin: ConditionOrigin
    kind: str
    detail: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "kind",
            _token(self.kind, field_name="observation condition kind"),
        )
        if self.detail is not None:
            object.__setattr__(
                self,
                "detail",
                _text(self.detail, field_name="observation condition detail"),
            )


@dataclass(frozen=True, slots=True)
class OrchestrationContext:
    """Optional Lab-run association that never substitutes source identity."""

    run_identity: IdentityAssertion


@dataclass(frozen=True, slots=True)
class SemanticClaim(Generic[T]):
    """One semantically atomic assertion.

    The value remains family-owned: the common model deliberately does not
    prescribe a universal payload shape.
    """

    family: SemanticFamily
    subject: SubjectScope
    epistemic_kind: str
    value: T

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "epistemic_kind",
            _token(self.epistemic_kind, field_name="epistemic kind"),
        )

    @property
    def authority(self) -> AuthorityDomain:
        return self.family.authority


@dataclass(frozen=True, slots=True)
class SemanticObservation(Generic[T]):
    """Transport-independent operational semantic observation."""

    claim: SemanticClaim[T]
    acquisition: AcquisitionBasis
    asserter: ActorRef
    producer: ActorRef
    domain_time: tuple[DomainTimeRef, ...] = ()
    context_time: tuple[DomainTimeRef, ...] = ()
    identity_links: tuple[IdentityLink, ...] = ()
    lineage: Lineage = field(default_factory=Lineage)
    conditions: tuple[ObservationCondition, ...] = ()
    orchestration: OrchestrationContext | None = None

    def __post_init__(self) -> None:
        mismatched = tuple(
            time_ref for time_ref in self.domain_time if time_ref.domain is not self.claim.authority
        )
        if mismatched:
            raise ValueError(
                "primary domain-time references must belong to the claim authority; "
                "cross-domain references belong in context_time"
            )

    @property
    def authority(self) -> AuthorityDomain:
        return self.claim.authority

    @property
    def family(self) -> SemanticFamily:
        return self.claim.family

    def has_identity_conflict(self) -> bool:
        return any(link.state is IdentityLinkState.CONFLICT for link in self.identity_links)

    def source_conditions(self) -> tuple[ObservationCondition, ...]:
        return tuple(
            condition
            for condition in self.conditions
            if condition.origin is ConditionOrigin.SOURCE
        )

    def plane_conditions(self) -> tuple[ObservationCondition, ...]:
        return tuple(
            condition
            for condition in self.conditions
            if condition.origin is ConditionOrigin.PLANE
        )


__all__ = [
    "AcquisitionBasis",
    "ActorRef",
    "AuthorityDomain",
    "ConditionDimension",
    "ConditionOrigin",
    "DomainTimeRef",
    "IdentityAssertion",
    "IdentityLink",
    "IdentityLinkState",
    "IdentityRef",
    "Lineage",
    "LineageSourceRef",
    "ObservationCondition",
    "OrchestrationContext",
    "SemanticClaim",
    "SemanticContractRef",
    "SemanticFamily",
    "SemanticObservation",
    "SubjectScope",
    "TransformationRef",
]
