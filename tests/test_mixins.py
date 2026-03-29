"""Unit tests for all mixins: LifeLet, TickLet, ProgLet, GitLet, LogLet, MulLet, SuppressLet."""
from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from coglet import (
    Coglet, CogBase, CogletRuntime, Command,
    LifeLet, TickLet, ProgLet, Program, GitLet, LogLet, MulLet, SuppressLet,
    listen, enact, every,
)


# ======== LifeLet ========

class TrackingLifeLet(Coglet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.started = False
        self.stopped = False

    async def on_start(self) -> None:
        self.started = True

    async def on_stop(self) -> None:
        self.stopped = True


@pytest.mark.asyncio
async def test_lifelet_start_stop():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=TrackingLifeLet))
    cog: TrackingLifeLet = handle.coglet
    assert cog.started is True
    assert cog.stopped is False
    await rt.shutdown()
    assert cog.stopped is True


class FailingLifeLet(Coglet, LifeLet):
    async def on_start(self) -> None:
        raise ValueError("start failed")


@pytest.mark.asyncio
async def test_lifelet_start_failure_propagates():
    rt = CogletRuntime()
    with pytest.raises(ValueError, match="start failed"):
        await rt.spawn(CogBase(cls=FailingLifeLet))
    await rt.shutdown()


# ======== TickLet ========

class CounterTicker(Coglet, TickLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.time_count = 0
        self.tick_count_manual = 0

    @every(0.05, "s")
    async def fast_tick(self) -> None:
        self.time_count += 1

    @every(3, "ticks")
    async def manual_tick(self) -> None:
        self.tick_count_manual += 1


@pytest.mark.asyncio
async def test_ticklet_time_based():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=CounterTicker))
    cog: CounterTicker = handle.coglet
    await asyncio.sleep(0.15)
    assert cog.time_count >= 2
    await rt.shutdown()


@pytest.mark.asyncio
async def test_ticklet_manual():
    cog = CounterTicker()
    cog._tick_count = 0

    for _ in range(9):
        await cog.tick()

    assert cog.tick_count_manual == 3  # fires at tick 3, 6, 9


@pytest.mark.asyncio
async def test_ticklet_stop_cancels_tasks():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=CounterTicker))
    cog: CounterTicker = handle.coglet
    assert len(cog._tick_tasks) == 1  # only time-based
    await rt.shutdown()
    assert len(cog._tick_tasks) == 0


class SyncTicker(Coglet, TickLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.count = 0

    @every(2, "ticks")
    def sync_tick(self) -> None:
        self.count += 1


@pytest.mark.asyncio
async def test_ticklet_sync_handler():
    cog = SyncTicker()
    for _ in range(4):
        await cog.tick()
    assert cog.count == 2


class MinuteTicker(Coglet, TickLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.count = 0

    @every(1, "m")
    async def minute_tick(self) -> None:
        self.count += 1


def test_ticklet_minute_unit():
    """Minute tickers are registered."""
    assert len(MinuteTicker._every_handlers) == 1
    name, interval, unit = MinuteTicker._every_handlers[0]
    assert unit == "m"
    assert interval == 1


# ======== ProgLet ========

class PolicyProgLet(Coglet, ProgLet):
    pass


@pytest.mark.asyncio
async def test_proglet_register():
    cog = PolicyProgLet()
    assert cog.programs == {}

    def my_fn(x):
        return x * 2

    await cog._dispatch_enact(Command("register", {"double": Program(executor="code", fn=my_fn)}))
    assert "double" in cog.programs
    assert await cog.invoke("double", 5) == 10


@pytest.mark.asyncio
async def test_proglet_update():
    cog = PolicyProgLet()
    await cog._dispatch_enact(Command("register", {"f": Program(executor="code", fn=lambda x: x)}))
    await cog._dispatch_enact(Command("register", {"f": Program(executor="code", fn=lambda x: x + 1)}))
    assert await cog.invoke("f", 0) == 1


@pytest.mark.asyncio
async def test_proglet_multiple():
    cog = PolicyProgLet()
    await cog._dispatch_enact(Command("register", {
        "add": Program(executor="code", fn=lambda a: a[0] + a[1]),
        "mul": Program(executor="code", fn=lambda a: a[0] * a[1]),
    }))
    assert await cog.invoke("add", (2, 3)) == 5
    assert await cog.invoke("mul", (2, 3)) == 6


# ======== GitLet ========

class PolicyGitLet(Coglet, GitLet):
    pass


@pytest.mark.asyncio
async def test_gitlet_default_repo_path():
    cog = PolicyGitLet()
    assert cog.repo_path == os.getcwd()


@pytest.mark.asyncio
async def test_gitlet_custom_repo_path():
    cog = PolicyGitLet(repo_path="/tmp/test-repo")
    assert cog.repo_path == "/tmp/test-repo"


@pytest.mark.asyncio
async def test_gitlet_git_command():
    """_git runs git commands in repo_path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cog = PolicyGitLet(repo_path=tmpdir)
        # Init a repo
        proc = await asyncio.create_subprocess_exec(
            "git", "init", cwd=tmpdir,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        result = await cog._git("status")
        assert "On branch" in result or "No commits" in result


@pytest.mark.asyncio
async def test_gitlet_git_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        cog = PolicyGitLet(repo_path=tmpdir)
        # No git repo → git status fails
        with pytest.raises(RuntimeError, match="git .* failed"):
            await cog._git("log")


@pytest.mark.asyncio
async def test_gitlet_commit_enact():
    """GitLet has a 'commit' enact handler registered."""
    assert "commit" in PolicyGitLet._enact_handlers


# ======== LogLet ========

class LoggingCoglet(Coglet, LogLet):
    pass


@pytest.mark.asyncio
async def test_loglet_default_level():
    cog = LoggingCoglet()
    assert cog._log_level == "info"


@pytest.mark.asyncio
async def test_loglet_log_at_level():
    cog = LoggingCoglet()
    sub = cog._bus.subscribe("log")

    await cog.log("info", "test message")
    result = await asyncio.wait_for(sub.get(), timeout=1.0)
    assert result == {"level": "info", "data": "test message"}


@pytest.mark.asyncio
async def test_loglet_filters_below_level():
    cog = LoggingCoglet()
    sub = cog._bus.subscribe("log")

    await cog.log("debug", "should be filtered")

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(sub.get(), timeout=0.05)


@pytest.mark.asyncio
async def test_loglet_set_level():
    cog = LoggingCoglet()
    sub = cog._bus.subscribe("log")

    await cog._dispatch_enact(Command("log_level", "debug"))
    assert cog._log_level == "debug"

    await cog.log("debug", "now visible")
    result = await asyncio.wait_for(sub.get(), timeout=1.0)
    assert result["level"] == "debug"


@pytest.mark.asyncio
async def test_loglet_error_always_passes():
    cog = LoggingCoglet(log_level="error")
    sub = cog._bus.subscribe("log")

    await cog.log("warn", "filtered")
    await cog.log("error", "passes")

    result = await asyncio.wait_for(sub.get(), timeout=1.0)
    assert result["level"] == "error"


def test_loglet_level_values():
    cog = LoggingCoglet()
    assert cog._level_value("debug") == 0
    assert cog._level_value("info") == 1
    assert cog._level_value("warn") == 2
    assert cog._level_value("error") == 3
    assert cog._level_value("unknown") == 0


# ======== MulLet ========

class Worker(Coglet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.received: list[Any] = []

    @listen("task")
    async def on_task(self, data: Any) -> None:
        self.received.append(data)
        await self.transmit("result", f"done:{data}")

    @enact("cmd")
    async def on_cmd(self, data: Any) -> None:
        self.received.append(("cmd", data))


class Fleet(Coglet, MulLet):
    pass


class CustomFleet(Coglet, MulLet):
    """Custom map/reduce."""
    def map(self, event: Any) -> list[tuple[int, Any]]:
        # Only send to first child
        return [(0, event)]

    def reduce(self, results: list[Any]) -> Any:
        return ",".join(str(r) for r in results)


@pytest.mark.asyncio
async def test_mullet_create_mul():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Fleet))
    fleet: Fleet = handle.coglet

    await fleet.create_mul(3, CogBase(cls=Worker))
    assert len(fleet._mul_children) == 3

    await rt.shutdown()


@pytest.mark.asyncio
async def test_mullet_guide_mapped():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Fleet))
    fleet: Fleet = handle.coglet

    await fleet.create_mul(3, CogBase(cls=Worker))
    await fleet.guide_mapped(Command("cmd", "hello"))

    for child_handle in fleet._mul_children:
        child: Worker = child_handle.coglet
        assert ("cmd", "hello") in child.received

    await rt.shutdown()


@pytest.mark.asyncio
async def test_mullet_scatter_broadcast():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Fleet))
    fleet: Fleet = handle.coglet

    await fleet.create_mul(3, CogBase(cls=Worker))
    await fleet.scatter("task", "job1")

    for child_handle in fleet._mul_children:
        child: Worker = child_handle.coglet
        assert "job1" in child.received

    await rt.shutdown()


@pytest.mark.asyncio
async def test_mullet_gather():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Fleet))
    fleet: Fleet = handle.coglet

    await fleet.create_mul(2, CogBase(cls=Worker))

    # Pre-subscribe before scatter triggers transmit
    subs = []
    for child_handle in fleet._mul_children:
        subs.append(child_handle.coglet._bus.subscribe("result"))

    # Scatter triggers transmit("result", ...) in each worker
    await fleet.scatter("task", "x")

    results = []
    for sub in subs:
        results.append(await asyncio.wait_for(sub.get(), timeout=1.0))
    assert len(results) == 2
    assert all(r == "done:x" for r in results)

    await rt.shutdown()


@pytest.mark.asyncio
async def test_mullet_default_map_broadcast():
    fleet = Fleet()
    fleet._mul_children = [None, None, None]  # type: ignore
    mappings = fleet.map("event")
    assert mappings == [(0, "event"), (1, "event"), (2, "event")]


@pytest.mark.asyncio
async def test_mullet_default_reduce():
    fleet = Fleet()
    assert fleet.reduce([1, 2, 3]) == [1, 2, 3]


@pytest.mark.asyncio
async def test_mullet_custom_map():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=CustomFleet))
    fleet: CustomFleet = handle.coglet

    await fleet.create_mul(3, CogBase(cls=Worker))
    await fleet.scatter("task", "only-first")

    # Only first child should have received
    assert "only-first" in fleet._mul_children[0].coglet.received
    assert fleet._mul_children[1].coglet.received == []
    assert fleet._mul_children[2].coglet.received == []

    await rt.shutdown()


@pytest.mark.asyncio
async def test_mullet_custom_reduce():
    fleet = CustomFleet()
    result = fleet.reduce(["a", "b", "c"])
    assert result == "a,b,c"
