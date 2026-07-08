---
name: commit-confirm
description: Approval-first wrapper for the commit skill. Requires the commit skill; selected installs must also install commit. Use when the user asks to commit with confirmation, review commits first, propose commits, wait for "go", or ask before committing.
---

# Commit Confirm

Use this skill to run `$commit` in approval-first mode.

Before starting, load and follow `$commit`. This skill only changes the approval behavior; `$commit` owns working-tree inspection, grouping, message style, staging, committing, and reporting.

Selected installs do not install dependencies automatically. If `$commit` is not installed or available, stop before staging or committing. Tell the user to install it with:

```bash
npx skills add LegendApp/legend-skills --skill commit
```

Then ask them to retry after installation.

## Approval Override

When using `$commit`, force plan mode:

- Always present a commit plan first and wait for explicit approval such as `go`.
- Do not stage or commit before approval, even if there is only one logical commit.
- After approval, create all agreed commits without asking again unless the working tree changes unexpectedly.
- If a previous turn presented a commit plan and the user now says `go`, treat that as approval for that plan. Re-check the working tree before staging.
- Stop before committing if mixed hunks cannot be staged safely, repository guidance conflicts with the user's request, or the intended grouping is ambiguous enough that committing would risk losing user intent.
