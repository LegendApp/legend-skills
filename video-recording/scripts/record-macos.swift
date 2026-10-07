import AppKit
import AVFoundation
import CoreGraphics
import Darwin
import Foundation
import ScreenCaptureKit

let usage = """
Usage: xcrun swift record-macos.swift --list
       xcrun swift record-macos.swift --window-id ID --output PATH.mp4
         --seconds N [--fps 60] [--width 1920] --reserve-bytes N

macOS 15+ continuous capture of exactly one existing window. No audio/cursor.
--seconds: 1...600; --fps: 1...120; --width: 320...3840.
--reserve-bytes is required; set it to the session's disk reserve.
Existing outputs are refused. Emits JSON ready/completed; SIGINT/TERM finalizes.
Outputs: PATH.mp4, PATH.mp4.frames.jsonl, PATH.mp4.capture.json.
Permission is checked, never requested or modified. --help prints this message.
"""

func emit(_ value: [String: Any], to handle: FileHandle = .standardOutput) {
    if let data = try? JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]) {
        handle.write(data + Data([10]))
    }
}

struct RecordingError: Error, CustomStringConvertible {
    let description: String
    init(_ description: String) { self.description = description }
}

final class CompletionGate<Value>: @unchecked Sendable {
    let lock = NSLock()
    var continuation: CheckedContinuation<Value, Error>?
    init(_ continuation: CheckedContinuation<Value, Error>) { self.continuation = continuation }
    func resolve(_ result: Result<Value, Error>) {
        lock.lock()
        let pending = continuation; continuation = nil
        lock.unlock()
        pending?.resume(with: result)
    }
}

func boundedResultOperation<Value>(_ name: String, timeout: Double = 10, _ operation: (@escaping @Sendable (Result<Value, Error>) -> Void) -> Void) async throws -> Value {
    try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Value, Error>) in
        let gate = CompletionGate(continuation)
        DispatchQueue.global().asyncAfter(deadline: .now() + timeout) {
            gate.resolve(.failure(RecordingError("Native \(name) callback timed out after \(timeout) seconds.")))
        }
        operation { gate.resolve($0) }
    }
}

func boundedOperation(_ name: String, timeout: Double = 10, _ operation: (@escaping @Sendable (Error?) -> Void) -> Void) async throws {
    try await boundedResultOperation(name, timeout: timeout) { callback in
        operation { error in callback(error.map { .failure($0) } ?? .success(())) }
    }
}

func availableBytes(_ path: String) throws -> UInt64 {
    var volume = statfs()
    guard statfs(path, &volume) == 0 else { throw RecordingError("Cannot measure disk: \(path)") }
    return UInt64(volume.f_bavail) * UInt64(volume.f_bsize)
}

func checkSpace(directory: String, reserve: UInt64, estimate: UInt64 = 0) throws {
    for path in Set([directory, "/System/Volumes/Data"]) {
        let available = try availableBytes(path)
        guard available > reserve, available - reserve > estimate else {
            throw RecordingError("Disk reserve reached or insufficient headroom: \(available) bytes available at \(path), reserve \(reserve), estimated growth \(estimate). Stop and obtain explicit cleanup/resume authorization.")
        }
    }
}

@available(macOS 15.0, *)
final class Recorder: NSObject, SCStreamOutput, SCStreamDelegate, SCRecordingOutputDelegate, @unchecked Sendable {
    let lock = NSLock()
    let file: FileHandle
    var origin: Double?
    var lastTime = 0.0
    var frameCount = 0
    var started = false
    var finished = false
    var failure: String?
    var stopReason: String?

    init(file: FileHandle) { self.file = file }

    func snapshot() -> (Bool, Bool, Double?, String?, String?) {
        lock.lock(); defer { lock.unlock() }
        return (started, finished, origin, failure, stopReason)
    }

    func announceReady(output: String, windowID: UInt32, fps: Int) throws -> Double {
        lock.lock(); defer { lock.unlock() }
        if let failure { throw RecordingError(failure) }
        guard stopReason == nil, started, let origin else { throw RecordingError("Stopped or incomplete before ready.") }
        let readyAt = ProcessInfo.processInfo.systemUptime
        emit(["type": "ready", "output": output, "windowId": windowID,
              "firstFrameHostSeconds": origin, "hostSeconds": readyAt, "targetFPS": fps])
        return readyAt
    }

    func requestStop(_ reason: String) {
        lock.lock(); defer { lock.unlock() }
        if stopReason == nil { stopReason = reason }
    }

    func fail(_ error: Error) {
        lock.lock(); defer { lock.unlock() }
        failure = String(describing: error)
        stopReason = "error"
    }

    func finalize(_ header: [String: Any]) -> [String: Any] {
        lock.lock(); defer { lock.unlock() }
        var final = header
        final["type"] = "final"; final["completed"] = finished && failure == nil
        final["firstFrameHostSeconds"] = origin
        final["lastFrameTime"] = lastTime; final["completeFrames"] = frameCount
        final["stopReason"] = stopReason; final["error"] = failure
        emit(final, to: file)
        return final
    }

    func stream(_ stream: SCStream, didStopWithError error: Error) { fail(error) }
    func recordingOutput(_ recordingOutput: SCRecordingOutput, didFailWithError error: Error) { fail(error) }
    func recordingOutputDidStartRecording(_ recordingOutput: SCRecordingOutput) {
        lock.lock(); started = true; lock.unlock()
    }
    func recordingOutputDidFinishRecording(_ recordingOutput: SCRecordingOutput) {
        lock.lock(); finished = true; lock.unlock()
    }

    func stream(_ stream: SCStream, didOutputSampleBuffer buffer: CMSampleBuffer, of type: SCStreamOutputType) {
        guard type == .screen, buffer.isValid,
              let attachments = CMSampleBufferGetSampleAttachmentsArray(buffer, createIfNecessary: false) as? [[SCStreamFrameInfo: Any]],
              let raw = attachments.first?[.status] as? Int,
              let status = SCFrameStatus(rawValue: raw) else { return }
        let pts = CMTimeGetSeconds(buffer.presentationTimeStamp)
        guard pts.isFinite else { return }
        lock.lock(); defer { lock.unlock() }
        if origin == nil && status == .complete { origin = pts }
        guard let origin else { return }
        lastTime = pts - origin
        frameCount += status == .complete ? 1 : 0
        emit(["type": "frame", "t": lastTime, "ptsHostSeconds": pts, "status": raw], to: file)
    }
}

func parseOptions() throws -> [String: String] {
    let args = Array(CommandLine.arguments.dropFirst())
    if args.contains("--help") { print(usage); exit(0) }
    if args == ["--list"] { return ["--list": "true"] }
    let allowed = Set(["--window-id", "--output", "--seconds", "--fps", "--width", "--reserve-bytes"])
    var options: [String: String] = [:]
    var i = 0
    while i < args.count {
        guard allowed.contains(args[i]), i + 1 < args.count, options[args[i]] == nil else {
            throw RecordingError("Invalid or duplicate option: \(args[i]). See --help.")
        }
        options[args[i]] = args[i + 1]; i += 2
    }
    return options
}

@available(macOS 15.0, *)
func run(_ options: [String: String]) async throws -> Int32 {
    guard CGPreflightScreenCaptureAccess() else {
        throw RecordingError("Screen Recording permission denied for the controlling host. Enable it in System Settings > Privacy & Security > Screen Recording, restart that host, then retry. No permission changes or fallback capture were attempted.")
    }
    let content: SCShareableContent = try await boundedResultOperation("window enumeration") { callback in
        SCShareableContent.getExcludingDesktopWindows(false, onScreenWindowsOnly: true) { content, error in
            if let error { callback(.failure(error)) }
            else if let content { callback(.success(content)) }
            else { callback(.failure(RecordingError("Window enumeration returned no content."))) }
        }
    }
    if options["--list"] != nil {
        emit(["type": "windows", "windows": content.windows.map { w in
            ["id": w.windowID, "title": w.title ?? "", "owner": w.owningApplication?.applicationName ?? "",
             "pid": w.owningApplication?.processID ?? 0, "width": w.frame.width, "height": w.frame.height] as [String: Any]
        }])
        return 0
    }
    guard let id = UInt32(options["--window-id"] ?? ""),
          let path = options["--output"], path.hasSuffix(".mp4"),
          let seconds = Double(options["--seconds"] ?? ""), seconds.isFinite, (1...600).contains(seconds),
          let reserve = UInt64(options["--reserve-bytes"] ?? ""),
          let fps = Int(options["--fps"] ?? "60"), (1...120).contains(fps),
          let width = Int(options["--width"] ?? "1920"), (320...3840).contains(width), width % 2 == 0 else {
        throw RecordingError("Require --window-id, --output .mp4, --seconds 1...600, --reserve-bytes, fps 1...120, and even width 320...3840. See --help.")
    }
    guard let window = content.windows.first(where: { $0.windowID == id }), window.frame.width > 0, window.frame.height > 0 else {
        throw RecordingError("Window \(id) not found. Re-list; do not capture another window as fallback.")
    }
    let output = URL(fileURLWithPath: path).standardizedFileURL
    let directory = output.deletingLastPathComponent().path
    var isDirectory: ObjCBool = false
    guard FileManager.default.fileExists(atPath: directory, isDirectory: &isDirectory), isDirectory.boolValue else {
        throw RecordingError("Output directory must already exist: \(directory)")
    }
    let sidecar = output.path + ".frames.jsonl"
    let metadata = output.path + ".capture.json"
    guard [output.path, sidecar, metadata].allSatisfy({ !FileManager.default.fileExists(atPath: $0) }) else {
        throw RecordingError("An output already exists. Choose a new name; nothing was overwritten.")
    }
    let height = max(2, Int(Double(width) * window.frame.height / window.frame.width) / 2 * 2)
    let estimate = UInt64(Double(width * height * fps) * seconds * 0.5) + 10_000_000
    try checkSpace(directory: directory, reserve: reserve, estimate: estimate)
    let descriptor = open(sidecar, O_WRONLY | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR)
    guard descriptor >= 0 else { throw RecordingError("Cannot exclusively claim sidecar/output stem; choose a new name.") }
    let file = FileHandle(fileDescriptor: descriptor, closeOnDealloc: true)
    defer { try? file.close() }
    let header: [String: Any] = ["type": "header", "schema": "video-recording-v1", "backend": "ScreenCaptureKit",
        "windowId": id, "ownerPID": window.owningApplication?.processID ?? 0,
        "output": output.path, "targetFPS": fps, "width": width, "height": height,
        "timeOrigin": "first-complete-sample-pts", "createdAt": ISO8601DateFormatter().string(from: Date())]
    emit(header, to: file)
    let recorder = Recorder(file: file)
    let diskGuard = DispatchSource.makeTimerSource(queue: .global())
    diskGuard.schedule(deadline: .now() + 20, repeating: 20)
    diskGuard.setEventHandler {
        do { try checkSpace(directory: directory, reserve: reserve) }
        catch {
            recorder.fail(error)
            emit(["type": "error", "message": String(describing: error)], to: .standardError)
        }
    }
    diskGuard.resume()
    defer { diskGuard.cancel() }
    let config = SCStreamConfiguration()
    config.width = width; config.height = height
    config.minimumFrameInterval = CMTime(value: 1, timescale: Int32(fps))
    config.queueDepth = 6; config.showsCursor = false; config.capturesAudio = false
    config.ignoreShadowsSingleWindow = true
    let stream = SCStream(filter: SCContentFilter(desktopIndependentWindow: window), configuration: config, delegate: recorder)
    try stream.addStreamOutput(recorder, type: .screen, sampleHandlerQueue: DispatchQueue(label: "video-recording.samples"))
    let recordingConfig = SCRecordingOutputConfiguration()
    recordingConfig.outputURL = output; recordingConfig.videoCodecType = .h264; recordingConfig.outputFileType = .mp4
    let recording = SCRecordingOutput(configuration: recordingConfig, delegate: recorder)
    try stream.addRecordingOutput(recording)
    let signals = [SIGINT, SIGTERM].map { number -> DispatchSourceSignal in
        signal(number, SIG_IGN)
        let source = DispatchSource.makeSignalSource(signal: number, queue: .global())
        source.setEventHandler { recorder.requestStop("signal-\(number)") }; source.resume()
        return source
    }
    defer { signals.forEach { $0.cancel() } }
    var startRequested = false
    do {
        startRequested = true
        try await boundedOperation("startCapture") { stream.startCapture(completionHandler: $0) }
        let waitingSince = ProcessInfo.processInfo.systemUptime
        while !recorder.snapshot().0 || recorder.snapshot().2 == nil {
            let state = recorder.snapshot()
            if let failure = state.3 { throw RecordingError(failure) }
            if state.4 != nil { throw RecordingError("Stopped before ready.") }
            if ProcessInfo.processInfo.systemUptime - waitingSince > 10 { throw RecordingError("No complete native frame/recording ready signal within 10 seconds.") }
            try await Task.sleep(nanoseconds: 50_000_000)
        }
        let readyAt = try recorder.announceReady(output: output.path, windowID: id, fps: fps)
        while ProcessInfo.processInfo.systemUptime - readyAt < seconds, recorder.snapshot().4 == nil {
            try await Task.sleep(nanoseconds: 100_000_000)
        }
        recorder.requestStop("duration")
    } catch { recorder.fail(error) }
    if startRequested {
        do { try await boundedOperation("stopCapture") { stream.stopCapture(completionHandler: $0) } }
        catch { recorder.fail(error) }
        let stoppingAt = ProcessInfo.processInfo.systemUptime
        while !recorder.snapshot().1, ProcessInfo.processInfo.systemUptime - stoppingAt < 10 {
            try await Task.sleep(nanoseconds: 50_000_000)
        }
        if !recorder.snapshot().1, recorder.snapshot().3 == nil { recorder.fail(RecordingError("Recording finalization timed out.")) }
    }
    do { try checkSpace(directory: directory, reserve: reserve) } catch { recorder.fail(error) }
    let final = recorder.finalize(header)
    try file.synchronize()
    try JSONSerialization.data(withJSONObject: final, options: [.prettyPrinted, .sortedKeys]).write(to: URL(fileURLWithPath: metadata), options: .withoutOverwriting)
    emit(final)
    return recorder.snapshot().3 == nil && recorder.snapshot().1 ? 0 : 1
}

do {
    let options = try parseOptions()
    if #available(macOS 15.0, *) {
        NSApplication.shared.setActivationPolicy(.prohibited)
        Task {
            do { exit(try await run(options)) }
            catch { emit(["type": "error", "message": String(describing: error)], to: .standardError); exit(2) }
        }
        RunLoop.main.run()
    } else { throw RecordingError("Native recorder requires macOS 15 or later.") }
} catch { emit(["type": "error", "message": String(describing: error)], to: .standardError); exit(2) }
