"""Tests for LLMExecutor — mock-based, no real API calls."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, AsyncMock

from coglet.llm_executor import LLMExecutor
from coglet.proglet import Program


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_text_response(text: str, stop_reason: str = "end_turn"):
    block = MagicMock()
    block.type = "text"
    block.text = text

    resp = MagicMock()
    resp.stop_reason = stop_reason
    resp.content = [block]
    return resp


def _make_tool_use_response(tool_id: str, name: str, input_data: dict):
    block = MagicMock()
    block.type = "tool_use"
    block.name = name
    block.input = input_data
    block.id = tool_id

    resp = MagicMock()
    resp.stop_reason = "tool_use"
    resp.content = [block]
    return resp


def _make_client(*responses):
    client = MagicMock()
    client.messages.create.side_effect = list(responses)
    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_llm_executor_simple():
    """Single-turn: sends context, gets text back, parser applied."""
    client = _make_client(_make_text_response("hello world"))
    executor = LLMExecutor(client)

    program = Program(
        executor="llm",
        system="You are helpful.",
        tools=[],
        config={"max_turns": 1},
        parser=lambda t: t.upper(),
    )

    result = await executor.run(program, "greet me", AsyncMock())
    assert result == "HELLO WORLD"
    client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_llm_executor_no_parser():
    """Without a parser, raw text is returned."""
    client = _make_client(_make_text_response("raw output"))
    executor = LLMExecutor(client)

    program = Program(
        executor="llm",
        system="sys",
        tools=[],
        config={"max_turns": 1},
        parser=None,
    )

    result = await executor.run(program, "ctx", AsyncMock())
    assert result == "raw output"


@pytest.mark.asyncio
async def test_llm_executor_callable_system():
    """System prompt built from context via callable."""
    client = _make_client(_make_text_response("ok"))
    executor = LLMExecutor(client)

    program = Program(
        executor="llm",
        system=lambda ctx: f"Context is {ctx}",
        tools=[],
        config={"max_turns": 1},
        parser=None,
    )

    await executor.run(program, "abc", AsyncMock())
    call_kwargs = client.messages.create.call_args[1]
    assert call_kwargs["system"] == "Context is abc"


@pytest.mark.asyncio
async def test_llm_executor_tool_use():
    """LLM calls a tool, executor invokes it, feeds result back, gets final text."""
    tool_resp = _make_tool_use_response("t1", "search", {"query": "hi"})
    final_resp = _make_text_response("done")
    client = _make_client(tool_resp, final_resp)

    invoke = AsyncMock(return_value="search result")
    executor = LLMExecutor(client)

    program = Program(
        executor="llm",
        system="sys",
        tools=["search"],
        config={"max_turns": 5},
        parser=None,
    )

    result = await executor.run(program, "find stuff", invoke)
    assert result == "done"
    invoke.assert_awaited_once_with("search", {"query": "hi"})
    assert client.messages.create.call_count == 2


@pytest.mark.asyncio
async def test_llm_executor_max_turns_exhausted():
    """Returns None when the tool loop never ends within max_turns."""
    tool_resp = _make_tool_use_response("t1", "loop", {})
    client = _make_client(tool_resp, tool_resp, tool_resp)

    executor = LLMExecutor(client)

    program = Program(
        executor="llm",
        system="sys",
        tools=["loop"],
        config={"max_turns": 3},
        parser=None,
    )

    result = await executor.run(program, "go", AsyncMock(return_value="ok"))
    assert result is None
    assert client.messages.create.call_count == 3
