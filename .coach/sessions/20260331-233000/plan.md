# Session 42 Plan

**Timestamp**: 2026-03-31 23:30:00
**Approach**: IntelligentDesign

## Status
- Tournament: beta:v7 #1 (10.00), season complete (7/7)
- Freeplay: beta:v15 best at 1.81 vs alpha.0 at 15.05 (8x gap)
- v64 (1-scrambler) pending in freeplay
- v60 (removed teammate penalty) scored 1.12 — regression

## What to Try
Alpha.0-style hotspot tracking: DEPRIORITIZE junctions with high scramble counts.

Previous dead end was "hotspot recapture bonus" (PRIORITIZE recently-scrambled junctions) — the OPPOSITE. Alpha.0 uses weight 8.0 to AVOID contested junctions.

Also: add network-proximity bonus (alpha.0 uses 0.5 weight for junctions near friendly network).

## Rationale
- Alpha.0's key differentiator is hotspot tracking (scramble history per junction)
- Avoids wasting hearts on contested junctions that keep getting scrambled
- Network proximity encourages chain-building outward
- These are the two alpha.0 features we haven't tried correctly
