# scissors — Improvement TODOs

## In Progress
- [ ] (096) Expansion bonus weight increase (6.0→6.2): scissors:v12 qualifying - stronger expansion incentive (+3%, stacks with 087-095)
- [ ] (095) Emergency resource low threshold increase (1→2): scissors:v11 qualifying - earlier emergency mining (+100%, stacks with 087-094)
- [ ] (094) Scrambler heart batch target increase (2→3): scissors:v10 qualifying - better scrambler persistence (+50%, stacks with 087-093)
- [ ] (093) Junction alignment distance increase (15→16): scissors:v9 qualifying - chain-building reach (+7%, stacks with 087-092)
- [ ] (092) Hub alignment distance increase (25→26): scissors:v8 qualifying - extended hub reach (+4%, stacks with 087-091)
- [ ] (091) Target claim duration increase (30→32): scissors:v7 qualifying - longer claim validity (+7%, stacks with 087-090)
- [ ] (090) Claimed target penalty reduction (12.0→11.5): scissors:v6 qualifying - flexible claim override (-4%, stacks with 087-089)
- [ ] (089) Aligner HP threshold reduction (50→47): scissors:v5 qualifying - safer retreats for valuable role (-6%, stacks with 087+088)
- [ ] (088) Scrambler HP threshold increase (30→33): scissors:v4 qualifying - more aggressive disruption (+10% threshold, stacks with 087)
- [ ] (087) Miner HP threshold increase (15→18): scissors:v3 qualifying - more aggressive resource gathering (+20% threshold)

## Current Status (20260404 UTC)
**Tournament Rankings (beta-cvc):**
- 🏆 gamma_v6:v1: rank #9, 15.84 avg (27 matches) - **TOP 10!**
  - Stack: 014 + 015 + 016 + 018 (network_bonus 0.5→0.75)
- gamma_v5:v1: rank #11, 15.25 avg (30 matches)
  - Stack: 014 + 015 + 016 (previous best)
- gamma_v3:v1: rank #33, 12.02 avg (40 matches)
  - Stack: 014 + 015
- Baseline gamma:v1: rank #73, 7.45 avg (21 matches)

**Progress:** +113% improvement from baseline (7.45 → 15.84)

## Completed (Design Approach: 7 validated improvements)
- [x] (004) Hotspot penalty increase: 8→12 base - avoid contested far junctions
- [x] (007) Early scrambler: step 100→50 - earlier disruption vs 3 opponents
- [x] (011) Teammate penalty: 6.0→9.0 - better multi-agent coordination
- [x] (014) Enemy AOE penalty: 8.0→10.0 - avoid contested territory
- [x] (015) Scrambler blocked_neutrals: 6.0→8.0 - prioritize expansion-blocking
- [x] (016) Expansion bonus: 5.0→6.0 - aggressive safe territory expansion
- [x] (018) Network bonus: 0.5→0.75 - improved chain-building consolidation

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
- [x] (019) Hub penalty reduction (8.0→6.0): -48.6%
- [x] (020) Teammate penalty increase (9.0→10.0): -42.8%
- [x] (021) Hotspot weight base reduction (12.0→11.0): -9.8%
- [x] (022) Hotspot weight mid-tier reduction (6.0→5.5): canceled (built on failed 021)
- [x] (023) Hub penalty mid-tier reduction (3.0→2.7): -29.0%

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
