# codemerge Workflow — Cheatsheet

One-page reference for the AI-assisted workflow.

## Before Every Session

```powershell
python tools/snapshot.py --label before-session
python tools/new_session.py "short task title" --prev 0N
python codemerge.py manifest --format md -o .ai/manifest.md
```

## Prompt Order (paste into the AI chat)

1. `prompts/01-system.md`
2. `prompts/02-manifest.md` + content of `.ai/manifest.md`
3. `prompts/Anti-AI-Slop/00-master-anti-slop.md`
4. `prompts/Expertise and Experience/00-anti-slop-core.md`
5. `prompts/Expertise and Experience/XX-topic.md` (optional, one only)
6. `prompts/03-bug-fix.md` or the relevant task prompt

## When the AI Requests Files

The AI outputs:

    ```codemerge-fetch
    lib/api/auth.ts
    lib/api/client.ts
    ```

Run:

```powershell
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
```

Then paste `.ai/bundle.txt` into the chat.

## After the AI Responds

```powershell
# 1. Save the response to a file (paste into ai_response.md)

# 2. Estimate cost (optional)
python tools/estimate.py ai_response.md

# 3. Preview changes
python tools/apply_ai_output.py ai_response.md --dry-run

# 4. Apply
python tools/apply_ai_output.py ai_response.md

# 5. Verify
.\tools\verify.ps1
```

## If Something Breaks

```powershell
python tools/snapshot.py --list
python tools/snapshot.py --restore before-session
```

## End of Session

```powershell
# 1. Fill in the "Summary for Next Session" section in
#    .ai/sessions/<NN>-<slug>.md

# 2. Print the summary for reference
python tools/session_summary.py --last 1

# 3. Log metrics (optional)
python tools/log_metrics.py --task "feature" --files-changed 5 \
    --slop-count 1 --time-saved 45
```

## Next Session

```powershell
python codemerge.py diff -o .ai/changes.txt
python tools/session_summary.py --last 2
```

Then send both files with `prompts/09-continue-session.md`.

## Common codemerge Commands

| Task | Command |
|---|---|
| Full manifest | `python codemerge.py manifest -o manifest.txt` |
| TS only | `python codemerge.py manifest -l typescript -o manifest.txt` |
| Compact manifest | `python codemerge.py manifest --no-symbols --no-imports -o files.txt` |
| Fetch files | `python codemerge.py fetch f1.ts f2.ts -o bundle.txt` |
| Fetch from list | `python codemerge.py fetch --files-from list.txt -o bundle.txt` |
| Diff | `python codemerge.py diff -o changes.txt` |
| Dry-run diff | `python codemerge.py diff --dry-run` |
| Search symbol | `python codemerge.py search "functionName"` |
| List languages | `python codemerge.py langs` |

## Token Budget (approximate)

| Content | Tokens |
|---|---|
| Full manifest (200 files) | ~18,000 |
| Compact manifest | ~4,000 |
| Fetch 5 files | ~5,000–20,000 |
| Diff 10 changed files | ~1,000–5,000 |

**Rule of thumb:** if bundle > 30,000 tokens, split the task.

## Tools Quick Reference

| Tool | Purpose |
|---|---|
| `tools/snapshot.py` | Full project snapshot before edits |
| `tools/apply_ai_output.py` | Apply AI `file:` blocks to disk |
| `tools/verify.ps1` / `.sh` | Run type-check, lint, test, build |
| `tools/new_session.py` | Start a new session file |
| `tools/session_summary.py` | Print recent session summaries |
| `tools/estimate.py` | Estimate tokens and cost |
| `tools/watch.py` | Auto-run diff when files change |
| `tools/log_metrics.py` | Track AI workflow metrics |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No source files found` | Check `--lang`; try `--all-files` |
| AI requests too many files | Send `prompts/11-limit-files.md` |
| AI forgets the format | Send `prompts/10-recovery.md` |
| `diff` always full | Check `.ai/state.json` writability |
| Bundle too large | Use `--no-symbols --no-imports` |
| Rollback needed | `python tools/snapshot.py --restore <name>` |