#!/usr/bin/env python3
"""Exercise the recorder's actual callback deadline gate and run() refusals without capturing."""
import subprocess
import tempfile
from pathlib import Path


source = Path(__file__).with_name("record-macos.swift").read_text()
prefix = source.split("\ndo {\n    let options", 1)[0]
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
        if #available(macOS 15.0, *) {
            // Every case passes reserve UInt64.max, so a regressed guard still refuses before claiming outputs.
            let directory = CommandLine.arguments[1]
            try Data("keep".utf8).write(to: URL(fileURLWithPath: directory + "/existing.mp4.frames.jsonl"))
            func refuses(_ window: String, _ output: String, _ message: String, _ extra: [String: String] = [:]) async {
                var options = ["--window-id": window, "--output": directory + "/" + output, "--seconds": "1", "--reserve-bytes": String(UInt64.max)]
                options.merge(extra) { $1 }
                do { _ = try await run(options); fatalError("run() must refuse: \(message)") }
                catch { precondition(String(describing: error).contains(message), "\(error)") }
            }
            if !CGPreflightScreenCaptureAccess() {
                await refuses("1", "new.mp4", "permission denied")
                print("run() refused without Screen Recording permission.")
            } else {
                await refuses("1", "new.mov", "Require")
                await refuses("1", "new.mp4", "Require", ["--width": "321"])
                await refuses("1", "new.mp4", "Require", ["--seconds": "0"])
                await refuses(String(UInt32.max), "new.mp4", "not found")
                let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
                if let window = content.windows.first(where: { $0.frame.width > 0 && $0.frame.height > 0 }) {
                    let id = String(window.windowID)
                    await refuses(id, "missing/new.mp4", "Output directory must already exist")
                    await refuses(id, "existing.mp4", "already exists")
                    await refuses(id, "new.mp4", "Disk reserve")
                    print("run() refused invalid options, missing window/directory, existing outputs, and reserve.")
                } else {
                    print("run() refused invalid options and missing window; no on-screen window for path checks.")
                }
            }
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
    outputs = root / "outputs"
    outputs.mkdir()
    subprocess.run([str(root / "test"), str(outputs)], check=True, timeout=30)
    existing = outputs / "existing.mp4.frames.jsonl"
    assert list(outputs.iterdir()) == [existing], "run() refusals must not create files"
    assert existing.read_text() == "keep", "run() refusals must not overwrite outputs"
