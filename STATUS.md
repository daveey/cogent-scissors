# Scissors Status Report

**Generated**: 2026-04-04 07:10 UTC
**Agent**: scissors (The Trickster) via delta execution

## Current Activity

**Idle** - Attempts 036+037+038 stacked, pending tournament upload (no COGAMES_TOKEN)

## Latest Validated Improvement

**Attempt 018** (gamma_v6:v1):
- Network bonus increase (0.5 → 0.75 for chain-building)
- **Tournament Score**: 15.90 avg per cog, Rank #9 (30 matches)
- **vs Baseline** (gamma_v5:v1): +3.9% (15.90 vs 15.25)
- **Status**: VALIDATED ✓
- **Stack**: 014+015+016+018 (enemy_aoe, blocked_neutrals, expansion, network_bonus)

## Pending Attempts (Stacked on gamma_v6:v1)

**Attempt 036** (pending upload):
- Teammate penalty reduction (9.0 → 7.0, -22%)
- Less harsh overlap avoidance when multiple aligners near same junction

**Attempt 037** (pending upload):
- Hotspot weight reduction (12.0 → 11.0, -8%)  
- Makes contested junctions slightly more attractive in high-churn four_score

**Attempt 038** (pending upload):
- Enemy AOE penalty reduction (10.0 → 9.5, -5%)
- Encourages more territorial contestation near enemy junctions

**Unified Theme**: All three changes reduce penalties in aligner target selection, enabling more flexible and aggressive junction targeting without eliminating coordination or safety. Strategy shift from defensive/risk-averse to moderately more aggressive territory contestation.

**Status**: Built on gamma_v6:v1 baseline, needs tournament testing, cannot upload (no COGAMES_TOKEN)

## Tournament Performance (beta-cvc)

- **gamma_v6:v1** (current best): 15.90 avg, Rank #9 (30 matches) 
- **alpha.0:v922**: 18.18 avg, Rank #3 (gap: -2.28 points, -12.5%)
- **dinky:v27** (top): 26.60 avg, Rank #1 (gap: -10.70 points, -40.2%)

## Recent History

1. Reverted unvalidated parallel experiments (029-035) back to gamma_v6:v1 baseline
2. Completed 6-hour local validation of attempt 023 - superseded by evolution
3. Created focused stack 036+037+038 with unified penalty-reduction theme

## Parallel Experiments (029-035) - FAILED

All scissors_v1:vX uploads showed poor tournament performance:
- scissors_v1:v5-v13: 7.93-12.00 avg, ranks #33-#76
- **Conclusion**: Parallel parameter sweeps underperform vs focused improvements

## System Status

- **Mission**: four_score (4-team multi-directional)
- **Season**: beta-cvc  
- **Current Baseline**: gamma_v6:v1 (attempt 018, 15.90 avg, Rank #9)
- **Pending Stack**: Attempts 036+037+038 (penalty reduction theme)
- **Runtime**: Python 3 + cogames 0.23.1
- **Blocking Issue**: No COGAMES_TOKEN, cannot upload to tournament
- **Testing Strategy**: Tournament-based preferred (5-15 min vs 75+ min local CPU)

## Completed Improve Cycles (This Session)

1. **Cycle 1**: Created attempt 036 (teammate_penalty 7.0)
2. **Cycle 2**: Created attempt 037 (hotspot_weight 11.0)  
3. **Cycle 3**: Created attempt 038 (enemy_aoe 9.5)
4. **Status**: All three stacked on gamma_v6:v1, awaiting tournament upload capability

## Analysis: Penalty Reduction Strategy

Current gamma_v6:v1 may be too defensive/risk-averse:
- High teammate penalty (9.0) → agents avoid overlap, potential idle time
- High hotspot penalty (12.0) → agents avoid contested areas, miss valuable targets
- High enemy AOE penalty (10.0) → agents too cautious near enemies, lose territory

Hypothesis: Small penalty reductions across all three dimensions may enable more aggressive expansion without sacrificing coordination. Four_score's 4-team format rewards territorial contestation more than 2-team machina_1.

## Top Priorities

1. **CRITICAL**: Resolve COGAMES_TOKEN issue for tournament uploads
2. Test penalty reduction stack (036+037+038) via tournament
3. If successful (>15.90 avg), continue aggressive tuning toward alpha.0
4. If unsuccessful, revert to gamma_v6:v1 and try different approach (e.g., LLM improvements, retreat margin)

## Key Learnings

- **Local vs tournament**: Local testing has poor correlation, tournament is authoritative
- **Parallel experiments fail**: Focused sequential improvements outperform parameter sweeps
- **Conservative tuning**: Small percentage changes (-5% to -22%) safer than large shifts
- **Thematic stacking**: Multiple aligned changes may compound if they address same strategic gap
- **Four_score dynamics**: 4-team format may reward different risk/aggression profile than 2-team
