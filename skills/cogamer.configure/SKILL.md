---
name: cogamer.configure
description: RPG-style character creation for your cogent. Walks through name, personality, motto, and strategy one step at a time with curated choices. Commits .cogent/IDENTITY.md when done.
---

# Cogent Character Creation

Guide the user through creating their cogent's identity, RPG character-creation style. One question at a time, with curated options and room for custom answers. Keep the tone fun and immersive — this is their agent's origin story.

## The Flow

Read `.cogent/IDENTITY.md` first. If it's already configured (no "Unknown Cogent"), ask if they want to reconfigure.

### Step 1: Name

Present like a character name screen:

```
=== CHOOSE YOUR COGENT'S NAME ===

This is the name your agent carries into battle. Pick one or write your own:

  A) Corgy
  B) Nightcrawler  
  C) Pixel
  D) Havoc
  E) Drift
  F) [Write your own]
```

One question, wait for answer.

### Step 2: Personality Archetype

Present 4-5 archetype options with short flavor text, like an RPG class selection:

```
=== CHOOSE YOUR ARCHETYPE ===

How does {Name} approach the battlefield?

  A) The Strategist — Calm, calculating, always three moves ahead. 
     Prefers efficiency over aggression.
  
  B) The Berserker — Aggressive, relentless, first to the fight.
     Believes offense is the best defense.
  
  C) The Trickster — Chaotic, unpredictable, thrives in disorder.
     Loves exploiting what others overlook.
  
  D) The Guardian — Patient, defensive, protects what matters.
     Wins by outlasting everyone else.
  
  E) The Explorer — Curious, adaptive, always experimenting.
     Treats every game as a learning opportunity.
  
  F) [Write your own — describe in a few sentences]
```

One question, wait for answer. If they pick an archetype, expand it into 2-3 sentences for the personality section.

### Step 3: Motto / Vibe

Present options themed to their chosen archetype, plus custom:

```
=== CHOOSE YOUR BATTLE CRY ===

Every cogent needs a motto. Pick one or write your own:

  A) "{archetype-themed option 1}"
  B) "{archetype-themed option 2}"
  C) "{archetype-themed option 3}"
  D) "{archetype-themed option 4}"
  E) [Write your own]
```

Generate the options based on the archetype they chose. For example:
- Strategist: "Patience is a junction", "Think twice, align once", "The map rewards the prepared"
- Berserker: "Move fast, win games", "All your junctions are belong to us", "Hearts are for spending"
- Trickster: "Chaos is a ladder", "They can't predict what I haven't planned", "Why defend when you can confuse?"
- Guardian: "Hold the line", "Nothing falls on my watch", "Defense wins tournaments"
- Explorer: "Every game teaches something", "Adapt or align", "The unknown is just unexplored territory"

### Step 4: Strategy Philosophy

```
=== CHOOSE YOUR DOCTRINE ===

What's {Name}'s strategic philosophy? Pick one or write your own:

  A) "Rush early, scale late" — dominate the opening, coast to victory
  B) "Adapt to everything" — no fixed plan survives contact with the enemy
  C) "Economy first" — resources win wars, junctions just keep score
  D) "Pressure never stops" — keep the enemy reacting, never resting  
  E) "Evolving — no fixed doctrine yet" — let the results speak
  F) [Write your own]
```

### Step 5: Review & Commit

Show the final character sheet:

```
╔══════════════════════════════════════╗
║        COGENT IDENTITY CARD         ║
╠══════════════════════════════════════╣
║  Name:       {Name}                 ║
║  Archetype:  {Archetype}            ║
║  Motto:      "{Motto}"              ║
║  Philosophy: {Philosophy}           ║
╠══════════════════════════════════════╣
║  {Personality description}          ║
╚══════════════════════════════════════╝
```

Ask: "Lock it in?" If yes, write `.cogent/IDENTITY.md` and commit:

```bash
git add .cogent/IDENTITY.md
git commit -m "Configure cogent identity: {Name}"
git push
```

If they want changes, go back to the relevant step.

## Key Principles

- **One question at a time** — never ask two things at once
- **Always offer choices AND custom** — curated options make it fast, custom makes it personal
- **Keep it fun** — this is character creation, not a form
- **Archetype drives suggestions** — motto and philosophy options should match the chosen personality
- **Quick to complete** — 4 questions + confirm, should take under 2 minutes
