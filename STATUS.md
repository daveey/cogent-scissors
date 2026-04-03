# Delta Status Report

**Generated**: 2026-04-03 21:42 UTC

## Current Activity

**Testing attempt 011**: RETREAT_MARGIN 15→20 (match alpha.0)
- **Status**: In progress (seed 42 started 21:45 UTC)
- **Test PID**: 2246
- **Expected completion**: ~22:50 UTC (60-75 min)

## Latest Improvement

**Attempt 007** (validated, current baseline):
- Early scrambler activation (step 100→50)
- **Score**: 9.74 avg per cog (+7.84% over previous)
- Seeds: 9.37, 11.44, 19.86, 2.64, 5.38

## Most Recent Test: 010-llm-softer (REVERTED)

**Change**: Enhanced LLM analysis prompt with softer stagnation detection
- Added explicit definitions of Stalled/Oscillating
- Suggestive examples instead of prescriptive rules
- Strong bias toward null (maintain current role)

**Result**: **MAJOR REGRESSION** -39.4% (5.91 vs 9.74 baseline)
- Seeds: 6.03, 7.48, 5.98, 4.71, 5.33

**Analysis**: Both prescriptive (002: -41.6%) and suggestive (010: -39.4%) LLM role guidance approaches fail with similar magnitude. The problem is not phrasing but the mechanism itself. **LLM-driven role changes marked as ABANDONED** - neither approach works.

## Recent History

- **010-llm-softer-reverted**: Softer LLM stagnation → -39.4% (verbose guidance no better)
- **012-reverted**: Nearby teammate LLM → +3.8% but 40% catastrophic failure rate
- **010-reverted**: Mid-game pressure 3000→2000 → -47.1% (premature resource burn)
- **009-reverted**: Claim duration 30→20 steps → -53.0% (too short, duplication)
- **008-reverted**: Scrambler threat_bonus 10→15 → -17.0% (over-defending)
- **007-validated**: Early scrambler step 100→50 → +7.84% ✓
- **006-reverted**: Network bonus 0.5→1.5 → -64.2% (clustering)
- **005-reverted**: Remove corner pressure → -0.77% (minimal)
- **004-validated**: Hotspot penalty 8→12 → +107.9% ✓
- **003-reverted**: Early pressure 30→15 steps → -6.0% (economy disruption)
- **002-reverted**: LLM prescriptive rules → -41.6% (role churn)

## Top Priorities

1. ~~Softer LLM stagnation detection~~ **ABANDONED** (tested, failed)
2. Teammate role awareness (avoid duplicate aligners) - non-LLM approach
3. Teammate vibe awareness in targeting
4. Four_score spawn corner adjustments
5. Analyze parameter differences vs alpha.0 reference

## System Status

- **Mission**: four_score (4-team multi-directional)
- **Season**: beta-cvc (beta-four-score not available)
- **Auth**: No COGAMES_TOKEN (cannot upload/check leaderboard)
- **Baseline**: 9.74 avg per cog (attempt 007)
- **Runtime**: Python 3 + cogames 0.23.1 (globally available)

## Key Learnings

- **LLM role guidance**: Both prescriptive and suggestive approaches fail (-40% range). Mechanism itself appears flawed.
- **Testing speed**: CPU-only testing takes 10-15 min/seed, ~60-75 min for 5-seed validation
- **Pressure timing**: Multiple attempts to adjust pressure ramps have failed. Current timing appears near-optimal.
