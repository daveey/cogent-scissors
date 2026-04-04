# Test In Progress: 20260404-012-delta

**Status**: Testing across seeds 42-46
**Started**: 2026-04-04 00:15 UTC
**Output**: test_results_012_delta.txt

## Change

**Focus**: Scrambler corner_pressure divisor adjustment

**File**: `src/cogamer/cvc/agent/scoring.py` - line 143

**Description**: 
Adjusted scrambler `corner_pressure` divisor from 8.0 to 7.0 (~14% increase). This makes distant enemy junctions moderately more attractive to scramblers for better disruption of expanding opponents in 4-team format.

**Hypothesis**: In four_score with 4 corner teams, current divisor 8.0 may slightly under-weight distant disruption. Conservative 8.0→7.0 adjustment could improve enemy expansion blocking.

## Baseline

Current baseline: **9.74 avg per cog** (from attempt 007: early scrambler activation)
- Seeds 42-46: 9.37, 11.44, 19.86, 2.64, 5.38

## Results

**Seed 42**: 5.42 per cog (baseline: 9.37) → **-42.2% regression**
**Seed 43**: Running...
**Seeds 44-46**: Pending

**Early indication**: Major regression on seed 42. Increased corner_pressure may be over-incentivizing distant scramblers, hurting local defense.
