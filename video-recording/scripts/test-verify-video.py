#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("verify-video.py")


class VideoChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="video-recording-checks-")
        cls.root = Path(cls.temp.name)
        cls.smooth = cls.root / "smooth.mp4"
        encode = ["-c:v", "libx264", "-threads", "2", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p"]
        def ffmpeg(*args):
            subprocess.run(["ffmpeg", "-v", "error", "-nostdin", *args], check=True)
        ffmpeg("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=60", "-t", "3", *encode, str(cls.smooth))
        ffmpeg("-i", str(cls.smooth), "-vf", "setpts=if(lt(N\\,60)\\,N\\,N+30)/60/TB",
               "-fps_mode", "cfr", *encode, str(cls.root / "stalled.mp4"))
        ffmpeg("-i", str(cls.smooth), "-vf", "tpad=stop_mode=clone:stop_duration=1", *encode, str(cls.root / "static-tail.mp4"))
        ffmpeg("-i", str(cls.smooth), "-vf", "select=not(between(t\\,1\\,1.5))",
               "-fps_mode", "vfr", *encode, str(cls.root / "gappy.mp4"))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def check_video(self, name="smooth.mp4", *args, code=0):
        process = subprocess.run([sys.executable, str(SCRIPT), str(self.root / name), *args], capture_output=True, text=True)
        self.assertEqual(process.returncode, code, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def sidecar(self, fps=60, missing_final=False, bad_status=False):
        header = {"type": "header", "schema": "video-recording-v1", "backend": "ScreenCaptureKit",
                  "windowId": 123, "timeOrigin": "first-complete-sample-pts", "targetFPS": 60}
        frames = [{"type": "frame", "t": i / fps, "status": 3 if bad_status and i == fps else 0}
                  for i in range(3 * fps + 1)]
        final = {"type": "final", "completed": True, "windowId": 123,
                 "completeFrames": sum(f["status"] == 0 for f in frames)}
        path = self.root / f"timings-{fps}-{missing_final}-{bad_status}.jsonl"
        path.write_text("\n".join(json.dumps(item) for item in [header, *frames, *([] if missing_final else [final])]))
        return str(path)

    def test_smooth_motion_passes(self):
        result = self.check_video("smooth.mp4", "--motion", "0.1:2.9")
        self.assertFalse(result["capture"]["available"])
        self.assertEqual(result["status"], "automated-motion-checks-passed")

    def test_cfr_freeze_fails_despite_sixty_fps_metadata(self):
        result = self.check_video("stalled.mp4", "--motion", "0.1:2.9", code=1)
        self.assertEqual(result["encodedFrameRate"], "60/1")
        self.assertIn("visible-stalls-during-expected-motion", [f["kind"] for f in result["findings"]])

    def test_intentional_static_tail_is_ignored_outside_motion(self):
        self.check_video("static-tail.mp4", "--motion", "0.1:2.9")
        self.check_video("static-tail.mp4", "--motion", "3.1:3.9", code=1)

    def test_vfr_capture_gap_fails(self):
        result = self.check_video("gappy.mp4", "--motion", "0.1:2.9", code=1)
        self.assertIn("export-frame-gaps", [f["kind"] for f in result["findings"]])

    def test_native_cadence_is_measured_instead_of_encoded_rate(self):
        self.check_video("smooth.mp4", "--motion", "0.1:2.9", "--timings", self.sidecar(), "--min-motion-fps", "60")
        result = self.check_video("smooth.mp4", "--motion", "0.1:2.9", "--timings", self.sidecar(20), "--min-motion-fps", "60", code=1)
        self.assertEqual(result["capture"]["cadence"][0]["medianCompleteFPS"], 20)

    def test_capture_must_finalize_and_suspended_samples_fail(self):
        self.check_video("smooth.mp4", "--motion", "0.1:2.9", "--timings", self.sidecar(missing_final=True), code=2)
        result = self.check_video("smooth.mp4", "--motion", "0.1:2.9", "--timings", self.sidecar(bad_status=True), code=1)
        self.assertIn("blank-suspended-or-stopped-source", [f["kind"] for f in result["findings"]])

    def test_missing_motion_or_invalid_intervals_cannot_pass(self):
        self.check_video(code=2)
        self.check_video("smooth.mp4", "--motion", "0:4", code=2)
        self.check_video("smooth.mp4", "--motion", "0:2", "--min-motion-fps", "60", code=2)

    def test_report_cannot_overwrite_video(self):
        size = self.smooth.stat().st_size
        self.check_video("smooth.mp4", "--motion", "0.1:2.9", "--report", str(self.smooth), code=2)
        self.assertEqual(self.smooth.stat().st_size, size)

    def test_malformed_sidecar_is_a_structured_error(self):
        path = Path(self.sidecar())
        path.write_text(path.read_text() + "\n[]\n")
        result = self.check_video("smooth.mp4", "--motion", "0.1:2.9", "--timings", str(path), code=2)
        self.assertEqual(result["status"], "error")

    def test_overflowing_sidecar_timestamp_is_a_structured_error(self):
        path = Path(self.sidecar())
        records = [json.loads(line) for line in path.read_text().splitlines()]
        records[1]["t"] = 10 ** 400
        path.write_text("\n".join(json.dumps(record) for record in records))
        result = self.check_video("smooth.mp4", "--motion", "0.1:2.9", "--timings", str(path), code=2)
        self.assertEqual(result["status"], "error")

    def test_error_report_cannot_create_a_missing_input(self):
        missing = self.root / "missing.mp4"
        self.check_video("missing.mp4", "--motion", "0:1", "--report", str(missing), code=2)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
