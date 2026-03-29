---
name: coach.improve
description: This skill should be used when the user asks to "improve the agent", "run a coaching session", "coach improve", "iterate on the policy", or wants to test and submit agent changes to the CvC tournament. Runs one focused improvement iteration with local testing, tournament submission, and logging.
---

# Iterative Agent Improvement Session

Act as the Coach. Each session: iteratively improve the agent, test changes locally, submit to the tournament, and learn from results.

**Read `cvc/agent/README.md` first.** It has the full guide to how the agent works, how to test locally, submit, check scores, and debug. Do not duplicate that knowledge here -- refer to it.

## Directory Layout

```
.coach/
  state.json          # persistent state (best score, last session, etc.)
  todos.md            # running TODO list of improvement ideas
  sessions/
    <timestamp>/
      plan.md         # what this session is trying and why
      log.md          # running log: actions, results, observations, wait status
      diff.patch      # the code diff attempted (if any)
      results.json    # local + tournament results collected
```

## Session Protocol

### Step 1: Load State & Finalize Incomplete Sessions

1. Read `.coach/state.json` and `.coach/todos.md`.
2. Scan `.coach/sessions/` for the most recent session folder.
3. If the last session's `log.md` says **WAITING** (submitted but no results yet):
   - Check tournament scores now (see README for how).
   - Write findings into THIS session's log.
   - If the old session's changes improved scores, keep them. If scores dropped, consider reverting.
   - Update the old session's `results.json` and mark it finalized.

### Step 2: Create New Session

1. Create `.coach/sessions/YYYYMMDD-HHMMSS/`
2. Write `plan.md`: current best score/rank, what you're trying, which files, and why.
3. Start `log.md` with a timestamp and plan summary.

### Step 3: Analyze & Choose One Improvement

1. Check current tournament scores (leaderboard + recent matches).
2. Read `.coach/todos.md` for previously identified ideas.
3. Read the relevant policy code (see README for file map).
4. Pick ONE focused improvement. Don't stack multiple changes.

### Step 4: Test Locally

**Before any tournament submission, validate locally:**

```bash
cd /home/user/coglet/cogames
/home/user/.venv-cogames/bin/cogames scrimmage \
  -m machina_1 \
  -p class=cvc.cvc_policy.CogletPolicy \
  -c 8 -e 1 --seed 42 \
  --action-timeout-ms 30000
```

- Check the "Average Per-Agent Reward" in the output.
- Compare against baseline (previous local score before the change).
- If score dropped significantly, reconsider the change before submitting.
- Log the local test result in `log.md`.

For more confidence, run multiple episodes (`-e 3`) or different seeds.

### Step 5: Commit & Submit

1. Save diff: `git diff > .coach/sessions/<session>/diff.patch`
2. Commit with a descriptive message. Push to the feature branch.
3. Submit to tournament (see README for the `ship` command).
4. Log the submission in `log.md` with: "WAITING: submitted, checking results next session"

### Step 6: Update State

1. Update `.coach/state.json` (last_session, local score, etc.)
2. Update `.coach/todos.md` (mark done items, add new ideas, reprioritize)
3. Ensure `log.md` has a clear final status: DONE, WAITING, or FAILED

## Principles

1. **Test locally first.** Never submit untested changes to tournament.
2. **One change at a time.** Make one focused improvement per session.
3. **Don't break what works.** Conservative > ambitious. A regression is worse than no change.
4. **Log everything.** Clear trail of what was tried, local results, tournament results.
5. **Learn from results.** Read match logs. Understand why scores changed.
6. **Git discipline.** Commit before submitting. Push to the feature branch.
