---
name: git-conflicts
description: Recover active Git sequencer operations and run requested branch integration safely. Use for rebases, merges, cherry-picks, reverts, interrupted operations, conflict resolution, ours/theirs interpretation, or deciding when user guidance is required. Detect active Git state first and never guess an unclear operation or resolution.
---

# Git Conflicts

> **Hard stop:** Proceed only when the operation, target, and intended result of every conflict are 100% clear from Git state, explicit user intent, and repository evidence. Otherwise stop before editing, staging, continuing, skipping, aborting, or starting an operation, and ask the user. Never choose a default; an incorrect resolution is worse than an interruption.

## Workflow

1. **Inspect state.** Run full `git status`, `git status --short --branch`, and `scripts/inspect-conflicts.sh` when available. Resolve `rebase-merge`, `rebase-apply`, `MERGE_HEAD`, `CHERRY_PICK_HEAD`, and `REVERT_HEAD` with `git rev-parse --git-path`.

   Active Git state determines the operation to resume; do not start another. It does not determine the intended combined behavior. Before starting a new operation, identify pre-existing staged, unstaged, and untracked changes; ask if their ownership or interaction is unclear.

2. **Confirm a new operation.** With no active operation, require an explicit method and target: rebase onto a target, merge a target, cherry-pick commits, or revert commits. Ask if the method, target, commit set or order, or merge-commit mainline is missing or ambiguous. Do not default to rebase. Fetch only the required remote or ref when freshness matters.

   Start the confirmed operation non-interactively with `git rebase <target>`, `git merge --no-edit <target>`, `git cherry-pick <commits>`, or `GIT_EDITOR=true git revert <commits>`. Add `-m <parent>` only for a confirmed merge-commit mainline.

3. **Inspect every conflict before editing.** Check `git diff --name-only --diff-filter=U`, markers or index stages, and the exact change represented by `REBASE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, or `MERGE_HEAD`. Use surrounding history, callers, tests, and docs to state the intended result and evidence for every path.

   If any result is not 100% clear, resolve nothing. Report the exact Git state and paths, explain the competing intents and evidence, and offer concrete options. You may identify the likeliest option but must not select it. Always ask for divergent behavior, unclear delete/modify conflicts, uncertain binary/lock/generated files, competing refactors or evidence, and missing mainline parents. Formatting, imports, non-overlapping edits, moves, and generated files are direct only when repository evidence verifies the result.

4. **Resolve and verify.** Treat staged resolutions, `rerere`, merge drivers, and automatic resolutions as untrusted proposals. Once every path is clear, edit the files, regenerate generated output from its source, remove all markers, and stage only resolved paths. Verify no unmerged entries remain, review `git diff --cached`, and run the fastest meaningful focused check when the intermediate state is testable. Never accept `ours`, `theirs`, union merge, or generated output wholesale without independent verification.

5. **Continue the active operation.** Use the matching command:

   - `GIT_EDITOR=true git rebase --continue`
   - `GIT_EDITOR=true git merge --continue`
   - `GIT_EDITOR=true git cherry-pick --continue`
   - `GIT_EDITOR=true git revert --continue`

   Reinspect state after every continuation and apply the same hard stop to each new conflict.

6. **Finish.** Run focused validation, then report the completed operation, resolved paths, validation, and remaining tree changes.

## Ours And Theirs

- Rebase: `ours` is the branch rebased onto; `theirs` is the commit being replayed.
- Merge: `ours` is the current branch; `theirs` is the branch being merged.
- Cherry-pick: `ours` is the current branch; `theirs` is the commit being applied.
- Revert: infer nothing from the labels; compare current `HEAD`, the reverted commit, its selected parent, and the index stages.

## Safety

Never use destructive resets, abort an operation, skip commits, or overwrite unrelated changes without explicit approval. If completion is unclear or unsafe, preserve the exact state and ask whether to provide resolution guidance, use the matching `--abort`, or choose another integration strategy.

`scripts/inspect-conflicts.sh` prints the active operation, conflicted files, and marker locations.
