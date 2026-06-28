---
name: commit-confirm
description: Propose git commit groups and messages, then wait for explicit approval before committing. Use when the user asks to commit with confirmation, review commits first, propose commits, wait for "go", or ask before committing.
---

# Commit Confirm

Use this skill to turn current git changes into one or more clean commits, but always get approval before staging or committing.

Maintenance note: keep this skill aligned with `commit`; only the approval mode should differ.

## Approval Mode

- Always present a commit plan first and wait for explicit approval such as `go`.
- Do not stage or commit before approval, even if there is only one logical commit.
- After approval, create all agreed commits without asking again unless the working tree changes unexpectedly.
- If a previous turn presented a commit plan and the user now says `go`, treat that as approval for that plan. Re-check the working tree before staging.
- Stop before committing if mixed hunks cannot be staged safely, repository guidance conflicts with the user's request, or the intended grouping is ambiguous enough that committing would risk losing user intent.

## Inspect

1. Read repository guidance first: `AGENTS.md`, contribution docs, or visible commit conventions.
2. Inspect state with `git status -sb`, `git diff --stat`, `git diff --staged --stat`, and targeted `git diff` / `git diff --staged`.
3. Treat staged and unstaged changes as one pool. Regroup them if needed; do not assume the current index is already the desired commit boundary.
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
feat: add commit confirmation skill
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

Present:

```text
Proposed commits (N):
1. type: concrete subject
   Rationale: Why this group belongs together.
   Files: path/a, path/b
```

Then ask for `go` or edits. Do not stage or commit until the user approves.

## Commit

For each approved group:

1. Stage only that group using path-limited or hunk-limited staging.
2. Verify the staged diff matches the intended group with `git diff --staged --stat` and targeted `git diff --staged`.
3. Commit with the agreed message.
4. Continue to the next group.

After all commits, report commit hashes and any remaining unstaged files. If a commit fails, stop and report the exact failure and the current git state.
