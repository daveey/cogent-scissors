"""Integration tests: multi-layer coglet trees with mixins working together."""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

import pytest

from coglet import (
    Coglet, CogBase, CogletHandle, CogletRuntime, CogletTrace,
    Command, LifeLet, TickLet, ProgLet, Program, LogLet, MulLet, SuppressLet,
    listen, enact, every,
)


# ---- Integration: COG/LET hierarchy with observe/guide ----

class Supervisor(Coglet, LifeLet, LogLet):
    """COG that creates workers, observes results, guides them."""
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.observations: list[Any] = []
        self.worker_handle: CogletHandle | None = None

    async def on_start(self) -> None:
        self.worker_handle = await self.create(CogBase(cls=ReactiveWorker))

    async def run_task(self, task_data: Any) -> Any:
        """Subscribe first, then guide worker, observe result."""
        # Subscribe before guiding so we don't miss the transmit
        sub = self.worker_handle.coglet._bus.subscribe("result")
        await self.guide(self.worker_handle, Command("work", task_data))
        result = await sub.get()
        self.observations.append(result)
        return result


class ReactiveWorker(Coglet, LifeLet):
    """LET that processes commands and transmits results."""
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.started = False

    async def on_start(self) -> None:
        self.started = True

    @enact("work")
    async def on_work(self, data: Any) -> None:
        result = f"processed:{data}"
        await self.transmit("result", result)


@pytest.mark.asyncio
async def test_supervisor_worker_cycle():
    rt = CogletRuntime()
    sup_handle = await rt.spawn(CogBase(cls=Supervisor))
    sup: Supervisor = sup_handle.coglet

    assert sup.worker_handle is not None
    assert sup.worker_handle.coglet.started is True

    result = await asyncio.wait_for(sup.run_task("hello"), timeout=1.0)
    assert result == "processed:hello"
    assert sup.observations == ["processed:hello"]

    await rt.shutdown()


# ---- Integration: MulLet fan-out with observation ----

class FleetSupervisor(Coglet, MulLet, LifeLet):
    def __init__(self, n_workers: int = 3, **kwargs: Any):
        super().__init__(**kwargs)
        self.n_workers = n_workers

    async def on_start(self) -> None:
        await self.create_mul(self.n_workers, CogBase(cls=ReactiveWorker))


@pytest.mark.asyncio
async def test_fleet_scatter_gather():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=FleetSupervisor, kwargs={"n_workers": 4}))
    fleet: FleetSupervisor = handle.coglet

    assert len(fleet._mul_children) == 4

    # Pre-subscribe on each child's "result" channel so gather() picks them up
    for child_handle in fleet._mul_children:
        child_handle.coglet._bus.subscribe("result")

    # Guide all workers — triggers transmit("result", ...)
    await fleet.guide_mapped(Command("work", "batch-job"))

    # Gather results (gather creates its own subscriptions, but the data is
    # already queued since we triggered transmit above — we need to subscribe
    # before transmit). Let's fix by subscribing via gather first.
    # Actually gather() calls subscribe() then get() — but the transmit already
    # happened. We need to reverse the order: subscribe first.

    # Reset: use a fresh approach — subscribe, then guide, then collect
    await rt.shutdown()

    # Redo properly
    rt2 = CogletRuntime()
    handle2 = await rt2.spawn(CogBase(cls=FleetSupervisor, kwargs={"n_workers": 4}))
    fleet2: FleetSupervisor = handle2.coglet

    # Pre-subscribe on each child before guide
    subs = []
    for ch in fleet2._mul_children:
        subs.append(ch.coglet._bus.subscribe("result"))

    await fleet2.guide_mapped(Command("work", "batch-job"))

    results = []
    for sub in subs:
        results.append(await asyncio.wait_for(sub.get(), timeout=1.0))

    assert len(results) == 4
    assert all(r == "processed:batch-job" for r in results)

    await rt2.shutdown()


# ---- Integration: SuppressLet + LogLet ----

class SuppressedLogger(SuppressLet, Coglet, LogLet):
    @listen("data")
    async def on_data(self, data: Any) -> None:
        await self.log("info", f"received:{data}")
        await self.transmit("out", data)


@pytest.mark.asyncio
async def test_suppress_channels_while_logging():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=SuppressedLogger))
    cog: SuppressedLogger = handle.coglet

    log_sub = cog._bus.subscribe("log")
    out_sub = cog._bus.subscribe("out")

    # Normal: both log and out work
    await cog._dispatch_listen("data", "test1")
    log_msg = await asyncio.wait_for(log_sub.get(), timeout=1.0)
    out_msg = await asyncio.wait_for(out_sub.get(), timeout=1.0)
    assert log_msg["data"] == "received:test1"
    assert out_msg == "test1"

    # Suppress "out" but not "log"
    await cog._dispatch_enact(Command("suppress", {"channels": ["out"]}))

    await cog._dispatch_listen("data", "test2")
    log_msg = await asyncio.wait_for(log_sub.get(), timeout=1.0)
    assert log_msg["data"] == "received:test2"

    # "out" should be suppressed
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(out_sub.get(), timeout=0.05)

    await rt.shutdown()


# ---- Integration: ProgLet hot-swap ----

class HotSwapPolicy(Coglet, ProgLet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.results: list[Any] = []

    async def on_start(self) -> None:
        self.programs["process"] = Program(executor="code", fn=lambda x: x.upper())

    @listen("input")
    async def on_input(self, data: Any) -> None:
        if "process" in self.programs:
            result = await self.invoke("process", data)
            self.results.append(result)
            await self.transmit("output", result)


@pytest.mark.asyncio
async def test_proglet_hot_swap():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=HotSwapPolicy))
    cog: HotSwapPolicy = handle.coglet

    sub = cog._bus.subscribe("output")

    # Initial function: uppercase
    await cog._dispatch_listen("input", "hello")
    result = await asyncio.wait_for(sub.get(), timeout=1.0)
    assert result == "HELLO"

    # Hot-swap to reverse
    await cog._dispatch_enact(Command("register", {"process": Program(executor="code", fn=lambda x: x[::-1])}))

    await cog._dispatch_listen("input", "hello")
    result = await asyncio.wait_for(sub.get(), timeout=1.0)
    assert result == "olleh"

    await rt.shutdown()


# ---- Integration: TickLet + transmit ----

class Heartbeater(Coglet, TickLet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.beat_count = 0

    @every(0.05, "s")
    async def heartbeat(self) -> None:
        self.beat_count += 1
        await self.transmit("heartbeat", self.beat_count)


@pytest.mark.asyncio
async def test_ticker_transmits():
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=Heartbeater))
    cog: Heartbeater = handle.coglet

    sub = cog._bus.subscribe("heartbeat")

    # Wait for at least 2 heartbeats
    beats = []
    for _ in range(2):
        beat = await asyncio.wait_for(sub.get(), timeout=1.0)
        beats.append(beat)

    assert len(beats) == 2
    assert beats[0] < beats[1]  # increasing

    await rt.shutdown()


# ---- Integration: 3-level hierarchy with tracing ----

class TopLevel(Coglet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.mid_handle: CogletHandle | None = None

    async def on_start(self) -> None:
        self.mid_handle = await self.create(CogBase(cls=MidLevel))


class MidLevel(Coglet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.leaf_handle: CogletHandle | None = None

    async def on_start(self) -> None:
        self.leaf_handle = await self.create(CogBase(cls=LeafWorker))


class LeafWorker(Coglet):
    @enact("ping")
    async def on_ping(self, data: Any) -> None:
        await self.transmit("pong", f"reply:{data}")


@pytest.mark.asyncio
async def test_three_level_hierarchy():
    rt = CogletRuntime()
    top_handle = await rt.spawn(CogBase(cls=TopLevel))
    top: TopLevel = top_handle.coglet
    mid: MidLevel = top.mid_handle.coglet
    leaf_handle = mid.leaf_handle

    # Subscribe before guiding
    sub = leaf_handle.coglet._bus.subscribe("pong")

    # Guide the leaf from mid level
    await mid.guide(leaf_handle, Command("ping", "test"))

    result = await asyncio.wait_for(sub.get(), timeout=1.0)
    assert result == "reply:test"

    # Tree should show 3 levels
    tree = rt.tree()
    assert "TopLevel" in tree
    assert "MidLevel" in tree
    assert "LeafWorker" in tree

    await rt.shutdown()


@pytest.mark.asyncio
async def test_three_level_with_trace():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = f.name
    try:
        trace = CogletTrace(path)
        rt = CogletRuntime(trace=trace)
        top_handle = await rt.spawn(CogBase(cls=TopLevel))
        top: TopLevel = top_handle.coglet
        mid: MidLevel = top.mid_handle.coglet

        sub = mid.leaf_handle.coglet._bus.subscribe("pong")
        await mid.guide(mid.leaf_handle, Command("ping", "traced"))
        await asyncio.wait_for(sub.get(), timeout=1.0)

        await rt.shutdown()

        entries = CogletTrace.load(path)
        coglet_types = {e["coglet"] for e in entries}
        assert "LeafWorker" in coglet_types
        ops = {e["op"] for e in entries}
        assert "transmit" in ops
        assert "enact" in ops
    finally:
        Path(path).unlink(missing_ok=True)


# ---- Integration: restart with supervision ----

class SupervisingParent(Coglet, LifeLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.restart_count = 0

    async def on_child_error(self, handle: CogletHandle, error: Exception) -> str:
        self.restart_count += 1
        return "restart"


class FragileWorker(Coglet, LifeLet):
    instance_count = 0

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        FragileWorker.instance_count += 1
        self.instance_id = FragileWorker.instance_count

    async def on_start(self) -> None:
        pass

    @enact("work")
    async def on_work(self, data: Any) -> None:
        await self.transmit("result", f"instance-{self.instance_id}:{data}")


@pytest.mark.asyncio
async def test_restart_preserves_handle():
    """After restart, the same handle points to a new coglet instance."""
    FragileWorker.instance_count = 0
    rt = CogletRuntime()
    parent_handle = await rt.spawn(CogBase(cls=SupervisingParent))
    parent: SupervisingParent = parent_handle.coglet

    config = CogBase(cls=FragileWorker, restart="on_error", max_restarts=3, backoff_s=0.01)
    child_handle = await rt.spawn(config, parent=parent)

    assert child_handle.coglet.instance_id == 1

    await rt.handle_child_error(child_handle, RuntimeError("boom"))

    assert child_handle.coglet.instance_id == 2
    assert parent.restart_count == 1

    # New instance works
    sub = child_handle.coglet._bus.subscribe("result")
    await child_handle.guide(Command("work", "after-restart"))
    result = await asyncio.wait_for(sub.get(), timeout=1.0)
    assert "instance-2" in result

    await rt.shutdown()


# ---- Integration: multiple mixins on one coglet ----

class KitchenSink(SuppressLet, Coglet, LifeLet, TickLet, ProgLet, LogLet):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.lifecycle_events: list[str] = []
        self.tick_fired = False

    async def on_start(self) -> None:
        self.lifecycle_events.append("start")
        self.programs["greet"] = Program(executor="code", fn=lambda name: f"hello {name}")

    async def on_stop(self) -> None:
        self.lifecycle_events.append("stop")

    @every(0.05, "s")
    async def quick_tick(self) -> None:
        self.tick_fired = True

    @listen("input")
    async def on_input(self, data: Any) -> None:
        if "greet" in self.programs:
            result = await self.invoke("greet", data)
            await self.transmit("output", result)


@pytest.mark.asyncio
async def test_kitchen_sink():
    """All mixins work together on one coglet."""
    rt = CogletRuntime()
    handle = await rt.spawn(CogBase(cls=KitchenSink))
    cog: KitchenSink = handle.coglet

    assert cog.lifecycle_events == ["start"]
    assert "greet" in cog.programs

    # Subscribe to outputs
    out_sub = cog._bus.subscribe("output")
    log_sub = cog._bus.subscribe("log")

    # Process input
    await cog._dispatch_listen("input", "world")
    result = await asyncio.wait_for(out_sub.get(), timeout=1.0)
    assert result == "hello world"

    # Log something
    await cog.log("info", "test log")
    log_msg = await asyncio.wait_for(log_sub.get(), timeout=1.0)
    assert log_msg["data"] == "test log"

    # Suppress output channel
    await cog._dispatch_enact(Command("suppress", {"channels": ["output"]}))
    await cog._dispatch_listen("input", "suppressed")
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(out_sub.get(), timeout=0.05)

    # Wait for tick
    await asyncio.sleep(0.1)
    assert cog.tick_fired is True

    await rt.shutdown()
    assert cog.lifecycle_events == ["start", "stop"]
