"""Tests for GameState engine-wrapping adapter."""

from __future__ import annotations


def test_import():
    """GameState can be imported."""
    from cvc.game_state import GameState  # noqa: F401


def test_elements_round_robin():
    """Resource bias follows ELEMENTS[agent_id % 4]."""
    from cvc.game_state import _ELEMENTS, GameState
    from unittest.mock import MagicMock

    for agent_id in range(8):
        pei = MagicMock()
        pei.action_names = ["noop", "move_up"]
        pei.vibe_action_names = ["vibe_up"]
        gs = GameState(pei, agent_id=agent_id)
        assert gs.resource_bias == _ELEMENTS[agent_id % len(_ELEMENTS)], (
            f"agent_id={agent_id}: expected {_ELEMENTS[agent_id % len(_ELEMENTS)]}, "
            f"got {gs.resource_bias}"
        )


def test_reset_clears_state():
    """reset() zeroes all mutable state fields."""
    from unittest.mock import MagicMock

    from cvc.game_state import GameState

    pei = MagicMock()
    pei.action_names = ["noop", "move_up"]
    pei.vibe_action_names = ["vibe_up"]
    gs = GameState(pei, agent_id=2)

    # Mutate engine state to non-default values
    gs.step_index = 42
    gs.stalled_steps = 5
    gs.oscillation_steps = 3
    gs.explore_index = 7
    gs.role = "aligner"
    gs.resource_bias = "oxygen"

    gs.reset()

    assert gs.step_index == 0
    assert gs.stalled_steps == 0
    assert gs.oscillation_steps == 0
    assert gs.explore_index == 0
    assert gs.mg_state is None
    assert gs.role == "miner"
    # Resource bias should be reset to default for agent_id=2
    assert gs.resource_bias == "germanium"


def test_fallback_action_noop():
    """Fallback is 'noop' when available."""
    from unittest.mock import MagicMock

    from cvc.game_state import GameState

    pei = MagicMock()
    pei.action_names = ["move_up", "noop"]
    pei.vibe_action_names = []
    gs = GameState(pei, agent_id=0)
    assert gs.fallback == "noop"


def test_fallback_action_first():
    """Fallback is first action when 'noop' not available."""
    from unittest.mock import MagicMock

    from cvc.game_state import GameState

    pei = MagicMock()
    pei.action_names = ["move_up", "move_down"]
    pei.vibe_action_names = []
    gs = GameState(pei, agent_id=0)
    assert gs.fallback == "move_up"


def test_engine_created():
    """GameState creates a CogletAgentPolicy engine internally."""
    from unittest.mock import MagicMock

    from cvc.game_state import GameState
    from cvc.agent.coglet_policy import CogletAgentPolicy

    pei = MagicMock()
    pei.action_names = ["noop", "move_up"]
    pei.vibe_action_names = ["vibe_up"]
    gs = GameState(pei, agent_id=3)
    assert isinstance(gs.engine, CogletAgentPolicy)
    assert gs.agent_id == 3
