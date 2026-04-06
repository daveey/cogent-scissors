# scissors — Improvement TODOs

## Recent Wins
- [x] **Cycle 91: Junction AOE 10→20 (+1.5%)** — Alpha.0 parity: wider enemy detection for better survival
- [x] **Cycle 89: Scout HP 30→25 (+5.0%)** — Retreat optimization success (unlike scrambler)
- [x] **Cycle 87: Miner HP 15→12 (+3.2%)** — Continued retreat optimization pattern
- [x] **Cycle 86: Aligner HP 50→45 (+41.2%)** — MAJOR breakthrough! Less conservative retreat = more field time

## Next Candidates
- [ ] Expansion bonus weight: increase from 5.0 to 7.0 to encourage better map coverage
- [ ] Junction scoring parameter tuning: hub penalty, network bonus, teammate penalty  
- [ ] Explore non-HP parameters that can be validated locally
- [ ] **BLOCKED:** LLM-dependent changes (cannot validate without LLM access in local tests)

## Testing Protocol Issue
**Critical finding:** Local tests run with `ANTHROPIC_API_KEY=` (no LLM) per docs/cogames.md, but tournament uses Bedrock (LLM enabled). Cannot validate LLM-dependent changes locally. Cycle 94 reverted due to this issue.

## Completed
- [x] Hotspot tracking implemented
- [x] Wider enemy AOE for retreat (JUNCTION_AOE_RANGE 10→20) — IMPROVED!
- [x] RETREAT_MARGIN 15→20 tested and reverted
- [x] Aligner HP threshold optimization
- [x] Miner HP threshold optimization
- [x] Scrambler HP threshold 30→25 tested and reverted
- [x] Scout HP threshold optimization
- [x] LLM stagnation detection enhancement tested and reverted
- [x] Network bonus weight 0.5→1.0 tested and reverted
- [x] Late-game HP modifiers reduction tested and reverted
