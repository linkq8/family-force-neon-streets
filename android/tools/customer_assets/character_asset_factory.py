#!/usr/bin/env python3
"""Build a runtime-safe hero atlas from approved still-image action frames.

This tool never writes into app/src/main/assets.  Its output is a reviewable
customer-pack staging directory which must pass QA before the APK factory uses
it.  Pillow is the only third-party dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFilter

CELL = 192
COLS = 8
ROWS = (
    "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
    "jump", "special", "link", "hurt", "knockdown",
)
AIRBORNE = {"jump", "knockdown"}
ATLAS_SIZE = (CELL * COLS, CELL * len(ROWS))
MIN_UNIQUE = {
    "idle": 3, "walk": 5, "punch": 4, "kick": 4,
    "heavy_punch": 5, "heavy_kick": 5, "jump": 5, "special": 6,
    "link": 6, "hurt": 3, "knockdown": 5,
}
ACTION_SUFFIXES = {".png", ".webp"}
REFERENCE_SUFFIXES = ACTION_SUFFIXES | {".jpg", ".jpeg"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clear_transparent_rgb(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putdata([
        (0, 0, 0, 0) if a == 0 else (r, g, b, a)
        for r, g, b, a in rgba.getdata()
    ])
    return rgba


def defringe(image: Image.Image) -> Image.Image:
    """Remove colour stored under transparency and neutralise edge spill."""
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    opaque_neighbours = alpha.filter(ImageFilter.MaxFilter(3))
    pixels = []
    for (r, g, b, a), neighbour in zip(rgba.getdata(), opaque_neighbours.getdata()):
        if a < 8:
            pixels.append((0, 0, 0, 0))
        elif a < 224 and neighbour:
            # Premultiply edge RGB before alpha becomes binary; this avoids a
            # bright matte fringe when Android scales the sprite.
            pixels.append((r * a // 255, g * a // 255, b * a // 255, 255))
        else:
            pixels.append((r, g, b, 255))
    rgba.putdata(pixels)
    return clear_transparent_rgb(rgba)


def visible_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("frame has no visible pixels")
    return bbox


def normalize_frame(source: Image.Image, action: str) -> Image.Image:
    if source.getchannel("A").getextrema()[0] == 255:
        raise ValueError(
            f"{action}: action frame has no transparency; remove its background first"
        )
    image = defringe(source)
    bbox = visible_bbox(image)
    subject = image.crop(bbox)
    max_w, max_h = 174, (166 if action not in AIRBORNE else 176)
    scale = min(max_w / subject.width, max_h / subject.height, 1.0)
    size = (max(1, round(subject.width * scale)), max(1, round(subject.height * scale)))
    subject = subject.resize(size, Image.Resampling.LANCZOS)
    subject.putalpha(subject.getchannel("A").point(lambda a: 255 if a >= 96 else 0))
    subject = clear_transparent_rgb(subject)
    cell = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    x = (CELL - subject.width) // 2
    if action in AIRBORNE:
        y = (CELL - subject.height) // 2
    else:
        y = CELL - 6 - subject.height  # common six-pixel ground line
    cell.alpha_composite(subject, (x, y))
    return clear_transparent_rgb(cell)


def sheet_frames(path: Path) -> list[Image.Image]:
    with Image.open(path) as opened:
        sheet = opened.convert("RGBA")
    if sheet.width % COLS:
        raise ValueError(f"{path}: sheet width must divide into exactly {COLS} frames")
    frame_w = sheet.width // COLS
    return [sheet.crop((i * frame_w, 0, (i + 1) * frame_w, sheet.height)) for i in range(COLS)]


def load_action_frames(input_dir: Path, action: str) -> list[Image.Image]:
    directory = input_dir / "actions" / action
    sheet_candidates = [input_dir / "actions" / f"{action}{suffix}" for suffix in ACTION_SUFFIXES]
    if directory.is_dir():
        paths = sorted(p for p in directory.iterdir() if p.suffix.lower() in ACTION_SUFFIXES)
        if len(paths) != COLS:
            raise ValueError(f"{action}: expected exactly {COLS} still frames; found {len(paths)}")
        frames = []
        for path in paths:
            with Image.open(path) as opened:
                frames.append(opened.convert("RGBA"))
        return frames
    for candidate in sheet_candidates:
        if candidate.is_file():
            return sheet_frames(candidate)
    raise FileNotFoundError(f"{action}: missing actions/{action}/ or actions/{action}.png")


def changed_fraction(a: Image.Image, b: Image.Image) -> float:
    aa = a.getchannel("A").point(lambda v: 255 if v else 0)
    bb = b.getchannel("A").point(lambda v: 255 if v else 0)
    hist = ImageChops.difference(aa, bb).histogram()
    return sum(hist[1:]) / (CELL * CELL)


def validate_cells(action: str, cells: list[Image.Image]) -> dict:
    errors: list[str] = []
    rgba_hashes = {hashlib.sha256(cell.tobytes()).hexdigest() for cell in cells}
    alpha_hashes = {hashlib.sha256(cell.getchannel("A").tobytes()).hexdigest() for cell in cells}
    for index, cell in enumerate(cells):
        bbox = cell.getchannel("A").getbbox()
        if bbox is None:
            errors.append(f"frame {index + 1} is empty")
            continue
        l, t, r, b = bbox
        if min(l, t, CELL - r, CELL - b) < 2:
            errors.append(f"frame {index + 1} touches the cell edge: {bbox}")
        if any(a not in (0, 255) for a in set(cell.getchannel("A").getdata())):
            errors.append(f"frame {index + 1} has soft alpha")
        if action not in AIRBORNE and b != CELL - 6:
            errors.append(f"frame {index + 1} is not foot-anchored")
    peak_motion = max((changed_fraction(cells[i], cells[i + 1]) for i in range(7)), default=0)
    if len(rgba_hashes) < MIN_UNIQUE[action]:
        errors.append(f"only {len(rgba_hashes)} unique poses; require {MIN_UNIQUE[action]}")
    if len(alpha_hashes) < max(2, MIN_UNIQUE[action] - 1):
        errors.append(f"only {len(alpha_hashes)} unique silhouettes")
    if peak_motion < 0.003:
        errors.append(f"animation silhouette motion too low ({peak_motion:.4f})")
    return {
        "action": action, "unique_rgba": len(rgba_hashes),
        "unique_silhouettes": len(alpha_hashes), "peak_motion": round(peak_motion, 5),
        "passed": not errors, "errors": errors,
    }


def contact_sheet(atlas: Image.Image, reports: list[dict], character: str) -> Image.Image:
    label_w, header_h = 190, 52
    preview_cell = 112
    canvas = Image.new("RGB", (label_w + COLS * preview_cell, header_h + len(ROWS) * preview_cell), "#17192b")
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 16), f"{character} — ACTION ATLAS QA", fill="white")
    for row, (action, report) in enumerate(zip(ROWS, reports)):
        y = header_h + row * preview_cell
        colour = "#65e68b" if report["passed"] else "#ff6577"
        draw.text((12, y + 38), action.replace("_", " ").upper(), fill=colour)
        for col in range(COLS):
            frame = atlas.crop((col * CELL, row * CELL, (col + 1) * CELL, (row + 1) * CELL))
            frame.thumbnail((preview_cell, preview_cell), Image.Resampling.LANCZOS)
            tile = Image.new("RGBA", (preview_cell, preview_cell), (35, 38, 62, 255))
            tile.alpha_composite(frame, ((preview_cell - frame.width)//2, (preview_cell - frame.height)//2))
            canvas.paste(tile.convert("RGB"), (label_w + col * preview_cell, y))
    return canvas


def require_reference_files(input_dir: Path) -> dict[str, str]:
    result = {}
    for stem in ("portrait", "model_sheet"):
        matches = [input_dir / f"{stem}{suffix}" for suffix in REFERENCE_SUFFIXES]
        path = next((p for p in matches if p.is_file()), None)
        if path is None:
            raise FileNotFoundError(f"missing required approved reference: {stem}.png")
        with Image.open(path) as image:
            image.verify()
        result[stem] = str(path.resolve())
    return result


def build(args: argparse.Namespace) -> int:
    input_dir, output_dir = args.input.resolve(), args.output.resolve()
    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        raise FileExistsError(f"refusing to overwrite non-empty output: {output_dir} (use --force)")
    references = require_reference_files(input_dir)
    atlas = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    reports = []
    for row, action in enumerate(ROWS):
        cells = [normalize_frame(frame, action) for frame in load_action_frames(input_dir, action)]
        reports.append(validate_cells(action, cells))
        for col, cell in enumerate(cells):
            atlas.alpha_composite(cell, (col * CELL, row * CELL))
    output_dir.mkdir(parents=True, exist_ok=True)
    atlas_path = output_dir / f"{args.character}_anim.png"
    contact_path = output_dir / f"{args.character}_contact_sheet.png"
    report_path = output_dir / f"{args.character}_qa.json"
    atlas.save(atlas_path, optimize=True)
    contact_sheet(atlas, reports, args.character).save(contact_path, optimize=True)
    payload = {
        "schema_version": 1, "character": args.character,
        "contract": {"width": 1536, "height": 2112, "columns": 8, "rows": list(ROWS), "cell": 192},
        "approved_references": references, "source": str(input_dir),
        "atlas": {"path": str(atlas_path), "sha256": sha256(atlas_path)},
        "passed": all(report["passed"] for report in reports), "actions": reports,
    }
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"atlas": str(atlas_path), "contact": str(contact_path), "qa": str(report_path), "passed": payload["passed"]}))
    return 0 if payload["passed"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", required=True, help="safe lowercase character asset id")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true", help="replace staging output only")
    args = parser.parse_args()
    if not args.character.replace("_", "").isalnum() or args.character.lower() != args.character:
        parser.error("--character must contain lowercase letters, digits, or underscores")
    try:
        return build(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
