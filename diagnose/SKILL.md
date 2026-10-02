---
name: diagnose
description: "Use only when explicitly asked to run diagnose: investigate a bug through causal probes and recorded evidence."
---

# Diagnose

Use this workflow after an explicit diagnose or diagnose-fix-loop invocation. Ordinary bug reports and fix requests do not opt in.

Find and explain the cause of the requested symptom using discriminating evidence. Pursue stronger proof while a practical probe can change the conclusion; do not require a numeric confidence threshold before a credible, scoped fix.

Start from the user's concrete anchor: file, route, error, log, screen, branch, artifact, or reproduction step. Consult relevant architecture notes, ADRs, glossaries, and test docs. Inspect code, run safe tools or tests, and analyze existing artifacts.

Explicit invocation of Diagnose constitutes approval for behavior-neutral temporary instrumentation within the requested scope. Reuse authorization already present in the conversation or the diagnose-fix-loop invocation for scoped fixes. Ask only when a next action lacks that authorization or requires unavailable access or a material unresolved decision.

## References

Load only what applies:

- Browser or React web: [browser-react.md](references/browser-react.md)
- iOS, Android, React Native, macOS, TV, or physical device: [app-device.md](references/app-device.md)
- Logs, runtime probes, metrics, or debug hooks: [instrumentation.md](references/instrumentation.md)

## Evidence Loop

1. **Locate likely causes.** Inspect the code path and existing evidence around the user's anchor. Form the smallest useful set of likely areas and falsifiable candidate causes, including independent or contributing causes when applicable. Give each cause a distinguishing prediction and identify where those predictions diverge.

2. **Choose discriminating evidence.** Use existing tests, traces, and logs first. When they cannot distinguish the leading causes, load [instrumentation.md](references/instrumentation.md) and add temporary structured probes at the relevant boundaries. Instrument competing causes together when one reproduction can distinguish them.

   Before reproducing, define the probe contract:

   - the exact trigger and visible symptom
   - the questions this run will answer
   - each candidate cause's distinguishing prediction
   - the events, fields, and correlation IDs that test those predictions
   - how the evidence will be tied to the exact visible failure
   - the intended process, build, window, document, and runtime identity when applicable

   A baseline reproduction may establish the symptom before instrumentation. Before treating a reproduction as causal evidence, ensure its observations distinguish the leading candidates and confirm the exact symptom.

3. **Reproduce the issue.** Use the fastest deterministic signal that represents the reported symptom: focused test, script, browser test, trace replay, harness, repeat loop, profiler, app/device automation, or structured human reproduction. Run it when safe and observable. For intermittent failures, run enough repetitions to compare causes.

   When reproduction requires inaccessible state, credentials, devices, subjective interaction, or risky actions, first prepare the capture, exact steps, expected observation, and artifact to inspect. Ask the user to reproduce and reply `done`; confirm the returned evidence matches the reported failure.

   If the user corrects the trigger, affected component, lifecycle, or visible symptom, invalidate evidence and probes that target the previous interpretation. Return to cause location and instrumentation before reproducing again; do not continue with a nearby but mismatched reproduction.

4. **Collect and analyze.** Collect the complete output, correlate events across boundaries, compare it with each prediction, and record evidence for and against every cause. If the logs are incomplete or ambiguous, identify how the likely areas or instrumentation must change before another reproduction.

5. **Determine confidence.** Rank each cause by role (root, contributing, or alternative), `0-100%` confidence, supporting and conflicting evidence, and the next evidence that could change its score or rank. Treat scores as qualitative judgments, not calibrated statistical probabilities. Assign 100% operational confidence only when:

   - the exact symptom is reproduced
   - the causal chain from trigger to failure is observed
   - controlling the suspected boundary reliably controls the symptom
   - the cause or combination of causes explains every relevant observation
   - plausible alternatives are falsified or included as contributing causes
   - intermittent behavior is repeated enough to distinguish causality from coincidence

   If proof is incomplete, choose the safest practical probe likely to add discriminating evidence and state which results would raise, lower, or redistribute confidence. Revise the likely areas or instrumentation and repeat the loop only while such a probe exists; do not repeat an equivalent pass without changing its inputs, boundary, or instrumentation.

   Stop probing when no available probe should increase confidence, a pass adds no evidence and no distinct boundary remains, or the needed evidence requires unavailable access, user action, unacceptable risk, or disproportionate effort. Report Supported if the available evidence justifies a credible cause and scoped fix; otherwise report Incomplete. Never label unresolved proof as proven.

## Output

Lead with one status:

- **Proven — 100%:** every applicable cause meets the proof standard with no unresolved plausible alternative.
- **Supported:** evidence identifies a credible cause and scoped fix, with specific remaining uncertainty.
- **Incomplete:** available evidence does not yet support a credible cause or fix.

For **Proven** or **Supported**, report the cause, causal chain, decisive evidence, code or runtime boundary, and any remaining uncertainty. For **Incomplete**, rank candidates, explain why evidence is insufficient, and identify the smallest useful next probe. Always name the validation signal. Confidence scores are judgments, not measured probabilities.

## Temporary Diagnostics

Keep diagnostic logs until the user requests cleanup or they become durable diagnostics. If committing while temporary diagnostics remain, stage only intended durable changes and report what remains unstaged.

## Delegation

Use subagents only when the user explicitly requests delegation, subagents, parallel work, or token optimization. Delegate bounded mechanical collection to faster or cheaper agents: known commands or repro loops, logs, screenshots, traces, profiles, extraction, or artifact comparison. Give each task a success condition, output format, runtime boundary, and no-edit instruction unless mutation is explicit.

Keep feedback-loop design, hypothesis ranking, confidence scoring, ambiguous interpretation, and the final diagnosis in the main thread. Verify delegated evidence and inspect the working tree and background processes before continuing.
