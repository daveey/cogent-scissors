# scissors — Improvement TODOs

## In Progress
- [ ] (113) Aligner expansion bonus cap increase (36.0→36.5): scissors_v29:v1 qualifying - extreme expansion cases (+1.4%, stacks with 087-112)
- [ ] (112) Aligner hub penalty 10-15 base reduction (2.0→1.96): scissors_v28:v1 qualifying - 10-15 range base penalty (-2%, stacks with 087-111)
- [ ] (111) Aligner hub penalty far-range multiplier reduction (8.0→7.92): scissors_v27:v1 qualifying - far-range multiplier penalty (-1%, stacks with 087-110)
- [ ] (110) Aligner hub penalty far-range base reduction (50.0→49.5): scissors_v26:v1 qualifying - far-range base penalty (-1%, stacks with 087-109)
- [ ] (109) Aligner teammate penalty increase (9.0→9.15): scissors_v25:v1 qualifying - stronger coordination (+2%, stacks with 087-108)
- [ ] (108) Aligner hub penalty 15-25 base reduction (10.0→9.8): scissors_v24:v1 qualifying - 15-25 range base penalty (-2%, stacks with 087-107)
- [ ] (107) Scrambler corner_pressure divisor reduction (8.0→7.8): scissors_v23:v1 qualifying - faster far-enemy pressure growth (-3%, stacks with 087-106)
- [ ] (106) Aligner hub penalty 15-25 range reduction (3.0→2.94): scissors_v22:v1 qualifying - 15-25 range penalty (-2%, stacks with 087-105)
- [ ] (105) Aligner hub penalty mid-range reduction (1.5→1.46): scissors_v21:v1 qualifying - mid-range hub proximity (-3%, stacks with 087-104)
- [ ] (104) Aligner mid-range hotspot weight reduction (6.0→5.8): scissors_v20:v1 qualifying - mid-range contested recapture (-3%, stacks with 087-103)
- [ ] (103) Aligner near-hub hotspot weight reduction (2.0→1.9): scissors_v19:v1 qualifying - stronger near-hub recapture (-5%, stacks with 087-102)
- [ ] (102) Aligner hub penalty reduction (0.3→0.28): scissors_v18:v1 qualifying - tighter hub clustering (-7%, stacks with 087-101)
- [ ] (101) Aligner enemy_aoe penalty weight increase (10.0→10.3): scissors_v17:v1 qualifying - stronger enemy avoidance (+3%, stacks with 087-100)
- [ ] (100) Scrambler corner_pressure cap increase (10.0→10.5): scissors_v16:v1 qualifying - stronger far-enemy disruption (+5%, stacks with 087-099)
- [ ] (099) Scrambler threat_bonus weight increase (10.0→10.3): scissors_v15:v1 qualifying - modest defensive priority (+3%, stacks with 087-098)
- [ ] (098) Scrambler blocked_neutrals weight increase (8.0→8.5): scissors_v14:v1 qualifying - stronger expansion-blocking (+6%, stacks with 087-097)
- [ ] (097) Network bonus weight increase (0.75→0.77): scissors:v13 qualifying - stronger chain-building (+3%, stacks with 087-096)
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
