#!/usr/bin/env python3
"""Build compact, original campaign music locally (no AI service or video)."""

import math
import pathlib
import random
import shutil
import struct
import subprocess
import tempfile
import wave

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "app" / "src" / "main" / "assets" / "audio"
RATE = 22050

TRACKS = {
    "story": (82, 0, (0, 3, 7, 10), 24),
    "stage_market": (116, 2, (0, 4, 7, 11), 28),
    "stage_transit": (132, 5, (0, 3, 7, 9), 28),
    "stage_harbor": (104, -2, (0, 5, 7, 10), 28),
    "stage_palace": (142, 7, (0, 3, 6, 10), 28),
    "boss": (154, -5, (0, 3, 6, 8), 24),
    "final_boss": (166, -8, (0, 3, 6, 11), 24),
    "tally": (126, 9, (0, 4, 7, 12), 18),
    "ending": (94, 4, (0, 4, 7, 11), 24),
}

STINGS = {
    **{f"stage_{stage}_intro": (60 + stage * 2, True) for stage in range(1, 5)},
    **{f"stage_{stage}_clear": (72 + stage * 2, False) for stage in range(1, 5)},
}


def hz(note):
    return 440.0 * 2.0 ** ((note - 69) / 12.0)


def square(phase):
    return 1.0 if math.sin(phase) >= 0 else -1.0


def synth(name, bpm, transpose, chord, seconds, destination):
    random.seed(0xF04CE + sum(map(ord, name)))
    samples = []
    beat = 60.0 / bpm
    base = 45 + transpose
    melody = [0, 7, 12, 7, 3, 10, 7, 15, 12, 7, 4, 10, 7, 3, 0, 7]
    total = int(seconds * RATE)
    fade = int(0.08 * RATE)
    for index in range(total):
        time = index / RATE
        beat_index = int(time / (beat / 2))
        measure = beat_index // 8
        root = base + (chord[measure % len(chord)] if name != "story" else chord[(measure // 2) % len(chord)])
        bass_phase = 2 * math.pi * hz(root) * time
        lead_note = root + 12 + melody[beat_index % len(melody)]
        lead_phase = 2 * math.pi * hz(lead_note) * time
        local = (time % (beat / 2)) / (beat / 2)
        lead_env = max(0.0, 1.0 - local * 1.25)
        kick_local = (time % beat) / beat
        kick = math.sin(2 * math.pi * (58 - 26 * kick_local) * time) * max(0.0, 1 - kick_local * 5)
        hat_step = (time % (beat / 4)) / (beat / 4)
        hat = (random.random() * 2 - 1) * max(0.0, 1 - hat_step * 7)
        warmth = math.sin(bass_phase) * 0.18 + square(bass_phase) * 0.07
        lead = square(lead_phase) * lead_env * (0.13 if name == "story" else 0.18)
        rhythm = kick * (0.10 if name == "story" else 0.19) + hat * (0.025 if name == "story" else 0.06)
        value = warmth + lead + rhythm
        edge = min(1.0, index / fade, (total - index - 1) / fade)
        samples.append(max(-32767, min(32767, int(value * edge * 22000))))
    with wave.open(str(destination), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))


def synth_sting(name, root, rising, destination):
    seconds = 1.15
    samples = []
    notes = (root, root + (4 if rising else 3), root + 7, root + 12)
    for index in range(int(seconds * RATE)):
        time = index / RATE
        step = min(3, int(time / (seconds / 4)))
        note = notes[step if rising else 3 - step]
        local = (time % (seconds / 4)) / (seconds / 4)
        tone = square(2 * math.pi * hz(note) * time) * max(0.0, 1 - local) * 0.32
        shine = math.sin(2 * math.pi * hz(note + 12) * time) * max(0.0, 1 - local * 1.4) * 0.13
        samples.append(max(-32767, min(32767, int((tone + shine) * 24000))))
    with wave.open(str(destination), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))


def main():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required to encode compact OGG assets")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="family_force_audio_") as temp:
        temp_dir = pathlib.Path(temp)
        for name, specification in TRACKS.items():
            wav = temp_dir / f"{name}.wav"
            synth(name, *specification, wav)
            target = OUTPUT / f"{name}.ogg"
            subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-i", str(wav),
                            "-ac", "2", "-strict", "experimental", "-c:a", "vorbis", "-q:a", "3",
                            str(target)], check=True)
            print(f"built {target.relative_to(ROOT)} ({target.stat().st_size} bytes)")
        for name, specification in STINGS.items():
            target = OUTPUT / f"{name}.wav"
            synth_sting(name, *specification, target)
            print(f"built {target.relative_to(ROOT)} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
