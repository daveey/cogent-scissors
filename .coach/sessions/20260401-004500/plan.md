# Session 44 Plan

**Timestamp**: 2026-04-01 00:45:00
**Approach**: IntelligentDesign

## Status
- Tournament: new season stage 1/7, v67+v71 entered
- Freeplay: qualifying, v66+v70 entered

## What to Try
1. ~~Early pressure ramp (step 200 instead of 3000)~~ — reverted, -8.8% self-play
2. Junction memory increase 400→800 — more junction awareness over the game

## Rationale
- Longer junction memory = more targets available for aligners
- In a 10,000 step game, 400-step memory forgets junctions too quickly
- Matches extractor memory pattern (600 steps)
