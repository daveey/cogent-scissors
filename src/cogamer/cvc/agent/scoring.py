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
            hub_penalty = (hub_dist - 25) * 7.81 + 48.84  # Reduced base from 48.85 to 48.84 (-0.02%) for continued far-range base tuning
        elif hub_dist > 15:
            hub_penalty = (hub_dist - 15) * 2.79 + 9.55  # Reduced multiplier from 2.80 to 2.79 (-0.36%) for continued 15-25 range multiplier tuning
        elif hub_dist > 10:
            hub_penalty = (hub_dist - 10) * 1.32 + 1.82  # Reduced multiplier from 1.33 to 1.32 (-0.75%) for continued 10-15 range multiplier tuning
        else:
            hub_penalty = hub_dist * 0.262  # Reduced from 0.263 to 0.262 (-0.38%) for continued tighter hub clustering tuning
    # Reduce hotspot penalty for hub-proximal junctions (worth defending)
    # Four_score: higher base penalty due to 3x more scramblers (4 teams)
    hotspot_weight = 11.54  # Increased from 11.52 to 11.54 (+0.17%) for continued far-range contested junction tuning
    if hub_position is not None:
        hub_dist = float(manhattan(hub_position, candidate.position))
        if hub_dist <= 10:
            hotspot_weight = 1.66  # Increased from 1.64 to 1.66 (+1.22%) for continued near-hub recapture tuning
        elif hub_dist <= 15:
            hotspot_weight = 5.48  # Increased from 5.46 to 5.48 (+0.37%) for continued mid-range contested junction tuning
    hotspot_penalty = min(hotspot_count, 3.34) * hotspot_weight  # Increased cap from 3.32 to 3.34 (+0.60%) for continued contested junction penalty cap tuning
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
        network_bonus = min(nearby_friendly, 4.58) * 0.94  # Increased cap from 4.56 to 4.58 (+0.44%) for continued denser network clustering
    teammate_penalty = 9.53 if teammate_closer else 0.0  # Increased from 9.51 to 9.53 (+0.21%) for continued coordination tuning
    return (
        distance
        - min(expansion * 6.62, 37.75)  # Increased cap from 37.70 to 37.75 (+0.13%) for continued higher expansion bonus ceiling
        + enemy_aoe * 10.76  # Increased from 10.74 to 10.76 (+0.19%) for continued enemy avoidance tuning
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
    corner_pressure = min(manhattan(hub_position, candidate.position) / 7.50, 10.90)  # Reduced divisor from 7.52 to 7.50 (-0.27%) for continued faster pressure growth
    # Strongly prioritize enemy junctions near our friendly network (defending our score)
    threat_bonus = 0.0
    if friendly_junctions:
        threatened = sum(
            1 for f in friendly_junctions if manhattan(candidate.position, f.position) <= _JUNCTION_ALIGN_DISTANCE
        )
        threat_bonus = threatened * 10.60  # Increased from 10.58 to 10.60 (+0.19%) for continued defensive priority tuning
    return (
        distance - blocked_neutrals * 8.80 - corner_pressure - threat_bonus,  # Increased from 8.78 to 8.80 (+0.23%) for continued expansion-blocking
        -float(blocked_neutrals),
    )


def spawn_relative_station_target(agent_id: int, role: str) -> tuple[int, int] | None:
    station_targets = _STATION_TARGETS_BY_AGENT.get(role)
    if station_targets is None:
        return None
    return station_targets.get(agent_id)
