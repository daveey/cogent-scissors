# Session 46 Log

**Timestamp**: 2026-04-01 02:00:00
**Approach**: IntelligentDesign

## Status: WAITING

Submitted beta:v80 (freeplay) and beta:v81 (tournament).

## Changes Attempted

### 1. Scrambler batch 2→1 (REVERTED)
Reduced scrambler heart batch target from 2 to 1 so it goes out sooner.
- Result: **-34.1%** regression (1.61→1.06). Two seeds hit 0.00. More aggressive scrambler wastes hearts and disrupts economy.
- Reverted immediately. Dead end confirmed.

### 2. Extractor memory 600→800 (KEPT)
Increased extractor memory to match junction memory (both now 800 steps).
- Result: **+4.1%** (1.61→1.67). No zero seeds. More consistent resource targeting.

## Test Results (Self-Play, extractor mem 800)

| Seed | Previous | +ExtMem | Diff |
|------|----------|---------|------|
| 42 | 2.07 | 1.06 | -1.01 |
| 43 | 2.40 | 2.55 | +0.15 |
| 44 | 0.62 | 0.92 | +0.30 |
| 45 | 2.00 | 1.40 | -0.60 |
| 46 | 1.23 | 1.98 | +0.75 |
| 47 | 1.09 | 2.06 | +0.97 |
| 48 | 1.83 | 1.73 | -0.10 |
| **Avg** | **1.61** | **1.67** | **+0.07 (+4.1%)** |

Cumulative vs original baseline: **+37.9%** (1.21→1.67)

All changes in v80/v81:
1. Hotspot tracking (deprioritize contested junctions)
2. Network proximity bonus (chain-building, weight 0.5)
3. Junction memory 400→800
4. Hub-proximal hotspot discount
5. Extractor memory 600→800

## Submissions
- Freeplay: beta:v80 (beta-cvc)
- Tournament: beta:v81 (beta-teams-tiny-fixed)
