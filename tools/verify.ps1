# tools/verify.ps1
# Run project checks after AI edits.
#
# Usage:
#   .\tools\verify.ps1
#   .\tools\verify.ps1 -SkipTests
#   .\tools\verify.ps1 -SkipBuild
#   .\tools\verify.ps1 -Only "type-check","lint"

param(
    [switch]$SkipTests,
    [switch]$SkipBuild,
    [string[]]$Only = @()
)

$ErrorActionPreference = "Continue"

function Test-ShouldRun {
    param([string]$Name)
    if ($Only.Count -eq 0) { return $true }
    return $Only -contains $Name
}

function Run-Step {
    param(
        [string]$Name,
        [scriptblock]$Block
    )
    if (-not (Test-ShouldRun $Name)) {
        Write-Host "`n=== $Name (skipped) ===" -ForegroundColor DarkGray
        return 0
    }

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    $start = Get-Date
    & $Block
    $code = $LASTEXITCODE
    $elapsed = ((Get-Date) - $start).TotalSeconds

    if ($code -eq 0) {
        $msg = "  PASS  ({0:N2}s)" -f $elapsed
        Write-Host $msg -ForegroundColor Green
    } else {
        $msg = "  FAIL  (exit $code, {0:N2}s)" -f $elapsed
        Write-Host $msg -ForegroundColor Red
    }
    return $code
}

if (-not (Test-Path "package.json")) {
    Write-Host "No package.json found. Run this from the project root." `
        -ForegroundColor Red
    exit 2
}

$results = [ordered]@{}

if (Test-ShouldRun "type-check") {
    $results["type-check"] = Run-Step "Type check" {
        npx tsc --noEmit
    }
}

if (Test-ShouldRun "lint") {
    $results["lint"] = Run-Step "Lint" {
        npm run lint --silent
    }
}

if (-not $SkipTests -and (Test-ShouldRun "test")) {
    $results["test"] = Run-Step "Tests" {
        npm test --silent
    }
}

if (-not $SkipBuild -and (Test-ShouldRun "build")) {
    $results["build"] = Run-Step "Build" {
        npm run build --silent
    }
}

Write-Host "`n========== Summary ==========" -ForegroundColor Cyan
$failed = 0
foreach ($k in $results.Keys) {
    $v = $results[$k]
    if ($v -eq 0) {
        Write-Host "  [OK]   $k" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $k" -ForegroundColor Red
        $failed++
    }
}

if ($failed -gt 0) {
    Write-Host "`n$failed check(s) failed. Rollback options:" `
        -ForegroundColor Yellow
    Write-Host "  python tools/snapshot.py --list"
    Write-Host "  python tools/snapshot.py --restore <name>"
    exit 1
}

Write-Host "`nAll checks passed." -ForegroundColor Green
exit 0
