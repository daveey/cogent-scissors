---
name: coach.improve
description: Run one coaching session to improve the CvC tournament agent. Plays a game, runs PCO (CvCLearner) to propose program patches, tests locally, and submits. Use when asked to "improve the agent", "run a coaching session", or "coach improve".
---

# Coach Improvement Session

Act as the Coach. Each session: play a game, collect experience, run CvCLearner to propose program patches, test, submit.

## Architecture

The tournament policy is `CvCPolicy` (`cogs/cogames/cvc/cvc_policy.py`), a ProgLet-based policy with a program table:

```
CvCPolicy (MultiAgentPolicy)
  └── CvCPolicyImpl (per-agent)
       └── GameState → CogletAgentPolicy (CvcEngine)
       └── Program table (programs.py) — evolvable by PCO
       └── LLM brain (periodic analysis)
```

**Each agent is fully independent. NO shared state between agents.**

### Key Files

Policy & programs:
- `cogs/cogames/cvc/cvc_policy.py` — CvCPolicy (MultiAgentPolicy + program table)
- `cogs/cogames/cvc/programs.py` — program table (32 programs, evolvable by CvCLearner)
- `cogs/cogames/cvc/game_state.py` — GameState adapter (delegates to engine)

Engine (decision tree, pathfinding, role logic):
- `cogs/cogames/cvc/agent/main.py` — CvcEngine core decision tree
- `cogs/cogames/cvc/agent/roles.py` — role actions (miner, aligner, scrambler)
- `cogs/cogames/cvc/agent/navigation.py` — A* pathfinding
- `cogs/cogames/cvc/agent/targeting.py` — target selection, claims
- `cogs/cogames/cvc/agent/pressure.py` — role budgets, retreat
- `cogs/cogames/cvc/agent/junctions.py` — junction memory
- `cogs/cogames/cvc/agent/helpers/targeting.py` — scoring functions
- `cogs/cogames/cvc/agent/helpers/types.py` — constants

PCO (optimization loop):
- `cogs/cogames/cvc/pco_runner.py` — `run_pco_epoch()` orchestrator
- `cogs/cogames/cvc/learner.py` — CvCLearner (LLM proposes program patches)
- `cogs/cogames/cvc/critic.py` — CvCCritic (evaluates experience)
- `cogs/cogames/cvc/losses.py` — ResourceLoss, JunctionLoss, SurvivalLoss
- `cogs/cogames/cvc/constraints.py` — SyntaxConstraint, SafetyConstraint

Reference (alpha.0, scores ~14 in tournament):
- `/Users/daveey/code/metta.1/cog-cyborg/src/cog_cyborg/policy/` — alpha.0 source

## Directory Layout

```
.coach/
  state.json          # persistent state (best score, latest submission)
  todos.md            # TODO list + dead ends (DON'T RETRY dead ends)
  sessions/
    <timestamp>/
      plan.md         # what this session is trying and why
      log.md          # running log: actions, results, observations
```

## Session Protocol

If invoked with an argument (e.g. `beta`), use that as the policy name. Otherwise read from `.coach/state.json`.

### Step 1: Load State & Check Previous Results

1. Read `.coach/state.json` and `.coach/todos.md`.
2. Read the most recent session's `log.md`.
3. If previous session says **WAITING**: check tournament scores, log findings, revert if regressed.

### Step 2: Create New Session

1. Create `.coach/sessions/YYYYMMDD-HHMMSS/`
2. Write `plan.md` and start `log.md`.

### Step 3: Play a Game & Collect Experience

```bash
cd /Users/daveey/code/coglet/coglet.1/cogs/cogames
cogames scrimmage -m machina_1 \
  -p class=cvc.cvc_policy.CvCPolicy \
  -c 8 -e 1 --seed 42 \
  --action-timeout-ms 30000
```

Experience is collected automatically by CvCPolicy (snapshots every 500 steps) and written to `$COGLET_LEARNINGS_DIR` (default `/tmp/coglet_learnings/`).

### Step 4: Run CvCLearner (PCO Epoch)

Load the experience and run one PCO epoch:

```python
import asyncio, json, anthropic
from cvc.pco_runner import run_pco_epoch
from cvc.programs import all_programs

# Load experience from learnings file
with open("/tmp/coglet_learnings/<game_id>.json") as f:
    learnings = json.load(f)
experience = learnings["snapshots"]

# Run PCO epoch — learner proposes program patches
result = asyncio.run(run_pco_epoch(
    experience=experience,
    programs=all_programs(),
    client=anthropic.Anthropic(),
))

# result = {"accepted": bool, "signals": [...], "patch": {...}}
```

The CvCLearner:
1. Receives experience + evaluation + loss signals
2. Sees all 32 program source codes
3. Proposes patches as `{"program_name": {"type": "code", "source": "def ..."}}`
4. Patches validated by SyntaxConstraint + SafetyConstraint

### Step 5: Apply & Test

If PCO produced an accepted patch:
1. Apply the patched functions to `cogs/cogames/cvc/programs.py`
2. Test locally across 5+ seeds
3. If improved, keep. If regressed, revert.

If no accepted patch, analyze loss signals to identify weakness and make a targeted change to the engine code.

### Step 6: Submit

```bash
cd /Users/daveey/code/coglet/coglet.1/cogs/cogames
cogames upload \
  -p class=cvc.cvc_policy.CvCPolicy \
  -n <policy_name> \
  -f cvc -f mettagrid_sdk -f setup_policy.py \
  --setup-script setup_policy.py \
  --season <season>
```

### Step 7: Update State

1. Update `.coach/state.json`
2. Update `.coach/todos.md` (mark done, add dead ends if failed)
3. Log final status in `log.md`

## Principles

1. **Use CvCLearner first.** Let the LLM propose patches to programs.py via PCO.
2. **One change at a time.** Isolate what works.
3. **Don't retry dead ends.** Check todos.md before trying anything.
4. **Test across 5+ seeds.** Single-seed results are noise.
5. **No shared state.** Agents must be fully independent.
6. **Compare with alpha.0.** When stuck, diff against the proven top scorer.
7. **Local scores lie.** Submit and check tournament.
