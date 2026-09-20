# codemerge Prompts

This folder contains ready-to-use prompts for working with the AI assistant using the `codemerge.py` tool.

## Usage Order

### First Session

1. `01-system.md` — once at the beginning of the session
2. `01-system-append-2.md` — editing and output rules (always with the previous)
3. `02-manifest.md` — after that, along with manifest content
4. `Anti-AI-Slop/00-master-anti-slop.md` — general anti-slop layer
5. `Expertise and Experience/00-anti-slop-core.md` — project-specific anti-slop layer
6. One expertise file (`Expertise and Experience/XX-*.md`) — at most one
7. One task file (`03-bug-fix.md` to `08-explain-code.md`) — depending on the task

### Subsequent Sessions

1. `01-system.md` + `01-system-append-2.md` — again if using a new assistant
2. `09-continue-session.md` — to continue

### Auxiliary Prompts (as needed)

- `10-recovery.md` — when AI goes off track
- `11-limit-files.md` — when AI requests too many files
- `12-long-response.md` — when AI response is too long
- `13-final-summary.md` — for getting a final summary
- `14-checklist.md` — AI internal checklist

## Full Workflow Example

```bash
# 1. Build manifest
python codemerge.py manifest --format md -o .ai/manifest.md

# 2. Copy content of 01-system.md and 01-system-append-2.md and send to AI
# 3. Copy content of 02-manifest.md + manifest content and send to AI

# 4. Select task and send (e.g., 03-bug-fix.md)

# 5. AI requests files in codemerge-fetch format
# 6. Execute AI request
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o bundle.txt

# 7. Send bundle.txt to AI

# 8. Apply AI-proposed changes

# 9. Save state for diff
python codemerge.py diff -o changes.txt

# 10. In next session
#     Copy content of 09-continue-session.md + content of changes.txt and send to AI
```

## Important Notes

- **Always send prompt 01 and 01-append first** — without them, AI doesn't know what tool it's working with or what format to use.
- **Send prompt 02 immediately after them** — along with manifest content.
- **For each task, send one task prompt** — not multiple tasks in one message.
- **At the end of the session, send prompt 13** — to have a ready summary for the next session.
- **In the next session, use prompt 09** — along with the previous session summary and diff output.
