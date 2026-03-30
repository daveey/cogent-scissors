"""Flat program table: all CvC programs in one dict, operating on GameState.

Every program is evolvable by PCO. Programs read from / write to GameState
(from cvc.game_state), not any engine instance. The ``all_programs()`` function
returns a dict[str, Program] with query, action, and decision programs.

``seed_programs()`` is kept as a backward-compat alias.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from coglet.proglet import Program
from mettagrid.simulator import Action

from cvc.agent import helpers as _h
from cvc.agent.helpers.types import KnownEntity

_ELEMENTS = ("carbon", "oxygen", "germanium", "silicon")

# Role allocation constants (simplified from PressureMixin)
_ALIGNER_PRIORITY = (4, 5, 6, 7, 3)
_SCRAMBLER_PRIORITY = (7, 6)

# ---------------------------------------------------------------------------
# Query programs — read from GameState
# ---------------------------------------------------------------------------


def _hp(gs: Any) -> int:
    return int(gs.mg_state.self_state.inventory.get("hp", 0))


def _step_num(gs: Any) -> int:
    return gs.step_index


def _position(gs: Any) -> tuple[int, int]:
    return _h.absolute_position(gs.mg_state)


def _inventory(gs: Any) -> dict:
    return dict(gs.mg_state.self_state.inventory)


def _resource_bias(gs: Any) -> str:
    return gs.resource_bias


def _team_resources(gs: Any) -> dict[str, int]:
    if gs.mg_state.team_summary is None:
        return {e: 0 for e in _ELEMENTS}
    return {
        e: int(gs.mg_state.team_summary.shared_inventory.get(e, 0))
        for e in _ELEMENTS
    }


def _resource_priority(gs: Any) -> list[str]:
    return _h.resource_priority(gs.mg_state, resource_bias=gs.resource_bias)


def _nearest_hub(gs: Any) -> KnownEntity | None:
    team = _h.team_id(gs.mg_state)
    hub = gs.world_model.nearest(
        position=_h.absolute_position(gs.mg_state),
        entity_type="hub",
        predicate=lambda e: e.team == team,
    )
    if hub is not None:
        return hub
    # Bootstrap fallback
    from mettagrid_sdk.games.cogsguard import COGSGUARD_BOOTSTRAP_HUB_OFFSETS
    offset = COGSGUARD_BOOTSTRAP_HUB_OFFSETS.get(gs.agent_id)
    if offset is None:
        return None
    return KnownEntity(
        entity_type="hub",
        global_x=offset[0],
        global_y=offset[1],
        labels=(),
        team=team,
        owner=team,
        last_seen_step=gs.step_index,
        attributes={},
    )


def _nearest_extractor(gs: Any, resource: str) -> KnownEntity | None:
    current_pos = _h.absolute_position(gs.mg_state)
    return gs.world_model.nearest(
        position=current_pos,
        entity_type=f"{resource}_extractor",
        predicate=lambda e: _h.is_usable_recent_extractor(
            e, step=gs.step_index
        ),
    )


def _known_junctions(gs: Any, predicate: Any = None) -> list[KnownEntity]:
    if predicate is None:
        predicate = lambda e: True  # noqa: E731
    return list(gs.world_model.entities(entity_type="junction", predicate=predicate))


def _safe_distance(gs: Any) -> int:
    hub = _nearest_hub(gs)
    if hub is None:
        return 0
    return _h.manhattan(_h.absolute_position(gs.mg_state), hub.position)


def _has_role_gear(gs: Any, role: str) -> bool:
    return _h.has_role_gear(gs.mg_state, role)


def _team_can_afford_gear(gs: Any, role: str) -> bool:
    return _h.team_can_afford_gear(gs.mg_state, role)


def _needs_emergency_mining(gs: Any) -> bool:
    return _h.needs_emergency_mining(gs.mg_state)


def _is_stalled(gs: Any) -> bool:
    return gs.stalled_steps >= 12


def _is_oscillating(gs: Any) -> bool:
    return gs.oscillation_steps >= 4


# ---------------------------------------------------------------------------
# Action programs — produce Action objects
# ---------------------------------------------------------------------------


def _action(gs: Any, name: str, vibe: str | None = None) -> Action:
    action_name = name if name in gs.action_names else gs.fallback
    vibe_name = vibe if vibe in gs.vibe_actions else None
    return Action(name=action_name, vibe=vibe_name)


def _move_to(gs: Any, target: tuple[int, int]) -> Action:
    current = _h.absolute_position(gs.mg_state)
    if current == target:
        return _action(gs, gs.fallback)
    blocked = gs.world_model.occupied_cells()
    blocked.update(set(gs.temp_blocks.keys()))
    next_cell = _h.greedy_step(current, target, blocked)
    if next_cell is None:
        return _action(gs, gs.fallback)
    direction = _h.direction_from_step(current, next_cell)
    return _action(gs, f"move_{direction}")


def _hold(gs: Any) -> Action:
    return _action(gs, gs.fallback)


def _explore(gs: Any, role: str = "miner") -> Action:
    current_pos = _h.absolute_position(gs.mg_state)
    hub = _nearest_hub(gs)
    center = (hub.global_x, hub.global_y) if hub is not None else current_pos
    offsets = _h.explore_offsets(role)
    offset_index = (gs.agent_id + gs.explore_index) % len(offsets)
    target = offsets[offset_index]
    absolute_target = (center[0] + target[0], center[1] + target[1])
    if _h.manhattan(current_pos, absolute_target) <= 2:
        gs.explore_index += 1
        offset_index = (gs.agent_id + gs.explore_index) % len(offsets)
        target = offsets[offset_index]
        absolute_target = (center[0] + target[0], center[1] + target[1])
    return _move_to(gs, absolute_target)


def _unstick(gs: Any, role: str = "miner") -> Action:
    current = _h.absolute_position(gs.mg_state)
    gs.explore_index += 1
    blocked = gs.world_model.occupied_cells()
    blocked.update(set(gs.temp_blocks.keys()))
    for direction in _h.unstick_directions(gs.agent_id, gs.step_index):
        dx, dy = _h._MOVE_DELTAS[direction]
        nxt = (current[0] + dx, current[1] + dy)
        if nxt in blocked:
            continue
        return _action(gs, f"move_{direction}")
    return _hold(gs)


# ---------------------------------------------------------------------------
# Decision programs — compose queries and actions
# ---------------------------------------------------------------------------


def _desired_role(gs: Any) -> str:
    step = gs.step_index
    if step < 300:
        aligner_budget = 2
        scrambler_budget = 0
    else:
        aligner_budget = 4
        scrambler_budget = 1
    scrambler_ids = set(_SCRAMBLER_PRIORITY[:scrambler_budget])
    aligner_ids: list[int] = []
    for aid in _ALIGNER_PRIORITY:
        if aid in scrambler_ids:
            continue
        if len(aligner_ids) == aligner_budget:
            break
        aligner_ids.append(aid)
    if gs.agent_id in scrambler_ids:
        return "scrambler"
    if gs.agent_id in aligner_ids:
        return "aligner"
    return "miner"


def _should_retreat(gs: Any) -> bool:
    hp = _hp(gs)
    role = gs.role
    threshold = _h.retreat_threshold(gs.mg_state, role)
    hub = _nearest_hub(gs)
    if hub is None:
        return hp <= threshold
    safe_steps = max(
        0,
        _h.manhattan(_h.absolute_position(gs.mg_state), hub.position)
        - _h._JUNCTION_AOE_RANGE,
    )
    margin = 15
    return hp <= safe_steps + margin


def _retreat(gs: Any) -> Action:
    hub = _nearest_hub(gs)
    if hub is not None:
        return _move_to(gs, hub.position)
    return _hold(gs)


def _mine(gs: Any) -> Action:
    priorities = _resource_priority(gs)
    current_pos = _h.absolute_position(gs.mg_state)
    for resource in priorities:
        extractor = _nearest_extractor(gs, resource)
        if extractor is not None:
            return _move_to(gs, extractor.position)
    return _explore(gs, role="miner")


def _align(gs: Any) -> Action:
    team = _h.team_id(gs.mg_state)
    neutrals = _known_junctions(
        gs,
        predicate=lambda e: e.owner in {None, "neutral"},
    )
    if neutrals:
        current_pos = _h.absolute_position(gs.mg_state)
        target = min(
            neutrals,
            key=lambda e: (_h.manhattan(current_pos, e.position), e.position),
        )
        return _move_to(gs, target.position)
    return _explore(gs, role="aligner")


def _scramble(gs: Any) -> Action:
    team = _h.team_id(gs.mg_state)
    enemies = _known_junctions(
        gs,
        predicate=lambda e: e.owner not in {None, "neutral", team},
    )
    if enemies:
        current_pos = _h.absolute_position(gs.mg_state)
        target = min(
            enemies,
            key=lambda e: (_h.manhattan(current_pos, e.position), e.position),
        )
        return _move_to(gs, target.position)
    return _explore(gs, role="scrambler")


def _step(gs: Any) -> Action:
    """Main dispatch — follows CvcEngine._choose_action priority chain."""
    hp = _hp(gs)
    step = _step_num(gs)
    hub = _nearest_hub(gs)
    safe_dist = 0 if hub is None else _h.manhattan(
        _h.absolute_position(gs.mg_state), hub.position
    )
    role = gs.role

    # 1. Heal at hub
    if hp < 100 and hp > 0 and hub is not None and safe_dist <= 3 and step <= 20:
        return _hold(gs)

    # 2. Early retreat
    if step < 150 and hub is not None and safe_dist > 8:
        if hp < 40 or (hp < 50 and safe_dist > 15):
            return _retreat(gs)

    # 3. Wipeout
    if hp == 0 and hub is not None:
        if safe_dist > 5:
            return _retreat(gs)
        return _mine(gs)

    # 4. Should retreat
    if _should_retreat(gs):
        if hub is not None and safe_dist > 2:
            return _retreat(gs)
        if _has_role_gear(gs, role):
            return _hold(gs)

    # 5. Oscillating or stalled
    if _is_oscillating(gs):
        return _unstick(gs, role)
    if _is_stalled(gs):
        return _unstick(gs, role)

    # 6. Emergency mining
    if role != "miner" and _needs_emergency_mining(gs):
        return _mine(gs)

    # 7. No gear
    if not _has_role_gear(gs, role):
        if not _team_can_afford_gear(gs, role):
            return _mine(gs)
        # Move to hub to get gear
        if hub is not None:
            return _move_to(gs, hub.position)

    # 8. Role action
    if role == "miner":
        return _mine(gs)
    if role == "aligner":
        return _align(gs)
    if role == "scrambler":
        return _scramble(gs)
    return _explore(gs, role=role)


def _summarize(gs: Any) -> dict:
    """Experience snapshot for PCO learner."""
    hp = _hp(gs)
    pos = _position(gs)
    hub = _nearest_hub(gs)
    return {
        "step": _step_num(gs),
        "agent_id": gs.agent_id,
        "hp": hp,
        "position": pos,
        "role": gs.role,
        "resource_bias": gs.resource_bias,
        "team_resources": _team_resources(gs),
        "inventory": _inventory(gs),
        "safe_distance": _safe_distance(gs),
        "stalled": _is_stalled(gs),
        "oscillating": _is_oscillating(gs),
        "has_gear": _has_role_gear(gs, gs.role),
        "emergency_mining": _needs_emergency_mining(gs),
    }


# ---------------------------------------------------------------------------
# LLM program: analyze
# ---------------------------------------------------------------------------


def _build_analysis_prompt(context: dict) -> str:
    """Build the LLM analysis prompt from extracted game context."""
    lines = [
        f"CvC game step {context['step']}/10000. 88x88 map, 8 agents per team.",
        f"Agent {context['agent_id']}: HP={context['hp']}, Hearts={context['hearts']}",
        f"Gear: aligner={context['aligner']} scrambler={context['scrambler']} miner={context['miner']}",
        f"Hub resources: {context['resources']}",
    ]
    if context["roles"]:
        lines.append(f"Team roles: {context['roles']}")

    j = context["junctions"]
    lines.append(
        f"Visible junctions: friendly={j['friendly']} enemy={j['enemy']} neutral={j['neutral']}"
    )

    lines.append(
        "\nRespond with ONLY a JSON object (no other text):"
        '\n{"resource_bias": "carbon"|"oxygen"|"germanium"|"silicon",'
        ' "analysis": "1-2 sentence analysis"}'
        "\nChoose resource_bias = the element with lowest supply."
    )
    return "\n".join(lines)


def _parse_analysis(text: str) -> dict:
    """Parse the LLM response text into a directive dict."""
    result: dict[str, Any] = {"analysis": text[:100]}
    try:
        directive = json.loads(text)
        if isinstance(directive, dict):
            if directive.get("resource_bias") in _ELEMENTS:
                result["resource_bias"] = directive["resource_bias"]
            result["analysis"] = directive.get("analysis", text[:100])
    except (json.JSONDecodeError, ValueError):
        pass
    return result


# ---------------------------------------------------------------------------
# Backward-compat: StepContext (used by table_policy.py, will be removed)
# ---------------------------------------------------------------------------


@dataclass
class StepContext:
    """Legacy context object — kept for backward compatibility."""
    engine: Any
    state: Any
    role: str
    invoke: Callable[[str, "StepContext"], Any]


# ---------------------------------------------------------------------------
# all_programs / seed_programs
# ---------------------------------------------------------------------------


def all_programs() -> dict[str, Program]:
    """Return the flat program table — all programs evolvable by PCO."""
    return {
        # Query programs
        "hp": Program(executor="code", fn=_hp),
        "step_num": Program(executor="code", fn=_step_num),
        "position": Program(executor="code", fn=_position),
        "inventory": Program(executor="code", fn=_inventory),
        "resource_bias": Program(executor="code", fn=_resource_bias),
        "team_resources": Program(executor="code", fn=_team_resources),
        "resource_priority": Program(executor="code", fn=_resource_priority),
        "nearest_hub": Program(executor="code", fn=_nearest_hub),
        "nearest_extractor": Program(executor="code", fn=_nearest_extractor),
        "known_junctions": Program(executor="code", fn=_known_junctions),
        "safe_distance": Program(executor="code", fn=_safe_distance),
        "has_role_gear": Program(executor="code", fn=_has_role_gear),
        "team_can_afford_gear": Program(executor="code", fn=_team_can_afford_gear),
        "needs_emergency_mining": Program(executor="code", fn=_needs_emergency_mining),
        "is_stalled": Program(executor="code", fn=_is_stalled),
        "is_oscillating": Program(executor="code", fn=_is_oscillating),
        # Action programs
        "action": Program(executor="code", fn=_action),
        "move_to": Program(executor="code", fn=_move_to),
        "hold": Program(executor="code", fn=_hold),
        "explore": Program(executor="code", fn=_explore),
        "unstick": Program(executor="code", fn=_unstick),
        # Decision programs
        "desired_role": Program(executor="code", fn=_desired_role),
        "should_retreat": Program(executor="code", fn=_should_retreat),
        "retreat": Program(executor="code", fn=_retreat),
        "mine": Program(executor="code", fn=_mine),
        "align": Program(executor="code", fn=_align),
        "scramble": Program(executor="code", fn=_scramble),
        "step": Program(executor="code", fn=_step),
        "summarize": Program(executor="code", fn=_summarize),
        # LLM program
        "analyze": Program(
            executor="llm",
            system=_build_analysis_prompt,
            parser=_parse_analysis,
            config={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 150,
                "temperature": 0.2,
                "max_turns": 1,
            },
        ),
    }


# Backward compatibility alias
seed_programs = all_programs
