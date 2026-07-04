---
name: git-conflicts
description: Recover active Git sequencer operations and run requested branch-integration commands safely. Use when asked to run a rebase, merge a branch, cherry-pick or revert a commit, continue an interrupted operation, fix conflicts during rebasing, or resolve conflicts from an in-progress merge, cherry-pick, or revert. First detect whether a Git operation is already in progress and continue that operation before asking for a target branch.
---

# Git Conflicts

Recover active Git conflict operations first. If no operation is active, run
the branch-integration operation the user requested. Default to rebase only
when the user did not request merge, cherry-pick, or revert.

## Workflow

1. Check repo and operation state.
Use:
- `git status --short --branch`
- `git rev-parse --abbrev-ref HEAD`
- `git rev-parse --git-path rebase-merge`
- `git rev-parse --git-path rebase-apply`
- `git rev-parse --git-path MERGE_HEAD`
- `git rev-parse --git-path CHERRY_PICK_HEAD`
- `git rev-parse --git-path REVERT_HEAD`

2. If any operation is active, continue that operation.
Do not ask what to rebase onto. Treat `git status` and the Git state files as
the source of truth, even when the user says "rebase" but Git is actually in a
merge, cherry-pick, or revert.

3. If no operation is active, identify the requested operation.
Follow explicit user intent:
- rebase: rebase the current branch onto the requested target branch
- merge: merge the requested branch or commit
- cherry-pick: cherry-pick the requested commit(s)
- revert: revert the requested commit(s)

If the user did not specify an operation, default to rebase. If the needed
branch or commit is missing, ask for it before making changes.

4. Start the requested operation.
Use:
- `git fetch --all --prune` if remote updates matter for branch targets
- `git rebase <target-branch>`
- `git merge <branch-or-commit>`
- `git cherry-pick <commit>...`
- `git revert <commit>...`

5. If conflicts occur, inspect and classify.
Use:
- `git status --short`
- `git diff --name-only --diff-filter=U`
- `scripts/list-rebase-conflicts.sh` if present

6. Resolve straightforward conflicts directly, then stage files.
Use:
- edit files to remove markers and preserve correct combined behavior
- `git add <file> ...`

7. Continue after each conflict batch with the active operation's command.
Use:
- rebase: `GIT_EDITOR=true git rebase --continue`
- merge: `GIT_EDITOR=true git merge --continue`
- cherry-pick: `GIT_EDITOR=true git cherry-pick --continue`
- revert: `GIT_EDITOR=true git revert --continue`
- repeat until complete

8. Validate and summarize.
Use:
- run relevant tests/lint if feasible
- summarize which operation was started or continued, what was auto-resolved, and what required user input

## Conflict Policy

Treat as straightforward only when intent is unambiguous:
- trivial formatting/import ordering differences
- non-overlapping line edits that can be merged without changing behavior
- generated file conflicts where regeneration is deterministic and safe

Escalate to the user when any of these appear:
- behavioral or product decision conflicts
- both sides changed same logic in different ways
- delete/modify conflicts where ownership is unclear
- lockfile or generated artifact conflicts with uncertain source of truth
- large refactors where preserving both sides is risky

When escalating, provide:
1. file path(s)
2. short description of each competing change
3. concrete options and recommended default

## Operation Safety Notes

Identify the active operation before interpreting conflict sides:
- during rebase, `--ours` is the branch being rebased onto and `--theirs` is the commit currently being replayed
- during cherry-pick or revert, `--ours` is the current branch and `--theirs` is the picked or reverted commit
- during merge, `--ours` is the current branch and `--theirs` is the branch being merged

Do not use destructive resets unless explicitly requested.
Do not skip commits unless the user approves.

If the operation cannot be completed safely, stop and ask whether to:
1. continue with manual guidance
2. abort the active operation with the matching `--abort` command
3. apply a different strategy

## Resources

### scripts/list-rebase-conflicts.sh

Print the active operation, conflicted files, and conflict marker locations for fast triage.
