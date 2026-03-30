# Coach TODO

## Current Priorities
- [ ] Close the 2x gap to alpha.0 (6.18 local avg vs 14.66 top)
- [ ] Reduce score variance (1.63-21.59 across seeds)
- [ ] Fix late-game collapse — agents stuck with 0 hearts, 0 resources
- [ ] Fix resource imbalance — germanium chronically starved
- [ ] Investigate why seed 43 scores 21.59 but others score 1-4 — what's different?

## Improvement Ideas
- [ ] Reduce scrambler count early game — scramblers useless before enemy junctions exist
- [ ] Agent-specific resource bias fix — miners biased to carbon/oxygen, no germanium miner
- [ ] Better heart cycling — aligners spend too long acquiring hearts vs aligning
- [ ] Junction network expansion strategy — build connected chains from hub outward
- [ ] Investigate why only 24-26 of 65 junctions discovered — need broader exploration
- [ ] Tune PressureMixin._pressure_budgets resource thresholds for better economy

## Dead Ends (Don't Retry)
- [x] Retreat threshold tuning — always trades deaths for score regression
- [x] Pressure budget changes (aligner/scrambler counts for 8-agent) — 4a/1s at step 300 is optimal
- [x] Heart batch target changes — 3 for aligners is the sweet spot
- [x] Outer explore ring at manhattan 35 — sends agents too far, they die
- [x] Remove alignment network filter — required by game mechanics (exp A: 0.83 avg)
- [x] Expand alignment range +5 — causes targeting unreachable junctions (exp C: 0.84 avg)
- [x] Remove scramblers entirely — defensive value exists (exp B: 0.99 avg)

## Done
- [x] Establish baseline: 1.31 on machina_1 (seed 42)
- [x] Remove LLM resource herding: 1.31 → 1.72
- [x] Full ProgLet policy (GameState wraps engine): 1.76
- [x] PCO pipeline validated (learner proposes patches)
- [x] Session 5: tested retreat/budget/heart tuning — no improvement found
- [x] Session 6: fixed 4-agent role allocation (0.00 → ~0.95), submitted v13
- [x] Session 7: fixed coglet imports for tournament bundle, limited emergency mining (0.59 → 0.95 local, v14=3.05 tournament)
- [x] Session 8: shared junction memory + wider exploration (0.95 → 1.65 local avg, v16 submitted)
- [x] Session 9: fixed role misassignment from team_summary.members visibility bug (1.65 → 6.18 local avg, v17 submitted)
