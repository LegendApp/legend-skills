---
name: video-recording
description: Record running app flows, animations, and bug reproductions as videos, with continuous capture and verification of the exported motion timing. Use when producing or evaluating app recordings; use screenshot tooling for still images.
---

# Video Recording

Deliver a playable recording of the actual running app, with evidence that it
captures the requested behavior and preserves its timing. Keep recording
independent of navigation and inspection tools.

## Capture

- Identify the requested app, window or device, flow, and output location. Reuse
  an existing app session. Scope capture to that surface; an app with multiple
  windows needs an exact window selection, not whichever becomes foreground.
- Choose a continuous recorder. For native macOS, read
  [macos.md](references/macos.md) and use the window recorder supplied here or
  an already-working native recorder. For other targets, read
  [platforms.md](references/platforms.md). Prefer the environment's designated
  recording tool; do not install software or change permissions without the
  applicable authorization.
- Target 60 fps for animation review where supported; 30 fps can suffice for
  ordinary flows. A target or exported frame-rate label is not a measurement of
  captured motion. Preserve source sample timestamps when the recorder exposes
  them. Never assemble UI-tool screenshots into a video to judge animation
  smoothness: tool waits, focus changes, and request timestamps distort motion.
- Verify capture permission and available disk space before starting. Honor the
  session's reserve, monitor at least every 30 seconds during writing, retain
  process handles, and bound recording duration. Do not delete artifacts without
  authorization. Stop at permission or capacity failures; surface the blocker
  rather than silently substituting a low-rate capture.
- Record a 3–5 second calibration of known continuous motion. Verify it before
  the full run. Do not accept black frames or a still screenshot as calibration.
- Start recording and await the recorder's ready signal before navigation. Allow
  a short lead-in, traverse the flow with deliberate pauses, then allow a tail.
  Record uninterrupted across tool calls; inspection may wait for UI stability,
  but the recorder must not. Always stop/finalize, including after an error, and
  verify that this thread's recorder has stopped.

## Verify and deliver

Keep the original recording. Optional edits may trim known setup or settled
pauses, but preserve the timing of motion, failures, and transitions under
review. Do not interpolate motion, speed up animations, or replace missed
frames to conceal a capture failure. Disclose any edits.

Read [verification.md](references/verification.md). Run the verifier on the
final exported video using intervals where motion is expected, and source
timings when available:

```sh
python3 scripts/verify-video.py flow.mp4 --motion 1.2:2.4 --motion 5.1:6.3 \
  --timings flow.mp4.frames.jsonl --report flow.quality.json
```

Watch every requested transition at normal speed in a supported video player.
A contact sheet establishes coverage, not smoothness. Automated checks flag
stalls; they cannot alone establish their cause or certify visual quality.
Distinguish observed app behavior, capture defects, and unresolved uncertainty.
Do not report passed verification based only on a successful export or decode.

Embed or link the final video. Briefly report duration, actual cadence evidence
and limitations, requested flow coverage, edits, and sizable intermediates.
If recording is blocked, deliver the exact blocker and prepared command or flow
instead of presenting still captures as a faithful video.
