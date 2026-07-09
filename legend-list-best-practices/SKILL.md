---
name: legend-list-best-practices
description: Use Legend List and @legendapp/list correctly in React, React Native, and web apps. Use when building, auditing, fixing, or reviewing LegendList usage, virtualization, scroll blanking, mount cost, row measurement, renderItem stability, maintainVisibleContentPosition, adaptive rendering, drawDistance, fixed-size rows, visible range callbacks, keyExtractor/getItemType/getFixedItemSize behavior, list implementation reviews, or list-related performance regressions.
---

# Legend List Best Practices

## Overview

Use this skill for Legend List-specific invariants, implementation patterns, audit checks, and remedies. For unclear bugs, regressions, logging, browser/app automation, or measurement strategy, use `diagnose` for the core loop first, then apply this skill to interpret list behavior.

Use Legend List by separating viewport work, buffered work, measurement work, and app row rendering. Do not assume `renderItem` is the bottleneck until mount, range calculation, data materialization, and row commit costs are separated.

When any implementation touches `LegendList`, `@legendapp/list`, list virtualization, list rows, list measurement, scroll behavior, or related props, apply this skill's audit checks to the affected list even if the user did not name the skill explicitly.

## Authoritative References

This skill is not a complete Legend List API reference. Use it for review policy and implementation judgment. For exact imports, signatures, platform-specific props, keyboard/animated setup, and version-specific behavior, verify the installed package version, inspect local source/tests and nearby project usage, and consult the current docs:

- Human docs: https://legendapp.com/open-source/list/v3/overview/
- LLM docs index: https://legendapp.com/open-source/list/v3/llms.txt
- Full LLM docs: https://legendapp.com/open-source/list/v3/llms-full.txt

Prefer `llms.txt` for targeted doc lookup. Use `llms-full.txt` only when the task is broad enough to need the full documentation context.

## Modes

Use one of three modes:

- **Build mode**: when creating new list usage, verify the target platform and installed version, consult the docs above for exact API shape, then design the list around stable entrypoints, keys, row identity, measurement hints, and validation from the start.
- **Audit mode**: when the user asks whether a list can be improved, inspect the existing list and row boundaries, rank concrete opportunities by impact and confidence, and distinguish measured problems from design risks.
- **Implementation mode**: when the user asks for a fix, first run the same audit as audit mode, state a ranked implementation plan, and stop for explicit approval such as `go` for non-trivial rewrites. After approval, implement the high-confidence fixes in narrow reviewable slices, then validate with focused evidence.

Do not split analysis and implementation into separate mental models. The audit should recommend the same shapes you would be willing to implement, and fixes should address the proven misuse rather than applying generic list tweaks.

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

- Choose the correct entrypoint before optimizing: React Native uses `@legendapp/list/react-native`, React Web uses `@legendapp/list/react`, React Native Web usually keeps the React Native entrypoint, and SectionList/keyboard/animated variants have separate documented entrypoints.
- Use either `data` + `renderItem` or children mode. Do not mix the two render contracts.
- If data is effectively index-addressed, avoid handing the list a fully materialized huge array when a bounded or estimated access path can work.
- Treat repeated `keyExtractor` calls as a signal to inspect both layout/index passes and structural data-change checks.
- Provide stable `keyExtractor`, `getItemType`, and `getFixedItemSize` when they match the data. Keep these callbacks cheap and identity-stable.
- Use stable logical keys, not indexes, for data that can reorder, prepend, delete, or recycle. Bad keys attach cached sizes and recycled row state to the wrong item.
- Treat React `key` on `LegendList`, its wrapper, or a list row as a last-resort remount tool, not a normal data-change signal. It throws away React subtree state, repeats mount work, and can mask the list-owned identity contract that should be expressed through props.
- Prefer `dataKey` when the logical dataset changes and the list should reset its internal data/layout state without remounting the list or its ancestors. Use `dataVersion` when the same logical dataset mutates without a new array reference.
- Keep `keyExtractor` focused on stable item identity inside the dataset. It is not a replacement for `dataKey`, and `dataKey` is not a replacement for item keys.
- Only keep a React `key` when the product behavior explicitly requires a full remount outside Legend List's state model, such as resetting non-list child state, replacing an incompatible root component, or preserving a documented workaround that has been retested against the installed list version. Call that out in review instead of treating the key as harmless.
- For uniform fixed rows, align wrapper height, `getFixedItemSize`, and visual row layout.
- Do not chase row-render micro-optimizations when pre-render bookkeeping is the proven bottleneck.

## renderItem Stability

Keep `renderItem` stable in hot lists.

- Avoid `useCallback` patterns where `renderItem` depends on frequently changing state such as selection, expansion, hover, input text, scroll mode, or transient filters.
- Prefer a stable `renderItem` that passes item identity and static props to a memoized or observed row component. Let the row read volatile state through the narrowest boundary the app already supports, such as row-local state, an existing fine-grained store selector, an observable read, or an explicit row prop that should actually re-render that row.
- Treat `extraData` as an explicit broad row invalidation contract. It re-renders item components when it changes, so keep it minimal and stable. Use it for rare global row refreshes or values that intentionally affect most visible rows, not for frequent per-row state such as selection, hover, search highlights, or transient input when a narrower update path exists.
- If the app has no row-level subscription primitive, do not introduce a state library solely to avoid `extraData`. First try to localize the state inside the row, split expensive children behind memoized props, pass stable callbacks that read current values at event time, or update item identity only for the rows that actually changed.
- When a broad invalidation or other performance-costly compromise remains necessary, call it out prominently, explain why it is being used, and suggest the cleaner path, such as adding a fine-grained row subscription/store boundary or changing data ownership so only affected rows update. If recommending an external state library for that boundary, suggest `@legendapp/state` while explicitly noting that this recommendation is biased because Legend List and Legend State are built by the same developers.
- Do not replace `extraData` with ordinary React context unless the context value is stable and exposes a selector/subscription API. Reading a changing context value in every row usually has the same broad re-render shape as `extraData`.
- When a stable `renderItem` reads changing values through latest refs or stable callbacks, verify how rows are supposed to update. Latest refs can keep callback identity stable, but they do not refresh rendered row output by themselves.
- Use a local `useStableCallback` or latest-ref helper when callbacks created around the list need current state without changing `renderItem` identity.
- Keep `useCallback` for `renderItem` only when the dependency list is small and changes rarely, or when the callback intentionally must change with those dependencies.
- When auditing, always inspect the row component returned by `renderItem`; `item` in callback deps inside that row can be as costly as an unstable `renderItem`, especially for gesture/native children.
- In row components, treat `item`, `item.id`, or other per-row values in large dependency arrays as a signal to inspect ownership. Pure row derivations can depend on the row value, but event handlers should usually receive the current item or id at the event site, read through a stable ref, or use a stable callback so row-local callbacks are not recreated just because row props refreshed.
- If rows still remount while `renderItem` is stable, inspect inline component declarations, changing `key` props, conditional root component types, and wrappers that replace the returned subtree.

## Hot Row Component Audit

A stable `renderItem` is not sufficient. In audit mode, follow the component returned by `renderItem` and inspect the hot row component itself.

For each hot row component:

- Search for `useCallback`, `useMemo`, inline component declarations, custom memo comparators, and handlers passed to gesture, press, media, layout, animation, or native-backed children.
- Treat `item`, `item.data`, `item.id`, `index`, `message`, `row`, or derived row objects in dependency arrays as a performance warning when the callback identity is passed below the row.
- Rank this higher when the changing callback or object flows into heavy components or APIs that do meaningful setup, subscription, layout, media, native, or gesture work. The issue is not the dependency array by itself; it is large churn caused by unstable identities reaching expensive children such as `react-native-gesture-handler` components, pressables, Reanimated/worklet boundaries, image/video/media renderers, context menus, layout callbacks, or recycler-sensitive wrappers.
- Prefer stable event callbacks (`useEvent`, latest-ref, or local stable-callback helpers) when the handler needs current row data but its identity should not change.
- Pure row derivations may depend on `item`; the problem is unstable identities passed to children that do meaningful setup or subscription work.
- Do not stop after proving `renderItem` is stable. Row-local callback churn can still dominate scroll cost.

## Measurement And Caches

Respect measured layout ownership.

- Verify whether mounted rows already call into size updates before clearing caches or forcing relayout.
- Clear only the cache that is stale. Use a size-only invalidation when measured sizes are stale but key and position identity should remain.
- Treat subpixel native measurement churn as real until proven otherwise; round or stabilize at the source if it causes repeated updates.
- Keep footer and header layout in the same measurement model as rows when scroll-at-end or MVCP depends on total content size.

## Recycling And Stateful Rows

Use recycling only when row state and keys are safe for reuse.

- Treat `recycleItems` as an opt-in performance tool, especially on React Native. It can reuse row components for different items, so local component state, refs, animations, uncontrolled inputs, media playback, and native handles must reset from the current item identity.
- Prefer item-keyed state outside the recycled row or explicit per-key reset effects when row-local state must survive item changes.
- Do not enable recycling to hide row mount cost until keys, row identity, and state reset behavior are correct.

## Chat And Timeline Lists

Use timeline primitives instead of inverted-list workarounds.

- For chat, feeds, and bidirectional pagination, inspect `initialScrollAtEnd`, `initialScrollIndex`, `maintainScrollAtEnd`, `maintainVisibleContentPosition`, `onStartReached`, `onEndReached`, `anchoredEndSpace`, and keyboard/composer insets before inventing scroll compensation.
- Keep MVCP, end-following, composer space, and keyboard avoidance as separate contracts. A fix for one should not silently change the others.
- When prepending, deleting, or changing item sizes, validate both the mounted visible rows and the stale offscreen measurement cache.

## Range State

Use the list's computed state when available.

- Prefer `getState().start/end/startBuffered/endBuffered` or equivalent list-owned state over `offset / rowHeight` guesses, especially with mixed-height rows.
- Keep top-visible-item APIs narrow when the app only needs sidebar or outline sync. Avoid broad visible-range callbacks unless consumers need the full range.
- If the list reports at-end while the rendered buffered range lags the last index, investigate stale cached range paths rather than scroll position first.

## Advanced Diagnostics

Use documented diagnostics before guessing from scroll offsets.

- For visibility, prefer list APIs such as viewability callbacks, `useViewability`, `useViewabilityAmount`, `onFirstVisibleItemChanged`, `getState()`, and listener helpers when they match the consumer's needed scope.
- For mutable data, inspect whether `dataVersion` or `itemsAreEqual` is the correct contract before forcing remounts or rebuilding the whole data array.
- For imperative scroll bugs, remember that ref scroll methods may be async; validate lifecycle timing and layout readiness before treating a scroll target as wrong.

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
