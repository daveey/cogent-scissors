# Session 10 Plan

## Current State
- Best local: 6.18 avg (5 seeds), v17 submitted
- Tournament best: v14 at 3.96 (422 matches), v17 qualifying
- Top: alpha.0 at 14.69
- Gap: ~2.4x to top

## Focus: Investigate high-variance seeds and improve economy

The 13x variance (1.63-21.59) across seeds suggests we're highly dependent on
junction placement RNG. Seed 43 scores 21.59 — if we can make other seeds
perform closer to that, avg would jump dramatically.

Hypothesis: on low-scoring seeds, the hub is far from junctions, so aligners
can't find/reach junctions within the alignment network. The PressureMixin
budget system also uses resource thresholds that may starve aligners when
economy is weak.

Plan:
1. Run scrimmages with verbose logging to understand junction discovery patterns
2. Compare seed 43 (high) vs seed 42 (low) junction layouts
3. Identify the bottleneck causing low seeds to fail
4. Make a targeted fix

## One change rule
Only modify one thing. Test on 3+ seeds before committing.
