---
name: legend-state-best-practices
description: Use Legend State and @legendapp/state effectively in React, React Native, and TypeScript code. Use when implementing, auditing, introducing, or refactoring observables, replacing prop-drilled React state, removing manual subscription bridges, designing settings/session stores, choosing reactive ownership boundaries, preferring useValue/useObserveEffect/peek patterns, migrating deprecated use$/useSelector usage, or reducing re-renders with field-level reactive boundaries.
---

# Legend State Best Practices

## Overview

Use this skill for Legend State-specific reactive ownership, subscription, persistence, and API guidance. For unclear bugs, regressions, logging, browser/app automation, or performance measurement, use `diagnose` for the core loop first.

Use Legend State to move reactive ownership to the smallest useful boundary. Prefer it when state would otherwise be copied through parents, mirrored by effects, or fanned out through props just to update leaf UI.

## Authoritative References

This skill is not a complete Legend State API reference. Use it for review policy and implementation judgment. For exact imports, signatures, persistence/sync setup, and version-specific behavior, verify the installed package version, inspect local source/tests and nearby project usage, and consult the current docs:

- Human docs: https://legendapp.com/open-source/state/v3/intro/introduction/
- LLM docs index: https://legendapp.com/open-source/state/v3/llms.txt
- Full LLM docs: https://legendapp.com/open-source/state/v3/llms-full.txt

Prefer `llms.txt` for targeted doc lookup. Use `llms-full.txt` only when the task is broad enough to need the full documentation context.

## Modes

Use one of three modes:

- **Build mode**: when creating new Legend State usage, verify the installed version, consult the docs above for exact API shape, then choose observable ownership, subscription boundaries, persistence/sync setup, and validation before writing code.
- **Audit mode**: when reviewing existing usage, inspect ownership, render subscriptions, non-reactive reads, effects, persistence boundaries, and hot paths. Rank findings by likely user impact and confidence, and distinguish proven misuse from optional cleanup.
- **Implementation mode**: when fixing incorrect usage, first run the same audit as audit mode, state a ranked implementation plan for non-trivial rewrites, and stop for explicit approval such as `go` when the fix changes ownership, persistence, or broad render behavior. After approval, implement the high-confidence fixes in narrow reviewable slices and validate the changed behavior.

Do not split analysis and implementation into separate mental models. The audit should recommend the same ownership and boundary shapes you would be willing to implement, and fixes should address the proven misuse rather than applying generic observable rewrites.

## First Pass

Before changing code:

- Search for existing observable helpers, store factories, persistence wrappers, and hook naming conventions.
- Check which Legend State major/API style the target uses. Prefer the current documented subscription hook for that version; in modern code this is usually `useValue`. Treat deprecated aliases as migration candidates when the target version documents them as deprecated.
- For non-trivial implementation, consult the docs above before inventing API shapes or persistence/sync configuration.
- Identify which values must update rendered UI and which values only need current reads inside commands, event handlers, native bridges, or async work.
- Find broad React state, context values, `useSyncExternalStore` bridges, or parent props that exist mostly to relay state to children.
- Check whether backward compatibility for persisted state is required. If resets are acceptable, prefer complete `initialValue` defaults over runtime default-merging helpers.
- When editing `legend-state` itself, preserve granular entrypoint boundaries and include public export/type coverage for surface changes.

## Ownership

Put state where it naturally changes and is consumed.

- Use observables for shared UI/session state, settings, document state, command state, selection state, and other values that have many narrow consumers.
- Use `useObservable` for component-owned state when nested UI needs field-level reactivity or command handlers need a stable observable handle.
- Keep truly local one-off UI state in React state when no broader ownership, imperative current read, or render fanout exists.
- Avoid copying observable values into React state unless integrating with a non-reactive API that requires it.
- Store canonical data once; derive display values with computed selectors or local render derivation.
- Keep app-specific persistence, file picking, native calls, and routing outside generic observable helpers.

## Reactive Boundaries

Subscribe at the leaf that needs the value.

- Prefer field-level reads such as `state.someField.get()` over reading a whole object in a parent.
- Use the target version's current React subscription hook for components that need observable values or selectors.
- Do not introduce deprecated subscription hooks. Replace them when changing nearby code if the version supports the replacement.
- Do not introduce new `observer` wrappers. If existing code already uses `observer`, preserve it unless the task is explicitly to migrate that area.
- Avoid unobserved `get()` calls in React render paths unless the target has configured auto tracking intentionally.
- For derived render values, subscribe to the derived result instead of subscribing broadly and comparing after render. Prefer `useValue(() => selectedIndex$.get() === index)` over `useValue(selectedIndex$) === index` so only rows whose rendered boolean changes need to rerender.
- Use built-in reactive components before inventing custom subscription plumbing: `Memo` for inline reactive text/children without parent rerender, `Computed` for a computed render fragment, `Show`/`Switch` for conditional UI, and `For` for observable arrays, objects, or maps.
- Avoid direct observable subscriptions in every hot row when a list-level invalidation or row-version signal is the intended boundary.
- Preserve stable parent structure. Let parents choose layout; let observable leaves read volatile values.

## Tracking Semantics

Be explicit about subscription breadth.

- `get()` tracks the node being read. `peek()` reads without tracking.
- `get(true)`, `Object.keys`, `Object.entries`, array length reads, and `For` list reads are shallow-style boundaries; use them when membership or shape changes matter but child field updates should stay in children.
- Accessing an observable object property does not subscribe by itself; the subscription happens when a tracked read such as `get()` occurs.
- Avoid selectors that return fresh broad objects unless that identity churn is intentional. Select the primitive or stable derived value the component actually renders.
- Use `batch` when multiple observable mutations should notify as one logical change outside an already batched path.

## Fresh Reads

Choose reactive or non-reactive reads intentionally.

- Use reactive reads when UI should update from the value.
- Use `peek` or equivalent non-reactive reads in event handlers, commands, async tasks, and imperative bridges when reading current state should not subscribe the caller.
- Use latest-ref or stable-callback patterns when integrating observables with external listeners that need fresh values but stable identities.
- Avoid large dependency arrays created only because React state is carrying values that could be read from the observable at the action boundary.

## React-To-Observable Mirrors

Treat `useEffect` or `useLayoutEffect` that calls `.set(...)`, `.assign(...)`, `mergeIntoObservable(...)`, or similar observable writes from React props, React state, or memoized render objects as a warning.

This is usually an anti-pattern when the observable exists only to relay the latest React-rendered value to children. It makes React the real owner and turns the observable into a delayed notification bus.

Prefer one of these instead:

- Make the observable the canonical owner and update it at the mutation or source boundary.
- Use `useObservable(() => derivedValue, deps)` or `useComputed` when an observable should be derived from explicit dependencies.
- Pass stable props directly when broad rerender is acceptable and matches the UI invalidation scope.
- Use latest refs or stable callbacks for imperative current reads.
- Keep commands and functions out of render-state observables unless UI truly renders from them.

Allowed effect writes are narrow: synchronize an observable change to an external imperative system, native bridge, storage, measurement cache, or lifecycle command where the effect is the integration boundary, not a mirror for render state.

## Effects

Prefer observable-driven effects for observable state changes.

- Use `observe`, `useObserve`, `useObserveEffect`, `when`, or `whenReady` when an observable change should trigger a command, cache invalidation, measurement reset, persistence action, or native update.
- Prefer observing the source of the change over waiting for a later React commit path when ordering matters.
- Keep effects narrow and cleanup explicit.
- Do not use effects to mirror observable values into React state, synchronize two local state variables, or dispatch commands that could run at the mutation site.
- Use `event()` for one-shot invalidation or command signals instead of ad hoc counters or boolean flip-flops.

## Persistence And Settings

Keep persisted observable stores simple.

- Put complete defaults in the store's `initialValue` when compatibility allows.
- Use typed field hooks for settings consumers instead of exposing manual subscribe/get bridges.
- Normalize at the field boundary when persisted values need validation.
- Preserve literal types with `const` generics or explicit store types when generic helpers would widen values.
- Audit sibling apps or packages before assuming they share the same anti-pattern.
- For real sync or local-first data, prefer `synced`, `configureSynced`, `syncState`, transforms, retry, `waitFor`, and the existing persist plugins over hand-rolled load/save effects.
- Keep storage transforms and validation at the persist/sync boundary so render consumers read the normalized local shape.

## Lists And Hot Paths

Treat observable reads inside virtualized rows carefully.

- Avoid making every row subscribe to broad theme, font, settings, or selection objects.
- In row fanout cases, look for `useValue(source$) === rowKey`, `useValue(source$).includes(rowKey)`, or similar local comparisons that rerender every subscriber on source changes. Replace them with a selector-style `useValue(() => source$.get() === rowKey)` or another primitive derived value when that matches the UI.
- Prefer row-local observables, row-version stamps, selector-style reads, or list `extraData` only when the invalidation scope matches the UI.
- For observable collections in React, consider `For` first: it shallow-tracks collection membership and passes `item$` to stable row components.
- Keep row geometry stable when using observables to blank or simplify expensive content.
- When observable changes affect measured sizes, invalidate the measured-size cache only if mounted rows cannot naturally remeasure the stale offscreen state.

## Validation

Match tests to the behavior changed.

- React selector or boundary changes: test that only intended consumers update.
- Core tracking changes: test tracked vs non-tracked reads and shape/membership subscriptions.
- Persistence or sync changes: test defaults, normalization, pending-change state, and metadata behavior.
- Public package-surface changes: run the package's typecheck and export-surface tests when available.

## Review Checklist

- Does each observable read intentionally subscribe this component?
- Can a broad parent read move into a smaller observed leaf?
- Can an event or command use a non-reactive current read instead of causing a render dependency?
- Does any `useEffect` or `useLayoutEffect` write to an observable from React props, React state, or memo values?
- Is an observable the canonical owner, or is it just mirroring a React value after commit?
- Could a React-to-observable mirror be replaced with source-boundary writes, `useObservable(() => value, deps)`, `useComputed`, stable props, or latest refs?
- Is an effect synchronizing with the outside world, or just compensating for state shape?
- Is a built-in reactive primitive (`useValue`, `Memo`, `Show`, `For`, `observe`, `when`, `event`) a simpler fit than a custom bridge?
- Did this change avoid adding deprecated subscription APIs?
- Are persisted defaults and normalization handled at one boundary?
- Are list rows protected from broad observable churn?
