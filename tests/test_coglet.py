"""Unit tests for coglet.coglet: Coglet base class, listen/enact decorators, dispatch."""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from coglet import Coglet, CogBase, CogletRuntime, Command, listen, enact


# ---- Decorator tests ----

class SimpleLET(Coglet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.heard: list[Any] = []
        self.enacted: list[Any] = []

    @listen("input")
    async def on_input(self, data: Any) -> None:
        self.heard.append(data)

    @enact("do")
    async def on_do(self, data: Any) -> None:
        self.enacted.append(data)


class SyncHandlers(Coglet):
    """Test sync (non-async) handlers work."""
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.heard: list[Any] = []

    @listen("sync_ch")
    def on_sync(self, data: Any) -> None:
        self.heard.append(data)

    @enact("sync_cmd")
    def on_sync_cmd(self, data: Any) -> None:
        self.heard.append(("cmd", data))


class ChildLET(SimpleLET):
    """Inherits parent handlers and adds new ones."""
    @listen("extra")
    async def on_extra(self, data: Any) -> None:
        self.heard.append(("extra", data))


class OverrideLET(SimpleLET):
    """Overrides parent handler for same channel."""
    @listen("input")
    async def on_input(self, data: Any) -> None:
        self.heard.append(("override", data))


# ---- Tests ----

def test_listen_decorator_sets_attribute():
    @listen("test")
    async def handler(self, data): pass
    assert handler._listen_channel == "test"


def test_enact_decorator_sets_attribute():
    @enact("cmd")
    async def handler(self, data): pass
    assert handler._enact_command == "cmd"


def test_handler_discovery():
    assert "input" in SimpleLET._listen_handlers
    assert SimpleLET._listen_handlers["input"] == "on_input"
    assert "do" in SimpleLET._enact_handlers
    assert SimpleLET._enact_handlers["do"] == "on_do"


def test_inherited_handlers():
    assert "input" in ChildLET._listen_handlers
    assert "extra" in ChildLET._listen_handlers


def test_overridden_handlers():
    assert OverrideLET._listen_handlers["input"] == "on_input"


@pytest.mark.asyncio
async def test_dispatch_listen():
    cog = SimpleLET()
    await cog._dispatch_listen("input", "hello")
    assert cog.heard == ["hello"]


@pytest.mark.asyncio
async def test_dispatch_listen_unknown_channel():
    """Unknown channel is silently ignored."""
    cog = SimpleLET()
    await cog._dispatch_listen("unknown", "data")
    assert cog.heard == []


@pytest.mark.asyncio
async def test_dispatch_enact():
    cog = SimpleLET()
    await cog._dispatch_enact(Command("do", "task"))
    assert cog.enacted == ["task"]


@pytest.mark.asyncio
async def test_dispatch_enact_unknown():
    cog = SimpleLET()
    await cog._dispatch_enact(Command("nope", None))
    assert cog.enacted == []


@pytest.mark.asyncio
async def test_dispatch_sync_handlers():
    cog = SyncHandlers()
    await cog._dispatch_listen("sync_ch", "data")
    await cog._dispatch_enact(Command("sync_cmd", "cmd_data"))
    assert cog.heard == ["data", ("cmd", "cmd_data")]


@pytest.mark.asyncio
async def test_dispatch_override():
    cog = OverrideLET()
    await cog._dispatch_listen("input", "test")
    assert cog.heard == [("override", "test")]


@pytest.mark.asyncio
async def test_dispatch_inherited():
    cog = ChildLET()
    await cog._dispatch_listen("input", "base")
    await cog._dispatch_listen("extra", "ext")
    assert cog.heard == ["base", ("extra", "ext")]


# ---- Transmit ----

@pytest.mark.asyncio
async def test_transmit():
    cog = SimpleLET()
    sub = cog._bus.subscribe("out")
    await cog.transmit("out", "hello")
    result = await sub.get()
    assert result == "hello"


@pytest.mark.asyncio
async def test_transmit_sync():
    cog = SimpleLET()
    sub = cog._bus.subscribe("out")
    cog.transmit_sync("out", "fast")
    result = await sub.get()
    assert result == "fast"


# ---- COG interface ----

@pytest.mark.asyncio
async def test_create_requires_runtime():
    cog = SimpleLET()
    with pytest.raises(RuntimeError, match="not attached to a runtime"):
        await cog.create(CogBase(cls=SimpleLET))


@pytest.mark.asyncio
async def test_create_and_guide():
    rt = CogletRuntime()
    parent_handle = await rt.spawn(CogBase(cls=SimpleLET))
    parent = parent_handle.coglet

    child_handle = await parent.create(CogBase(cls=SimpleLET))
    assert child_handle in parent._children

    await parent.guide(child_handle, Command("do", "task"))
    assert child_handle.coglet.enacted == ["task"]

    await rt.shutdown()


@pytest.mark.asyncio
async def test_observe():
    rt = CogletRuntime()
    parent_handle = await rt.spawn(CogBase(cls=SimpleLET))
    parent = parent_handle.coglet

    child_handle = await parent.create(CogBase(cls=SimpleLET))
    child = child_handle.coglet

    # Start observing in background
    observed = []

    async def observer():
        async for data in parent.observe(child_handle, "out"):
            observed.append(data)
            if len(observed) == 2:
                break

    task = asyncio.create_task(observer())
    await asyncio.sleep(0.01)  # let observer subscribe
    await child.transmit("out", "a")
    await child.transmit("out", "b")
    await asyncio.wait_for(task, timeout=1.0)

    assert observed == ["a", "b"]
    await rt.shutdown()


# ---- on_child_error default ----

@pytest.mark.asyncio
async def test_on_child_error_default():
    cog = SimpleLET()
    result = await cog.on_child_error(None, RuntimeError("test"))
    assert result == "stop"


# ---- Multiple mixins don't interfere ----

class MultiMixin(Coglet):
    @listen("a")
    async def on_a(self, data): pass

    @listen("b")
    async def on_b(self, data): pass

    @enact("x")
    async def on_x(self, data): pass

    @enact("y")
    async def on_y(self, data): pass


def test_multiple_handlers_same_class():
    assert set(MultiMixin._listen_handlers.keys()) == {"a", "b"}
    assert set(MultiMixin._enact_handlers.keys()) == {"x", "y"}
