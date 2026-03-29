import asyncio
import pytest
from coglet import CogletRuntime, CogBase
from coglet.pco.learner import LearnerCoglet


class EchoLearner(LearnerCoglet):
    async def learn(self, experience, evaluation, signals):
        return {"diff": f"fix based on {len(signals)} signals"}


@pytest.mark.asyncio
async def test_learner_produces_patch():
    runtime = CogletRuntime()
    handle = await runtime.spawn(CogBase(cls=EchoLearner))
    coglet = handle.coglet

    patches = []
    async def collect():
        async for p in handle.observe("update"):
            patches.append(p)
            break

    task = asyncio.create_task(collect())
    await asyncio.sleep(0.01)

    await coglet._dispatch_listen("context", {
        "experience": {"data": "some rollout"},
        "evaluation": {"score": 5},
        "signals": [
            {"name": "policy", "magnitude": 0.5},
            {"name": "complexity", "magnitude": 0.3},
        ],
    })

    await asyncio.wait_for(task, timeout=1.0)
    assert "2 signals" in patches[0]["diff"]
    await runtime.shutdown()
