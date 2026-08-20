"""Structural and pinned-toolchain tests for the SNES audio pack."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools/generate_audio.py"
AUDIO_DIR = ROOT / "audio"
EXPECTED_FRAMES = {
    "punch": 1_280,
    "jump": 2_304,
    "damage": 3_072,
    "pickup": 2_048,
    "confirm": 1_536,
    "victory": 6_144,
}


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_audio", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load tools/generate_audio.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_pvsneslib_home() -> Path | None:
    candidates = []
    if os.environ.get("PVSNESLIB_HOME"):
        candidates.append(Path(os.environ["PVSNESLIB_HOME"]))
    candidates.append(Path.home() / ".codex/tools/pvsneslib-4.6.0/pvsneslib")
    for candidate in candidates:
        if (candidate / "devkitsnes/tools/snesbrr").is_file():
            return candidate.resolve()
    return None


class AudioSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generator = load_generator()

    def test_wav_contract_and_headroom(self) -> None:
        for name, expected_frames in EXPECTED_FRAMES.items():
            path = AUDIO_DIR / f"{name}.wav"
            with self.subTest(effect=name), wave.open(str(path), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), 8_000)
                self.assertEqual(wav_file.getnframes(), expected_frames)
                samples = struct.unpack(
                    f"<{expected_frames}h", wav_file.readframes(expected_frames)
                )
                peak = max(abs(value) for value in samples)
                self.assertGreater(peak, 8_000, "effect is unexpectedly quiet")
                self.assertLessEqual(peak, 22_500, "effect has insufficient peak headroom")
                self.assertEqual(samples[-1], 0, "release fade must end at digital silence")

    def test_generator_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="family-audio-source-") as temp_dir:
            output = Path(temp_dir)
            result = subprocess.run(
                (
                    sys.executable,
                    str(GENERATOR_PATH),
                    "--output-dir",
                    str(output),
                    "--skip-convert",
                ),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in EXPECTED_FRAMES:
                with self.subTest(effect=name):
                    self.assertEqual(
                        (output / f"{name}.wav").read_bytes(),
                        (AUDIO_DIR / f"{name}.wav").read_bytes(),
                    )
            self.assertEqual(
                (output / "stage_loop.it").read_bytes(),
                (AUDIO_DIR / "stage_loop.it").read_bytes(),
            )

    def test_impulse_tracker_structure(self) -> None:
        data = (AUDIO_DIR / "stage_loop.it").read_bytes()
        self.assertEqual(data[:4], b"IMPM")
        ordnum, insnum, smpnum, patnum = struct.unpack_from("<4H", data, 32)
        flags = struct.unpack_from("<H", data, 44)[0]
        self.assertEqual((ordnum, insnum, smpnum, patnum), (2, 5, 5, 1))
        self.assertTrue(flags & 0x04, "module must be in instrument mode")
        self.assertTrue(flags & 0x08, "module must use linear frequency slides")
        self.assertFalse(flags & 0x10, "SNESMOD forbids old-effects mode")
        self.assertEqual(data[50:52], bytes((6, 150)))

        cursor = 192
        self.assertEqual(data[cursor : cursor + ordnum], bytes((0, 255)))
        cursor += ordnum
        instrument_offsets = struct.unpack_from(f"<{insnum}I", data, cursor)
        cursor += insnum * 4
        sample_offsets = struct.unpack_from(f"<{smpnum}I", data, cursor)
        cursor += smpnum * 4
        (pattern_offset,) = struct.unpack_from("<I", data, cursor)

        for index, offset in enumerate(instrument_offsets, start=1):
            with self.subTest(instrument=index):
                self.assertEqual(data[offset : offset + 4], b"IMPI")
                # Every note maps to exactly one defined sample, as SNESMOD requires.
                note_map = data[offset + 64 : offset + 304]
                self.assertEqual(note_map[1::2], bytes((index,)) * 120)

        for index, offset in enumerate(sample_offsets, start=1):
            with self.subTest(sample=index):
                self.assertEqual(data[offset : offset + 4], b"IMPS")
                flags = data[offset + 18]
                length, loop_start, loop_end, _, _, _, sample_pointer = struct.unpack_from(
                    "<7I", data, offset + 48
                )
                self.assertTrue(flags & 0x01)
                self.assertLess(sample_pointer + length, len(data) + 1)
                if flags & 0x10:
                    self.assertEqual(loop_start % 16, 0)
                    self.assertEqual(loop_end % 16, 0)

        packed_length, row_count = struct.unpack_from("<HH", data, pattern_offset)
        self.assertEqual(row_count, 128)
        packed = data[pattern_offset + 8 : pattern_offset + 8 + packed_length]
        position = 0
        row = 0
        masks = [0] * 64
        found_loop = False
        while position < len(packed) and row < row_count:
            channel = packed[position]
            position += 1
            if channel == 0:
                row += 1
                continue
            channel_index = (channel & 0x7F) - 1
            self.assertLess(channel_index, 6)
            if channel & 0x80:
                masks[channel_index] = packed[position]
                position += 1
            mask = masks[channel_index]
            if mask & 0x01:
                position += 1
            if mask & 0x02:
                instrument = packed[position]
                position += 1
                self.assertIn(instrument, range(1, 6))
            if mask & 0x04:
                volume = packed[position]
                position += 1
                self.assertLessEqual(volume, 64)
            if mask & 0x08:
                command, parameter = packed[position : position + 2]
                position += 2
                if row == 127 and command == 2 and parameter == 0:
                    found_loop = True
        self.assertEqual(row, row_count)
        self.assertEqual(position, len(packed))
        self.assertTrue(found_loop, "final row must contain the supported B00 order jump")


@unittest.skipUnless(find_pvsneslib_home(), "PVSnesLib converters are not installed")
class PinnedConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pvsneslib_home = find_pvsneslib_home()
        assert cls.pvsneslib_home is not None
        cls.snesbrr = cls.pvsneslib_home / "devkitsnes/tools/snesbrr"
        cls.smconv = cls.pvsneslib_home / "devkitsnes/tools/smconv"

    def test_brr_outputs_match_converter_and_decode(self) -> None:
        with tempfile.TemporaryDirectory(prefix="family-brr-test-") as temp_dir:
            temp = Path(temp_dir)
            for name, expected_frames in EXPECTED_FRAMES.items():
                with self.subTest(effect=name):
                    encoded = temp / f"{name}.brr"
                    decoded = temp / f"{name}-decoded.wav"
                    encode = subprocess.run(
                        (str(self.snesbrr), "-e", str(AUDIO_DIR / f"{name}.wav"), str(encoded)),
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(encode.returncode, 0, encode.stderr)
                    payload = encoded.read_bytes()
                    self.assertEqual(payload, (AUDIO_DIR / f"{name}.brr").read_bytes())
                    self.assertGreater(len(payload), 9)
                    self.assertEqual(len(payload) % 9, 0)
                    headers = payload[0::9]
                    self.assertTrue(headers[-1] & 0x01, "last BRR block needs the END flag")
                    self.assertEqual(sum(bool(value & 0x01) for value in headers), 1)

                    decode = subprocess.run(
                        (str(self.snesbrr), "-d", "-p", "0x400", str(encoded), str(decoded)),
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(decode.returncode, 0, decode.stderr)
                    with wave.open(str(decoded), "rb") as wav_file:
                        self.assertEqual(wav_file.getnchannels(), 1)
                        self.assertEqual(wav_file.getsampwidth(), 2)
                        self.assertEqual(wav_file.getframerate(), 8_000)
                        self.assertLessEqual(abs(wav_file.getnframes() - expected_frames), 16)

    def test_smconv_460_accepts_stage_loop(self) -> None:
        with tempfile.TemporaryDirectory(prefix="family-smconv-test-") as temp_dir:
            soundbank = Path(temp_dir) / "soundbank"
            result = subprocess.run(
                (
                    str(self.smconv),
                    "-s",
                    "-o",
                    str(soundbank),
                    "-V",
                    "-b",
                    "5",
                    str(AUDIO_DIR / "stage_loop.it"),
                ),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Instruments: [5/64]", result.stdout)
            self.assertIn("Samples: [5/64]", result.stdout)
            for suffix in (".asm", ".bnk", ".h"):
                path = soundbank.with_suffix(suffix)
                self.assertTrue(path.is_file(), f"missing {path.name}")
                self.assertGreater(path.stat().st_size, 0)
            self.assertIn(".BANK 5", soundbank.with_suffix(".asm").read_text())


if __name__ == "__main__":
    unittest.main()
