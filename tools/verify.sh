#!/usr/bin/env bash
# tools/verify.sh
# Run project checks after AI edits.

set -u

SKIP_TESTS=0
SKIP_BUILD=0
ONLY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-tests) SKIP_TESTS=1; shift ;;
        --skip-build) SKIP_BUILD=1; shift ;;
        --only) ONLY="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [[ ! -f "package.json" ]]; then
    echo "No package.json found. Run from the project root." >&2
    exit 2
fi

should_run() {
    local name="$1"
    if [[ -z "$ONLY" ]]; then return 0; fi
    [[ ",$ONLY," == *",$name,"* ]]
}

run_step() {
    local name="$1"
    shift

    if ! should_run "$name"; then
        echo ""
        echo "=== $name (skipped) ==="
        return 0
    fi

    echo ""
    echo "=== $name ==="
    local start
    start=$(date +%s)

    "$@"
    local code=$?

    local elapsed=$(( $(date +%s) - start ))
    if [[ $code -eq 0 ]]; then
        printf "  PASS  (%ss)\n" "$elapsed"
    else
        printf "  FAIL  (exit %s, %ss)\n" "$code" "$elapsed"
    fi
    return $code
}

declare -A results
failed=0

run_step "type-check" npx tsc --noEmit
results["type-check"]=$?

run_step "lint" npm run lint --silent
results["lint"]=$?

if [[ $SKIP_TESTS -eq 0 ]]; then
    run_step "test" npm test --silent
    results["test"]=$?
fi

if [[ $SKIP_BUILD -eq 0 ]]; then
    run_step "build" npm run build --silent
    results["build"]=$?
fi

echo ""
echo "========== Summary =========="
for k in "${!results[@]}"; do
    v="${results[$k]}"
    if [[ "$v" -eq 0 ]]; then
        printf "  [OK]   %s\n" "$k"
    else
        printf "  [FAIL] %s\n" "$k"
        failed=$((failed + 1))
    fi
done

if [[ $failed -gt 0 ]]; then
    echo ""
    echo "$failed check(s) failed. Rollback options:"
    echo "  python tools/snapshot.py --list"
    echo "  python tools/snapshot.py --restore <name>"
    exit 1
fi

echo ""
echo "All checks passed."
exit 0
