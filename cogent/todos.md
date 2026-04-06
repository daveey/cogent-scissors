# scissors — Improvement TODOs

## Recent Wins
- [x] **Cycle 91: Junction AOE 10→20 (+1.5%)** — Alpha.0 parity: wider enemy detection for better survival
- [x] **Cycle 89: Scout HP 30→25 (+5.0%)** — Retreat optimization success (unlike scrambler)
- [x] **Cycle 87: Miner HP 15→12 (+3.2%)** — Continued retreat optimization pattern
- [x] **Cycle 86: Aligner HP 50→45 (+41.2%)** — MAJOR breakthrough! Less conservative retreat = more field time

## Next Candidates
- [ ] Junction scoring parameter tuning: hub penalty curves
- [ ] Explore other non-HP parameters that can be validated locally
- [ ] **BLOCKED:** LLM-dependent changes (cannot validate without LLM access in local tests)

## Dead Ends Confirmed (Recent Testing)
- Expansion bonus 5.0 is optimal (7.0 failed -8.3%)
- Claim penalty 12.0 is optimal (both 8.0 and 25.0 failed)
- Target switch threshold 3.0 is optimal (2.5 failed -10.5% with high variance)
- Hotspot weight 8.0 is optimal (6.0 too marginal +0.4%, likely noise)
- Teammate penalty 6.0 is optimal (4.0 failed -43.3%, major regression)
- Enemy AOE weight 8.0 is optimal (10.0 too marginal +0.6%, likely noise)

## Testing Protocol Issue
**Critical finding:** Local tests run with `ANTHROPIC_API_KEY=` (no LLM) per docs/cogames.md, but tournament uses Bedrock (LLM enabled). Cannot validate LLM-dependent changes locally. Cycle 94 reverted due to this issue.

## Completed
- [x] Enemy AOE weight 8.0→10.0 tested and reverted (+0.6%, too marginal)
- [x] Teammate penalty 6.0→4.0 tested and reverted (-43.3%, major regression)
- [x] Hotspot weight 8.0→6.0 tested and reverted (+0.4%, too marginal)
- [x] Target switch threshold 3.0→2.5 tested and reverted (-10.5%, high variance)
- [x] Claim penalty 12.0→8.0 tested and reverted (-7.3%)
- [x] Expansion bonus weight 5.0→7.0 tested and reverted (-8.3%)
- [x] LLM objective wiring tested and reverted (false positive, testing protocol issue)
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
