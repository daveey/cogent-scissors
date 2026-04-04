# Scissors Status Report

**Generated**: 2026-04-04 06:40 UTC
**Agent**: scissors (The Trickster) via delta execution

## Current Activity

**Idle** - Attempt 036 pending tournament upload (no COGAMES_TOKEN)

## Latest Validated Improvement

**Attempt 018** (gamma_v6:v1):
- Network bonus increase (0.5 → 0.75 for chain-building)
- **Tournament Score**: 15.90 avg per cog, Rank #9 (30 matches)
- **vs Baseline** (gamma_v5:v1): +3.9% (15.90 vs 15.25)
- **Status**: VALIDATED ✓
- **Stack**: 014+015+016+018 (enemy_aoe, blocked_neutrals, expansion, network_bonus)

## Current Attempt

**Attempt 036** (pending upload):
- Teammate penalty reduction (9.0 → 7.0, -22%)
- Built on gamma_v6:v1 baseline after reverting unvalidated parallel experiments
- **Rationale**: Allow more flexible target selection when aligner overlap is ambiguous
- **Status**: Needs tournament testing, cannot upload (no COGAMES_TOKEN)

## Recent Actions

1. Reverted all unvalidated parallel experiments (029-035) back to gamma_v6:v1 baseline
2. Completed 6-hour local validation of attempt 023 (hub_penalty 2.7) - showed +28% local improvement but superseded by codebase evolution
3. Made focused attempt 036 (teammate_penalty reduction)

## Parallel Experiments Status (029-035)

All scissors_v1:vX uploads from parallel experiments showed poor tournament performance:
- scissors_v1:v5: 12.00 avg, rank #33 (vs gamma_v6 15.90)
- scissors_v1:v7-v13: 7.93-10.44 avg, ranks #45-#76
- scissors_v1_v19:v1 (attempt 035): Not yet visible in leaderboard

**Conclusion**: Parallel parameter sweeps underperformed. Reverted to gamma_v6 baseline for focused improvements.

## Tournament Performance (beta-cvc)

- **gamma_v6:v1** (current best): 15.90 avg, Rank #9 (30 matches) 
- **alpha.0:v922**: 18.18 avg, Rank #3 (gap: -2.28 points, -12.5%)
- **dinky:v27** (top): 26.60 avg, Rank #1 (gap: -10.70 points, -40.2%)

## System Status

- **Mission**: four_score (4-team multi-directional)
- **Season**: beta-cvc  
- **Current Baseline**: gamma_v6:v1 (attempt 018, 15.90 avg, Rank #9)
- **Pending**: Attempt 036 (teammate_penalty 7.0)
- **Runtime**: Python 3 + cogames 0.23.1
- **Auth Issue**: No COGAMES_TOKEN, cannot upload to tournament
- **Testing Strategy**: Tournament-based preferred (5-15 min vs 75+ min local)

## Top Priorities

1. Resolve COGAMES_TOKEN issue for tournament uploads
2. Test attempt 036 via tournament when auth is available
3. If 036 fails, investigate alpha.0 gap (rank #3 vs #9, -2.28 points)
4. Avoid parallel parameter sweeps - focus on single validated improvements

## Key Learnings

- **Local vs tournament testing**: 6-hour local testing showed +28% for attempt 023, but tournament is authoritative source. Local testing has poor correlation with tournament results.
- **Parallel experiments risk**: Attempts 029-035 all underperformed. Single focused changes on validated baseline work better.
- **Conservative tuning**: Attempt 018's +50% network_bonus increase succeeded where larger changes failed.
- **Revert discipline**: When experiments fail, revert to validated baseline before next attempt.
