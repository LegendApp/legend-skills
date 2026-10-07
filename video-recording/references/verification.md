# Verify the delivered motion

The verifier requires Python 3, ffmpeg and ffprobe already installed. It reads
the video and optionally writes a small JSON report. It does not modify the
recording or install dependencies. Run `--help` for configurable thresholds.

Mark bounded intervals in seconds relative to the video where something should
be continuously moving. Exclude intentional delays and settled pauses. Use a
known calibration animation when the app's expected timing is uncertain. At
least one interval is required for the motion checks to return success.

```sh
python3 scripts/verify-video.py flow.mp4 --motion 1.2:2.4 \
  --max-gap-ms 100 --freeze-ms 150 --report flow.quality.json
```

The report separates:

- **Export timing:** decoded frame PTS gaps and frame-rate metadata. Constant
  frame-rate exports can repeat an old frame and still look perfect by PTS.
- **Visible stalls:** ffmpeg `freezedetect` runs overlapping expected motion.
  Codec noise and a very small/slow animation can affect detection. Inspect the
  flagged time, use `--crop x:y:width:height` for the moving region when useful,
  or tune the noise threshold; never relax checks just to label a clip smooth.
- **Capture timing:** optional native `.frames.jsonl` sample PTS and statuses.
  Complete-frame gaps, blank/suspended samples, or a stream failure during
  expected motion flag capture uncertainty. Idle status means the source did
  not change; a freeze with idle samples could be an app pause. Gaps alone do
  not establish cause. Normalize sidecar timestamps to the edited video with
  `--timing-offset` only when a documented single leading trim explains it;
  arbitrary edits require a corresponding timing map or raw-video validation.

`--min-motion-fps` optionally enforces measured complete-source median cadence
within motion intervals. It requires native timings. Do not apply a 60 fps
requirement to a backend that only supports 30; report the measured limitation.
The helper's header/final events must identify successful continuous native
capture. Merely supplying a timestamp file does not establish provenance.

Exit 0 means the requested automated checks passed, not that a human watched it
or that app motion is smooth. Exit 1 flags quality findings; exit 2 is a command,
decode, sidecar, or evidence error (including no motion intervals). Intentional
static content outside motion intervals does not fail. The report distinguishes
missing capture telemetry from zero dropped frames.

Watch the final export at normal speed and check the beginning, middle, and end
of every requested transition. In headless environments where playback is not
available, inspect dense ordered frame sequences around each transition, report
that limitation, and do not claim normal-speed visual review. A few thumbnails
or a contact sheet only verifies coverage. Do not classify a freeze as an app
bug until capture evidence or an independent native observation supports it.
