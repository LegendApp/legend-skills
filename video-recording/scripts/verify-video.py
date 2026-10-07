#!/usr/bin/env python3
"""Check exported motion and optional native capture telemetry without rewriting video."""
import argparse
import json
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path


def interval(value):
    try:
        start, end = map(float, value.split(":"))
        if not all(map(math.isfinite, (start, end))) or not 0 <= start < end:
            raise ValueError()
        return start, end
    except ValueError:
        raise argparse.ArgumentTypeError("Expected START:END with 0 <= START < END.")


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Expected a finite positive number.")
    return number


def command(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode:
        raise ValueError(f"{args[0]} failed ({result.returncode}): {result.stderr[-3000:]}")
    return result


def overlap(start, end, windows):
    return max((max(0, min(end, b) - max(start, a)) for a, b in windows), default=0)


def gaps(times, windows, max_gap):
    return [{"start": round(a, 6), "end": round(b, 6), "gapMs": round((b - a) * 1000, 3)}
            for a, b in zip(times, times[1:])
            if b - a > max_gap and overlap(a, b, windows) > max_gap]


def read_timings(path, offset):
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if any(not isinstance(record, dict) for record in records):
        raise ValueError("Every timing record must be a JSON object.")
    if not records or records[0].get("schema") != "video-recording-v1" or records[0].get("backend") != "ScreenCaptureKit":
        raise ValueError("Timing sidecar must be native video-recording-v1 ScreenCaptureKit telemetry.")
    header, final = records[0], records[-1]
    if header.get("type") != "header" or header.get("timeOrigin") != "first-complete-sample-pts":
        raise ValueError("Unsupported timing origin/header.")
    if final.get("type") != "final" or not final.get("completed") or final.get("windowId") != header.get("windowId"):
        raise ValueError("Capture was not successfully finalized for the selected window.")
    frames = [f for f in records if f.get("type") == "frame"]
    if not frames:
        raise ValueError("Timing sidecar contains no source samples.")
    if any(type(f.get("status")) is not int or f["status"] not in range(6) for f in frames):
        raise ValueError("Unknown source frame status.")
    times = [float(f["t"]) - offset for f in frames]
    if not all(math.isfinite(t) for t in times) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("Source timestamps must be finite and strictly increasing.")
    complete = [t for t, f in zip(times, frames) if f.get("status") == 0]
    if len(complete) < 2:
        raise ValueError("Fewer than two complete source frames.")
    if final.get("completeFrames") != len(complete):
        raise ValueError("Sidecar complete-frame count does not match its final event.")
    return header, frames, times, complete


def verify(args):
    windows = args.motion or []
    if not windows:
        raise ValueError("Supply --motion START:END for expected continuous motion; metadata alone cannot verify smoothness.")
    if args.min_motion_fps and not args.timings:
        raise ValueError("--min-motion-fps requires native --timings; encoded fps cannot substitute.")
    if args.timing_offset and not args.timings:
        raise ValueError("--timing-offset requires --timings.")
    metadata = json.loads(command(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams",
                                   "-show_format", "-of", "json", str(args.video)]).stdout)
    if not metadata.get("streams"):
        raise ValueError("No video stream.")
    stream = metadata["streams"][0]
    duration = float(metadata["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0 or any(end > duration + 0.001 for _, end in windows):
        raise ValueError("Motion interval exceeds video duration.")
    if duration > 600:
        raise ValueError("Verifier is bounded to 600-second clips; split long recordings into documented segments.")
    timestamps = json.loads(command(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(args.video)]).stdout)
    times = [float(f["best_effort_timestamp_time"]) for f in timestamps["frames"]
             if "best_effort_timestamp_time" in f]
    if len(times) < 2 or not all(math.isfinite(t) for t in times) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("Export has missing/invalid decoded frame timestamps.")
    origin = times[0]
    times = [t - origin for t in times]
    filters = []
    if args.crop:
        filters.append(f"crop={args.crop[2]}:{args.crop[3]}:{args.crop[0]}:{args.crop[1]}")
    filters.append(f"freezedetect=n={args.noise_db}dB:d={args.freeze_ms / 1000}")
    # Decode errors must fail even when ffmpeg could conceal them and finish.
    detection = command(["ffmpeg", "-nostdin", "-hide_banner", "-v", "info", "-xerror",
        "-i", str(args.video), "-map", "0:v:0", "-vf", ",".join(filters), "-an", "-f", "null", "-"])
    freezes = []
    start = None
    for kind, value in re.findall(r"freeze_(start|end):\s*([-+\d.eE]+)", detection.stderr):
        point = float(value) - origin
        if kind == "start":
            start = point
        elif start is not None:
            freezes.append((start, point)); start = None
    if start is not None:
        freezes.append((start, duration))
    visible = [{"start": round(a, 6), "end": round(b, 6),
                "motionOverlapMs": round(overlap(a, b, windows) * 1000, 3)}
               for a, b in freezes if overlap(a, b, windows) >= args.freeze_ms / 1000]
    max_gap = args.max_gap_ms / 1000
    findings = []
    export_gaps = gaps([0] + times + [duration], windows, max_gap)
    if export_gaps:
        findings.append({"kind": "export-frame-gaps", "intervals": export_gaps})
    if visible:
        findings.append({"kind": "visible-stalls-during-expected-motion", "intervals": visible,
                         "cause": "unresolved: inspect capture evidence and app behavior"})
    capture = {"available": False}
    warnings = ["Automated motion checks do not replace normal-speed visual review."]
    if args.timings:
        header, samples, source_times, complete = read_timings(args.timings, args.timing_offset)
        if source_times[0] > min(a for a, _ in windows) or source_times[-1] < max(b for _, b in windows) - max_gap:
            raise ValueError("Capture timings do not cover the motion intervals; verify the raw video or supply its documented leading trim offset.")
        capture_gaps = gaps([source_times[0]] + complete + [source_times[-1]], windows, max_gap)
        bad = [{"t": round(t, 6), "status": f.get("status")} for t, f in zip(source_times, samples)
               if f.get("status") in (2, 3, 5) and any(a <= t < b for a, b in windows)]
        cadence = []
        for a, b in windows:
            selected = [t for t in complete if a <= t <= b]
            deltas = [y - x for x, y in zip(selected, selected[1:])]
            fps = 1 / statistics.median(deltas) if deltas else None
            cadence.append({"start": a, "end": b, "medianCompleteFPS": round(fps, 3) if fps else None})
        capture = {"available": True, "backend": header["backend"], "windowId": header["windowId"],
                   "sourceOutput": header.get("output"), "targetFPS": header.get("targetFPS"),
                   "completeFrames": len(complete), "cadence": cadence}
        if capture_gaps:
            findings.append({"kind": "complete-source-frame-gaps", "intervals": capture_gaps,
                             "cause": "source/capture stall; idle content and app pauses also create gaps"})
        if bad:
            findings.append({"kind": "blank-suspended-or-stopped-source", "samples": bad})
        if args.min_motion_fps:
            slow = [item for item in cadence if item["medianCompleteFPS"] is None or item["medianCompleteFPS"] < args.min_motion_fps * 0.98]
            if slow:
                findings.append({"kind": "insufficient-complete-source-cadence", "intervals": slow})
        warnings.append("Sidecar reports this recorder's native stream; it is not independent proof of app smoothness or artifact identity. Validate raw video if edits changed timing.")
    else:
        warnings.append("Capture telemetry unavailable: encoded FPS and decoded frame PTS can hide duplicated capture frames.")
    return {"status": "findings" if findings else "automated-motion-checks-passed", "video": str(args.video.resolve()),
            "durationSeconds": duration, "width": stream["width"], "height": stream["height"],
            "codec": stream["codec_name"], "sampleAspectRatio": stream.get("sample_aspect_ratio"),
            "encodedFrameRate": stream.get("avg_frame_rate"),
            "decodedFrames": len(times), "motionIntervals": windows, "capture": capture,
            "findings": findings, "warnings": warnings}


def crop(value):
    try:
        x, y, width, height = map(int, value.split(":"))
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError()
        return x, y, width, height
    except ValueError:
        raise argparse.ArgumentTypeError("Expected nonnegative x:y and positive width:height.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--motion", action="append", type=interval, help="Expected continuous motion START:END, seconds; repeatable.")
    parser.add_argument("--timings", type=Path, help="Native recorder .frames.jsonl sidecar.")
    parser.add_argument("--timing-offset", type=float, default=0, help="Seconds trimmed from the front of the native recording.")
    parser.add_argument("--min-motion-fps", type=positive, help="Require measured native cadence; needs --timings.")
    parser.add_argument("--max-gap-ms", type=positive, default=100)
    parser.add_argument("--freeze-ms", type=positive, default=150)
    parser.add_argument("--noise-db", type=float, default=-60, help="ffmpeg freezedetect tolerance, default -60 dB.")
    parser.add_argument("--crop", type=crop, help="Inspect moving region x:y:width:height (encoded pixels).")
    parser.add_argument("--report", type=Path, help="Write JSON to a new file; refuses overwriting inputs/existing files.")
    args = parser.parse_args()
    if not math.isfinite(args.timing_offset) or args.timing_offset < 0 or not math.isfinite(args.noise_db) or args.noise_db > 0:
        parser.error("Require nonnegative finite timing offset and finite noise-db <= 0.")
    protected = [args.video.resolve()] + ([args.timings.resolve()] if args.timings else [])
    can_write_report = args.report and not args.report.exists() and args.report.resolve() not in protected
    try:
        if args.report and not can_write_report:
            raise ValueError("Report already exists or names an input; choose a new path.")
        result = verify(args)
        code = 1 if result["findings"] else 0
    except (ValueError, OSError, KeyError, TypeError, OverflowError) as error:
        result = {"status": "error", "message": str(error)}
        code = 2
    output = json.dumps(result, indent=2)
    if can_write_report:
        try:
            with args.report.open("x") as handle:
                handle.write(output + "\n")
        except OSError as error:
            print(f"Cannot write report: {error}", file=sys.stderr)
            code = 2
    print(output)
    return code


if __name__ == "__main__":
    sys.exit(main())
