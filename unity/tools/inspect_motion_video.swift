// Read-only OCR of the on-screen counter in a real Android screen recording.
// This counts visible frames, not the animator's internal catch-up loop logs.
import Foundation
import AVFoundation
import Vision

let input = CommandLine.arguments[1]
let asset = AVURLAsset(url: URL(fileURLWithPath: input))
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero
let seconds = CMTimeGetSeconds(asset.duration)
var seen = Set<Int>()
var observations = [[String: Any]]()
let regex = try NSRegularExpression(pattern: "FRAME\\s*(\\d+)\\s*/\\s*12", options: [.caseInsensitive])
for index in 0..<Int(seconds * 30) {
    autoreleasepool {
        let time = Double(index) / 30
        guard let image = try? generator.copyCGImage(at: CMTime(seconds: time, preferredTimescale: 600), actualTime: nil) else { return }
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.usesLanguageCorrection = false
        request.recognitionLanguages = ["en-US"]
        request.regionOfInterest = CGRect(x: 0, y: 0.71, width: 0.27, height: 0.19)
        try? VNImageRequestHandler(cgImage: image).perform([request])
        for result in request.results ?? [] {
            guard let text = result.topCandidates(1).first?.string else { continue }
            let ns = text as NSString
            if let match = regex.firstMatch(in: text, range: NSRange(location: 0, length: ns.length)),
               let frame = Int(ns.substring(with: match.range(at: 1))), (1...12).contains(frame) {
                seen.insert(frame)
                observations.append(["seconds": time, "frame": frame, "ocr": text])
            }
        }
    }
}
let output: [String: Any] = ["video": input, "duration": seconds,
    "visible_walk_frames": seen.sorted(), "unique_count": seen.count,
    "sample_fps": 30, "observations": observations,
    "limitation": "OCR proves visible counter states in emulator video; not natural gait quality or physical-device performance."]
let data = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted, .sortedKeys])
if CommandLine.arguments.count > 2 { try data.write(to: URL(fileURLWithPath: CommandLine.arguments[2])) }
print("VISIBLE_WALK_FRAMES=\(seen.sorted()) COUNT=\(seen.count)")
