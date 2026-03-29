import asyncio
import pytest
from coglet import CogletRuntime, CogBase
from coglet.pco.constraint import ConstraintCoglet


class MaxLines(ConstraintCoglet):
    async def check(self, patch):
        lines = len(patch["diff"].splitlines())
        if lines > 10:
            return {"accepted": False, "reason": f"too many lines: {lines}"}
        return {"accepted": True}


@pytest.mark.asyncio
async def test_constraint_rejects_large_patch():
    runtime = CogletRuntime()
    handle = await runtime.spawn(CogBase(cls=MaxLines))
    coglet = handle.coglet

    verdicts = []
    async def collect():
        async for v in handle.observe("verdict"):
            verdicts.append(v)
            break

    task = asyncio.create_task(collect())
    await asyncio.sleep(0.01)

    big_patch = {"diff": "\n".join(f"line {i}" for i in range(20))}
    await coglet._dispatch_listen("update", big_patch)

    await asyncio.wait_for(task, timeout=1.0)
    assert verdicts[0]["accepted"] is False
    assert "too many lines" in verdicts[0]["reason"]
    await runtime.shutdown()


@pytest.mark.asyncio
async def test_constraint_accepts_small_patch():
    runtime = CogletRuntime()
    handle = await runtime.spawn(CogBase(cls=MaxLines))
    coglet = handle.coglet

    verdicts = []
    async def collect():
        async for v in handle.observe("verdict"):
            verdicts.append(v)
            break

    task = asyncio.create_task(collect())
    await asyncio.sleep(0.01)

    small_patch = {"diff": "one line"}
    await coglet._dispatch_listen("update", small_patch)

    await asyncio.wait_for(task, timeout=1.0)
    assert verdicts[0]["accepted"] is True
    await runtime.shutdown()
