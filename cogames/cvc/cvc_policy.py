"""Coglet policy for cogames CvC — wraps the cogora policy.

Uses AlphaCyborgPolicy (semantic heuristic without LLM) as baseline.
AnthropicCyborgPolicy adds LLM-based runtime improvements on top.
"""
from __future__ import annotations

from cvc.policy.anthropic_pilot import AlphaCyborgPolicy, AnthropicCyborgPolicy


class CogletPolicy(AlphaCyborgPolicy):
    """cogames policy — semantic heuristic baseline (no LLM)."""
    short_names = ["coglet", "coglet-policy"]


class CogletLLMPolicy(AnthropicCyborgPolicy):
    """cogames policy — semantic baseline + LLM runtime improvements."""
    short_names = ["coglet-llm"]
