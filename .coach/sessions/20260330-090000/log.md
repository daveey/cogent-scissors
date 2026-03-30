# Session Log: 20260330-090000

## 2026-03-30 09:00 — Session started
Focus: remove alignment network bottleneck

## Previous Session Results (v16)
- v16 still qualifying (2 matches)
- v15 entered competition: 2.03 (12 matches)
- v14 now at 1.95 (9 matches) — dropped from initial 3.05
- v6 remains most stable: 2.32 (102 matches)

## Experiment A: Remove alignment network filter
- Hypothesis: filter too restrictive, preventing junctions from being targeted
- Result: avg 0.83 (seeds 42=0.00, 43=2.49, 44=0.00) — REGRESSION
- Conclusion: filter IS required by game mechanics. Reverted.

## Experiment B: Remove scramblers (set scrambler_budget=0)
- Hypothesis: cooperative scoring means scramblers hurt both teams
- Result: avg 0.99 — REGRESSION
- Conclusion: scramblers have defensive value. Reverted.

## Experiment C: Expand alignment range +5 cells
- Hypothesis: agents can't reach junctions at exact alignment boundary
- Result: avg 0.84 (seeds 42=0.55, 43=1.46, 44=0.50) — REGRESSION
- Conclusion: expanding range causes agents to target unreachable junctions. Reverted.

## Experiment D: Remove broken _desired_role override ✅
- Root cause: `CogletAgentPolicy._desired_role` used `team_summary.members` count
  to detect small teams, but members only includes *visible* teammates
- When agents couldn't see all 7 teammates (early game, spread maps),
  `num_agents` was too low (e.g. 4-5), triggering small-team path
- This caused massive role misassignment: e.g. 4 scramblers instead of
  proper 4-aligner + 1-scrambler split
- Fix: remove the override, let PressureMixin._desired_role handle it
  with reliable priority arrays that don't depend on visibility

### Results
| Seed | Baseline (v16) | After Fix | Change |
|------|----------------|-----------|--------|
| 42   | 0.49           | 2.16      | +341%  |
| 43   | 4.62           | 21.59     | +367%  |
| 44   | 0.68           | 1.75      | +157%  |
| 45   | —              | 3.78      | —      |
| 46   | —              | 1.63      | —      |
| **Avg** | **1.93**    | **6.18**  | **+220%** |

## Actions
- Committed: `f443383` fix: remove broken small-team role override
- Pushed to main
- Submitted as coglet-v0:v17

## Status: WAITING
Submitted v17, checking tournament results next session.
