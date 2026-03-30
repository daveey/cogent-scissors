# Coach Workflow

How a user goes from zero to competing in a Softmax CogGames tournament, guided by a coding agent (coach).

## The Idea

You open your favorite coding agent (Claude Code, Cursor, etc.) and tell it:

> Read http://softmax.com/play.md

The agent reads the guide, and from there handles everything: account setup, repo fork, first submission, local testing, and iterative improvement. You watch your scores climb, steer your agent with high-level guidance, and review replays and stats on the Softmax dashboard.

## Flow Diagram

```
                         YOU (human)
                          |
                    "read play.md"
                          |
                          v
               +--------------------+
               |   CODING AGENT     |    <-- Claude Code, Cursor, etc.
               |     (Coach)        |
               +--------------------+
                          |
          reads play.md --+-- follows instructions
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
    +-----------+   +-----------+   +-----------+
    |  Sign Up  |   | Fork Repo |   |  Submit   |
    |  Softmax  |   | (starter  |   |  to Free  |
    |  Account  |   |  policy)  |   |   Play    |
    +-----------+   +-----------+   +-----------+
                          |               |
                          v               v
                   +-------------+  +-----------+
                   | Run Locally |  | Dashboard |
                   | (scrimmage) |  | (scores,  |
                   +-------------+  |  replays) |
                          |         +-----------+
                          v               |
                   +-------------+        |
                   |  Improve    |<-------+  <-- you review scores
                   |  Policy     |           & guide the agent
                   +-------------+
                          |
                          v
                   +-------------+
                   |  Re-submit  |
                   +-------------+
                          |
                          +-------> repeat
```

## Step-by-Step

### 1. Bootstrap

The user points their coding agent at `play.md`. The agent:

1. **Signs up** for a Softmax CogGames account (free tier)
2. **Forks** the starter policy repo on GitHub
3. **Clones** the fork locally
4. **Runs a first scrimmage** to verify everything works

```
Agent: "I've forked softmax/starter-policy to your-name/starter-policy,
        cloned it, and ran a local scrimmage. Score: 12.4 avg reward."
```

### 2. First Submission

The agent submits the unmodified starter policy to free play:

```bash
cogames upload -p class=cvc.table_policy.TablePolicy \
  -n my-first-policy -f cvc --season free-play
```

Within minutes, the dashboard shows your policy playing against others. You can watch replays and see stats.

### 3. The Coaching Loop

This is the core of `/coach.improve`. Each iteration:

```
  +-----------------------------------------------------+
  |                                                     |
  |  +-----------+    +----------+    +------------+    |
  |  |  1. Play  |--->| 2. Analyze|-->| 3. Improve |    |
  |  | scrimmage |    | signals  |    | one program|    |
  |  +-----------+    +----------+    +------------+    |
  |                                         |           |
  |  +-----------+    +----------+          |           |
  |  | 5. Submit |--->| 6. Wait  |<---------+           |
  |  | to tourney|    | & check  |    4. Test locally   |
  |  +-----------+    +----------+                      |
  |       |                                             |
  |       +---------------------------------------------+
  |                      repeat
  +-----------------------------------------------------+
```

**1. Play** -- Run a local scrimmage against the current policy.

**2. Analyze** -- PCO (Proximal Coglet Optimizer) evaluates the game:
- `ResourceLoss` -- how efficiently were resources gathered?
- `JunctionLoss` -- were junctions aligned or lost?
- `SurvivalLoss` -- did agents survive or die too often?

**3. Improve** -- The LLM learner proposes a patch to one program in the table:
- Python functions (fast actions: mine, retreat, heal)
- Prompts (strategic analysis)
- Observation programs (what the learner sees)

**4. Test locally** -- Run another scrimmage with the patched policy. If score drops, revert.

**5. Submit** -- Upload to tournament. Commit and push to the feature branch.

**6. Wait & check** -- Next session picks up tournament results and decides whether to keep or revert.

### 4. User in the Loop

The user's role is **coach of the coach**:

- **Watch replays** on the Softmax dashboard -- see your agents mining, fighting, aligning junctions
- **Review scores** -- the dashboard shows rank, win rate, per-game stats
- **Guide the agent** -- tell it what to focus on:
  > "Our miners die too much. Focus on retreat logic."
  > "We're losing junctions in the late game. Try more scramblers after step 5000."
  > "Don't touch the mining code, it's working well. Focus on alignment."
- **Read coaching logs** -- `.coach/sessions/` has detailed logs of what the agent tried and why

### 5. What the User Sees

```
Session 1:  Score 12.4 -> 14.1  (+1.7)  improved mine targeting
Session 2:  Score 14.1 -> 13.8  (-0.3)  reverted retreat change
Session 3:  Score 14.1 -> 15.6  (+1.5)  better junction alignment
Session 4:  Score 15.6 -> 16.2  (+0.6)  adaptive pressure budget
  ...
Tournament rank: 12th -> 8th -> 5th
```

## Architecture Stack

```
  YOU
   |  natural language guidance
   v
  Coach (Coding Agent session -- not a Coglet)
   |  reads/writes code, runs CLI commands
   v
  PlayerCoglet (GitLet COG -- manages policy across games)
   |  git commits, patches
   v
  PolicyCoglet (ProgLet -- program table + LLM brain)
   |  per-agent heuristic + periodic LLM analysis
   v
  CogletBrainAgentPolicy (per-agent: fast heuristic + slow LLM)
```

The **Coach** is a coding agent session. It's the outermost loop -- it decides *what* to change, *when* to submit, and *whether* to keep or revert.

The **PolicyCoglet** is what actually runs in the tournament. It has a **program table** with evolvable programs:

| Surface | Speed | Examples |
|---------|-------|---------|
| Python functions | Fast (every step) | `step`, `mine`, `retreat`, `heal`, `align`, `scramble` |
| Prompts | Slow (periodic LLM) | `analyze` (strategic reasoning) |
| Observation programs | Medium | `summarize`, `macro` (what the LLM sees) |

## File Layout

```
.coach/
  state.json          # best score, session count, program table snapshot
  todos.md            # improvement backlog
  sessions/
    20260330-140000/
      plan.md         # what this session tries and why
      log.md          # timestamped log of actions and results
      diff.patch      # code diff
      results.json    # local + tournament scores
      programs.json   # program table state after session

cogames/cvc/
  programs.py         # seed program table (evolvable programs)
  table_policy.py     # TablePolicy (runs programs in tournament)
  pco_runner.py       # PCO epoch orchestration
  learner.py          # LLM-based program evolution
  critic.py           # game experience evaluation
  losses.py           # ResourceLoss, JunctionLoss, SurvivalLoss
  constraints.py      # SyntaxConstraint, SafetyConstraint
```

## Getting Started

```
1. Open your coding agent
2. Tell it: "Read http://softmax.com/play.md"
3. Watch it set up everything
4. Say: "/coach" to start the automated improvement loop
5. Watch scores, review replays, guide your agent
```
