"""Unit tests for coglet.proglet: ProgLet mixin."""
from __future__ import annotations

import pytest

from coglet import Coglet, Command
from coglet.proglet import Program, Executor, CodeExecutor, ProgLet


class ProgCoglet(Coglet, ProgLet):
    pass


# --- Program dataclass ---

def test_program_defaults():
    p = Program(executor="code")
    assert p.executor == "code"
    assert p.fn is None
    assert p.system is None
    assert p.tools == []
    assert p.parser is None
    assert p.config == {}


def test_program_with_fn():
    fn = lambda x: x * 2
    p = Program(executor="code", fn=fn, config={"temperature": 0.5})
    assert p.fn is fn
    assert p.config == {"temperature": 0.5}


# --- CodeExecutor ---

@pytest.mark.asyncio
async def test_code_executor_sync():
    executor = CodeExecutor()
    prog = Program(executor="code", fn=lambda ctx: ctx + 1)
    result = await executor.run(prog, 10, None)
    assert result == 11


@pytest.mark.asyncio
async def test_code_executor_async():
    async def async_fn(ctx):
        return ctx * 3

    executor = CodeExecutor()
    prog = Program(executor="code", fn=async_fn)
    result = await executor.run(prog, 7, None)
    assert result == 21


# --- ProgLet register and invoke ---

@pytest.mark.asyncio
async def test_proglet_register_and_invoke():
    cog = ProgCoglet()
    prog = Program(executor="code", fn=lambda ctx: ctx + 100)
    await cog._dispatch_enact(Command("register", {"add100": prog}))
    assert "add100" in cog.programs
    result = await cog.invoke("add100", 5)
    assert result == 105


@pytest.mark.asyncio
async def test_proglet_register_multiple():
    cog = ProgCoglet()
    progs = {
        "double": Program(executor="code", fn=lambda ctx: ctx * 2),
        "negate": Program(executor="code", fn=lambda ctx: -ctx),
    }
    await cog._dispatch_enact(Command("register", progs))
    assert await cog.invoke("double", 4) == 8
    assert await cog.invoke("negate", 4) == -4


@pytest.mark.asyncio
async def test_proglet_update_program():
    cog = ProgCoglet()
    await cog._dispatch_enact(Command("register", {
        "f": Program(executor="code", fn=lambda ctx: ctx),
    }))
    await cog._dispatch_enact(Command("register", {
        "f": Program(executor="code", fn=lambda ctx: ctx + 1),
    }))
    assert await cog.invoke("f", 0) == 1


@pytest.mark.asyncio
async def test_proglet_invoke_missing_program():
    cog = ProgCoglet()
    with pytest.raises(KeyError):
        await cog.invoke("nonexistent")


@pytest.mark.asyncio
async def test_proglet_invoke_missing_executor():
    cog = ProgCoglet()
    cog.programs["bad"] = Program(executor="no_such_executor")
    with pytest.raises(KeyError):
        await cog.invoke("bad")


@pytest.mark.asyncio
async def test_proglet_async_code_program():
    async def compute(ctx):
        return ctx ** 2

    cog = ProgCoglet()
    await cog._dispatch_enact(Command("register", {
        "square": Program(executor="code", fn=compute),
    }))
    assert await cog.invoke("square", 5) == 25


@pytest.mark.asyncio
async def test_proglet_register_custom_executor():
    class EchoExecutor:
        async def run(self, program, context, invoke):
            return f"echo:{context}"

    assert isinstance(EchoExecutor(), Executor)

    cog = ProgCoglet()
    await cog._dispatch_enact(Command("executor", {"echo": EchoExecutor()}))
    await cog._dispatch_enact(Command("register", {
        "greet": Program(executor="echo"),
    }))
    assert await cog.invoke("greet", "hello") == "echo:hello"
