# Native macOS window capture

The supplied recorder uses ScreenCaptureKit's desktop-independent window filter
and native H.264 recording output. It requires macOS 15+, the Swift toolchain,
and Screen Recording permission for the controlling host. It does not request
permission, grant access, foreground apps, navigate, or capture the desktop.

Read `--help` first. Execute from an authorized scratch directory. Swift may
write compiler caches; check disk before invocation. A compiled executable may
be reused from the same scratch directory if subsequent invocations would
otherwise recompile it. Do not create duplicate build trees.

```sh
xcrun swift /absolute/skill/scripts/record-macos.swift --help
xcrun swift /absolute/skill/scripts/record-macos.swift --list
```

The list returns window IDs, titles, owner names and PIDs. Select the exact
audience/app window by that evidence; never choose by position in the list.
Re-list after a window is closed or recreated.

```sh
xcrun swift /absolute/skill/scripts/record-macos.swift \
  --window-id 12345 --output /absolute/scratch/flow.mp4 \
  --seconds 90 --fps 60 --width 1920 --reserve-bytes 50000000000
```

Set `--reserve-bytes` to the applicable session reserve (the example is 50 GB).
The recorder checks the output volume and startup data volume before writing,
estimates recording growth, and rechecks every 20 seconds. This is a cooperative
guard, not a quota or guarantee against simultaneous writers. Still retain its
process handle and follow the session's monitoring rules during compilation.

The process emits JSON `ready` only after native recording starts. Begin the
flow after that signal. Duration is bounded (maximum 600 seconds); SIGINT/SIGTERM
request graceful stop/finalization. Window enumeration, native start/stop
callbacks, and output finalization each have a 10-second deadline, including a
missing callback. A disk reserve failure also stops this recorder and returns nonzero. Never terminate other threads' recorders.

Outputs are the MP4, `.frames.jsonl` source timing sidecar, and `.capture.json`
metadata. Existing output files are refused. Frame sidecar `t` values are
native presentation timestamps relative to the first complete frame, not UI
tool request times. The ready signal and metadata expose the first frame's host
timestamp; correlate interaction markers to the video timeline rather than
assuming a key request happened at that exact frame. The stream may emit idle
samples on static content. Low cadence while intentionally still is expected.
Native output can end before the requested stop duration if the final content
stays idle; check the exported duration and disclose omitted trailing still time.

The entire selected window is captured, including any titlebar. If the requested
delivery is content-only, crop a verified, fixed content rectangle afterward,
preserve its aspect ratio, retain the original, and verify the cropped export.
Never remove a window switch from evidence of the app's behavior without
disclosing it.

## Blockers

- A preflight denial or ScreenCaptureKit error `-3801` is a permission blocker.
  Ask the user to enable Screen Recording for the indicated controlling host
  in System Settings and restart that host. Do not repeatedly prompt, alter TCC
  databases, retry under different identities, or use a screenshot-loop fallback.
- If permission is granted but displays are unavailable while windows exist,
  inspect display sleep/headless session state. When available, use the
  `macos-screen-capture-setup` skill. A bounded `caffeinate -u` wake followed by
  `caffeinate -d` for the recording may resolve sleep; re-probe afterward. Do not
  restart WindowServer or other shared services.
- If output has capture gaps during known motion, fix the capture path and
  repeat calibration. A complete source stream with visible stalls warrants
  app investigation; frame duplication alone cannot distinguish app and recorder.

Source APIs: [window filter](https://developer.apple.com/documentation/screencapturekit/sccontentfilter/init(desktopindependentwindow:)),
[frame interval](https://developer.apple.com/documentation/screencapturekit/scstreamconfiguration/minimumframeinterval),
[recording output](https://developer.apple.com/documentation/screencapturekit/screcordingoutput),
[frame status](https://developer.apple.com/documentation/screencapturekit/scframestatus).
