# Proximal Coglet Optimizer (PCO)

*PPO expressed as a coglet graph.*

## Core Idea

Every component of PPO — actor, critic, losses, learner, constraints — is a coglet with the standard COG/LET interface. The optimizer itself is a COG that orchestrates the training loop. The "parameters" being optimized are source code and prompts. The "gradient step" is an LLM code edit.

## Signature

```python
class ProximalCogletOptimizer(Coglet, TickLet):
    def __init__(
        self,
        actor_config: CogBase,
        critic_config: CogBase,
        losses: list[LossCoglet],
        constraints: list[ConstraintCoglet],
        learner: LearnerCoglet,
    ): ...
```

**Owned** (created by PCO, enactable):
- `actor` — created from config, receives patches via `enact("update")`
- `critic` — created from config, receives patches via `enact("update")`

**Plugged** (passed in, observe-only):
- `losses[]` — each scores a dimension, transmits signals
- `constraints[]` — each gates updates, transmits accept/reject
- `learner` — produces code patches from loss signals

Plugged coglets may have their own optimizers underneath — the fractal property. PCO doesn't need to know.

## Loop (one epoch)

```
1. PCO wraps actor in Rollout, runs games
2. Rollout observes actor, transmits "experience"
3. PCO feeds experience to critic
4. Critic transmits "evaluation"
5. PCO feeds (experience, evaluation) to each loss
6. Each loss transmits "signal" (insight + magnitude)
7. PCO aggregates signals, feeds to learner
8. Learner transmits "update" (a patch)
9. PCO feeds patch to each constraint
10. Each constraint transmits accept/reject
11. If rejected: feed reason back to learner, goto 8
12. If accepted: PCO.guide(actor, patch) → enact("update")
13. Repeat
```

## Channel & Control Flow

```
┌─ PCO ──────────────────────────────────────────────────┐
│                                                         │
│  create(actor_config) ──→ actor_handle                  │
│  create(critic_config) ──→ critic_handle                │
│                                                         │
│  LOOP:                                                  │
│    observe(actor, "experience") ──→ experience          │
│    feed experience to critic (transmit)                  │
│    observe(critic, "evaluation") ──→ evaluation          │
│    feed (experience, evaluation) to each loss            │
│    observe(loss[i], "signal") ──→ signals[]              │
│    feed signals to learner                               │
│    observe(learner, "update") ──→ patch                  │
│    feed patch to each constraint                         │
│    observe(constraint[i], "verdict") ──→ accept/reject   │
│    guide(actor, patch)    # enact("update")              │
│    guide(critic, patch)   # enact("update")              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Data plane** (listen/transmit): experience → evaluation → signals → patch → verdict
**Control plane** (guide/enact): PCO applies accepted patches to actor/critic
**Fractal**: any plugged coglet can have its own PCO underneath

## Mapping to PPO

| PPO Concept | Coglet Equivalent |
|---|---|
| Policy network θ | Actor coglet (source code) |
| Value network φ | Critic coglet (prompt + logic) |
| Rollout buffer | Experience channel data |
| Advantage estimation | Critic's evaluation |
| Policy loss (clipped surrogate) | PolicyLoss coglet |
| Value loss | ValueLoss coglet |
| Entropy bonus | EntropyLoss coglet |
| Weight decay / L2 regularization | ComplexityLoss coglet |
| Gradient descent step | Learner coglet (code edit) |
| Learning rate | Learner aggressiveness (guidable) |
| Trust region / max step size | ChangeMagnitude constraint |
| Epoch | One full loop iteration |
| θ_old (frozen reference) | Git commit before update |

**Key difference from neural PPO**: parameters are discrete (source code + prompts), so there's no continuous gradient. The learner makes semantic edits. Git gives you θ_old (previous commit), rollback (revert), and parallel experiments (branches) for free.

## Coglet Categories

Three categories of pluggable coglets:

- **Losses** — score the current state of actor/critic
- **Constraints** — gate updates before they're applied
- **Learner** — produces updates from loss signals

## CvC Instance

```python
pco = ProximalCogletOptimizer(
    actor_config=CogBase(cls=CvcActor),
    critic_config=CogBase(cls=CvcCritic),
    losses=[
        PolicyLoss(),
        ValueLoss(),
        EntropyLoss(),
        ComplexityLoss(),
    ],
    constraints=[
        ChangeMagnitude(max_diff_lines=50),
    ],
    learner=CodeLearner(),
)
```

| Component | Implementation |
|---|---|
| Actor | `cvc/agent/` heuristic engine. `enact("update")` applies a git patch. |
| Critic | LLM prompt that reads game logs, predicts whether a change will improve or hurt score. |
| PolicyLoss | Compare scores before/after update. |
| ValueLoss | Did the critic's prediction match the actual score delta? |
| EntropyLoss | Are role distributions and strategies varied enough across games? |
| ComplexityLoss | LOC, cyclomatic complexity, number of special cases in actor code. |
| ChangeMagnitude | Reject patches over N lines. |
| Learner | LLM that reads loss signals and produces a focused code edit. |

## Ideas from MaestroMotif (Klissarov et al., 2024)

[MaestroMotif](https://arxiv.org/abs/2412.08542) decomposes RL into LLM-orchestrated skill learning. Several patterns map directly to PCO.

### LLM-as-Reward (Motif)

Instead of hand-engineering loss functions, use LLM preferences to *derive* them. Show the LLM pairs of experience traces and ask "which is better for [objective]?" Train a reward model from these preferences (Bradley-Terry). Each LossCoglet could use this pattern — the loss prompt asks the LLM to judge experience quality rather than computing a fixed metric.

```python
class PreferenceLoss(LossCoglet):
    """LLM compares pairs of experience traces, producing a preference signal."""
    @listen("experience")
    def evaluate(self, experience):
        # Show LLM pairs of traces, ask which is better
        # Distill preferences into scalar signal
        self.transmit("signal", preference_score)
```

### Code-as-Policy with Self-Test Refinement

MaestroMotif's LLM writes policy code, generates a unit test, runs it, evaluates the trace, and rewrites if the trace doesn't match intent. This maps to our Learner → Constraint loop but adds a self-test step:

1. Learner produces patch
2. Learner also produces a test that exercises the patch
3. Test runs, producing a trace
4. Learner evaluates: does the trace match intent?
5. If not, learner rewrites before submitting to constraints

This is internal to the Learner coglet — it self-refines before transmitting the update. The constraint pipeline is a separate external gate.

### Skill Decomposition as Coglet Hierarchy

MaestroMotif decomposes behavior into skills (options framework) with initiation/termination conditions. Each skill maps to a child coglet:

```
Actor (COG)
  ├── MinerSkill (LET) — initiation: no role gear; termination: resources deposited
  ├── AlignerSkill (LET) — initiation: has aligner gear + hearts; termination: junction aligned
  └── ScramblerSkill (LET) — initiation: has scrambler gear + hearts; termination: junction scrambled
```

The Actor's high-level policy (which skill to activate) is itself code that the Learner can edit. The low-level skill policies are separate edit targets. This gives the PCO two granularities: editing the skill selector vs editing individual skills.

### Emergent Curriculum

When multiple losses compete for learner attention, a natural curriculum emerges. Early epochs focus on PolicyLoss (basic score improvement) because it dominates. As scores plateau, EntropyLoss and ComplexityLoss become the binding constraints. The PCO doesn't need to schedule this — it falls out of the loss magnitudes.

### LLM Scale and Refinement

MaestroMotif finds that self-refinement only helps at large model scale (405B benefits, 8B does not). Implication for PCO: the Learner coglet should use the strongest available model, and the self-test refinement loop is only worth the cost at that scale. Smaller models work fine for losses and constraints where the task is judgment, not generation.
