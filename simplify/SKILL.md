---
name: simplify
description: "Simplify the requested code or diff while preserving behavior and meaningful coverage."
---

# Simplify

Produce the smallest clear implementation that fully satisfies the required behavior. Minimize concepts and moving parts, not line count.

## Cadence

- Before adding code, decide the smallest change that meets the requirement; each new concept must earn its place.
- During construction, apply the priorities locally while discovering behavior. Allow clearly temporary instrumentation or scaffolding when it accelerates learning.
- At convergence, once a logical behavior slice passes, simplify that slice, remove superseded attempts and scaffolding, and rerun focused validation.
- For an explicitly requested branch audit, compare with the intended base. Otherwise review only the requested change; do not broaden a small cleanup into a whole-branch audit.

## Workflow

1. Identify the required behavior, invariants, constraints, and non-goals.
2. Inspect the relevant diff and separate it into logical concepts. For a final branch audit, compare the full branch with its merge base and check history for superseded attempts when relevant.
3. Inspect the existing owners, sources of truth, common path, decision points, and nearby code style before adding anything.
4. Choose the design with the fewest necessary concepts and the least work at runtime.
5. When changes are requested, implement directly and reuse existing mechanisms where they fit.
6. Validate behavior with checks proportional to the risk.
7. Review the final code, tests, names, comments, documentation, configuration, and relevant history for anything that no longer earns its complexity.

## Simplification Priorities

- Match the repository's existing style and patterns: naming, file layout, error handling, test style, and the libraries it already uses. Do not introduce a new pattern where an existing one fits.
- Prefer deletion, reuse, or a direct change over a new abstraction.
- Keep one source of truth; avoid mirrored state, overlapping guards, duplicate registries, and compensating mechanisms.
- Where the repository has no convention, prefer straightforward positive control flow over early-return chains or empty branches.
- On hot paths, minimize allocations, callback recreation, subscriptions, renders, passes, I/O, and native work.
- For prose, remove repetition and keep the shortest wording or example that remains self-sufficient.

## Over-engineering Checklist

Remove these when they serve no required behavior, invariant, useful clarity, measured performance need, or existing repository convention:

- one-use helpers that can be inlined instead;
- defensive null or type checks for states the types or callers already rule out;
- config flags, options, or parameters for variation no current caller needs;
- wrapper types or classes that only forward;
- new files, modules, or abstractions where an existing owner fits;
- fallback, compatibility, or migration paths the task does not require;
- try/catch blocks that swallow errors or silently fall back;
- speculative generality: extension points or cases nothing uses yet.

## Existing Work

Establish a passing baseline before simplifying working code. Test one questionable concept at a time, rerun the relevant validation, and restore it if behavior or meaningful coverage weakens. Do not restructure several accumulated fix attempts before establishing which changes are causally necessary.

When duplicate or ineffective regression coverage is suspected, deliberately break the claimed invariant and confirm the remaining test fails. Passing tests alone do not prove that every test or implementation concept is necessary.

Do not rewrite branch history without authorization.

## Performance Changes

Name the exact common-path work being removed: allocations, scans, mounts, renders, subscriptions, I/O, or native calls. Control-flow evidence plus regression tests can justify removing work that is structurally unused. Require a benchmark, profile, or repeated repro when an optimization changes semantics or introduces a tradeoff. Do not add complexity for theoretical gains.

## Guardrails

- Preserve correctness, required behavior, type safety, distinct regression coverage, and useful clarity.
- Do not replace clear code with compressed or clever code merely to reduce lines.
- Make scoped, behavior-preserving improvements directly. If a simplification beyond the requested change would alter a public API or add a new concept, explain and suggest it instead.
- Leave unrelated and user-authored changes untouched.

Stop when every remaining concept supports a requirement, invariant, useful clarity, existing repository convention, or measured performance need. Report only material simplifications, validation, and unresolved opportunities.
