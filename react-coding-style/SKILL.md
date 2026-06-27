---
name: react-coding-style
description: React, React Native, and TypeScript implementation style focused on small render surfaces, stable identities, direct data flow, and minimal effects. Use when changing components, hooks, callbacks, subscriptions, context/state reads, list rows, render-sensitive code, or TypeScript UI architecture; when avoiding unnecessary re-renders, large dependency arrays, broad state propagation, effect-heavy control flow, compatibility shims, or premature abstractions matters.
---

# React Coding Style

## Overview

Use this skill to keep React and TypeScript changes local, predictable, and render-conscious. Treat re-render avoidance as a design constraint, but do not add complexity without a measured or clearly reasoned benefit.

Prefer the correct architecture first. Do not preserve awkward old shapes with compatibility shims unless there is an explicit external contract, migration requirement, or staged rollout need.

This is a style skill, not a debugging workflow. For unclear bugs, regressions, logging, browser/app automation, or performance diagnosis, use `diagnose` first and return here for implementation shape.

## First Pass

Before changing code, inspect the nearby patterns:

- Prefer existing repo helpers such as memo wrappers, observer wrappers, latest-ref hooks, stable-callback hooks, selector hooks, or local observable helpers over inventing a new pattern.
- Identify which values must update the UI and which values only need to be read by an event handler, async task, subscription, or imperative bridge.
- Find the smallest component or selector that actually needs each dynamic value.
- Identify the best ownership, data-flow, and API shape before preserving existing call sites. If the existing structure is wrong, prefer updating it directly over adding a wrapper, adapter, alias, fallback path, or bridge layer.

## Render Boundaries

Avoid broad re-renders by default.

- Keep parent components structurally stable. Let parents choose layout and composition; let leaves read volatile state.
- Move changing data reads to the smallest leaf node that displays or acts on them.
- Prefer selector-style subscriptions that return exactly the value needed instead of subscribing a broad parent to an entire object.
- Split a component when it prevents unrelated siblings from re-rendering, clarifies data ownership, or lets a memo/observer boundary be meaningful.
- Avoid passing freshly created objects, arrays, functions, or inline component definitions through hot paths unless the receiving boundary is supposed to update.
- Use memoization as a boundary around stable props, not as a substitute for fixing state shape or prop churn.
- When a re-render is required, make it intentional and local. Add a test or runtime evidence for render-sensitive behavior when the change touches lists, layout, virtualization, or subscriptions.

## Callbacks And Freshness

Prefer stable callbacks with fresh reads over large dependency arrays.

- Use a local `useStableCallback` helper when available for event handlers that need current values without changing identity.
- Use a latest-ref pattern, such as `useLatestRef`, for imperative callbacks, animation frame coalescers, event listeners, or bridges that must stay stable while seeing fresh inputs.
- Keep `useCallback` for simple callbacks with small, honest dependencies or where the existing codebase already uses it plainly.
- Treat a large dependency array as a design smell. Look for a smaller data boundary, a stable callback, a ref, a selector, or moving the code into the event site.
- Do not silence exhaustive-deps as the first move. Only suppress it when the code intentionally captures an initial value or uses a stable/freshness pattern that makes the dependency irrelevant.
- Avoid callback chains where each callback exists only to stabilize another callback. Collapse the logic or move it closer to the leaf.

## Effects

Avoid `useEffect` unless the code is synchronizing with something outside render.

- Prefer deriving values during render, `useMemo` for expensive pure derivations, event handlers for user actions, and explicit state initialization for initial values.
- Use effects for subscriptions, timers, DOM/native listeners, async lifecycle work, measurements, or cleanup.
- Keep effects narrow: one synchronization concern per effect, with explicit cleanup when a resource is registered.
- Avoid effect-driven state copying. If state can be computed from props or existing state during render, compute it there.
- Avoid using effects as command dispatch after state changes when the command can run directly in the event or mutation path.
- Be skeptical of effects that exist only to keep two pieces of local state in sync.

## State Shape

Keep state close to the consumer and avoid bouncing state through parents.

- Prefer local state for truly local UI concerns and external/store state for shared or cross-screen concerns.
- Store canonical data once. Derive views, filters, counts, and display groupings close to where they are rendered.
- Preserve object identity when publishing no-op or equivalent updates. Avoid cloning or spreading data just to touch a path.
- For mutable or observable models, prefer field-level reads/bindings and leaf observers over reading a full object in a parent.
- Use `peek`-style non-reactive reads only in event handlers or imperative code where UI reactivity is not intended.

## Dependency Discipline

Use dependency arrays as a signal about design quality.

- Empty dependencies are acceptable for true one-time initialization, stable object construction, or callbacks that read through refs/observables intentionally.
- Small dependency arrays are fine when they directly model pure derivation.
- Large dependency arrays usually mean too much logic is in one component or the wrong abstraction owns freshness.
- Do not add dependencies mechanically if doing so changes identity in a hot path without improving correctness.
- When changing dependencies, reason through whether the output should update on each dependency change and whether that update should rerender this component or a smaller child.

## Implementation Shape

Keep changes direct and behavior-preserving.

- Prefer simple conditionals and local guards over early-return-heavy flows when a single guarded block keeps behavior readable.
- Avoid compatibility shims by default. A shim is justified only for a real public API contract, cross-version migration, third-party integration, or explicitly requested staged rollout; otherwise update the callers and remove the obsolete shape.
- Try the best architecture first rather than layering around a bad boundary. If the smaller direct fix requires touching more call sites, make the coherent change instead of adding indirection that future work must unwind.
- Preserve the existing public surface and local naming style unless the task requires otherwise.
- Add abstractions only when they remove real duplication, clarify ownership, or create a useful render/subscription boundary.
- Keep instrumentation temporary unless it is explicitly part of the product or test surface.
- Validate render-sensitive fixes with focused tests, runtime logs, or UI evidence that proves the intended boundary changed.
