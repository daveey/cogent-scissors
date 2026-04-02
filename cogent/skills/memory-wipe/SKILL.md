# Memory Wipe

Nuclear option: blow away all `cogent/memory/` contents and reset state files. Identity survives.

## What Gets Wiped

- `cogent/memory/` — all session logs, summaries, learnings (entire directory contents)
- `cogent/state.json` — reset to empty state
- `cogent/todos.md` — cleared

## What Survives

- `cogent/IDENTITY.md` — the cogent's identity
- `cogent/INTENTION.md` — the cogent's purpose

## Steps

1. **Confirm with the user.** Show what will be deleted (list files in `cogent/memory/`, note state.json and todos.md). Ask: "Wipe all memory? This cannot be undone."

2. **If confirmed:**
   ```bash
   rm -rf cogent/memory/*
   ```
   Reset `cogent/state.json` to:
   ```json
   {
     "approach_stats": {
       "pco": {"attempts": 0, "improvements": 0, "last_used": null},
       "design": {"attempts": 0, "improvements": 0, "last_used": null}
     }
   }
   ```
   Clear `cogent/todos.md` to:
   ```markdown
   # TODOs

   _No items yet._
   ```

3. **Report** what was removed (file count, total size).
