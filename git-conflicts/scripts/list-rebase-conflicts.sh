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
    echo "Active operation: $operation"
else
    echo "No rebase, merge, cherry-pick, or revert in progress."
fi

conflicted=()
while IFS= read -r line; do
    conflicted+=("$line")
done < <(git diff --name-only --diff-filter=U)

if [[ ${#conflicted[@]} -eq 0 ]]; then
    echo "No conflicted files."
    exit 0
fi

echo "Conflicted files (${#conflicted[@]}):"
for file in "${conflicted[@]}"; do
    echo " - $file"
done

echo
echo "Conflict marker locations:"
for file in "${conflicted[@]}"; do
    echo "==> $file"
    if command -v rg >/dev/null 2>&1; then
        rg -n "^(<<<<<<<|=======|>>>>>>>)" "$file" || true
    else
        grep -nE "^(<<<<<<<|=======|>>>>>>>)" "$file" || true
    fi
    echo
done
