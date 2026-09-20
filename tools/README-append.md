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