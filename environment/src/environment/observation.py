"""W1 local observation pipeline (docs/design/archive/symbiont-world-v1.md §12.1).

No real fields/resources exist yet (deferred to W2's Genesis ground truth).
This only exercises ObservableSource -> WorldObservation end to end with a
single synthetic, opaque signal: local occupancy density around a body.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import math

from environment.contracts import WorldObservation
from environment.genesis import WorldEnvironment
from environment.topology import BodyPlacement, HexCoord, HexTopology, OccupancyGrid




@dataclass(frozen=True, slots=True)
class ResourcePoolItem:
    """One opaque Environment resource amount at one World cell."""

    resource_id: str
    amount: float
    capacity: float
    quantity_kind: str = "model_amount"

    def __post_init__(self) -> None:
        resource_id = self.resource_id.strip()
        if not resource_id:
            raise ValueError("resource_id must not be empty")
        amount = float(self.amount)
        capacity = float(self.capacity)
        if not math.isfinite(amount) or not math.isfinite(capacity) or capacity < 0.0:
            raise ValueError("resource amount/capacity must be finite and capacity non-negative")
        if not 0.0 <= amount <= capacity:
            raise ValueError("resource amount must be within [0, capacity]")
        if self.quantity_kind != "model_amount":
            raise ValueError("resource quantity_kind must be model_amount")
        object.__setattr__(self, "resource_id", resource_id)
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "capacity", capacity)


@dataclass(frozen=True, slots=True)
class ResourcePoolObservation:
    """Environment-owned logical resource-pool state for one hex cell.

    Hex coordinates are the current Environment representation, not a universal
    spatial ontology. Resource ids are opaque Environment ids.
    """

    q: int
    r: int
    resources: tuple[ResourcePoolItem, ...]
    world_tick: int
    contract_revision: str = "v1"

    def __post_init__(self) -> None:
        if isinstance(self.q, bool) or not isinstance(self.q, int):
            raise ValueError("q must be an integer")
        if isinstance(self.r, bool) or not isinstance(self.r, int):
            raise ValueError("r must be an integer")
        if isinstance(self.world_tick, bool) or not isinstance(self.world_tick, int) or self.world_tick < 0:
            raise ValueError("world_tick must be a non-negative integer")
        resources = tuple(self.resources)
        if any(not isinstance(item, ResourcePoolItem) for item in resources):
            raise ValueError("resources must contain ResourcePoolItem values")
        ids = tuple(item.resource_id for item in resources)
        if len(set(ids)) != len(ids):
            raise ValueError("resource ids must be unique in one cell")
        revision = self.contract_revision.strip()
        if not revision:
            raise ValueError("contract_revision must not be empty")
        object.__setattr__(self, "resources", resources)
        object.__setattr__(self, "contract_revision", revision)

def opaque_signal_id(label: str) -> str:
    """Stable hash of an apparatus-only label. The label itself never
    reaches WorldObservation -- only its hash does (docs/design §3 inv. 1)."""
    return sha256(f"symbiont-world:signal:{label}".encode("utf-8")).hexdigest()[:16]


LOCAL_OCCUPANCY_SIGNAL = opaque_signal_id("local-occupancy-density")
_LOCAL_OCCUPANCY_SIGNAL = LOCAL_OCCUPANCY_SIGNAL


def local_observation(
    topology: HexTopology,
    occupancy: OccupancyGrid,
    body: BodyPlacement,
    environment: WorldEnvironment | None = None,
) -> WorldObservation:
    visited: set[HexCoord] = {body.occupied_cell}
    frontier: set[HexCoord] = {body.occupied_cell}
    occupied_neighbors = 0
    total_neighbors = 0

    for _ in range(max(body.interaction_radius, 0)):
        next_frontier: set[HexCoord] = set()
        for cell in frontier:
            for direction in range(6):
                neighbor = cell.neighbor(direction)
                if neighbor in visited or not topology.in_bounds(neighbor):
                    continue
                visited.add(neighbor)
                next_frontier.add(neighbor)
                total_neighbors += 1
                if occupancy.is_occupied(neighbor):
                    occupied_neighbors += 1
        frontier = next_frontier

    density = occupied_neighbors / total_neighbors if total_neighbors else 0.0
    signals: dict[str, float] = {_LOCAL_OCCUPANCY_SIGNAL: density}

    if environment is not None:
        signals.update(environment.field_values())
        signals.update(environment.resource_pool(body.occupied_cell))
        signals.update(environment.hazard_exposures_at(body.occupied_cell, density))

    return WorldObservation(signals=signals)


def resource_pool_observation(
    environment: WorldEnvironment,
    cell: HexCoord,
) -> ResourcePoolObservation | None:
    """Return passive logical resource state for an already materialized cell.

    Observation never materializes a new pool and therefore cannot change World
    state merely because a consumer asked to observe it.
    """

    if not environment.is_materialized(cell):
        return None
    pool = environment.resource_pool(cell)
    items = tuple(
        ResourcePoolItem(
            resource_id=resource_id,
            amount=float(amount),
            capacity=float(environment.ground_truth.resource_law(cell, resource_id).capacity),
        )
        for resource_id, amount in sorted(pool.items())
    )
    return ResourcePoolObservation(
        q=cell.q,
        r=cell.r,
        resources=items,
        world_tick=environment.current_tick,
    )
