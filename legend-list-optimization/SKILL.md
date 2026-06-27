---
name: legend-list-optimization
description: Optimize and debug Legend List usage in React, React Native, and web apps. Use when working with @legendapp/list, LegendList, virtualization, scroll blanking, mount cost, row measurement, maintainVisibleContentPosition, adaptive rendering, drawDistance, fixed-size rows, visible range callbacks, keyExtractor/getItemType/getFixedItemSize behavior, or list-related performance regressions.
---

# Legend List Optimization

## Overview

Use this skill for Legend List-specific invariants and remedies. For unclear bugs, regressions, logging, browser/app automation, or measurement strategy, use `diagnose` for the core loop first, then apply this skill to interpret list behavior.

Optimize Legend List by separating viewport work, buffered work, measurement work, and app row rendering. Do not assume `renderItem` is the bottleneck until mount, range calculation, data materialization, and row commit costs are separated.

## Diagnosis Order

Start with the actual symptom:

- **Blanking while scrolling**: inspect visible range calculation, draw distance, row commit cost, adaptive rendering, and whether fixed-size hints are accurate.
- **Slow mount**: inspect full-data passes, `keyExtractor`, `getItemType`, `getFixedItemSize`, initial layout readiness, and whether the data source is unnecessarily materialized.
- **Wrong scroll or highlight position**: inspect measured range state, mixed-height rows, MVCP, and whether the app is recomputing from offsets.
- **Jump-to-index or scrollTo issues**: separate user-driven jumps from programmatic lifecycle scrolls.
- **Layout jumps**: inspect row measurement, cached sizes, footer/header sizing, and `contentContainerStyle` vs list `style`.

## Viewport First

Prioritize the rows the user can see.

- Render the exact viewport first, then schedule buffer or draw-distance prewarm.
- Use visible-range and buffered-range concepts separately; do not treat overscan as equally urgent.
- For large user scroll jumps, prefer a visible-first pass plus one deduped follow-up pass to restore full draw distance.
- Keep programmatic scroll lifecycles conservative. Do not apply emergency user-jump behavior to initial scroll, scrollTo, scroll-to-end, or MVCP unless the contract is explicitly revisited.

## Adaptive Rendering

Use adaptive rendering to reduce row commit cost under pressure.

- Keep adaptive render opt-in and default to normal rendering when no config exists.
- Gate velocity-driven mode switching behind the list being ready to render.
- Light rows should preserve the same layout and geometry while blanking or simplifying expensive subcontent.
- Reset adaptive render immediately when the config is disabled, including pending timeouts.
- Do not use adaptive render to hide wrong measurement or range logic; fix those separately.

## Data And Mount Cost

Avoid unnecessary full-data work.

- If data is effectively index-addressed, avoid handing the list a fully materialized huge array when a bounded or estimated access path can work.
- Treat repeated `keyExtractor` calls as a signal to inspect both layout/index passes and structural data-change checks.
- Provide stable `keyExtractor`, `getItemType`, and `getFixedItemSize` when they match the data. Keep these callbacks cheap and identity-stable.
- For uniform fixed rows, align wrapper height, `getFixedItemSize`, and visual row layout.
- Do not chase row-render micro-optimizations when pre-render bookkeeping is the proven bottleneck.

## Measurement And Caches

Respect measured layout ownership.

- Verify whether mounted rows already call into size updates before clearing caches or forcing relayout.
- Clear only the cache that is stale. Use a size-only invalidation when measured sizes are stale but key and position identity should remain.
- Treat subpixel native measurement churn as real until proven otherwise; round or stabilize at the source if it causes repeated updates.
- Keep footer and header layout in the same measurement model as rows when scroll-at-end or MVCP depends on total content size.

## Range State

Use the list's computed state when available.

- Prefer `getState().start/end/startBuffered/endBuffered` or equivalent list-owned state over `offset / rowHeight` guesses, especially with mixed-height rows.
- Keep top-visible-item APIs narrow when the app only needs sidebar or outline sync. Avoid broad visible-range callbacks unless consumers need the full range.
- If the list reports at-end while the rendered buffered range lags the last index, investigate stale cached range paths rather than scroll position first.

## Layout Props

Keep viewport sizing distinct from content sizing.

- Put viewport sizing such as `flex: 1` on the LegendList `style` prop.
- Use `contentContainerStyle` for inner content layout only.
- Preserve stable dimensions for row content that participates in virtualization measurement.

## Validation

Use list-specific evidence.

- Validate blanking fixes with fast-scroll or jump fixtures, not just static tests.
- Validate measurement fixes with cases for mounted rows and offscreen cached rows.
- Keep performance fixes narrow; split adaptive render, visible range, MVCP, and representation changes into separate reviewable slices.
