"""Unit tests for coglet.runtime: CogletRuntime spawn, shutdown, tree, tracing, restart."""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

import pytest

from coglet import (
    Coglet, CogBase, CogletHandle, CogletRuntime, CogletTrace,
    Command, LifeLet, TickLet, listen, enact,
)


# ---- Helpers ----

class Node(Coglet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.started = False
        self.stopped = False

    async def on_start(self) -> None:
        self.started = True

    async def on_stop(self) -> None:
        self.stopped = True


class TickNode(Coglet, TickLet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.started = False
        self.stopped = False
        self.ticks = 0

    async def on_start(self) -> None:
        self.started = True

    async def on_stop(self) -> None:
        self.stopped = True

    @staticmethod
    def _every_placeholder():
        pass  # TickLet needs at least one handler from subclass or base


class Plain(Coglet):
    pass


# ---- spawn / shutdown ----

@pytest.mark.asyncio
async def test_spawn_basic():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Plain))
    assert handle.coglet in rt._coglets
    assert handle in rt._handles
    await rt.shutdown()


@pytest.mark.asyncio
async def test_spawn_calls_on_start():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Node))
    assert handle.coglet.started is True
    await rt.shutdown()


@pytest.mark.asyncio
async def test_shutdown_reverse_order():
    rt = CogletRuntime()
    h1 = await rt.spawn(CogBase(cls=Node))
    h2 = await rt.spawn(CogBase(cls=Node))
    h3 = await rt.spawn(CogBase(cls=Node))

    stop_order = []
    original_stop1 = h1.coglet.on_stop

    async def track1():
        stop_order.append(1)
        await original_stop1()

    original_stop2 = h2.coglet.on_stop

    async def track2():
        stop_order.append(2)
        await original_stop2()

    original_stop3 = h3.coglet.on_stop

    async def track3():
        stop_order.append(3)
        await original_stop3()

    h1.coglet.on_stop = track1
    h2.coglet.on_stop = track2
    h3.coglet.on_stop = track3

    await rt.shutdown()
    assert stop_order == [3, 2, 1]


@pytest.mark.asyncio
async def test_shutdown_clears_state():
    rt = CogletRuntime()
    await rt.spawn(CogBase(cls=Plain))
    await rt.spawn(CogBase(cls=Plain))
    await rt.shutdown()
    assert rt._coglets == []
    assert rt._handles == []
    assert rt._configs == {}
    assert rt._parents == {}


@pytest.mark.asyncio
async def test_run_is_spawn():
    rt = CogletRuntime()
    handle = await rt.run(CogBase(cls=Node))
    assert handle.coglet.started is True
    await rt.shutdown()


# ---- Parent tracking ----

@pytest.mark.asyncio
async def test_parent_tracking():
    rt = CogletRuntime()
    parent_handle = await rt.spawn(CogBase(cls=Plain))
    parent = parent_handle.coglet

    child_handle = await parent.create(CogBase(cls=Plain))
    child = child_handle.coglet

    assert rt._parents[id(child)] is parent
    assert id(parent) not in rt._parents  # root has no parent

    await rt.shutdown()


# ---- Tree visualization ----

@pytest.mark.asyncio
async def test_tree_single_node():
    rt = CogletRuntime()
    await rt.spawn(CogBase(cls=Plain))
    tree = rt.tree()
    assert "CogletRuntime" in tree
    assert "Plain" in tree
    await rt.shutdown()


@pytest.mark.asyncio
async def test_tree_hierarchy():
    rt = CogletRuntime()
    root_handle = await rt.spawn(CogBase(cls=Node))
    root = root_handle.coglet

    await root.create(CogBase(cls=Plain))
    await root.create(CogBase(cls=Plain))

    tree = rt.tree()
    assert "Node" in tree
    assert tree.count("Plain") == 2
    # Should have tree connectors
    assert "├" in tree or "└" in tree
    await rt.shutdown()


@pytest.mark.asyncio
async def test_tree_shows_mixins():
    rt = CogletRuntime()
    await rt.spawn(CogBase(cls=Node))
    tree = rt.tree()
    assert "LifeLet" in tree
    await rt.shutdown()


@pytest.mark.asyncio
async def test_tree_shows_channels():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Plain))
    cog = handle.coglet
    cog._bus.subscribe("events")
    tree = rt.tree()
    assert "events" in tree
    await rt.shutdown()


@pytest.mark.asyncio
async def test_tree_empty():
    rt = CogletRuntime()
    assert "empty" in rt.tree()


# ---- Trace ----

@pytest.mark.asyncio
async def test_trace_records_transmit():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        trace = CogletTrace(path)
        rt = CogletRuntime(trace=trace)
        handle = await rt.spawn(CogBase(cls=Plain))
        cog = handle.coglet

        await cog.transmit("ch", "data1")
        await cog.transmit("ch", "data2")

        await rt.shutdown()
        entries = CogletTrace.load(path)
        transmits = [e for e in entries if e["op"] == "transmit"]
        assert len(transmits) == 2
        assert transmits[0]["target"] == "ch"
        assert transmits[1]["data"] == "data2"
    finally:
        Path(path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_trace_records_enact():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        trace = CogletTrace(path)
        rt = CogletRuntime(trace=trace)

        class Enactable(Coglet):
            @enact("ping")
            async def on_ping(self, data): pass

        handle = await rt.spawn(CogBase(cls=Enactable))
        await handle.guide(Command("ping", "pong"))

        await rt.shutdown()
        entries = CogletTrace.load(path)
        enacts = [e for e in entries if e["op"] == "enact"]
        assert len(enacts) >= 1
        assert enacts[0]["target"] == "ping"
    finally:
        Path(path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_trace_timestamps_increase():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        trace = CogletTrace(path)
        rt = CogletRuntime(trace=trace)
        handle = await rt.spawn(CogBase(cls=Plain))

        await handle.coglet.transmit("a", 1)
        await asyncio.sleep(0.01)
        await handle.coglet.transmit("a", 2)

        await rt.shutdown()
        entries = CogletTrace.load(path)
        assert len(entries) >= 2
        assert entries[-1]["t"] >= entries[0]["t"]
    finally:
        Path(path).unlink(missing_ok=True)


# ---- Restart / supervision ----

class RestartParent(Coglet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.errors: list[Exception] = []

    async def on_child_error(self, handle: CogletHandle, error: Exception) -> str:
        self.errors.append(error)
        return "restart"


@pytest.mark.asyncio
async def test_restart_replaces_coglet():
    rt = CogletRuntime()
    parent_handle = await rt.spawn(CogBase(cls=RestartParent))
    parent = parent_handle.coglet

    config = CogBase(cls=Node, restart="on_error", max_restarts=3, backoff_s=0.01)
    child_handle = await rt.spawn(config, parent=parent)
    old = child_handle.coglet

    await rt.handle_child_error(child_handle, RuntimeError("fail"))

    assert child_handle.coglet is not old
    assert child_handle.coglet.started is True
    assert old.stopped is True

    await rt.shutdown()


@pytest.mark.asyncio
async def test_restart_respects_max():
    rt = CogletRuntime()
    parent_handle = await rt.spawn(CogBase(cls=RestartParent))
    parent = parent_handle.coglet

    config = CogBase(cls=Node, restart="on_error", max_restarts=2, backoff_s=0.01)
    child_handle = await rt.spawn(config, parent=parent)

    # First restart
    await rt.handle_child_error(child_handle, RuntimeError("1"))
    second_coglet = child_handle.coglet

    # Second restart
    await rt.handle_child_error(child_handle, RuntimeError("2"))
    third_coglet = child_handle.coglet

    # Third error: max_restarts=2, so this should stop instead
    await rt.handle_child_error(child_handle, RuntimeError("3"))

    # Should have stopped (removed from coglets)
    assert third_coglet not in rt._coglets

    await rt.shutdown()


@pytest.mark.asyncio
async def test_stop_child_removes_from_runtime():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Node))
    cog = handle.coglet
    assert cog in rt._coglets

    await rt._stop_coglet(cog)
    assert cog not in rt._coglets
    assert cog.stopped is True


@pytest.mark.asyncio
async def test_handle_child_error_no_parent():
    """Child with no parent just gets stopped."""
    rt = CogletRuntime()
    config = CogBase(cls=Node)
    handle = await rt.spawn(config)
    cog = handle.coglet

    await rt.handle_child_error(handle, RuntimeError("orphan"))
    assert cog not in rt._coglets

    await rt.shutdown()
