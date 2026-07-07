# Legend Skills

Reusable agent skills for debugging, React/TypeScript style, and Legend ecosystem optimization.

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
npx skills add LegendApp/legend-skills --skill legend-list-optimization
npx skills add LegendApp/legend-skills --skill legend-state-optimization
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

- `commit`: creates one or more clean logical git commits using repository commit-message conventions.
- `commit-confirm`: proposes commit groups and waits for `go` before staging or committing.
- `diagnose`: disciplined debugging loop for hard bugs, browser bugs, app/device bugs, and performance regressions.
- `diagnose-fix-loop`: iterates diagnosis, a scoped fix, verification, and fresh diagnosis until no useful fix remains.
- `git-conflicts`: runs or continues rebases, merges, cherry-picks, and conflict resolution safely.
- `react-coding-style`: React, React Native, and TypeScript implementation style focused on small render surfaces and stable identities.
- `legend-list-optimization`: optimization and debugging guidance for `@legendapp/list` and `LegendList`.
- `legend-state-optimization`: effective Legend State usage for React, React Native, and TypeScript code.

## Dependency Policy

Skills may depend on another skill when that avoids copying a shared workflow. A dependent skill must clearly name its dependency, stop before acting if the dependency is unavailable, tell the user how to install the missing skill, and keep only the instructions that modify or extend the dependency's behavior.
