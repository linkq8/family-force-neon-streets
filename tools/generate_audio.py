#!/usr/bin/env python3
"""Generate the project's original SNES-ready music and sound effects.

The generator intentionally uses only Python's standard library and
mathematical waveforms.  No recorded, sampled, or model-generated source
material is used, so every byte can be reproduced from this file.

Outputs:
  audio/stage_loop.it
  audio/{punch,jump,damage,pickup,confirm,victory}.wav
  audio/{punch,jump,damage,pickup,confirm,victory}.brr (when snesbrr exists)
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import wave


SFX_RATE = 8_000
IT_C5_RATE = 8_363
SFX_NAMES = ("punch", "jump", "damage", "pickup", "confirm", "victory")


class Noise:
    """Tiny deterministic PRNG used as a noise oscillator."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def sample(self) -> float:
        self.state = (1_664_525 * self.state + 1_013_904_223) & 0xFFFFFFFF
        return ((self.state >> 8) / 0xFFFFFF) * 2.0 - 1.0


def clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def fade_edges(samples: list[float], attack: int = 12, release: int = 48) -> list[float]:
    result = samples[:]
    for index in range(min(attack, len(result))):
        result[index] *= index / max(1, attack)
    for offset in range(min(release, len(result))):
        result[-1 - offset] *= offset / max(1, release)
    return result


def normalize(samples: list[float], peak_dbfs: float = -4.0) -> list[int]:
    peak = max(abs(value) for value in samples) or 1.0
    target = 10.0 ** (peak_dbfs / 20.0)
    scale = target / peak
    return [int(round(clamp(value * scale) * 32767.0)) for value in samples]


def punch_sfx() -> list[int]:
    count = 1_280
    noise = Noise(0x50554E43)
    phase = 0.0
    values: list[float] = []
    for index in range(count):
        time = index / SFX_RATE
        progress = index / count
        frequency = 155.0 - 105.0 * progress
        phase += math.tau * frequency / SFX_RATE
        body = math.sin(phase) + 0.35 * math.sin(phase * 0.49)
        transient = noise.sample() * math.exp(-time * 72.0)
        envelope = math.exp(-time * 24.0)
        values.append(body * envelope * 0.72 + transient * 0.48)
    return normalize(fade_edges(values, 4, 64), -3.5)


def jump_sfx() -> list[int]:
    count = 2_304
    phase = 0.0
    values: list[float] = []
    for index in range(count):
        progress = index / count
        frequency = 210.0 + 670.0 * progress * progress
        phase += math.tau * frequency / SFX_RATE
        triangle = 2.0 / math.pi * math.asin(math.sin(phase))
        shimmer = 0.18 * math.sin(phase * 2.01)
        envelope = (1.0 - math.exp(-progress * 28.0)) * (1.0 - progress) ** 0.55
        values.append((triangle * 0.80 + shimmer) * envelope)
    return normalize(fade_edges(values, 10, 96), -5.0)


def damage_sfx() -> list[int]:
    count = 3_072
    noise = Noise(0x44414D47)
    phase = 0.0
    previous_noise = 0.0
    values: list[float] = []
    for index in range(count):
        time = index / SFX_RATE
        progress = index / count
        frequency = 490.0 * (1.0 - progress) + 92.0
        phase += math.tau * frequency / SFX_RATE
        raw_noise = noise.sample()
        rough_noise = raw_noise - previous_noise * 0.55
        previous_noise = raw_noise
        buzz = math.sin(phase) + 0.40 * math.sin(phase * 1.47)
        wobble = 0.70 + 0.30 * math.sin(math.tau * 23.0 * time)
        envelope = math.exp(-time * 9.0) * (1.0 - progress)
        values.append((buzz * 0.55 + rough_noise * 0.34) * wobble * envelope)
    return normalize(fade_edges(values, 5, 112), -4.0)


def pickup_sfx() -> list[int]:
    count = 2_048
    notes = (659.255, 830.609, 1108.731)
    values = [0.0] * count
    note_length = 640
    for note_index, frequency in enumerate(notes):
        start = note_index * 480
        for local in range(note_length):
            index = start + local
            if index >= count:
                break
            time = local / SFX_RATE
            envelope = math.exp(-time * 25.0) * (1.0 - math.exp(-time * 180.0))
            tone = math.sin(math.tau * frequency * time)
            tone += 0.28 * math.sin(math.tau * frequency * 2.0 * time)
            values[index] += tone * envelope
    return normalize(fade_edges(values, 4, 80), -5.0)


def confirm_sfx() -> list[int]:
    count = 1_536
    values = [0.0] * count
    for start, frequency in ((0, 493.883), (640, 739.989)):
        for local in range(720):
            index = start + local
            if index >= count:
                break
            time = local / SFX_RATE
            envelope = math.exp(-time * 30.0) * (1.0 - math.exp(-time * 220.0))
            values[index] += (
                math.sin(math.tau * frequency * time)
                + 0.20 * math.sin(math.tau * frequency * 2.0 * time)
            ) * envelope
    return normalize(fade_edges(values, 4, 64), -6.0)


def victory_sfx() -> list[int]:
    count = 6_144
    values = [0.0] * count
    notes = (440.000, 554.365, 659.255, 880.000)
    starts = (0, 880, 1_760, 2_720)
    lengths = (1_160, 1_160, 1_280, 3_200)
    for note_index, (frequency, start, length) in enumerate(zip(notes, starts, lengths)):
        for local in range(length):
            index = start + local
            if index >= count:
                break
            time = local / SFX_RATE
            progress = local / length
            envelope = (1.0 - math.exp(-time * 150.0)) * (1.0 - progress) ** 1.7
            tone = math.sin(math.tau * frequency * time)
            tone += 0.24 * math.sin(math.tau * frequency * 2.0 * time)
            tone += 0.08 * math.sin(math.tau * frequency * 3.0 * time)
            values[index] += tone * envelope * (0.90 if note_index < 3 else 1.0)
    # A quiet final A-major chord makes the reward read clearly on tiny speakers.
    for frequency in (440.000, 554.365, 659.255):
        start = 3_200
        length = 2_700
        for local in range(length):
            index = start + local
            if index >= count:
                break
            time = local / SFX_RATE
            envelope = math.exp(-time * 5.5) * (1.0 - math.exp(-time * 90.0))
            values[index] += math.sin(math.tau * frequency * time) * envelope * 0.24
    return normalize(fade_edges(values, 4, 160), -4.5)


def write_wav(path: Path, samples: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = struct.pack(f"<{len(samples)}h", *samples)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SFX_RATE)
        wav_file.writeframes(payload)


def signed_byte(value: float) -> int:
    return max(-127, min(127, int(round(value))))


def music_samples() -> list[dict[str, object]]:
    lead: list[int] = []
    bass: list[int] = []
    for index in range(64):
        phase = (index % 16) / 16.0
        # Soft 25% pulse; the edge samples reduce BRR ringing.
        pulse = 83.0 if phase < 0.25 else -61.0
        edge = 13.0 * math.sin(math.tau * phase)
        lead.append(signed_byte(pulse + edge))
        triangle = 2.0 / math.pi * math.asin(math.sin(math.tau * phase))
        bass.append(signed_byte(triangle * 92.0))

    kick_noise = Noise(0x4B49434B)
    kick: list[int] = []
    phase = 0.0
    for index in range(768):
        time = index / IT_C5_RATE
        progress = index / 768
        phase += math.tau * (175.0 - 125.0 * progress) / IT_C5_RATE
        value = math.sin(phase) * math.exp(-time * 24.0) * 105.0
        value += kick_noise.sample() * math.exp(-time * 95.0) * 22.0
        kick.append(signed_byte(value))

    snare_noise = Noise(0x534E4152)
    snare: list[int] = []
    low = 0.0
    for index in range(1_024):
        time = index / IT_C5_RATE
        raw = snare_noise.sample()
        low = low * 0.62 + raw * 0.38
        high = raw - low
        body = math.sin(math.tau * 185.0 * time) * 0.25
        value = (high * 0.88 + body) * math.exp(-time * 22.0) * 105.0
        snare.append(signed_byte(value))

    hat_noise = Noise(0x48415421)
    hat: list[int] = []
    previous = 0.0
    for index in range(384):
        time = index / IT_C5_RATE
        raw = hat_noise.sample()
        high = raw - previous
        previous = raw
        hat.append(signed_byte(high * math.exp(-time * 54.0) * 76.0))

    return [
        {"name": "Street Pulse", "data": lead, "loop": True, "volume": 43},
        {"name": "Round Bass", "data": bass, "loop": True, "volume": 45},
        {"name": "Kick", "data": kick, "loop": False, "volume": 58},
        {"name": "Snare", "data": snare, "loop": False, "volume": 48},
        {"name": "Hat", "data": hat, "loop": False, "volume": 30},
    ]


NOTE_INDEX = {name: index for index, name in enumerate(("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"))}


def note(name: str, octave: int) -> int:
    """Return an Impulse Tracker note value (C-0 is 1)."""
    return 1 + octave * 12 + NOTE_INDEX[name]


def pattern_events() -> tuple[int, dict[int, list[tuple[int, dict[str, int]]]]]:
    rows = 128
    events: dict[int, list[tuple[int, dict[str, int]]]] = {row: [] for row in range(rows)}

    lead_bars = (
        (("E", 5), ("A", 5), ("C", 6), ("B", 5), ("A", 5), ("E", 5), ("G", 5), ("A", 5)),
        (("C", 6), ("A", 5), ("G", 5), ("E", 5), ("F", 5), ("A", 5), ("C", 6), ("A", 5)),
        (("F", 5), ("A", 5), ("D", 6), ("C", 6), ("A", 5), ("F", 5), ("E", 5), ("A", 5)),
        (("G#", 5), ("B", 5), ("E", 6), ("D", 6), ("B", 5), ("G#", 5), ("E", 5), ("B", 5)),
        (("A", 5), ("C", 6), ("E", 6), ("C", 6), ("B", 5), ("A", 5), ("E", 5), ("G", 5)),
        (("G", 5), ("E", 5), ("C", 6), ("G", 5), ("E", 5), ("D", 5), ("G", 5), ("E", 5)),
        (("A", 5), ("C", 6), ("F", 6), ("E", 6), ("C", 6), ("A", 5), ("G", 5), ("C", 6)),
        (("B", 5), ("G#", 5), ("E", 6), ("B", 5), ("D", 6), ("B", 5), ("G#", 5), ("E", 5)),
    )
    chords = (
        (("A", 3), ("C", 4), ("E", 4)),
        (("F", 3), ("A", 3), ("C", 4)),
        (("D", 3), ("F", 3), ("A", 3)),
        (("E", 3), ("G#", 3), ("B", 3)),
        (("A", 3), ("C", 4), ("E", 4)),
        (("C", 3), ("E", 3), ("G", 3)),
        (("F", 3), ("A", 3), ("C", 4)),
        (("E", 3), ("G#", 3), ("B", 3)),
    )

    for bar, melody in enumerate(lead_bars):
        base = bar * 16
        for step, pitch in enumerate(melody):
            row = base + step * 2
            events[row].append((1, {"note": note(*pitch), "instrument": 1, "volume": 41}))
            if row + 1 < rows:
                events[row + 1].append((1, {"note": 254}))

        chord = chords[bar]
        for step, offset in enumerate((0, 4, 8, 12)):
            pitch = chord[(step + bar) % 3]
            events[base + offset].append((2, {"note": note(*pitch), "instrument": 1, "volume": 25}))
            events[base + offset + 3].append((2, {"note": 254}))

        root = chord[0]
        fifth = chord[2]
        events[base].append((3, {"note": note(*root), "instrument": 2, "volume": 42}))
        events[base + 8].append((3, {"note": note(*fifth), "instrument": 2, "volume": 38}))

        for offset in (0, 8):
            events[base + offset].append((4, {"note": note("C", 5), "instrument": 3, "volume": 52}))
        for offset in (4, 12):
            events[base + offset].append((5, {"note": note("C", 5), "instrument": 4, "volume": 46}))
        for offset in range(0, 16, 2):
            hat_volume = 23 if offset % 4 == 0 else 17
            events[base + offset].append((6, {"note": note("C", 5), "instrument": 5, "volume": hat_volume}))

    # B00 is supported by SNESMOD and makes the loop intention explicit.
    events[127].append((1, {"command": 2, "parameter": 0}))
    return rows, events


def pack_pattern(rows: int, events: dict[int, list[tuple[int, dict[str, int]]]]) -> bytes:
    packed = bytearray()
    for row in range(rows):
        for channel, event in sorted(events[row], key=lambda item: item[0]):
            mask = 0
            if "note" in event:
                mask |= 0x01
            if "instrument" in event:
                mask |= 0x02
            if "volume" in event:
                mask |= 0x04
            if "command" in event:
                mask |= 0x08
            packed.extend((0x80 | channel, mask))
            if mask & 0x01:
                packed.append(event["note"])
            if mask & 0x02:
                packed.append(event["instrument"])
            if mask & 0x04:
                packed.append(event["volume"])
            if mask & 0x08:
                packed.extend((event["command"], event.get("parameter", 0)))
        packed.append(0)
    return struct.pack("<HHI", len(packed), rows, 0) + packed


def padded_ascii(text: str, length: int) -> bytes:
    return text.encode("ascii")[:length].ljust(length, b"\0")


def instrument_header(name: str, sample_number: int) -> bytes:
    header = bytearray()
    header.extend(b"IMPI")
    header.extend(b"\0" * 12)  # DOS filename
    header.extend((0, 0, 0, 0))  # zero, NNA=cut, duplicate check/action off
    header.extend(struct.pack("<H", 0))  # fadeout
    header.extend((0, 60, 128, 0xA0, 0, 0))  # PPS/PPC/GbV/DfP/RV/RP
    header.extend(struct.pack("<HBB", 0x0214, 1, 0))
    header.extend(padded_ascii(name, 26))
    header.extend((0, 0, 0, 0))  # filter cutoff/resonance, MIDI channel/program
    header.extend(struct.pack("<H", 0))  # MIDI bank
    for tracker_note in range(120):
        header.extend((tracker_note, sample_number))
    # Disabled volume, panning, and pitch envelopes (82 bytes each).
    for _ in range(3):
        header.extend(b"\0" * 82)
    header.extend(b"\0" * 4)
    if len(header) != 554:
        raise AssertionError(f"unexpected IT instrument header size: {len(header)}")
    return bytes(header)


def sample_header(sample: dict[str, object], data_pointer: int) -> bytes:
    data = sample["data"]
    assert isinstance(data, list)
    looped = bool(sample["loop"])
    flags = 0x01 | (0x10 if looped else 0)
    length = len(data)
    header = bytearray()
    header.extend(b"IMPS")
    header.extend(b"\0" * 12)
    header.extend((0, 64, flags, int(sample["volume"])))
    header.extend(padded_ascii(str(sample["name"]), 26))
    header.extend((1, 32))  # signed PCM conversion, centered default pan
    header.extend(
        struct.pack(
            "<7I",
            length,
            0,
            length if looped else 0,
            IT_C5_RATE,
            0,
            0,
            data_pointer,
        )
    )
    header.extend((0, 0, 0, 0))  # no auto-vibrato
    if len(header) != 80:
        raise AssertionError(f"unexpected IT sample header size: {len(header)}")
    return bytes(header)


def align4(value: int) -> int:
    return (value + 3) & ~3


def build_it_module() -> bytes:
    samples = music_samples()
    rows, events = pattern_events()
    pattern = pack_pattern(rows, events)
    orders = bytes((0, 255))
    instrument_count = len(samples)
    sample_count = len(samples)
    pattern_count = 1

    table_end = 192 + len(orders) + 4 * (instrument_count + sample_count + pattern_count)
    instrument_offsets: list[int] = []
    cursor = align4(table_end)
    for sample in samples:
        instrument_offsets.append(cursor)
        cursor += len(instrument_header(str(sample["name"]), len(instrument_offsets)))
        cursor = align4(cursor)

    sample_offsets: list[int] = []
    for _ in samples:
        sample_offsets.append(cursor)
        cursor += 80
        cursor = align4(cursor)

    pattern_offset = cursor
    cursor = align4(cursor + len(pattern))
    sample_data_offsets: list[int] = []
    for sample in samples:
        sample_data_offsets.append(cursor)
        data = sample["data"]
        assert isinstance(data, list)
        cursor = align4(cursor + len(data))

    header = bytearray()
    header.extend(b"IMPM")
    header.extend(padded_ascii("Family Street Stage", 26))
    header.extend(struct.pack("<H", 0x1004))  # row highlight: 4 minor, 16 major
    header.extend(struct.pack("<4H", len(orders), instrument_count, sample_count, pattern_count))
    header.extend(struct.pack("<4H", 0x0214, 0x0214, 0x000D, 0))
    header.extend((112, 48, 6, 150, 128, 0))
    header.extend(struct.pack("<HI", 0, 0))  # no song message
    header.extend(b"SNES")
    header.extend(bytes((24, 40, 32, 32, 32, 40)))
    header.extend(bytes((0xA0,)) * 58)
    header.extend(bytes((48, 36, 44, 54, 48, 28)))
    header.extend(bytes((64,)) * 58)
    if len(header) != 192:
        raise AssertionError(f"unexpected IT module header size: {len(header)}")

    output = bytearray(header)
    output.extend(orders)
    output.extend(struct.pack(f"<{instrument_count}I", *instrument_offsets))
    output.extend(struct.pack(f"<{sample_count}I", *sample_offsets))
    output.extend(struct.pack("<I", pattern_offset))
    output.extend(b"\0" * (align4(len(output)) - len(output)))

    for index, sample in enumerate(samples, start=1):
        expected = instrument_offsets[index - 1]
        output.extend(b"\0" * (expected - len(output)))
        output.extend(instrument_header(str(sample["name"]), index))
        output.extend(b"\0" * (align4(len(output)) - len(output)))

    for sample, offset, data_offset in zip(samples, sample_offsets, sample_data_offsets):
        output.extend(b"\0" * (offset - len(output)))
        output.extend(sample_header(sample, data_offset))
        output.extend(b"\0" * (align4(len(output)) - len(output)))

    output.extend(b"\0" * (pattern_offset - len(output)))
    output.extend(pattern)
    output.extend(b"\0" * (align4(len(output)) - len(output)))

    for sample, offset in zip(samples, sample_data_offsets):
        output.extend(b"\0" * (offset - len(output)))
        data = sample["data"]
        assert isinstance(data, list)
        output.extend(struct.pack(f"<{len(data)}b", *data))
        output.extend(b"\0" * (align4(len(output)) - len(output)))
    return bytes(output)


def find_pvsneslib_home(explicit: str | None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    if os.environ.get("PVSNESLIB_HOME"):
        candidates.append(Path(os.environ["PVSNESLIB_HOME"]).expanduser())
    candidates.append(Path.home() / ".codex/tools/pvsneslib-4.6.0/pvsneslib")
    for candidate in candidates:
        if (candidate / "devkitsnes/tools/snesbrr").is_file():
            return candidate.resolve()
    return None


def run_converters(output_dir: Path, pvsneslib_home: Path) -> None:
    snesbrr = pvsneslib_home / "devkitsnes/tools/snesbrr"
    smconv = pvsneslib_home / "devkitsnes/tools/smconv"
    for name in SFX_NAMES:
        subprocess.run(
            (str(snesbrr), "-e", str(output_dir / f"{name}.wav"), str(output_dir / f"{name}.brr")),
            check=True,
        )

    # Verify the tracker module contract without leaving generated soundbank
    # intermediates in audio/. The project Makefile should own those outputs.
    if smconv.is_file():
        with tempfile.TemporaryDirectory(prefix="family-stage-smconv-") as temp_dir:
            soundbank = Path(temp_dir) / "soundbank"
            subprocess.run(
                (
                    str(smconv),
                    "-s",
                    "-o",
                    str(soundbank),
                    "-V",
                    "-b",
                    "5",
                    str(output_dir / "stage_loop.it"),
                ),
                check=True,
            )
            for suffix in (".asm", ".bnk", ".h"):
                if not soundbank.with_suffix(suffix).is_file():
                    raise RuntimeError(f"smconv did not create soundbank{suffix}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "audio",
        help="destination directory (default: repository audio/)",
    )
    parser.add_argument("--pvsneslib-home", help="path to the pinned PVSnesLib installation")
    parser.add_argument(
        "--skip-convert",
        action="store_true",
        help="write WAV/IT sources only; do not invoke snesbrr or smconv",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    effects = {
        "punch": punch_sfx(),
        "jump": jump_sfx(),
        "damage": damage_sfx(),
        "pickup": pickup_sfx(),
        "confirm": confirm_sfx(),
        "victory": victory_sfx(),
    }
    for name in SFX_NAMES:
        write_wav(output_dir / f"{name}.wav", effects[name])
    (output_dir / "stage_loop.it").write_bytes(build_it_module())

    if not args.skip_convert:
        pvsneslib_home = find_pvsneslib_home(args.pvsneslib_home)
        if pvsneslib_home is None:
            print(
                "warning: PVSnesLib tools not found; WAV and IT sources were generated, but BRR conversion was skipped",
                file=sys.stderr,
            )
        else:
            run_converters(output_dir, pvsneslib_home)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
