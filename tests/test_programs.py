"""Tests for cogames/cvc/programs.py — flat program table."""

from __future__ import annotations

from cvc.programs import all_programs, seed_programs, _parse_analysis
from coglet.proglet import Program


# Expected program names — all ~30 in one flat dict
_EXPECTED_NAMES = {
    # Query
    "hp", "step_num", "position", "inventory", "resource_bias",
    "team_resources", "resource_priority", "nearest_hub",
    "nearest_extractor", "known_junctions", "safe_distance",
    "has_role_gear", "team_can_afford_gear", "needs_emergency_mining",
    "is_stalled", "is_oscillating",
    # Action
    "action", "move_to", "hold", "explore", "unstick",
    # Decision
    "desired_role", "should_retreat", "retreat", "mine", "align",
    "scramble", "step", "summarize",
    # LLM
    "analyze",
}


def test_all_programs_expected_names():
    programs = all_programs()
    assert set(programs.keys()) == _EXPECTED_NAMES


def test_seed_programs_is_alias():
    """seed_programs() returns same result as all_programs() for backward compat."""
    assert seed_programs is all_programs
    assert set(seed_programs().keys()) == _EXPECTED_NAMES


def test_code_programs_callable():
    """All code programs have a callable fn."""
    programs = all_programs()
    for name, prog in programs.items():
        assert isinstance(prog, Program), f"{name} is not a Program"
        if prog.executor == "code":
            assert callable(prog.fn), f"{name}.fn should be callable"


def test_analyze_is_llm():
    """analyze is LLM with parser."""
    programs = all_programs()
    analyze = programs["analyze"]
    assert analyze.executor == "llm"
    assert analyze.parser is not None
    assert callable(analyze.parser)
    assert analyze.fn is None
    assert analyze.system is not None
    assert callable(analyze.system)
    assert "model" in analyze.config
    assert "max_tokens" in analyze.config


def test_parse_analysis_valid():
    result = _parse_analysis('{"resource_bias": "carbon", "analysis": "Low carbon supply"}')
    assert result["resource_bias"] == "carbon"
    assert "Low carbon" in result["analysis"]


def test_parse_analysis_invalid():
    result = _parse_analysis("not json at all")
    assert "analysis" in result
    assert "resource_bias" not in result


def test_parse_analysis_bad_resource():
    result = _parse_analysis('{"resource_bias": "unobtanium", "analysis": "test"}')
    assert "resource_bias" not in result
    assert result["analysis"] == "test"
