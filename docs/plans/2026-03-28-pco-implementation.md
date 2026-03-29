# Proximal Coglet Optimizer — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement PCO as a coglet that orchestrates PPO-style optimization over source code, using LLM prompts for each operation.

**Architecture:** PCO is a COG that creates actor + critic from configs, wires plugged losses/constraints/learner via channels, and runs the rollout→critic→losses→learner→constraint→enact loop. All components are standard coglets using @listen/@enact/transmit. Built on existing `src/coglet/` framework (Coglet, CogletRuntime, CogBase, CogletHandle, TickLet, LifeLet).

**Tech Stack:** Python 3.11+, asyncio, coglet framework, pytest + pytest-asyncio

**Design doc:** `docs/design/proximal_coglet_optimizer.md`

---

### Task 1: LossCoglet base class

The base class for all loss coglets. Listens on "experience" + "evaluation", transmits on "signal".

**Files:**
- Create: `src/coglet/pco/loss.py`
- Test: `tests/test_pco_loss.py`

**Step 1: Write the failing test**

```python
# tests/test_pco_loss.py
import asyncio
import pytest
from coglet import Coglet, CogletRuntime, CogBase, CogletHandle, listen

from coglet.pco.loss import LossCoglet


class ScoreLoss(LossCoglet):
    """Concrete loss: signals the raw score."""
    async def compute_loss(self, experience, evaluation):
        return {"name": "score", "magnitude": evaluation["score"]}


@pytest.mark.asyncio
async def test_loss_coglet_emits_signal():
    runtime = CogletRuntime()
    handle = await runtime.spawn(CogBase(cls=ScoreLoss))
    coglet = handle.coglet

    signals = []
    async def collect():
        async for s in handle.observe("signal"):
            signals.append(s)
            break

    task = asyncio.create_task(collect())
    await asyncio.sleep(0.01)

    await coglet._dispatch_listen("experience", {"replay": "data"})
    await coglet._dispatch_listen("evaluation", {"score": 42})

    await asyncio.wait_for(task, timeout=1.0)
    assert signals[0]["name"] == "score"
    assert signals[0]["magnitude"] == 42
    await runtime.shutdown()
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_loss.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# src/coglet/pco/__init__.py
```

```python
# src/coglet/pco/loss.py
"""LossCoglet — base class for PCO loss functions.

Listens on "experience" and "evaluation" channels. When both are received
for a given step, calls compute_loss() and transmits the result on "signal".
"""
from __future__ import annotations
from typing import Any

from coglet.coglet import Coglet, listen


class LossCoglet(Coglet):
    """Base loss coglet. Subclass and override compute_loss()."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._pending_experience: Any = None
        self._pending_evaluation: Any = None

    @listen("experience")
    async def _on_experience(self, data: Any) -> None:
        self._pending_experience = data
        await self._try_compute()

    @listen("evaluation")
    async def _on_evaluation(self, data: Any) -> None:
        self._pending_evaluation = data
        await self._try_compute()

    async def _try_compute(self) -> None:
        if self._pending_experience is None or self._pending_evaluation is None:
            return
        experience = self._pending_experience
        evaluation = self._pending_evaluation
        self._pending_experience = None
        self._pending_evaluation = None
        signal = await self.compute_loss(experience, evaluation)
        await self.transmit("signal", signal)

    async def compute_loss(self, experience: Any, evaluation: Any) -> Any:
        raise NotImplementedError
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_loss.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/coglet/pco/ tests/test_pco_loss.py
git commit -m "feat: add LossCoglet base class for PCO"
```

---

### Task 2: ConstraintCoglet base class

Gates patches with accept/reject. Listens on "update", transmits on "verdict".

**Files:**
- Create: `src/coglet/pco/constraint.py`
- Test: `tests/test_pco_constraint.py`

**Step 1: Write the failing test**

```python
# tests/test_pco_constraint.py
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
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_constraint.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# src/coglet/pco/constraint.py
"""ConstraintCoglet — base class for PCO update constraints.

Listens on "update" channel, calls check(), transmits verdict on "verdict".
"""
from __future__ import annotations
from typing import Any

from coglet.coglet import Coglet, listen


class ConstraintCoglet(Coglet):
    """Base constraint coglet. Subclass and override check()."""

    @listen("update")
    async def _on_update(self, patch: Any) -> None:
        verdict = await self.check(patch)
        await self.transmit("verdict", verdict)

    async def check(self, patch: Any) -> Any:
        raise NotImplementedError
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_constraint.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/coglet/pco/constraint.py tests/test_pco_constraint.py
git commit -m "feat: add ConstraintCoglet base class for PCO"
```

---

### Task 3: LearnerCoglet base class

Takes loss signals, produces code patches. Listens on "signals", transmits on "update".

**Files:**
- Create: `src/coglet/pco/learner.py`
- Test: `tests/test_pco_learner.py`

**Step 1: Write the failing test**

```python
# tests/test_pco_learner.py
import asyncio
import pytest
from coglet import CogletRuntime, CogBase

from coglet.pco.learner import LearnerCoglet


class EchoLearner(LearnerCoglet):
    async def learn(self, signals):
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

    await coglet._dispatch_listen("signals", [
        {"name": "policy", "magnitude": 0.5},
        {"name": "complexity", "magnitude": 0.3},
    ])

    await asyncio.wait_for(task, timeout=1.0)
    assert "2 signals" in patches[0]["diff"]
    await runtime.shutdown()
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_learner.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# src/coglet/pco/learner.py
"""LearnerCoglet — base class for PCO learners.

Listens on "signals" channel, calls learn(), transmits patch on "update".
"""
from __future__ import annotations
from typing import Any

from coglet.coglet import Coglet, listen


class LearnerCoglet(Coglet):
    """Base learner coglet. Subclass and override learn()."""

    @listen("signals")
    async def _on_signals(self, signals: Any) -> None:
        patch = await self.learn(signals)
        await self.transmit("update", patch)

    async def learn(self, signals: Any) -> Any:
        raise NotImplementedError
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_learner.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/coglet/pco/learner.py tests/test_pco_learner.py
git commit -m "feat: add LearnerCoglet base class for PCO"
```

---

### Task 4: ProximalCogletOptimizer — core loop

The COG that wires everything together. Creates actor + critic from configs, orchestrates the rollout→critic→losses→learner→constraint→enact cycle.

**Files:**
- Create: `src/coglet/pco/optimizer.py`
- Test: `tests/test_pco_optimizer.py`

**Step 1: Write the failing test**

```python
# tests/test_pco_optimizer.py
import asyncio
import pytest
from coglet import Coglet, CogletRuntime, CogBase, listen, enact

from coglet.pco.optimizer import ProximalCogletOptimizer
from coglet.pco.loss import LossCoglet
from coglet.pco.constraint import ConstraintCoglet
from coglet.pco.learner import LearnerCoglet


class FakeActor(Coglet):
    """Actor that transmits experience when it receives 'run'."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.version = 0

    @enact("run")
    async def run_rollout(self, data):
        await self.transmit("experience", {"score": 10 + self.version})

    @enact("update")
    async def apply_update(self, patch):
        self.version += 1


class FakeCritic(Coglet):
    @listen("experience")
    async def evaluate(self, experience):
        await self.transmit("evaluation", {"score": experience["score"]})

    @enact("update")
    async def apply_update(self, patch):
        pass


class ScoreLoss(LossCoglet):
    async def compute_loss(self, experience, evaluation):
        return {"name": "score", "magnitude": evaluation["score"]}


class AlwaysAccept(ConstraintCoglet):
    async def check(self, patch):
        return {"accepted": True}


class FakeLearner(LearnerCoglet):
    async def learn(self, signals):
        return {"diff": "improve things"}


@pytest.mark.asyncio
async def test_pco_runs_one_epoch():
    runtime = CogletRuntime()
    pco_handle = await runtime.spawn(CogBase(
        cls=ProximalCogletOptimizer,
        kwargs=dict(
            actor_config=CogBase(cls=FakeActor),
            critic_config=CogBase(cls=FakeCritic),
            losses=[ScoreLoss()],
            constraints=[AlwaysAccept()],
            learner=FakeLearner(),
        ),
    ))
    pco = pco_handle.coglet

    # Run one epoch
    result = await pco.run_epoch()

    assert result["accepted"] is True
    assert result["signals"][0]["name"] == "score"
    assert pco._actor_handle.coglet.version == 1
    await runtime.shutdown()
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_optimizer.py::test_pco_runs_one_epoch -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# src/coglet/pco/optimizer.py
"""ProximalCogletOptimizer — PPO as a coglet graph.

Creates actor + critic from configs. Orchestrates:
  rollout → critic → losses → learner → constraints → enact

All components are standard coglets using @listen/@enact/transmit.
"""
from __future__ import annotations

import asyncio
from typing import Any

from coglet.coglet import Coglet
from coglet.handle import CogBase, CogletHandle, Command
from coglet.lifelet import LifeLet
from coglet.pco.constraint import ConstraintCoglet
from coglet.pco.learner import LearnerCoglet
from coglet.pco.loss import LossCoglet


class ProximalCogletOptimizer(Coglet, LifeLet):
    """COG that orchestrates PCO training loop."""

    def __init__(
        self,
        *,
        actor_config: CogBase,
        critic_config: CogBase,
        losses: list[LossCoglet],
        constraints: list[ConstraintCoglet],
        learner: LearnerCoglet,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._actor_config = actor_config
        self._critic_config = critic_config
        self._losses = losses
        self._constraints = constraints
        self._learner = learner
        self._actor_handle: CogletHandle | None = None
        self._critic_handle: CogletHandle | None = None

    async def on_start(self) -> None:
        self._actor_handle = await self.create(self._actor_config)
        self._critic_handle = await self.create(self._critic_config)

    async def run_epoch(self) -> dict[str, Any]:
        """Execute one full PCO epoch. Returns result dict."""
        actor = self._actor_handle
        critic = self._critic_handle
        assert actor is not None and critic is not None

        # 1. Rollout: tell actor to run, collect experience
        experience = await self._rollout(actor)

        # 2. Critic: feed experience, get evaluation
        evaluation = await self._evaluate(critic, experience)

        # 3. Losses: feed (experience, evaluation), collect signals
        signals = await self._compute_losses(experience, evaluation)

        # 4. Learner: feed signals, get patch
        patch = await self._get_patch(signals)

        # 5. Constraints: check patch
        accepted, reason = await self._check_constraints(patch)

        if accepted:
            # 6. Enact: apply patch to actor and critic
            await self.guide(actor, Command(type="update", data=patch))
            await self.guide(critic, Command(type="update", data=patch))

        return {
            "accepted": accepted,
            "reason": reason,
            "signals": signals,
            "patch": patch,
        }

    async def _rollout(self, actor: CogletHandle) -> Any:
        collector = actor.coglet._bus.subscribe("experience")
        await self.guide(actor, Command(type="run"))
        return await asyncio.wait_for(collector.get(), timeout=30.0)

    async def _evaluate(self, critic: CogletHandle, experience: Any) -> Any:
        collector = critic.coglet._bus.subscribe("evaluation")
        await critic.coglet._dispatch_listen("experience", experience)
        return await asyncio.wait_for(collector.get(), timeout=30.0)

    async def _compute_losses(
        self, experience: Any, evaluation: Any
    ) -> list[Any]:
        signals = []
        for loss in self._losses:
            collector = loss._bus.subscribe("signal")
            await loss._dispatch_listen("experience", experience)
            await loss._dispatch_listen("evaluation", evaluation)
            signal = await asyncio.wait_for(collector.get(), timeout=30.0)
            signals.append(signal)
        return signals

    async def _get_patch(self, signals: list[Any]) -> Any:
        collector = self._learner._bus.subscribe("update")
        await self._learner._dispatch_listen("signals", signals)
        return await asyncio.wait_for(collector.get(), timeout=30.0)

    async def _check_constraints(
        self, patch: Any
    ) -> tuple[bool, str | None]:
        for constraint in self._constraints:
            collector = constraint._bus.subscribe("verdict")
            await constraint._dispatch_listen("update", patch)
            verdict = await asyncio.wait_for(collector.get(), timeout=30.0)
            if not verdict.get("accepted", False):
                return False, verdict.get("reason")
        return True, None
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_optimizer.py::test_pco_runs_one_epoch -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/coglet/pco/optimizer.py tests/test_pco_optimizer.py
git commit -m "feat: add ProximalCogletOptimizer core loop"
```

---

### Task 5: PCO constraint rejection + retry loop

Test that PCO retries the learner when a constraint rejects the patch.

**Files:**
- Modify: `src/coglet/pco/optimizer.py`
- Test: `tests/test_pco_optimizer.py`

**Step 1: Write the failing test**

```python
# append to tests/test_pco_optimizer.py

class RejectFirstConstraint(ConstraintCoglet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._calls = 0

    async def check(self, patch):
        self._calls += 1
        if self._calls == 1:
            return {"accepted": False, "reason": "try again"}
        return {"accepted": True}


class RetryLearner(LearnerCoglet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._calls = 0

    async def learn(self, signals):
        self._calls += 1
        return {"diff": f"attempt {self._calls}"}


@pytest.mark.asyncio
async def test_pco_retries_on_rejection():
    learner = RetryLearner()
    constraint = RejectFirstConstraint()
    runtime = CogletRuntime()
    pco_handle = await runtime.spawn(CogBase(
        cls=ProximalCogletOptimizer,
        kwargs=dict(
            actor_config=CogBase(cls=FakeActor),
            critic_config=CogBase(cls=FakeCritic),
            losses=[ScoreLoss()],
            constraints=[constraint],
            learner=learner,
            max_retries=3,
        ),
    ))
    pco = pco_handle.coglet

    result = await pco.run_epoch()

    assert result["accepted"] is True
    assert learner._calls == 2
    assert constraint._calls == 2
    await runtime.shutdown()
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_optimizer.py::test_pco_retries_on_rejection -v`
Expected: FAIL

**Step 3: Add retry loop to run_epoch**

Update `ProximalCogletOptimizer.__init__` to accept `max_retries` kwarg (default 3). Update `run_epoch` to retry the learner→constraints step:

```python
# In __init__, add:
self._max_retries = kwargs.pop("max_retries", 3)

# In run_epoch, replace steps 4-5 with:
patch = None
accepted = False
reason = None
for attempt in range(self._max_retries):
    if attempt == 0:
        patch = await self._get_patch(signals)
    else:
        # Feed rejection reason back to learner with the signals
        retry_signals = signals + [{"name": "rejection", "reason": reason}]
        patch = await self._get_patch(retry_signals)
    accepted, reason = await self._check_constraints(patch)
    if accepted:
        break
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_optimizer.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/coglet/pco/optimizer.py tests/test_pco_optimizer.py
git commit -m "feat: add constraint rejection retry loop to PCO"
```

---

### Task 6: PCO multi-epoch run with transmit

Test that PCO can run multiple epochs and transmits epoch results on "epoch" channel.

**Files:**
- Modify: `src/coglet/pco/optimizer.py`
- Test: `tests/test_pco_optimizer.py`

**Step 1: Write the failing test**

```python
# append to tests/test_pco_optimizer.py

@pytest.mark.asyncio
async def test_pco_multi_epoch():
    runtime = CogletRuntime()
    pco_handle = await runtime.spawn(CogBase(
        cls=ProximalCogletOptimizer,
        kwargs=dict(
            actor_config=CogBase(cls=FakeActor),
            critic_config=CogBase(cls=FakeCritic),
            losses=[ScoreLoss()],
            constraints=[AlwaysAccept()],
            learner=FakeLearner(),
        ),
    ))
    pco = pco_handle.coglet

    epochs = []
    async def collect():
        async for e in pco_handle.observe("epoch"):
            epochs.append(e)
            if len(epochs) >= 3:
                break

    task = asyncio.create_task(collect())
    await asyncio.sleep(0.01)

    await pco.run(num_epochs=3)

    await asyncio.wait_for(task, timeout=5.0)
    assert len(epochs) == 3
    assert all(e["accepted"] for e in epochs)
    # Actor should have been updated 3 times
    assert pco._actor_handle.coglet.version == 3
    await runtime.shutdown()
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_optimizer.py::test_pco_multi_epoch -v`
Expected: FAIL

**Step 3: Add run() method**

```python
# Add to ProximalCogletOptimizer:
async def run(self, num_epochs: int = 1) -> list[dict[str, Any]]:
    """Run multiple epochs, transmitting results on 'epoch' channel."""
    results = []
    for i in range(num_epochs):
        result = await self.run_epoch()
        result["epoch"] = i
        await self.transmit("epoch", result)
        results.append(result)
    return results
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_pco_optimizer.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/coglet/pco/optimizer.py tests/test_pco_optimizer.py
git commit -m "feat: add multi-epoch run with epoch channel to PCO"
```

---

### Task 7: Package exports and existing test regression check

Wire up `src/coglet/pco/__init__.py` exports. Verify all 146+ existing tests still pass.

**Files:**
- Modify: `src/coglet/pco/__init__.py`
- Run: all tests

**Step 1: Write package exports**

```python
# src/coglet/pco/__init__.py
from coglet.pco.loss import LossCoglet
from coglet.pco.constraint import ConstraintCoglet
from coglet.pco.learner import LearnerCoglet
from coglet.pco.optimizer import ProximalCogletOptimizer

__all__ = [
    "LossCoglet",
    "ConstraintCoglet",
    "LearnerCoglet",
    "ProximalCogletOptimizer",
]
```

**Step 2: Run ALL tests**

Run: `PYTHONPATH=src python -m pytest tests/ -v`
Expected: 146 existing + new PCO tests all PASS

**Step 3: Commit**

```bash
git add src/coglet/pco/__init__.py
git commit -m "feat: add pco package exports"
```
