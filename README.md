# Legend Skills

Legend Skills gives coding agents proven workflows in two groups:
1. **Legend library skills** for building fast, correct apps with Legend List and Legend State
2. **General React and React Native development skills** for debugging difficult issues, fixing them completely, protecting Git history, and high-performance React and React Native apps.

## Skills at a glance

| Skill | Useful for |
| --- | --- |
| [`diagnose`](#diagnose) | Proving the root cause of unclear, intermittent, platform-specific, or performance bugs before editing. |
| [`diagnose-fix-loop`](#diagnose-fix-loop) | Repeatedly diagnosing, fixing, and verifying until no useful evidence-backed improvement remains. |
| [`commit`](#commit) | Turning a mixed working tree into clean, focused commits that follow repository conventions. |
| [`commit-confirm`](#commit-confirm) | Reviewing proposed commit groups and messages before anything is staged or committed. |
| [`git-conflicts`](#git-conflicts) | Safely resolving or continuing rebases, merges, cherry-picks, and reverts. |
| [`react-coding-style`](#react-coding-style) | Building React, React Native, and TypeScript UI with narrow render boundaries and stable data flow. |
| [`legend-list-best-practices`](#legend-list-best-practices) | Building or auditing fast virtualized lists with correct measurement, recycling, and row invalidation. |
| [`legend-state-best-practices`](#legend-state-best-practices) | Designing observable state with clear ownership, fine-grained subscriptions, persistence, and sync. |

Use one skill for a focused task or combine workflow and domain skills so the agent knows both *how to work* and *which technical contracts to protect*.

## Example

Ask an agent to combine the diagnosis workflow with the relevant domain skill:

```text
Use $diagnose and $legend-list-best-practices to find why this chat list blanks
during fast scrolling. Reproduce and measure the problem first. If incorrect
LegendList usage is the cause, implement the smallest fix and verify the original
reproduction plus a focused regression test.
```

This tells the agent to prove the bottleneck before editing, apply Legend List's real data, measurement, recycling, and row-invalidation contracts, and verify the result against the original symptom.

## Install

Install all skills:

```bash
npx skills add LegendApp/legend-skills
```

Install globally:

```bash
npx skills add LegendApp/legend-skills -g
```

List the available skills without installing:

```bash
npx skills add LegendApp/legend-skills --list
```

Install selected skills:

```bash
npx skills add LegendApp/legend-skills --skill commit
npx skills add LegendApp/legend-skills --skill commit --skill commit-confirm
npx skills add LegendApp/legend-skills --skill diagnose
npx skills add LegendApp/legend-skills --skill diagnose --skill diagnose-fix-loop
npx skills add LegendApp/legend-skills --skill git-conflicts
npx skills add LegendApp/legend-skills --skill react-coding-style
npx skills add LegendApp/legend-skills --skill legend-list-best-practices
npx skills add LegendApp/legend-skills --skill legend-state-best-practices
```

## Skill dependencies

Selected installs do not resolve dependencies automatically:

- `commit-confirm` requires `commit`.
- `diagnose-fix-loop` requires `diagnose`.

The paired commands above install each wrapper with its dependency. Installing the full repository is the simplest way to make every skill available.

## Skills

### `commit`

Inspects the whole working tree, groups related changes, stages only the intended files or hunks, and creates one or more commits using repository conventions.

Use it when the work is ready and you want clean commits that can be reviewed or reverted independently.

It can usually be used without any additional guidance.

```text
$commit
```

### `commit-confirm`

Runs `commit` in approval-first mode: it proposes commit groups, messages, and files, then waits for explicit approval before staging or committing.

Use it when you want to review the commit boundaries first. Requires `commit`.

It can usually be used without any additional guidance.

```text
$commit-confirm
```

### `diagnose`

Runs an evidence-first loop to prove the causes of an issue with 100% operational confidence:

1. Determine likely areas in the code causing an issue
2. Instrument the code around the issue with extensive logging
3. Reproduce the issue, with the agent if possible or asking the user if necessary
4. Collect the logs and analyze them
5. Determine confidence in the cause. If not fully confident, repeat.

Use it when a bug or issue is unclear, intermittent, platform-specific, performance-related, or too risky for guess-and-check editing. The agent runs the repro automatically when it can observe a safe deterministic result; otherwise it prepares logging or capture first and gives the user an exact manual reproduction step.

```text
$diagnose to find why the checkout button sometimes submits twice
```

```text
$diagnose startup performance to find the top contributors to first paint time.
```

### `diagnose-fix-loop`

Runs `diagnose` in an iterative improvement loop:

1. diagnose to find the top opportunities for improvement
2. Choose the top fix and implement it
3. Verify its success
4. If any useful fixes remain, repeat until no evidence-backed improvement remains

Use it when you want the agent to keep working through a bug or performance problem instead of stopping after the first plausible fix. Requires `diagnose`.

```text
$diagnose-fix-loop to reduce the Profile screen's load time
```

### `git-conflicts`

Detects an active rebase, merge, cherry-pick, or revert before starting new work. If the operation or intended resolution is not 100% clear, it stops before editing, staging, or continuing and asks for guidance with concrete options.

Use it for branch integration or when Git is already stopped in a conflict and you want to avoid destructive recovery commands or incorrect `ours`/`theirs` assumptions.

To start a rebase:

```text
$git-conflicts rebase on main
```

To fix a conflicted rebase/merge:

```text
$git-conflicts
```

### `legend-list-best-practices`

Best-practice guidance for building, auditing, and improving [`@legendapp/list`](https://github.com/LegendApp/legend-list) and `LegendList` usage. It helps improve blanking while scrolling, mount cost, row measurement, `renderItem` stability, and performance issues.

Use it when using a `LegendList` to improve performance and correctness.

It will often apply automatically when it sees Legend List usage.

```text
Use $legend-list-best-practices to audit ChatMessages.tsx
```

### `legend-state-best-practices`

Guidance for building, auditing, and fixing [`@legendapp/state`](https://github.com/LegendApp/legend-state) usage in React, React Native, and TypeScript code. It focuses on observable ownership, narrow reactive boundaries, field-level subscriptions, persistence, settings stores, and avoiding unnecessary re-renders.

Use it when using Legend State, building new new observables, auditing incorrect usage, replacing React state, or fixing reactive ownership and subscription boundaries.

It will often apply automatically when it sees Legend State usage.

```text
Use $legend-state-best-practices to move this selection state out of the parent and make each row subscribe only to whether its own selected state changed.
```

### `react-coding-style`

Guides React, React Native, and TypeScript to render less, less often.

Use it for maximizing React performance. It helps reduce render work without trading away correctness or adding memoization that no consumer uses.

```text
Use $react-coding-style to refactor this settings panel so changing one field does
not re-render every section. Preserve behavior and verify the new render boundaries.
```
