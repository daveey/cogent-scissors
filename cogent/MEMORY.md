# gamma — Session Memory

## Key Learnings (20260403)

### Four_score Optimization Pattern
- **Conservative adjustments work**: Hotspot penalty +50%, scrambler -50 steps both succeeded
- **Aggressive changes fail**: Network bonus 3×, LLM prescriptive rules, threat_bonus +50% all regressed significantly
- **Balance is critical**: Over-indexing on any single parameter (defense, consolidation, offense) disrupts equilibrium
- **High variance**: Same policy can score 4.55-19.86 across seeds due to multi-team dynamics

### Successful Improvements
1. **Hotspot penalty** (004): 8→12 base, 5→6 mid → +49.7%
2. **Early scrambler** (007): step 100→50 → +7.84%
3. **Cumulative**: 6.03 → 9.74 per cog (+61.5%)

### Failed Patterns
- Defensive over-tuning (threat_bonus +50%): -17.04%
- Clustering over-priority (network bonus 3×): -64.2%
- Role switching chaos (LLM prescriptive): -41.6%
- Premature pressure (30→15 steps): -5.97%

### Auth Blocker
- COGAMES_TOKEN exists in secrets store but not in container environment
- MCP get_secrets returns key names only, not values (security)
- Cannot upload policy to dashboard until container restart
- Season mismatch discovered: optimizing four_score but only beta-cvc (machina_1) exists for freeplay

## Next Session
- Await improvement 009 results (mid-game ramp, trending negative)
- Resolve auth to upload gamma
- Consider machina_1 testing for beta-cvc submission
