# Coach TODO

## Current Priorities
- [ ] Close the 4x gap to alpha.0 (1.65 local avg vs 14.66 top)
- [ ] Reduce score variance (0.49-4.62 across seeds)
- [ ] Fix alignment network expansion — only 1-2 alignable junctions per seed
- [ ] Fix late-game collapse — agents stuck with 0 hearts, 0 resources
- [ ] Fix resource imbalance — germanium chronically starved

## Improvement Ideas
- [ ] Remove or relax `within_alignment_network` check — it may not be required by game mechanics
- [ ] Reduce scrambler count early game — scramblers useless before enemy junctions exist
- [ ] Agent-specific resource bias fix — miners biased to carbon/oxygen, no germanium miner
- [ ] Better heart cycling — aligners spend too long acquiring hearts vs aligning
- [ ] Hub proximity penalty too harsh — punishes junctions >25 cells that might be alignable
- [ ] Junction network expansion strategy — build connected chains from hub outward
- [ ] Investigate why only 24-26 of 65 junctions discovered — need broader exploration

## Dead Ends (Don't Retry)
- [x] Retreat threshold tuning — always trades deaths for score regression
- [x] Pressure budget changes (aligner/scrambler counts for 8-agent) — 4a/1s at step 300 is optimal
- [x] Heart batch target changes — 3 for aligners is the sweet spot
- [x] Outer explore ring at manhattan 35 — sends agents too far, they die

## Done
- [x] Establish baseline: 1.31 on machina_1 (seed 42)
- [x] Remove LLM resource herding: 1.31 → 1.72
- [x] Full ProgLet policy (GameState wraps engine): 1.76
- [x] PCO pipeline validated (learner proposes patches)
- [x] Session 5: tested retreat/budget/heart tuning — no improvement found
- [x] Session 6: fixed 4-agent role allocation (0.00 → ~0.95), submitted v13
- [x] Session 7: fixed coglet imports for tournament bundle, limited emergency mining (0.59 → 0.95 local, v14=3.05 tournament)
- [x] Session 8: shared junction memory + wider exploration (0.95 → 1.65 local avg, v16 submitted)
