---
name: diagnose
description: Disciplined diagnosis loop for hard bugs, browser bugs, app/device bugs, and performance regressions. Use when asked to debug, diagnose, investigate a bug, add logging, explain what is broken, reproduce a failure, or fix a regression with evidence.
---

# Diagnose

Use this skill to turn a symptom into evidence, a fix, and a regression check.

Start from the user's concrete anchor: file, route, error string, log line, screen, branch, bundle path, or repro step. If the user asks a question or asks what might be wrong, keep the pass read-only unless they ask for changes.

If present, use the repository's domain glossary, architecture notes, ADRs, and local test docs to understand the area before editing.

## Load References

Load only the references that match the task:

- Browser or React web bug: [browser-react.md](references/browser-react.md)
- iOS, Android, React Native, macOS, TV, or physical-device bug: [app-device.md](references/app-device.md)
- Runtime logs, probes, metrics, or temporary debug hooks: [instrumentation.md](references/instrumentation.md)

## Workflow

1. Build a feedback loop.
   Prefer the fastest deterministic pass/fail signal that reproduces the user's symptom: focused test, HTTP/CLI script, browser test, captured trace replay, throwaway harness, fuzz/repeat loop, app/device automation, or a structured human-in-the-loop script.

2. Reproduce the actual bug.
   Confirm the loop shows the same failure mode the user reported, not a nearby error. For flakes, raise the reproduction rate enough to debug.

3. Form falsifiable hypotheses.
   Generate 3-5 plausible causes with predictions. Show them to the user when the next step is expensive, high-risk, destructive, blocked on access, or the user explicitly asked for diagnosis before edits. Otherwise proceed with the strongest probe.

4. Instrument one boundary at a time.
   Prefer debugger/REPL inspection, then targeted logs or metrics. Probe the boundary that distinguishes hypotheses, not the visible symptom. If evidence is still not decisive, add a narrower probe before fixing.

5. Make the smallest credible fix.
   Fix the proven fault line. Do not stack speculative fixes. Revert failed experiments unless they are independently useful and intentionally kept.

6. Add regression coverage at the right seam.
   The test should exercise the real bug pattern as it occurs at the call site. If no correct seam exists, say so instead of adding a shallow test that gives false confidence.

7. Verify with the original loop.
   Re-run the original reproduction path, then the focused regression test, then broader checks only when the touched surface warrants them.

8. Account for temporary work.
   Keep diagnostic logs while diagnosis is ongoing. Remove them only when the user asks for cleanup or they become intentional durable diagnostics. If committing while logs remain, stage only the fix/test/product changes and leave temporary diagnostics unstaged.

## Stop Rules

Stop and ask for user input when:

- no credible feedback loop can be built from available code, tools, or artifacts
- the bug depends on inaccessible external state
- the next action is destructive or would transmit sensitive data
- the user explicitly requested read-only diagnosis and the next step would edit files

When blocked, report what was tried, what is still unknown, and the smallest artifact or access needed next.
