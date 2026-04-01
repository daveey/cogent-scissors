# Session 42 Log

**Timestamp**: 2026-03-31 23:30:00
**Approach**: IntelligentDesign

## Status: WAITING

Submitted beta:v66 (freeplay) and beta:v67 (tournament). Awaiting freeplay results.

## Analysis
- Tournament: beta:v7 rank #1 (10.00), season complete (7/7 stages)
- Freeplay: beta:v15 best at 1.81, alpha.0:v716 at 15.05 (8x gap)
- v64 (1-scrambler) submitted to freeplay, no results yet
- v60 (removed teammate penalty) scored 1.12 — regression confirmed
- SDK constants verified: JUNCTION_ALIGN_DISTANCE=15, JUNCTION_AOE_RANGE=10

## Change
Implemented alpha.0-style hotspot tracking (DEPRIORITIZE contested junctions).

Three files modified:
1. **junctions.py**: Track scramble events in `_update_junctions()` — when a junction transitions from friendly to non-friendly, increment hotspot counter
2. **helpers/targeting.py**: Add `hotspot_penalty = min(hotspot_count, 3) * 8.0` to `aligner_target_score()` (matches alpha.0's weight of 8.0, capped at 3 scrambles)
3. **targeting.py**: Wire up actual `self._hotspots.get(entity.position, 0)` in `_nearest_alignable_neutral_junction()` instead of hardcoded 0

Rationale:
- Previous dead end "hotspot recapture bonus" was the OPPOSITE (prioritize contested junctions)
- Alpha.0 DEPRIORITIZES contested junctions with weight 8.0 — avoiding wasting hearts on junctions that keep getting scrambled
- This is a key differentiator between alpha.0 (freeplay 15.05) and beta (freeplay 1.81)

## Test Results (Self-Play, same seeds, same run)

| Seed | Baseline | Hotspot | Diff |
|------|----------|---------|------|
| 42 | 2.07 | 2.31 | +0.24 |
| 43 | 2.46 | 2.53 | +0.07 |
| 44 | 0.00 | 0.91 | +0.91 |
| 45 | 1.53 | 1.53 | +0.00 |
| 46 | 0.00 | 1.78 | +1.78 |
| **Avg** | **1.21** | **1.81** | **+0.60 (+49.5%)** |

Notable: seeds 44 and 46 went from 0.00 to 0.91/1.78 — hotspot avoidance prevents wasting hearts on contested junctions, helping agents recover from junction collapse.

## Submissions
- Freeplay: beta:v66 (beta-cvc)
- Tournament: beta:v67 (beta-teams-tiny-fixed)
