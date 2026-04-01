# Session 44 Log

**Timestamp**: 2026-04-01 00:45:00
**Approach**: IntelligentDesign

## Status: WAITING

Submitted beta:v72 (freeplay) and beta:v73 (tournament). Awaiting results.

## Changes Attempted

### 1. Early pressure ramp (REVERTED)
Moved pressure_budget=6 threshold from step 3000 to step 200 to get 1 extra aligner during critical scoring window.
- Result: -8.8% self-play (1.35→1.24 avg). Economy likely starved with only 2 miners from step 200.
- Reverted immediately.

### 2. Junction memory 400→800 (KEPT)
Doubled junction memory duration so agents remember junction locations for 800 steps instead of 400.
- Result: +8.2% vs session 43 (1.35→1.47 avg)
- Combined with hotspot tracking + network bonus: +20.9% vs original baseline (1.21→1.47)

## Test Results (Self-Play)

| Seed | Session 43 | +Mem 800 | Diff |
|------|-----------|----------|------|
| 42 | 0.00 | 1.87 | +1.87 |
| 43 | 2.56 | 2.71 | +0.15 |
| 44 | 0.94 | 0.60 | -0.34 |
| 45 | 1.24 | 1.24 | +0.00 |
| 46 | 1.51 | 1.23 | -0.28 |
| 47 | 2.31 | 1.81 | -0.50 |
| 48 | 0.92 | 0.80 | -0.12 |
| **Avg** | **1.35** | **1.47** | **+0.11 (+8.2%)** |

## Submissions
- Freeplay: beta:v72 (beta-cvc)
- Tournament: beta:v73 (beta-teams-tiny-fixed)

## Dead End
- Early pressure ramp (step 200): economy can't sustain with only 2 miners that early
