"""Target scoring, claiming, and alignment network helpers."""

from __future__ import annotations

from cvc.agent.geometry import manhattan
from cvc.agent.types import (
    _CLAIMED_TARGET_PENALTY,
    _EXTRACTOR_MEMORY_STEPS,
    _HUB_ALIGN_DISTANCE,
    _JUNCTION_ALIGN_DISTANCE,
    _JUNCTION_AOE_RANGE,
    _STATION_TARGETS_BY_AGENT,
    _TARGET_CLAIM_STEPS,
    KnownEntity,
)


def within_alignment_network(
    candidate: tuple[int, int],
    sources: list[KnownEntity],
) -> bool:
    for source in sources:
        max_distance = _HUB_ALIGN_DISTANCE if source.entity_type == "hub" else _JUNCTION_ALIGN_DISTANCE
        if manhattan(candidate, source.position) <= max_distance:
            return True
    return False


def teammate_closer_to_target(
    *,
    current_position: tuple[int, int],
    target: tuple[int, int],
    teammate_positions: list[tuple[int, int]],
) -> bool:
    """Check if any teammate aligner is closer to the target than we are."""
    my_dist = manhattan(current_position, target)
    for pos in teammate_positions:
        if manhattan(pos, target) < my_dist:
            return True
    return False


def aligner_target_score(
    *,
    current_position: tuple[int, int],
    candidate: KnownEntity,
    unreachable: list[KnownEntity],
    enemy_junctions: list[KnownEntity],
    claimed_by_other: bool,
    hub_position: tuple[int, int] | None = None,
    friendly_sources: list[KnownEntity] | None = None,
    hotspot_count: int = 0,
    teammate_closer: bool = False,
) -> tuple[float, float]:
    distance = float(manhattan(current_position, candidate.position))
    expansion = sum(
        1 for entity in unreachable if manhattan(candidate.position, entity.position) <= _JUNCTION_ALIGN_DISTANCE
    )
    enemy_aoe = (
        1.0
        if any(manhattan(candidate.position, enemy.position) <= _JUNCTION_AOE_RANGE for enemy in enemy_junctions)
        else 0.0
    )
    # Strongly prefer hub-proximal junctions: less travel, safer, faster cycling
    hub_penalty = 0.0
    if hub_position is not None:
        hub_dist = float(manhattan(hub_position, candidate.position))
        if hub_dist > 25:
            hub_penalty = (hub_dist - 25) * 7.79 + 48.82  # Reduced base from 48.83 to 48.82 (-0.02%) for bidirectional far-range base tuning
        elif hub_dist > 15:
            hub_penalty = (hub_dist - 15) * 2.77 + 9.53  # Reduced base from 9.54 to 9.53 (-0.10%) for bidirectional 15-25 range base tuning
        elif hub_dist > 10:
            hub_penalty = (hub_dist - 10) * 1.30 + 1.80  # Reduced base from 1.81 to 1.80 (-0.55%) for bidirectional 10-15 range base tuning
        else:
            hub_penalty = hub_dist * 0.260  # Reduced from 0.261 to 0.260 (-0.38%) for bidirectional hub clustering tuning
    # Reduce hotspot penalty for hub-proximal junctions (worth defending)
    # Four_score: higher base penalty due to 3x more scramblers (4 teams)
    hotspot_weight = 11.52  # Increased from 11.50 to 11.52 (+0.17%) for bidirectional far-range contested junction tuning
    if hub_position is not None:
        hub_dist = float(manhattan(hub_position, candidate.position))
        if hub_dist <= 10:
            hotspot_weight = 1.64  # Increased from 1.62 to 1.64 (+1.23%) for bidirectional near-hub recapture tuning
        elif hub_dist <= 15:
            hotspot_weight = 5.46  # Increased from 5.44 to 5.46 (+0.37%) for bidirectional mid-range contested junction tuning
    hotspot_penalty = min(hotspot_count, 3.32) * hotspot_weight  # Increased cap from 3.30 to 3.32 (+0.61%) for bidirectional contested junction penalty cap tuning
    # Network bonus for chain-building near friendly junctions
    # Increased from alpha.0's 0.5 to 0.75 for better consolidation (gamma_v6 validated)
    # Further increased to 0.77 (+3%) for stronger chain-building incentive
    # Further increased to 0.78 (+1.3%) for continued chain-building emphasis
    network_bonus = 0.0
    if friendly_sources:
        nearby_friendly = sum(
            1
            for source in friendly_sources
            if source.entity_type != "hub"
            and manhattan(candidate.position, source.position) <= _JUNCTION_ALIGN_DISTANCE
        )
        network_bonus = min(nearby_friendly, 4.57) * 0.93  # Increased cap from 4.56 to 4.57 (+0.22%) for bidirectional network consolidation cap tuning
    teammate_penalty = 9.52 if teammate_closer else 0.0  # Increased from 9.51 to 9.52 (+0.11%) for bidirectional coordination tuning
    return (
        distance
        - min(expansion * 6.63, 37.75)  # Increased weight from 6.62 to 6.63 (+0.15%) for bidirectional expansion bonus weight tuning
        + enemy_aoe * 10.77  # Increased from 10.76 to 10.77 (+0.09%) for bidirectional enemy avoidance tuning
        + (_CLAIMED_TARGET_PENALTY if claimed_by_other else 0.0)
        + hub_penalty
        + hotspot_penalty
        - network_bonus
        + teammate_penalty,
        -float(expansion),
    )


def is_claimed_by_other(
    *,
    claims: dict[tuple[int, int], tuple[int, int]],
    candidate: tuple[int, int],
    agent_id: int,
    step: int,
) -> bool:
    claim = claims.get(candidate)
    if claim is None:
        return False
    owner_id, owner_step = claim
    if owner_id == agent_id:
        return False
    return step - owner_step <= _TARGET_CLAIM_STEPS


def is_usable_recent_extractor(entity: KnownEntity, *, step: int) -> bool:
    return step - entity.last_seen_step <= _EXTRACTOR_MEMORY_STEPS


def scramble_target_score(
    *,
    current_position: tuple[int, int],
    hub_position: tuple[int, int],
    candidate: KnownEntity,
    neutral_junctions: list[KnownEntity],
    friendly_junctions: list[KnownEntity] | None = None,
) -> tuple[float, float]:
    distance = float(manhattan(current_position, candidate.position))
    blocked_neutrals = sum(
        1 for neutral in neutral_junctions if manhattan(candidate.position, neutral.position) <= _JUNCTION_AOE_RANGE
    )
    corner_pressure = min(manhattan(hub_position, candidate.position) / 7.49, 10.91)  # Increased cap from 10.90 to 10.91 (+0.09%) for bidirectional corner pressure cap tuning
    # Strongly prioritize enemy junctions near our friendly network (defending our score)
    threat_bonus = 0.0
    if friendly_junctions:
        threatened = sum(
            1 for f in friendly_junctions if manhattan(candidate.position, f.position) <= _JUNCTION_ALIGN_DISTANCE
        )
        threat_bonus = threatened * 10.61  # Increased from 10.60 to 10.61 (+0.09%) for bidirectional defensive priority tuning
    return (
        distance - blocked_neutrals * 8.81 - corner_pressure - threat_bonus,  # Increased from 8.80 to 8.81 (+0.11%) for bidirectional expansion-blocking tuning
        -float(blocked_neutrals),
    )


def spawn_relative_station_target(agent_id: int, role: str) -> tuple[int, int] | None:
    station_targets = _STATION_TARGETS_BY_AGENT.get(role)
    if station_targets is None:
        return None
    return station_targets.get(agent_id)
