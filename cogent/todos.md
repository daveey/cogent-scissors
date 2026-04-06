# scissors — Improvement TODOs

## Recent Wins
- [x] **Cycle 89: Scout HP 30→25 (+5.0%)** — Retreat optimization success (unlike scrambler)
- [x] **Cycle 87: Miner HP 15→12 (+3.2%)** — Continued retreat optimization pattern
- [x] **Cycle 86: Aligner HP 50→45 (+41.2%)** — MAJOR breakthrough! Less conservative retreat = more field time

## Next Candidates
- [ ] Late-game HP threshold modifiers: test increasing modifiers (+10-15 currently)
- [ ] LLM stagnation detection: detect stuck agents and adjust directives
- [ ] Read teammate vibes for coordination
- [ ] Explore non-HP parameters: RETREAT_MARGIN, junction distances, etc.

## Completed
- [x] Hotspot tracking implemented
- [x] Wider enemy AOE for retreat (_NEAR_ENEMY_RADIUS=20)
- [x] RETREAT_MARGIN 15→20 tested and reverted
- [x] Aligner HP threshold optimization
- [x] Miner HP threshold optimization
- [x] Scrambler HP threshold 30→25 tested and reverted
- [x] Scout HP threshold optimization
