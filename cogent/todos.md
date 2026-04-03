# gamma — Improvement TODOs

## Completed
- [x] (ID) Wider enemy AOE for retreat: wired _near_enemy_territory (radius 20) into _should_retreat — +458% avg score
- [x] (20260403-001) LLM objective feature: wired up expand/defend/economy_bootstrap objectives to pressure budgets — was broken, now functional
- [x] (20260403-001) Documentation: added four_score.md, updated all docs for multi-team format
- [x] (20260403-004) Hotspot penalty increase: 8→12 base, 5→6 mid → +107.9% on seed 42 (6.03→12.54). Agents avoid contested far junctions in 4-team format.
- [x] (20260403-007) Early scrambler activation: step 100→50 → +7.84% avg (9.03→9.74). Earlier disruption against 3 opponents in 4-team, maintains 50-step resource bootstrap.

## Failed Attempts
- [x] (20260403-002-REVERTED) LLM stagnation: prescriptive role-change rules → -41.6% regression. Too aggressive switching disrupted stability.
- [x] (20260403-003-REVERTED) Early pressure ramp: 30→15 steps → -5.97% regression. Too early, disrupted resource bootstrapping.
- [x] (20260403-005-REVERTED) Defensive scrambling: removed corner_pressure bonus → -0.77% regression. Minimal impact, offensive push may help in 4-team.
- [x] (20260403-006-REVERTED) Network bonus increase: 0.5→1.5 (3×) → -64.2% regression. Too aggressive clustering, agents failed to expand.

## Candidates
- [ ] LLM stagnation detection: SOFTER approach needed - maybe increase role-change threshold or add cooldown between switches
- [ ] Read teammate vibes for coordination
- [ ] Four_score specific tuning: corner spawns, multi-directional expansion, higher junction churn
- [ ] Test mixed-policy matches (vs alpha.0, corgy) to validate competitive performance
- [ ] Analyze why stalled detection triggers: is threshold too sensitive? Are agents frequently stalling legitimately?
