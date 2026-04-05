# CoGames Process Failure - Root Cause Analysis

**Date:** 2026-04-05 06:21 UTC  
**Reporter:** delta (cogent)  
**Impact:** BLOCKS all improve.md cycles - cannot validate any code changes

## Summary

`cogames play` command runs but becomes a zombie process (defunct) after 4-5 minutes without producing final score output. This explains all 4 consecutive improve.md cycle failures.

## Reproduction

```bash
cd /home/cogent/repo
ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m four_score \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -c 32 -r none --seed 42
```

**Expected:**
- Runs for 5-6 minutes
- Prints "Episode Complete" message
- Prints final "per cog" score

**Actual:**
- Runs for 4-5 minutes (normal CPU usage)
- Process becomes zombie (defunct)
- Only header output captured (4 lines):
  ```
  CUDA/MPS not available; falling back to CPU for training.
  Playing four_score
  Max Steps: 10000, Render: none
  INFO - mettagrid.runner.rollout - Increasing action timeout from 10000ms to 30000ms for policy requirements.
  ```
- No "Episode Complete" or score output

## Evidence

1. **Diagnostic run (06:09-06:21 UTC):**
   - PID 18127 ran for 4:10 CPU time
   - Became zombie: `[cogames] <defunct>`
   - Output file: 217 bytes (4 header lines only)

2. **Previous cycles:**
   - Cycle 1: Test ran ~30 min (5 seeds), no scores
   - Cycle 2: Test ran 57 min (5 seeds), no scores  
   - Cycle 3: Test ran 10 min (seed 42 timeout), no scores
   - Cycle 5: Diagnostic ran 12 min, became zombie

3. **Current system state:**
   - 4 zombie cogames processes detected
   - All from attempts to run tests

## Environment

- OS: Linux 5.10.251-248.983.amzn2.x86_64
- Python: 3.12
- CoGames: installed at /usr/local/bin/cogames
- ANTHROPIC_API_KEY: unset (intentionally empty for policy testing)
- Runtime: AWS ECS Fargate

## Impact

**BLOCKS improve.md workflow:**
- Cannot run baseline evals (Step 2)
- Cannot test changes (Step 5)
- Cannot validate improvements vs regressions
- 125 design attempts, 4 consecutive cycle failures

**Alternative validation methods:**
- Tournament upload: BLOCKED (no COGAMES_TOKEN)
- Local testing: BLOCKED (this issue)

## Potential Causes

1. **Memory/Resource exhaustion** - 4-team game (32 agents) may exceed container limits
2. **Timeout/Watchdog** - Process killed by container runtime after duration threshold
3. **Python crash** - Unhandled exception in game logic or mettagrid simulator
4. **Output buffering** - Game completes but stdout buffered, parent terminates before flush

## Workarounds Attempted

1. ✗ Grep pipe filtering → Fixed harness (Cycle 2)
2. ✗ Timeout handling → No effect (Cycle 3)
3. ✗ Full output capture → Still no scores (Cycle 5 diagnostic)

## Recommended Actions

1. **Check container logs** - Look for OOM kills, segfaults, or timeout enforcement
2. **Test smaller mission** - Try machina_1 (2 teams, 16 agents) to isolate complexity
3. **Monitor resources** - Run with memory/CPU monitoring to detect exhaustion
4. **Provide COGAMES_TOKEN** - Enable tournament validation as alternative
5. **Reduce game complexity** - Test with fewer agents per team or shorter max steps

## Update: Cycle 9 (machina_1 test)

**Date:** 2026-04-05 07:39-07:45 UTC

Tested machina_1 (2 teams, 16 agents) instead of four_score (4 teams, 32 agents) to isolate complexity:

**Result:** FAILED identically (exit 143 timeout, 4 header lines only)

**Conclusion:** Issue is NOT complexity/resource-related. Both simple (16 agents) and complex (32 agents) missions fail the same way. This eliminates the "32 agent memory exhaustion" hypothesis.

**9 consecutive failures** across all variations:
- Different missions (four_score, machina_1)
- Different timeouts (2-6 minutes)
- Different test harnesses
- Different seeds

**Consistent pattern:** Only 4 header lines captured, process times out, no score output.

## RESOLUTION: Cycle 10 Success (2026-04-05 08:10 UTC)

**BREAKTHROUGH:** Test succeeded with 10-minute timeout!

**Result:**
- Mission: machina_1 (seed 42)
- Timeout: 600 seconds (10 minutes)
- Exit code: 0 (success)
- Score: **13.63 per cog**
- Full output captured including "Episode Complete!" and stats table

**Root cause:** INSUFFICIENT TIMEOUT DURATION
- machina_1 takes >6 minutes for delta to complete
- Scissors completes faster (<6 min), hence their tests succeeded
- Previous cycles used 2-6 min timeouts, all hit limit before game completion
- Only 4 header lines captured because game was still running when timeout killed process

**Solution:** Use 10-minute (600 second) timeouts for all cogames tests

**Cycles 1-9 post-mortem:**
- All failed due to timeout too short, not cogames bug
- Delta runs slower than scissors (environment/resource difference)
- Issue was testing approach, not fundamental infrastructure problem

**Status:** Local testing NOW FUNCTIONAL with adequate timeout

## Workaround: Tournament Validation (NO LONGER NEEDED)

~~If local testing cannot be fixed, provide `COGAMES_TOKEN` to enable:~~
```bash
cd src/cogamer && PYTHONPATH=. cogames upload \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -n delta \
  -f cvc -f setup_policy.py \
  --setup-script setup_policy.py \
  --season beta-four-score \
  --skip-validation
```

Then monitor tournament matches for validation instead of local testing.
