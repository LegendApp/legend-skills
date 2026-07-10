---
name: commit
description: Commit git working tree changes with clean logical grouping and repository commit-message conventions. Use when the user asks to commit changes, make a commit, commit all changes, split changes into commits, propose commit messages, or wait for "go" before committing.
---

# Commit

Use this skill to turn current git changes into one or more clean commits.

## Approval Modes

- **Direct mode**: If the user asks to commit, analyze the working tree and create the needed commit or commits without asking for a separate "go".
- **Plan mode**: If the user asks for a plan, asks to review commits first, says to wait, says to prompt or ask before committing, or otherwise requests approval first, present a commit plan and wait for explicit approval such as `go` before staging or committing. After approval, create all agreed commits without asking again unless the working tree changes unexpectedly.
- **Clarification stop**: In any mode, stop before committing if mixed hunks cannot be staged safely, repository guidance conflicts with the user's request, or the intended grouping is ambiguous enough that committing would risk losing user intent.
- **Approval response**: If a previous turn presented a commit plan and the user now says `go`, treat that as approval for that plan. Re-check the working tree before staging.

## Inspect

1. Read repository guidance first: `AGENTS.md`, contribution docs, or visible commit conventions.
2. Inspect state with `git status -sb`, `git diff --stat`, `git diff --staged --stat`, and targeted `git diff` / `git diff --staged`. Inspect relevant untracked files before staging them.
3. Record staged and unstaged changes separately, then treat them as one pool for logical grouping. Do not assume the current index is the intended commit boundary; preserve explicit exclusions and user intent when regrouping.
4. Respect explicit exclusions, such as debug logs or generated artifacts the user said not to commit. Leave excluded changes unstaged and report them afterward.
5. If the tree is clean, say so and stop.

## Group

Group by one coherent concept: feature, fix, refactor, test, docs, config, dependency, or subsystem. Prefer separate commits when changes would be reviewed, reverted, or explained independently.

If a file contains unrelated changes, split by hunk with `git add -p` or another path/hunk-limited staging method. Do not put unrelated hunks in one commit just because they share a file.

## Message Style

Follow repository guidance when present. Otherwise use this default:

- Conventional Commit `type: subject`
- no scope parentheses
- imperative, concrete subject
- no trailing period
- no `Co-authored-by` trailer unless the user explicitly asks

Good:

```text
fix: preserve scroll offset after prepend
feat: add commit planning skill
docs: document skills install flow
```

Avoid:

```text
fix(list): preserve scroll offset
update stuff
chore: misc.
```

Use a body for behavioral changes when the reason, invariant, or validation would not be obvious from the title.

## Plan Output

When plan mode is active, present:

```text
Proposed commits (N):
1. type: concrete subject
   Rationale: Why this group belongs together.
   Files: path/a, path/b
```

Then ask for `go` or edits. Do not stage or commit until the user approves.

In direct mode, do this planning internally. Only show a concise summary before or while committing if it helps the user follow a multi-commit split.

## Commit

For each group:

1. Stage only that group using path-limited or hunk-limited staging.
2. Verify the staged diff matches the intended group with `git diff --staged --stat`, targeted `git diff --staged`, and `git diff --staged --check`.
3. Commit with the agreed message.
4. Re-check the tree after hooks run, then continue to the next group.

After all commits, report commit hashes and any remaining unstaged files. If a commit fails, stop and report the exact failure and the current git state.
