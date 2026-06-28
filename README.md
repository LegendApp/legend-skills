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
npx skills add LegendApp/legend-skills --skill react-coding-style
npx skills add LegendApp/legend-skills --skill legend-list-optimization
npx skills add LegendApp/legend-skills --skill legend-state-optimization
```

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
- `react-coding-style`: React, React Native, and TypeScript implementation style focused on small render surfaces and stable identities.
- `legend-list-optimization`: optimization and debugging guidance for `@legendapp/list` and `LegendList`.
- `legend-state-optimization`: effective Legend State usage for React, React Native, and TypeScript code.
