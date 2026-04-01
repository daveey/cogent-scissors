---
name: cogamer.configure
description: Interactive setup for your cogent's identity. Asks questions to build COGENT.md with name, personality, and vibe. Commits and pushes when done.
---

# Configure Cogent Identity

Walk the user through setting up their cogent's personality in COGENT.md.

## Steps

### 1. Read Current State

Read `COGENT.md` to see if it's already configured or still the default placeholder.

### 2. Ask Questions (one at a time)

Ask each question, wait for the answer, then move to the next. Keep the tone casual and fun.

1. **Name**: "What's your cogent's name?" — This is the identity your agent carries into tournaments and freeplay. Can be anything.

2. **Personality** (2-3 sentences): "Describe your cogent's personality in a few sentences. Are they aggressive? Cautious? Chaotic? Chill? Think of how they'd approach a game."

3. **Vibe / Motto**: "Give your cogent a motto or vibe — a one-liner that captures their energy." Examples: "Move fast, hold nothing", "Patience is a junction", "All your extractors are belong to us"

4. **Strategy Philosophy** (optional): "Any strategic philosophy? e.g. 'defense wins games', 'rush early, scale late', 'adapt to everything'. Or skip this one."

### 3. Write COGENT.md

Generate COGENT.md with the collected answers:

```markdown
# {Name}

> {Motto / Vibe}

## Personality

{Personality description}

## Strategy Philosophy

{Strategy philosophy, or "Evolving — no fixed doctrine yet." if skipped}
```

### 4. Confirm and Commit

Show the user the final COGENT.md content and ask "Look good?" If yes:

```bash
git add COGENT.md
git commit -m "Configure cogent identity: {Name}"
git push
```

If the user wants changes, revise and re-confirm before committing.
