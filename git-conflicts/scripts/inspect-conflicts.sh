#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "Not inside a git repository." >&2
    exit 1
fi

operation=""
if [[ -d "$(git rev-parse --git-path rebase-merge)" || -d "$(git rev-parse --git-path rebase-apply)" ]]; then
    operation="rebase"
elif [[ -f "$(git rev-parse --git-path MERGE_HEAD)" ]]; then
    operation="merge"
elif [[ -f "$(git rev-parse --git-path CHERRY_PICK_HEAD)" ]]; then
    operation="cherry-pick"
elif [[ -f "$(git rev-parse --git-path REVERT_HEAD)" ]]; then
    operation="revert"
fi

if [[ -n "$operation" ]]; then
    printf 'Active operation: %s\n' "$operation"
else
    printf 'No rebase, merge, cherry-pick, or revert in progress.\n'
fi

conflicted=()
while IFS= read -r -d '' file; do
    conflicted+=("$file")
done < <(git diff --name-only --diff-filter=U -z)

if [[ ${#conflicted[@]} -eq 0 ]]; then
    printf 'No conflicted files.\n'
    exit 0
fi

printf 'Conflicted files (%d):\n' "${#conflicted[@]}"
for file in "${conflicted[@]}"; do
    printf ' - %q\n' "$file"
done

printf '\nConflict marker locations:\n'
for file in "${conflicted[@]}"; do
    printf '==> %q\n' "$file"
    if command -v rg >/dev/null 2>&1; then
        rg -n -- "^(<<<<<<<|=======|>>>>>>>)" "$file" || true
    else
        grep -nE -- "^(<<<<<<<|=======|>>>>>>>)" "$file" || true
    fi
    printf '\n'
done
