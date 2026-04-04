# scissors — Improvement TODOs

## In Progress
- [ ] (20260404-021) Hotspot weight reduction: 12.0→11.0 (-8%) with improved enemy_aoe avoidance. Uploaded as scissors_v1:v4, awaiting tournament validation.
- [ ] (20260404-020) Teammate penalty increase: 9.0→10.0 (+11%) for even better multi-agent coordination. Uploaded as scissors_v1:v3, awaiting tournament validation.
- [ ] (20260403-019) Hub penalty reduction: 8.0→6.0 (-25%) for far junctions (>25 distance) to encourage center-map control in four_score. Uploaded as scissors_v1:v2, awaiting tournament validation.

## Current Status (20260403 23:35 UTC)
**Tournament Rankings (beta-cvc):**
- 🏆 gamma_v5:v1: rank #10, 15.33 avg (8 matches) - **TOP 10!**
  - Stack: 014 (enemy_aoe 10.0) + 015 (blocked_neutrals 8.0) + 016 (expansion 6.0)
- gamma_v3:v1: rank #32, 11.78 avg (21 matches)
  - Stack: 014 + 015 (validated baseline: +51.8%)
- gamma_scissors:v1: in qualifying (improvement 017)
- Baseline gamma:v1: rank #67, 7.45 avg

**Progress:** +106% improvement from baseline (7.45 → 15.33)

## Completed (Design Approach: 6 validated improvements)
- [x] (004) Hotspot penalty increase: 8→12 base - avoid contested far junctions
- [x] (007) Early scrambler: step 100→50 - earlier disruption vs 3 opponents
- [x] (011) Teammate penalty: 6.0→9.0 - better multi-agent coordination
- [x] (014) Enemy AOE penalty: 8.0→10.0 - avoid contested territory
- [x] (015) Scrambler blocked_neutrals: 6.0→8.0 - prioritize expansion-blocking
- [x] (016) Expansion bonus: 5.0→6.0 - aggressive safe territory expansion
- [x] (017) Corner exploration: fixed OOB offsets - 100% valid exploration

## Candidates
- [ ] Test gamma_scissors:v1 performance once qualifying completes
- [ ] Analyze gamma_v5:v1 match replays for further optimization opportunities
- [ ] Consider stacking corner exploration (017) with expansion stack (014+015+016)
- [ ] Investigate claim duration tuning for far junctions (>30 distance)
- [ ] Read teammate vibes for better coordination
- [ ] Test mixed-policy matches vs alpha.0, dinky, slanky

## Failed Attempts
- [x] (002) LLM prescriptive role-change: -41.6%
- [x] (003) Early pressure ramp (30→15): -5.97%
- [x] (005) Defensive scrambler (remove corner_pressure): -0.77%
- [x] (006) Network bonus 3×: -64.2%
- [x] (008) Scrambler threat_bonus 15.0: -17.04%
- [x] (009) Claim duration 30→20: -53.0%
- [x] (010) Mid-game pressure ramp (3000→2000): -47.13%
- [x] (012) LLM teammate role awareness: +3.8% avg but 40% catastrophic failure
- [x] (010-llm-softer) Softer LLM stagnation: -39.4%
- [x] (017) Corner-safe exploration (22→15 offsets): -62.8%
- [x] (018) Network bonus +50% (0.5→0.75): -20%

## Strategy
- **Tournament-based validation** works well - continue using beta-cvc for fast feedback
- **Conservative incremental changes** succeed; aggressive tuning fails
- **Synergistic improvements** (014+015, 016) compound better than isolated changes
- **LLM role suggestions fundamentally flawed** - avoid this approach
- **Expansion vs defense balance critical** - over-indexing either way regresses

## Next Session
- Monitor gamma_scissors:v1 qualifying/match results
- If 017 validates, consider combining with 016 for ultimate stack
- Target: break into top 5 (currently #10)
