#!/usr/bin/env python3
"""Exercise the recorder's actual callback deadline gate without capture permission."""
import subprocess
import tempfile
from pathlib import Path


source = Path(__file__).with_name("record-macos.swift").read_text()
prefix = source.split("func parseOptions()", 1)[0]
harness = r'''
Task {
    do {
        try await boundedOperation("duplicate-callback", timeout: 0.2) { callback in
            callback(nil)
            callback(RecordingError("late duplicate must not resume twice"))
        }
        let start = ProcessInfo.processInfo.systemUptime
        do {
            try await boundedOperation("never-completes", timeout: 0.03) { _ in }
            fatalError("Missing callback must time out")
        } catch {
            precondition(String(describing: error).contains("timed out"))
            precondition(ProcessInfo.processInfo.systemUptime - start < 0.5)
        }
        do {
            try await boundedOperation("late-success", timeout: 0.03) { callback in
                DispatchQueue.global().asyncAfter(deadline: .now() + 0.08) { callback(nil) }
            }
            fatalError("Late success must not beat deadline")
        } catch {
            precondition(String(describing: error).contains("timed out"))
        }
        let result: Int = try await boundedResultOperation("value-result", timeout: 0.2) { callback in
            callback(.success(42))
            callback(.failure(RecordingError("late duplicate")))
        }
        precondition(result == 42)
        if #available(macOS 15.0, *) {
            for reason in ["incomplete", "stopped", "failed"] {
                let recorder = Recorder(file: .standardOutput)
                if reason != "incomplete" { recorder.started = true; recorder.origin = 1 }
                if reason == "stopped" { recorder.requestStop("signal") }
                if reason == "failed" { recorder.fail(RecordingError("delegate failed")) }
                var rejected = false
                do { _ = try recorder.announceReady(output: "unused", windowID: 1, fps: 60) }
                catch { rejected = true }
                precondition(rejected, "Never announce readiness after stop/failure or before a frame")
            }
            let recorder = Recorder(file: .standardOutput)
            recorder.started = true; recorder.origin = 1
            _ = try recorder.announceReady(output: "test-only", windowID: 1, fps: 60)
        }
        try await Task.sleep(nanoseconds: 150_000_000)
        do {
            try checkSpace(directory: NSTemporaryDirectory(), reserve: UInt64.max)
            fatalError("Insufficient headroom must refuse capture")
        } catch {
            precondition(String(describing: error).contains("Disk reserve"))
        }
        print("Callback deadlines, duplicate/late callbacks, readiness state, and reserve refusal passed.")
        exit(0)
    } catch {
        print(error); exit(1)
    }
}
RunLoop.main.run()
'''
with tempfile.TemporaryDirectory(prefix="video-recorder-lifecycle-") as directory:
    root = Path(directory)
    swift = root / "lifecycle.swift"
    swift.write_text(prefix + harness)
    subprocess.run(["xcrun", "swiftc", "-warnings-as-errors", str(swift), "-o", str(root / "test")], check=True)
    subprocess.run([str(root / "test")], check=True, timeout=5)
