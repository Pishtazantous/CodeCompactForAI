# tools/

Small helper scripts for the AI workflow.

## apply_ai_output.py

Parse and apply AI-generated file blocks. Each block must use:

    ```file:path/to/file.ts
    <complete file content>
    ```

### Usage

    python tools/apply_ai_output.py ai_response.md --dry-run
    python tools/apply_ai_output.py ai_response.md
    python tools/apply_ai_output.py ai_response.md --force
    cat ai_response.md | python tools/apply_ai_output.py --from-stdin

Existing files are backed up in `.ai/backups/<timestamp>/` before
overwriting. New files are only created with `--force`.

---

## snapshot.py

Full snapshots of project source files. Useful before large AI edits.

### Usage

    python tools/snapshot.py --label before-ai-edit
    python tools/snapshot.py --list
    python tools/snapshot.py --restore before-ai-edit
    python tools/snapshot.py --clean

Snapshots live in `.ai/snapshots/<timestamp>[-label]/`.
Only the last 10 snapshots are kept after `--clean`.

---

## verify.ps1 / verify.sh

Run project checks after AI edits: type-check, lint, tests, build.

### Usage (Windows)

    .\tools\verify.ps1
    .\tools\verify.ps1 -SkipTests
    .\tools\verify.ps1 -Only "type-check","lint"

### Usage (Linux / macOS)

    chmod +x tools/verify.sh
    ./tools/verify.sh
    ./tools/verify.sh --skip-tests
    ./tools/verify.sh --only type-check,lint

On failure, the script suggests snapshot rollback.

---

## new_session.py

Scaffold a new AI session.

### Usage

    python tools/new_session.py "auth refactor"
    python tools/new_session.py "payment bug" --prev 02

Creates `.ai/sessions/<NN>-<slug>.md` and updates `.ai/sessions/index.json`.

---

## session_summary.py

Print summaries of recent sessions.

### Usage

    python tools/session_summary.py
    python tools/session_summary.py --last 3
    python tools/session_summary.py --list
    python tools/session_summary.py -v

---

## End-to-End Workflow

```bash
# Start a new session
python tools/snapshot.py --label before-session
python tools/new_session.py "task title" --prev 0N
python codemerge.py manifest -o .ai/manifest.md

# After AI responds, save response to ai_response.md
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md
.\tools\verify.ps1

# If verify fails
python tools/snapshot.py --restore before-session

# End of session: fill Summary in .ai/sessions/<NN>-*.md
python tools/session_summary.py --last 1
```

---

## estimate.py

Estimate tokens and cost of a file before sending to AI.

### Usage

    python tools/estimate.py bundle.txt
    python tools/estimate.py bundle.txt --model deepseek-chat
    python tools/estimate.py bundle.txt --output-tokens 3000

### Notes

Uses `tiktoken` if installed for exact token counts, otherwise falls
back to a 4-characters-per-token heuristic. Prices are hardcoded and
may need updating as providers change them.

---

## watch.py

Watch the project and auto-run `codemerge diff` when files change.

### Usage

    python tools/watch.py
    python tools/watch.py --interval 5
    python tools/watch.py -o .ai/changes.txt
    python tools/watch.py -q

### Notes

Runs an initial diff immediately, then polls every `--interval`
seconds. Press Ctrl+C to stop.

---

## log_metrics.py

Track AI workflow metrics per session.

### Usage

    python tools/log_metrics.py --task "feature" --files-changed 5 \
        --slop-count 1 --time-saved 45
    python tools/log_metrics.py --show
    python tools/log_metrics.py --show --last 20
    python tools/log_metrics.py --reset

### Notes

Metrics are stored in `.ai/metrics.json`. After a few weeks, `--show`
reveals which tasks produce the most slop and how much time is being
saved.

---

## setup_profile.ps1

Install PowerShell shortcut functions for the AI workflow.

### Usage

    .\tools\setup_profile.ps1
    . $PROFILE        # reload the profile

After this, the following shortcuts are available:

| Shortcut | Runs |
|---|---|
| `cm-manifest` | `python codemerge.py manifest -o .ai/manifest.md` |
| `cm-fetch` | `python codemerge.py fetch @args -o .ai/bundle.txt` |
| `cm-diff` | `python codemerge.py diff -o .ai/changes.txt` |
| `cm-search` | `python codemerge.py search @args` |
| `cm-snapshot` | `python tools/snapshot.py @args` |
| `cm-apply` | `python tools/apply_ai_output.py @args` |
| `cm-verify` | `.\tools\verify.ps1 @args` |
| `cm-newsession` | `python tools/new_session.py @args` |
| `cm-summary` | `python tools/session_summary.py @args` |
| `cm-estimate` | `python tools/estimate.py @args` |
| `cm-metrics` | `python tools/log_metrics.py @args` |
| `cm-watch` | `python tools/watch.py @args` |

