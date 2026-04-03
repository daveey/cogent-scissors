# Delta Status Report

**Generated**: 2026-04-03 19:31 UTC

## Current Activity

**Testing attempt 010**: Softer LLM stagnation detection
- **Status**: In progress (seed 42 running, ~7 min in)
- **Test PID**: 1176
- **Started**: 19:23 UTC
- **Expected completion**: ~20:15 UTC (50-75 min total)

## Latest Improvement

**Attempt 007** (validated, current baseline):
- Early scrambler activation (step 100→50)
- **Score**: 9.74 avg per cog (+7.84% over previous)
- Seeds: 9.37, 11.44, 19.86, 2.64, 5.38

## Active Test: 010

**Change**: Enhanced LLM analysis prompt with softer stagnation detection
- Added explicit definitions of Stalled/Oscillating
- Suggestive examples instead of prescriptive rules
- Strong bias toward null (maintain current role)
- Better objective guidance

**Hypothesis**: Failed attempt 002 (-41.6%) was too prescriptive. This gives LLM better context while avoiding role churn.

**Files modified**: `src/cogamer/cvc/programs.py`

## Recent History

- **009-reverted**: Claim duration 30→20 steps → -53.0% (too short, duplication)
- **008-reverted**: Scrambler threat_bonus 10→15 → -17.0% (over-defending)
- **007-validated**: Early scrambler step 100→50 → +7.84% ✓
- **006-reverted**: Network bonus 0.5→1.5 → -64.2% (clustering)
- **005-reverted**: Remove corner pressure → -0.77% (minimal)
- **004-validated**: Hotspot penalty 8→12 → +107.9% ✓
- **003-reverted**: Early pressure 30→15 steps → -6.0% (economy disruption)
- **002-reverted**: LLM prescriptive rules → -41.6% (role churn)

## Top Priorities

1. ✓ Softer LLM stagnation detection (testing now)
2. Teammate role awareness (avoid duplicate aligners)
3. Teammate vibe awareness in targeting
4. Four_score spawn corner adjustments

## System Status

- **Mission**: four_score (4-team multi-directional)
- **Season**: beta-cvc (beta-four-score not available)
- **Auth**: No COGAMES_TOKEN (cannot upload/check leaderboard)
- **Disk**: 79% used (cleared cache earlier)
- **Runtime**: Python 3 + cogames 0.23.1 (globally available)

## Monitoring

Check test progress:
```bash
./check_test.sh
tail -f test_results.txt
```

Tick loop runs every 10 minutes to monitor and update status.
