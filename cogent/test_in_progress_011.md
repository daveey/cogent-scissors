# Test In Progress: 20260403-011

**Status**: Testing across seeds 42-46
**Started**: 2026-04-03 21:45 UTC
**PID**: 2246
**Output**: test_results_011.txt

## Change

**Focus**: RETREAT_MARGIN parameter adjustment

**File**: `src/cogamer/cvc/agent/budgets.py` - line 15

**Description**: 
Increased `_RETREAT_MARGIN` from 15 to 20 to match alpha.0's more conservative retreat threshold. This makes agents retreat to hub earlier when HP is low, potentially improving survival rates.

**Hypothesis**: Alpha.0 uses RETREAT_MARGIN = 20, we use 15. More conservative retreat could reduce agent deaths and improve overall performance. Simple parameter change, well-tested by alpha.0.

## Baseline

Current baseline: **9.74 avg per cog** (from attempt 007: early scrambler activation)
- Seeds 42-46: 9.37, 11.44, 19.86, 2.64, 5.38

## Results

(Pending - check test_results_011.txt when PID 2246 completes)

Expected completion: ~60-75 minutes (12-15 min/seed × 5 seeds)

## Monitoring

Check test status:
```bash
./check_test_011.sh
tail -f test_results_011.txt
```
