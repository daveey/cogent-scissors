# Scissors Tournament Uploads

Scissors branch uploads (independent of delta's stack):

## scissors_v1_v21:v1 (Attempt 039)
- **Uploaded**: 2026-04-04T06:33:58Z
- **Change**: Network bonus cap 4→5 (+25% max bonus: 3.0→3.75)
- **Base**: gamma_v6:v1 (e073b3e)
- **Status**: Awaiting tournament results (need 20+ matches)

## scissors_v1_v22:v1 (Attempt 040 - scissors variant)
- **Uploaded**: 2026-04-04T06:43:55Z
- **Change**: Expansion weight 6.0→6.25 (+4%)
- **Base**: Delta's 036-038 stack (teammate 7.0, hotspot 11.0, enemy_aoe 9.5)
- **Status**: Awaiting tournament results (need 20+ matches)
- **Note**: Conflicts with delta's 040 (claimed penalty). Both test different improvements.

Delta's 036-040 are committed but not uploaded (no COGAMES_TOKEN).

## scissors_v1_v23:v1 (Attempt 041)
- **Uploaded**: 2026-04-04T06:46:50Z
- **Change**: Scrambler blocked_neutrals weight 8.0→8.4 (+5%)
- **Base**: Delta's 036-038 stack
- **Status**: Awaiting tournament results (need 20+ matches)
- **Rationale**: Builds on attempt 015's success (6.0→8.0). Stronger scrambler targeting for expansion blocking.

## scissors_v1_v24:v1 (Attempt 042)
- **Uploaded**: 2026-04-04T06:50:06Z
- **Change**: Network bonus weight 0.75→0.8 (+7%)
- **Base**: Delta's 036-038 stack + scissors 041
- **Status**: Awaiting tournament results (need 20+ matches)
- **Rationale**: Builds on attempt 018's success (0.5→0.75, +3.9%). Strengthens chain-building.

## scissors_v1_v25:v1 (Attempt 043)
- **Uploaded**: 2026-04-04T06:52:25Z
- **Change**: Scrambler threat_bonus 10.0→10.5 (+5%)
- **Base**: Delta's 036-038 + scissors 039-042
- **Status**: Awaiting tournament results (need 20+ matches)
- **Rationale**: Conservative increase vs attempt 008's failed +50%. Defends consolidated networks.

## scissors_v1_v26:v1 (Attempt 044)
- **Uploaded**: 2026-04-04T07:04:19Z
- **Change**: Near-hub penalty 0.3→0.28 (-7%)
- **Base**: Delta's 036-038 + scissors 039-043
- **Status**: Awaiting tournament results (need 20+ matches)
- **Rationale**: Near-hub zone safest. Far/mid hub penalty reductions failed badly (019: -48.6%, 023: -29%).

## scissors_v1_v27:v1 (Attempt 045)
- **Uploaded**: 2026-04-04T07:07:35Z
- **Change**: Near-hub hotspot weight 2.0→1.9 (-5%)
- **Base**: Delta's 036-038 + scissors 039-044
- **Status**: Awaiting tournament results (need 20+ matches)
- **Rationale**: Completes near-hub optimization with 044. Encourages aggressive near-hub recapture despite contest.

## scissors_v1_v28:v1 (Attempt 046)
- **Uploaded**: 2026-04-04T07:11:17Z
- **Change**: Mid-range hotspot weight 6.0→5.8 (-3.3%)
- **Base**: Delta's 036-038 + scissors 039-045
- **Status**: Awaiting tournament results (need 20+ matches)
- **Rationale**: Extends hotspot optimization from near-hub (045) to mid-range (10-15 distance). More conservative than canceled 022 (-8.3%).

## scissors_v1_v29:v1 (Attempt 047)
- **Uploaded**: 2026-04-04T07:13:12Z
- **Change**: Mid-range hub penalty 1.5→1.47 (-2%)
- **Base**: Delta's 036-038 + scissors 039-046
- **Status**: Awaiting tournament results (need 20+ matches)
- **Rationale**: Completes mid-range optimization with 046. Targets 10-15 distance (safer than failed far/mid attempts 019/023).
