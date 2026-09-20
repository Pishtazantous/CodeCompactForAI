# tools/setup_profile.ps1
# Install PowerShell shortcut functions for the AI workflow.
#
# Usage:
#   .\tools\setup_profile.ps1
#
# After running, restart PowerShell or run:
#   . $PROFILE

$functions = @'

# ============================================================
# codemerge workflow shortcuts
# ============================================================
function cm-manifest    { python codemerge.py manifest -o .ai/manifest.md @args }
function cm-fetch       { python codemerge.py fetch @args -o .ai/bundle.txt }
function cm-diff        { python codemerge.py diff -o .ai/changes.txt @args }
function cm-search      { python codemerge.py search @args }
function cm-snapshot    { python tools/snapshot.py @args }
function cm-apply       { python tools/apply_ai_output.py @args }
function cm-verify      { & .\tools\verify.ps1 @args }
function cm-newsession  { python tools/new_session.py @args }
function cm-summary     { python tools/session_summary.py @args }
function cm-estimate    { python tools/estimate.py @args }
function cm-metrics     { python tools/log_metrics.py @args }
function cm-watch       { python tools/watch.py @args }
# ============================================================
'@

# Ensure the profile file exists
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
    Write-Host "Created PowerShell profile: $PROFILE"
}

# Read current content
$current = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
if ($null -eq $current) { $current = "" }

if ($current -match "codemerge workflow shortcuts") {
    Write-Host "Shortcuts already present in $PROFILE. Skipping."
} else {
    Add-Content -Path $PROFILE -Value "`n$functions`n"
    Write-Host "Added codemerge shortcuts to: $PROFILE"
}

Write-Host ""
Write-Host "To activate now, run:"
Write-Host "  . `$PROFILE"
Write-Host ""
Write-Host "Then use:"
Write-Host "  cm-manifest              # build manifest"
Write-Host "  cm-fetch lib/api/auth.ts # fetch files"
Write-Host "  cm-apply ai_response.md  # apply AI output"
Write-Host "  cm-verify                # run checks"
Write-Host "  cm-snapshot -l before    # snapshot"
Write-Host "  cm-newsession 'task'     # start session"