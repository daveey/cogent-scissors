"""Unit tests for coglet.handle: Command, CogBase, CogletHandle."""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from coglet import Coglet, CogBase, CogletHandle, Command, listen, enact


class Worker(Coglet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.commands: list[Any] = []

    @enact("work")
    async def on_work(self, data: Any) -> None:
        self.commands.append(data)
        await self.transmit("result", f"done:{data}")


# ---- Command ----

def test_command_defaults():
    cmd = Command(type="test")
    assert cmd.type == "test"
    assert cmd.data is None


def test_command_with_data():
    cmd = Command(type="go", data={"x": 1})
    assert cmd.data == {"x": 1}


# ---- CogBase ----

def test_config_defaults():
    cfg = CogBase(cls=Worker)
    assert cfg.cls is Worker
    assert cfg.kwargs == {}
    assert cfg.restart == "never"
    assert cfg.max_restarts == 3
    assert cfg.backoff_s == 1.0


def test_config_custom():
    cfg = CogBase(
        cls=Worker,
        kwargs={"name": "w1"},
        restart="on_error",
        max_restarts=5,
        backoff_s=0.5,
    )
    assert cfg.kwargs == {"name": "w1"}
    assert cfg.restart == "on_error"


# ---- CogletHandle ----

@pytest.mark.asyncio
async def test_handle_guide():
    worker = Worker()
    handle = CogletHandle(worker)
    await handle.guide(Command("work", "task1"))
    assert worker.commands == ["task1"]


@pytest.mark.asyncio
async def test_handle_observe():
    worker = Worker()
    handle = CogletHandle(worker)

    collected = []

    async def observer():
        async for data in handle.observe("result"):
            collected.append(data)
            if len(collected) == 1:
                break

    task = asyncio.create_task(observer())
    await asyncio.sleep(0.01)  # let observer subscribe
    await worker.transmit("result", "done:x")
    await asyncio.wait_for(task, timeout=1.0)
    assert collected == ["done:x"]


@pytest.mark.asyncio
async def test_handle_coglet_property():
    worker = Worker()
    handle = CogletHandle(worker)
    assert handle.coglet is worker


@pytest.mark.asyncio
async def test_handle_guide_then_observe():
    """Guide triggers enact which transmits, observe picks it up."""
    worker = Worker()
    handle = CogletHandle(worker)

    collected = []

    async def observer():
        async for data in handle.observe("result"):
            collected.append(data)
            if len(collected) == 1:
                break

    task = asyncio.create_task(observer())
    await asyncio.sleep(0.01)  # let observer subscribe
    await handle.guide(Command("work", "job"))
    await asyncio.wait_for(task, timeout=1.0)

    assert worker.commands == ["job"]
    assert collected == ["done:job"]
