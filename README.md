# Legend Skills

Reusable agent skills for debugging, Git workflows, React/TypeScript implementation, and Legend ecosystem best practices.

Skills are small instruction bundles for coding agents. Install this repo with `npx skills`, then ask your agent to use a skill by name, such as `$diagnose` or `$react-coding-style`.

## Install

Install all skills:

```bash
npx skills add LegendApp/legend-skills
```

Install selected skills:

```bash
npx skills add LegendApp/legend-skills --skill commit
npx skills add LegendApp/legend-skills --skill commit-confirm
npx skills add LegendApp/legend-skills --skill diagnose
npx skills add LegendApp/legend-skills --skill diagnose-fix-loop
npx skills add LegendApp/legend-skills --skill git-conflicts
npx skills add LegendApp/legend-skills --skill react-coding-style
npx skills add LegendApp/legend-skills --skill legend-list-best-practices
npx skills add LegendApp/legend-skills --skill legend-state-best-practices
```

Some selected skills build on other skills. Install their dependency before using them:

- `commit-confirm` requires `commit`.
- `diagnose-fix-loop` requires `diagnose`.

Install globally:

```bash
npx skills add LegendApp/legend-skills -g
```

List available skills without installing:

```bash
npx skills add LegendApp/legend-skills --list
```

## Skills

### `commit`

Creates one or more clean Git commits from the current working tree. It reads repository guidance, groups related changes, stages only the right files or hunks, uses conventional commit messages, and reports any remaining unstaged work.

Use it when you want the agent to commit changes directly.

Example:

```text
Use $commit to commit the current changes.
```

### `commit-confirm`

Approval-first version of `commit`. It proposes commit groups and messages, then waits for explicit approval such as `go` before staging or committing.

Use it when you want to review the commit plan first. Requires `commit`.

Example:

```text
Use $commit-confirm to propose commits for this branch, but wait for my approval.
```

### `diagnose`

Evidence-first debugging workflow for hard bugs, app/browser issues, logs, flaky behavior, and performance regressions. It focuses on building a reproducible feedback loop, proving the real fault line, making the smallest credible fix, and verifying with regression coverage.

Use it when a problem is unclear, intermittent, performance-related, or needs proof before editing.

Example:

```text
Use $diagnose to find why this test is failing and verify the smallest fix.
```

### `diagnose-fix-loop`

Iterative wrapper around `diagnose`. It runs a diagnosis pass, plans one scoped fix, implements it, verifies it, diagnoses the new state, and continues until no useful fix remains or user input is required.

Use it when you want the agent to keep improving a bug or performance issue until the evidence says to stop. Requires `diagnose`.

Example:

```text
Use $diagnose-fix-loop to keep debugging and fixing this slow screen until there is no clear next improvement.
```

### `git-conflicts`

Safely handles Git integration operations and conflicts. It detects whether a rebase, merge, cherry-pick, or revert is already in progress before doing anything else, resolves straightforward conflicts, and asks for help when the conflict requires product or ownership judgment.

Use it when you are rebasing, merging, cherry-picking, reverting, or stuck in an interrupted Git operation.

Example:

```text
Use $git-conflicts to continue this rebase and resolve any straightforward conflicts.
```

### `react-coding-style`

React, React Native, and TypeScript implementation guidance focused on small render surfaces, stable identities, direct data flow, and minimal effects. It helps avoid broad re-renders, large dependency arrays, effect-heavy control flow, unnecessary compatibility shims, and premature abstractions.

Use it when changing components, hooks, callbacks, subscriptions, context reads, list rows, or render-sensitive UI code.

Example:

```text
Use $react-coding-style to implement this component change without causing unnecessary re-renders.
```

### `legend-list-best-practices`

Best-practice and debugging guidance for [`@legendapp/list`](https://github.com/LegendApp/legend-list) and `LegendList`. It covers virtualization, blanking while scrolling, mount cost, row measurement, `renderItem` stability, fixed-size rows, visible range callbacks, adaptive rendering, and related performance issues.

Use it when working on a `LegendList`, diagnosing list performance, or reviewing a list implementation for avoidable row churn.

Example:

```text
Use $legend-list-best-practices to audit this LegendList for scroll blanking and unstable row renders.
```

### `legend-state-best-practices`

Guidance for using [`@legendapp/state`](https://github.com/LegendApp/legend-state) effectively in React, React Native, and TypeScript code. It focuses on observable ownership, narrow reactive boundaries, field-level subscriptions, persistence, settings stores, and avoiding unnecessary re-renders.

Use it when introducing or refactoring observables, replacing prop-drilled React state, migrating deprecated subscription APIs, or designing fine-grained reactive state.

Example:

```text
Use $legend-state-best-practices to refactor this prop-drilled settings state into narrow observable reads.
```

## Dependency Policy

Skills may depend on another skill when that avoids copying a shared workflow. A dependent skill must clearly name its dependency, stop before acting if the dependency is unavailable, tell the user how to install the missing skill, and keep only the instructions that modify or extend the dependency's behavior.
