#!/usr/bin/env python3
"""Build compact, labelled contact sheets for semantic animation-video QA."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACTORS = ROOT / "assets" / "higgsfield" / "android" / "animation_v2" / "actors"
DEFAULT_OUTPUT = ROOT / "android" / "app" / "build" / "reports" / "animation-video-contacts"
HERO_ACTIONS = (
    "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
    "jump", "special", "link", "hurt", "knockdown",
)
ENEMY_ACTIONS = ("idle", "walk", "attack1", "attack2", "hurt", "knockdown")
ACTORS = (
    "hero_1", "hero_2", "hero_3", "hero_4",
    "enemy_grunt", "enemy_skater", "enemy_brute", "boss_junk_king",
)


def probe_duration(video: Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(video),
    ], check=True, capture_output=True, text=True)
    return max(0.1, float(result.stdout.strip()))


def extract_frames(
    video: Path, temporary: Path, cell: int
) -> tuple[list[Image.Image], float]:
    duration = probe_duration(video)
    pattern = temporary / "%02d.png"
    subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(video),
        "-vf",
        f"fps={8 / duration:.8f},"
        f"scale={cell}:{cell}:force_original_aspect_ratio=decrease,"
        f"pad={cell}:{cell}:(ow-iw)/2:(oh-ih)/2:color=0x1d2238",
        "-frames:v", "8", str(pattern),
    ], check=True)
    frames = [Image.open(path).convert("RGB") for path in sorted(temporary.glob("*.png"))]
    return frames, duration


def build_actor(actor_root: Path, actor: str, output: Path, cell: int) -> tuple[int, int]:
    actions = HERO_ACTIONS if actor.startswith("hero_") else ENEMY_ACTIONS
    label_width = 122
    header_height = 24
    columns = 8
    canvas = Image.new(
        "RGB", (label_width + columns * cell, header_height + len(actions) * cell),
        (27, 31, 49),
    )
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, canvas.width, header_height - 1), fill=(11, 14, 28))
    draw.text((6, 7), actor, fill=(245, 247, 255))
    for column in range(columns):
        x = label_width + column * cell
        draw.text((x + 5, 7), f"{column * 12.5:.1f}%", fill=(174, 200, 255))
    completed = 0
    for row, action in enumerate(actions):
        top = header_height + row * cell
        draw.rectangle((0, top, label_width - 1, top + cell - 1), fill=(18, 22, 38))
        draw.text((6, top + 8), f"{row}: {action}", fill=(241, 244, 255))
        video = actor_root / actor / "videos" / f"{action}.mp4"
        if video.is_file() and video.stat().st_size:
            with tempfile.TemporaryDirectory(prefix=f"{actor}-{action}-") as directory:
                frames, duration = extract_frames(video, Path(directory), cell)
            draw.text((6, top + 24), f"{duration:.2f}s", fill=(167, 184, 218))
            for column, frame in enumerate(frames[:columns]):
                canvas.paste(frame, (label_width + column * cell, top))
            completed += 1
        else:
            draw.text(
                (label_width + 12, top + cell // 2), "MISSING / PENDING",
                fill=(255, 142, 142),
            )
        draw.line((label_width, top, canvas.width, top), fill=(99, 110, 142))
    for column in range(columns + 1):
        x = label_width + column * cell
        draw.line((x, header_height, x, canvas.height), fill=(76, 87, 116))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=92, optimize=True)
    return completed, len(actions)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actors-root", type=Path, default=DEFAULT_ACTORS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cell", type=int, default=176)
    args = parser.parse_args()
    assert 96 <= args.cell <= 256
    total_completed = total_expected = 0
    for actor in ACTORS:
        completed, expected = build_actor(
            args.actors_root, actor, args.output / f"{actor}.jpg", args.cell
        )
        total_completed += completed
        total_expected += expected
        print(f"{actor}: {completed}/{expected} -> {args.output / f'{actor}.jpg'}")
    print(f"Video contacts: {total_completed}/{total_expected} clips complete")


if __name__ == "__main__":
    main()
