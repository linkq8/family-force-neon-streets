#!/usr/bin/env python3
"""Validate the release invariants for the Family Force SNES ROM.

The validator is deliberately read-only.  It checks the exact cartridge shape
used by this project rather than trying to identify arbitrary SNES ROMs.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import List


ROM_SIZE = 4 * 1024 * 1024
LOROM_HEADER_OFFSET = 0x7FC0
TITLE_SIZE = 21
EXPECTED_TITLE = b"FAMILY FORCE RESCUE"

# Byte offsets are relative to the standard internal SNES header at $00:FFC0.
EXPECTED_HEADER_BYTES = {
    0x15: (0x30, "map mode (FastROM LoROM)"),
    0x16: (0x00, "cartridge type (ROM only)"),
    0x17: (0x0C, "ROM size exponent (4 MiB)"),
    0x18: (0x00, "SRAM size exponent (none)"),
    0x19: (0x01, "destination code (NTSC North America)"),
    0x1A: (0x00, "old licensee code"),
    0x1B: (0x00, "ROM version"),
}


def little_u16(data: bytes, offset: int) -> int:
    """Read one little-endian unsigned 16-bit value."""

    return data[offset] | (data[offset + 1] << 8)


def validate_rom(path: Path) -> List[str]:
    """Return every validation error found in *path*."""

    errors: List[str] = []
    try:
        rom = path.read_bytes()
    except OSError as exc:
        return [f"cannot read ROM: {exc}"]

    if len(rom) == ROM_SIZE + 512:
        errors.append(
            "ROM has a 512-byte copier header; release ROM must be headerless"
        )
    elif len(rom) != ROM_SIZE:
        errors.append(
            f"ROM size is {len(rom)} bytes; expected exactly {ROM_SIZE} bytes"
        )

    # Nothing below is meaningful if the image does not contain a LoROM header.
    if len(rom) < LOROM_HEADER_OFFSET + 0x40:
        errors.append("ROM is too short to contain a LoROM internal header")
        return errors

    header = rom[LOROM_HEADER_OFFSET : LOROM_HEADER_OFFSET + 0x40]
    title = header[:TITLE_SIZE]
    if not title.startswith(EXPECTED_TITLE):
        errors.append(
            "internal title is "
            f"{title!r}; expected it to start with {EXPECTED_TITLE!r}"
        )
    else:
        title_padding = title[len(EXPECTED_TITLE) :]
        if any(value not in (0x00, 0x20) for value in title_padding):
            errors.append(
                f"internal title has invalid padding bytes: {title_padding!r}"
            )

    for offset, (expected, description) in EXPECTED_HEADER_BYTES.items():
        actual = header[offset]
        if actual != expected:
            errors.append(
                f"{description} is 0x{actual:02X}; expected 0x{expected:02X}"
            )

    complement = little_u16(header, 0x1C)
    checksum = little_u16(header, 0x1E)
    if (complement ^ checksum) != 0xFFFF:
        errors.append(
            "checksum complement pair is invalid: "
            f"0x{complement:04X} XOR 0x{checksum:04X} != 0xFFFF"
        )

    # This project has a power-of-two ROM size, so the standard SNES checksum
    # is simply the 16-bit sum of every byte (including the balanced pair).
    calculated_checksum = sum(rom) & 0xFFFF
    if calculated_checksum != checksum:
        errors.append(
            f"checksum is 0x{checksum:04X}; calculated 0x{calculated_checksum:04X}"
        )

    reset_vector = little_u16(rom, LOROM_HEADER_OFFSET + 0x3C)
    if reset_vector < 0x8000:
        errors.append(
            f"native reset vector is 0x{reset_vector:04X}; expected ROM address >= 0x8000"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Family Force 4 MiB FastROM LoROM image."
    )
    parser.add_argument("rom", type=Path, help="path to the headerless .sfc file")
    args = parser.parse_args()

    errors = validate_rom(args.rom)
    if errors:
        print(f"FAIL: {args.rom}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    rom = args.rom.read_bytes()
    header = rom[LOROM_HEADER_OFFSET : LOROM_HEADER_OFFSET + 0x40]
    checksum = little_u16(header, 0x1E)
    print(f"OK: {args.rom}")
    print(f"  size: {len(rom)} bytes (headerless 4 MiB)")
    print("  header: FastROM LoROM, cartridge 0x00, no SRAM")
    print(f"  title: {header[:TITLE_SIZE].rstrip(bytes((0x00, 0x20))).decode('ascii')}")
    print(f"  checksum: 0x{checksum:04X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
