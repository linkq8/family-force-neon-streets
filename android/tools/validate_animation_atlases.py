#!/usr/bin/env python3
"""Strict QA for the runtime hero and enemy animation atlases.

This validator is intentionally separate from ``validate_assets.py`` so the
animation-generation pipeline can be checked while it is still being built.
It rejects placeholder rows that merely repeat one pose, unanchored frames,
opaque/key-colour backgrounds, soft/non-pixel alpha, and stale manifest data.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import statistics
import sys
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSETS = ROOT / "android" / "app" / "src" / "main" / "assets"


@dataclass(frozen=True)
class AtlasContract:
    relative: str
    columns: int
    rows: tuple[str, ...]
    cell_width: int
    cell_height: int
    minimum_unique_rgba: tuple[int, ...]
    minimum_unique_silhouettes: tuple[int, ...]
    minimum_peak_silhouette_change: tuple[float, ...]
    airborne_rows: frozenset[int] = frozenset()
    minimum_upright_median_height: int = 0

    @property
    def size(self) -> tuple[int, int]:
        return self.columns * self.cell_width, len(self.rows) * self.cell_height


HERO_ROWS = (
    "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
    "jump", "special", "link", "hurt", "knockdown",
)
ENEMY_ROWS = ("idle", "walk", "attack1", "attack2", "hurt", "knockdown")

# The source pipeline deliberately pads short clips to a fixed row width. The
# values below allow those repeated padding frames while still requiring each
# action to contain several materially different poses.
HERO_UNIQUE_RGBA = (3, 5, 4, 4, 5, 5, 5, 6, 6, 3, 5)
HERO_UNIQUE_ALPHA = (2, 4, 3, 3, 4, 4, 4, 4, 4, 2, 4)
HERO_PEAK_MOTION = (
    0.0005, 0.0075, 0.0060, 0.0060, 0.0075, 0.0075,
    0.0075, 0.0060, 0.0060, 0.0030, 0.0080,
)
ENEMY_UNIQUE_RGBA = (3, 4, 4, 4, 3, 4)
ENEMY_UNIQUE_ALPHA = (2, 3, 3, 3, 2, 3)
ENEMY_PEAK_MOTION = (0.0005, 0.0060, 0.0050, 0.0050, 0.0030, 0.0075)


def contracts() -> tuple[AtlasContract, ...]:
    hero_paths = ("parent", "adam", "shaikha", "sulaiman")
    enemy_paths = ("grunt", "skater", "brute", "boss", "striker", "shield_guard")
    heroes = tuple(
        AtlasContract(
            relative=f"heroes/{name}_anim.png",
            columns=8,
            rows=HERO_ROWS,
            cell_width=192,
            cell_height=192,
            minimum_unique_rgba=HERO_UNIQUE_RGBA,
            minimum_unique_silhouettes=HERO_UNIQUE_ALPHA,
            minimum_peak_silhouette_change=HERO_PEAK_MOTION,
            # Jump and knockdown intentionally move the body vertically.  They
            # still have to include a grounded take-off/landing frame below,
            # but cannot use the upright-cycle foot-anchor tolerance.
            airborne_rows=frozenset({
                HERO_ROWS.index("jump"),
                HERO_ROWS.index("knockdown"),
            }),
            minimum_upright_median_height=160,
        )
        for name in hero_paths
    )
    enemies = tuple(
        AtlasContract(
            relative=f"enemies/{name}_anim.png",
            columns=6,
            rows=ENEMY_ROWS,
            cell_width=160,
            cell_height=192,
            minimum_unique_rgba=ENEMY_UNIQUE_RGBA,
            minimum_unique_silhouettes=ENEMY_UNIQUE_ALPHA,
            minimum_peak_silhouette_change=ENEMY_PEAK_MOTION,
            airborne_rows=frozenset({ENEMY_ROWS.index("knockdown")}),
        )
        for name in enemy_paths
    )
    return heroes + enemies


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def binary_alpha(cell: Image.Image) -> Image.Image:
    return cell.getchannel("A").point(lambda value: 255 if value else 0)


def changed_fraction(first: Image.Image, second: Image.Image) -> float:
    difference = ImageChops.difference(first, second)
    histogram = difference.histogram()
    changed = sum(histogram[1:])
    return changed / (first.width * first.height)


def is_two_pixel_clustered(image: Image.Image) -> bool:
    if image.width % 2 or image.height % 2:
        return False
    down = image.resize(
        (image.width // 2, image.height // 2), Image.Resampling.NEAREST
    )
    return down.resize(image.size, Image.Resampling.NEAREST).tobytes() == image.tobytes()


def load_manifest_records(assets: Path) -> dict[str, dict]:
    manifest_path = assets / "asset_manifest.json"
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {manifest_path}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = payload.get("files")
    if not isinstance(records, list):
        raise AssertionError("asset_manifest.json has no files array")
    return {record.get("path"): record for record in records}


def validate_manifest_record(
    path: Path, relative: str, image: Image.Image, records: dict[str, dict]
) -> None:
    record = records.get(relative)
    assert record is not None, f"{relative}: missing asset_manifest.json record"
    expected = {
        "bytes": path.stat().st_size,
        "sha256": digest(path.read_bytes()),
        "width": image.width,
        "height": image.height,
        "mode": "RGBA",
    }
    for field, value in expected.items():
        assert record.get(field) == value, (
            f"{relative}: stale manifest {field}: "
            f"{record.get(field)!r} != {value!r}"
        )


def cell_for(image: Image.Image, contract: AtlasContract, column: int, row: int) -> Image.Image:
    left = column * contract.cell_width
    top = row * contract.cell_height
    return image.crop((
        left, top, left + contract.cell_width, top + contract.cell_height,
    ))


def validate_cell(
    relative: str, row_name: str, column: int, cell: Image.Image
) -> tuple[tuple[int, int, int, int], int]:
    alpha = cell.getchannel("A")
    bbox = alpha.getbbox()
    assert bbox is not None, f"{relative} {row_name}[{column}]: empty cell"
    alpha_values = set(alpha.getdata())
    assert alpha_values <= {0, 255}, (
        f"{relative} {row_name}[{column}]: soft alpha values present"
    )
    clear_with_rgb = sum(
        1
        for red, green, blue, opacity in cell.getdata()
        if opacity == 0 and (red or green or blue)
    )
    assert clear_with_rgb == 0, (
        f"{relative} {row_name}[{column}]: {clear_with_rgb} coloured clear pixels"
    )

    visible = sum(1 for opacity in alpha.getdata() if opacity)
    occupancy = visible / (cell.width * cell.height)
    assert 0.01 <= occupancy <= 0.78, (
        f"{relative} {row_name}[{column}]: implausible occupancy {occupancy:.3%}"
    )
    left, top, right, bottom = bbox
    assert right - left >= 16 and bottom - top >= 24, (
        f"{relative} {row_name}[{column}]: tiny visible bounds {bbox}"
    )
    margins = (left, top, cell.width - right, cell.height - bottom)
    assert min(margins) >= 2, (
        f"{relative} {row_name}[{column}]: cropped/touching edge; "
        f"bbox={bbox}, margins={margins}"
    )
    center_x = (left + right) * 0.5 / cell.width
    assert 0.20 <= center_x <= 0.80, (
        f"{relative} {row_name}[{column}]: bounds drift off anchor; "
        f"horizontal center={center_x:.3f}"
    )
    return bbox, visible


def validate_atlas(
    assets: Path,
    contract: AtlasContract,
    records: dict[str, dict],
    require_two_pixel_clusters: bool,
) -> dict:
    path = assets / contract.relative
    with Image.open(path) as source:
        source.verify()
    with Image.open(path) as source:
        assert source.format == "PNG", f"{contract.relative}: expected PNG"
        assert source.mode == "RGBA", (
            f"{contract.relative}: expected stored RGBA, got {source.mode}"
        )
        image = source.copy()

    assert image.size == contract.size, (
        f"{contract.relative}: {image.size} != {contract.size}"
    )
    assert image.getchannel("A").getextrema() == (0, 255), (
        f"{contract.relative}: atlas must contain transparent and opaque pixels"
    )
    if require_two_pixel_clusters:
        assert is_two_pixel_clustered(image), (
            f"{contract.relative}: pixels are not aligned to exact 2px clusters"
        )

    validate_manifest_record(path, contract.relative, image, records)
    row_reports: list[dict] = []
    for row, row_name in enumerate(contract.rows):
        cells = [cell_for(image, contract, column, row) for column in range(contract.columns)]
        bboxes = [
            validate_cell(contract.relative, row_name, column, cell)[0]
            for column, cell in enumerate(cells)
        ]
        rgba_hashes = {digest(cell.tobytes()) for cell in cells}
        silhouettes = [binary_alpha(cell) for cell in cells]
        alpha_hashes = {digest(mask.tobytes()) for mask in silhouettes}

        assert len(rgba_hashes) >= contract.minimum_unique_rgba[row], (
            f"{contract.relative} {row_name}: static/under-sampled RGB row; "
            f"{len(rgba_hashes)} unique, need {contract.minimum_unique_rgba[row]}"
        )
        assert len(alpha_hashes) >= contract.minimum_unique_silhouettes[row], (
            f"{contract.relative} {row_name}: poses do not change silhouette; "
            f"{len(alpha_hashes)} unique, need "
            f"{contract.minimum_unique_silhouettes[row]}"
        )

        peak_change = max(
            changed_fraction(first, second)
            for index, first in enumerate(silhouettes)
            for second in silhouettes[index + 1:]
        )
        required_change = contract.minimum_peak_silhouette_change[row]
        assert peak_change >= required_change, (
            f"{contract.relative} {row_name}: motion too small; peak changed-alpha "
            f"fraction {peak_change:.4%}, need {required_change:.4%}"
        )

        bottoms = [bbox[3] for bbox in bboxes]
        if row not in contract.airborne_rows:
            assert max(bottoms) - min(bottoms) <= 32, (
                f"{contract.relative} {row_name}: unstable foot/base anchor; "
                f"bottom range {min(bottoms)}..{max(bottoms)}"
            )
            assert sorted(bottoms)[len(bottoms) // 2] >= round(contract.cell_height * 0.70), (
                f"{contract.relative} {row_name}: sprite floats above its base anchor; "
                f"bottoms={bottoms}"
            )
        else:
            assert max(bottoms) >= round(contract.cell_height * 0.70), (
                f"{contract.relative} {row_name}: no grounded endpoint; "
                f"bottoms={bottoms}"
            )

        median_width = statistics.median(bbox[2] - bbox[0] for bbox in bboxes)
        median_height = statistics.median(bbox[3] - bbox[1] for bbox in bboxes)
        if row_name in {"idle", "walk"} and contract.minimum_upright_median_height:
            median_top = statistics.median(bbox[1] for bbox in bboxes)
            median_bottom = statistics.median(bbox[3] for bbox in bboxes)
            # A stride legitimately lowers the head and spreads the legs. Keep
            # idle at the full-size contract while allowing a small (10px)
            # crouch envelope for walk without accepting a shrunken sheet.
            minimum_upright_height = contract.minimum_upright_median_height
            if row_name == "walk":
                minimum_upright_height -= 10
            assert median_height >= minimum_upright_height, (
                f"{contract.relative} {row_name}: undersized source figure; median "
                f"alpha height {median_height}px, need at least "
                f"{minimum_upright_height}px"
            )
            assert 4 <= median_top <= 28, (
                f"{contract.relative} {row_name}: unreasonable upper margin; "
                f"median bbox top={median_top}px (expected 4..28px)"
            )
            assert median_bottom >= 176, (
                f"{contract.relative} {row_name}: upright figure is not grounded/full-size; "
                f"median bbox bottom={median_bottom}px"
            )

        row_reports.append({
            "row": row,
            "action": row_name,
            "unique_rgba": len(rgba_hashes),
            "unique_silhouettes": len(alpha_hashes),
            "peak_silhouette_change": round(peak_change, 6),
            "bottom_range": [min(bottoms), max(bottoms)],
            "median_bbox_width": round(median_width, 2),
            "median_bbox_height": round(median_height, 2),
        })

    return {
        "path": contract.relative,
        "size": list(image.size),
        "sha256": digest(path.read_bytes()),
        "rows": row_reports,
    }


def validate_hero_visible_scale(reports: list[dict]) -> dict | None:
    """Check source-cell fill so runtime centimetre scaling remains truthful.

    GameView applies the actual 177/108/108/124 cm ratios to atlas draw sizes.
    Therefore the four source sprites must fill their 192px cells similarly;
    otherwise a short source silhouette would be shrunk a second time.
    """
    by_path = {report["path"]: report for report in reports}
    paths = {
        "Essa": "heroes/parent_anim.png",
        "Adam": "heroes/adam_anim.png",
        "Shaikha": "heroes/shaikha_anim.png",
        "Sulaiman": "heroes/sulaiman_anim.png",
    }
    if not all(path in by_path for path in paths.values()):
        return None

    height_cm = {"Essa": 177.0, "Adam": 108.0, "Shaikha": 108.0, "Sulaiman": 124.0}
    source_idle_height = {
        name: float(by_path[path]["rows"][0]["median_bbox_height"])
        for name, path in paths.items()
    }
    essa_source = source_idle_height["Essa"]
    source_fill_ratio = {
        name: source_idle_height[name] / essa_source for name in paths
    }
    for name, ratio in source_fill_ratio.items():
        assert 0.85 <= ratio <= 1.15, (
            f"heroes/{name}: idle source-cell fill differs too much from Essa "
            f"({ratio:.3f}); real-height scaling would be distorted"
        )

    projected = {
        name: source_idle_height[name] * height_cm[name] / height_cm["Essa"]
        for name in paths
    }
    kid_equal_ratio = projected["Adam"] / projected["Shaikha"]
    assert 0.92 <= kid_equal_ratio <= 1.08, (
        f"Adam and Shaikha are both 108cm but project differently: "
        f"ratio={kid_equal_ratio:.3f}"
    )
    mean_younger = (projected["Adam"] + projected["Shaikha"]) * 0.5
    sulaiman_to_younger = projected["Sulaiman"] / mean_younger
    assert 1.04 <= sulaiman_to_younger <= 1.27, (
        f"Sulaiman 124cm-to-younger 108cm projected ratio is "
        f"{sulaiman_to_younger:.3f}; expected about {124 / 108:.3f}"
    )
    assert projected["Essa"] > projected["Sulaiman"] > mean_younger, (
        "projected visible-height order must be Essa > Sulaiman > Adam/Shaikha"
    )
    return {
        "height_cm": height_cm,
        "idle_source_bbox_height": source_idle_height,
        "source_fill_vs_essa": {
            name: round(value, 4) for name, value in source_fill_ratio.items()
        },
        "projected_relative_to_essa_cell": {
            name: round(value / projected["Essa"], 4)
            for name, value in projected.items()
        },
        "sulaiman_to_mean_younger": round(sulaiman_to_younger, 4),
    }


def checker_cell(width: int, height: int, tile: int = 8) -> Image.Image:
    background = Image.new("RGBA", (width, height), (36, 39, 55, 255))
    draw = ImageDraw.Draw(background)
    alternate = (53, 57, 76, 255)
    for top in range(0, height, tile):
        for left in range(0, width, tile):
            if (left // tile + top // tile) % 2:
                draw.rectangle((left, top, left + tile - 1, top + tile - 1), fill=alternate)
    return background


def write_contact_sheet(assets: Path, contract: AtlasContract, destination: Path) -> None:
    with Image.open(assets / contract.relative) as source:
        atlas = source.convert("RGBA")
    label_width = 118
    header_height = 22
    output = checker_cell(label_width + atlas.width, header_height + atlas.height)
    output.alpha_composite(atlas, (label_width, header_height))
    draw = ImageDraw.Draw(output)
    draw.rectangle((0, 0, output.width - 1, header_height - 1), fill=(16, 19, 32, 255))
    draw.text((6, 6), contract.relative, fill=(244, 246, 255, 255))
    for column in range(contract.columns):
        x = label_width + column * contract.cell_width
        draw.text((x + 4, 6), str(column), fill=(180, 205, 255, 255))
        draw.line((x, header_height, x, output.height), fill=(98, 110, 145, 210))
    for row, row_name in enumerate(contract.rows):
        top = header_height + row * contract.cell_height
        draw.rectangle((0, top, label_width - 1, top + contract.cell_height - 1),
                       fill=(22, 25, 42, 255))
        draw.text((6, top + 8), f"{row}: {row_name}", fill=(239, 242, 255, 255))
        draw.line((label_width, top, output.width, top), fill=(98, 110, 145, 210))
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.convert("RGB").save(destination, quality=92, optimize=True)


def group_pack_check(present: Iterable[str], expected: Iterable[str], label: str) -> None:
    present_set = set(present)
    expected_set = set(expected)
    partial = present_set & expected_set
    assert not partial or partial == expected_set, (
        f"partial {label} animation pack: {sorted(partial)}; "
        f"missing {sorted(expected_set - partial)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument(
        "--allow-missing", action="store_true",
        help="validate only complete packs that are present instead of failing on absent atlases",
    )
    parser.add_argument(
        "--allow-nonclustered", action="store_true",
        help="skip the exact 2px pixel-cluster check (not suitable for release QA)",
    )
    parser.add_argument(
        "--contact-dir", type=Path,
        help="write labelled JPEG contact sheets after each atlas passes",
    )
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args()

    atlas_contracts = contracts()
    expected = [contract.relative for contract in atlas_contracts]
    present = [relative for relative in expected if (args.assets / relative).is_file()]
    hero_expected = [relative for relative in expected if relative.startswith("heroes/")]
    enemy_expected = [relative for relative in expected if relative.startswith("enemies/")]
    group_pack_check(present, hero_expected, "hero")
    group_pack_check(present, enemy_expected, "enemy")

    missing = sorted(set(expected) - set(present))
    if missing and not args.allow_missing:
        raise AssertionError(f"missing animation atlases: {missing}")

    records = load_manifest_records(args.assets)
    reports = []
    by_path = {contract.relative: contract for contract in atlas_contracts}
    for relative in present:
        contract = by_path[relative]
        report = validate_atlas(
            args.assets, contract, records,
            require_two_pixel_clusters=not args.allow_nonclustered,
        )
        reports.append(report)
        if args.contact_dir:
            write_contact_sheet(
                args.assets,
                contract,
                args.contact_dir / f"{Path(relative).stem}_contact.jpg",
            )
        print(
            f"PASS {relative}: {len(contract.rows)} real-motion rows, "
            f"{contract.columns} fixed cells each"
        )

    hero_scale = validate_hero_visible_scale(reports)
    if hero_scale is not None:
        print(
            "PASS hero visible scale: Essa 177cm > Sulaiman 124cm > "
            "Adam/Shaikha 108cm"
        )

    payload = {
        "assets": str(args.assets.resolve()),
        "expected": len(expected),
        "validated": len(reports),
        "missing": missing,
        "atlases": reports,
        "hero_visible_scale": hero_scale,
    }
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(
        f"Validated {len(reports)}/{len(expected)} animation atlases"
        + (f"; missing {len(missing)} (allowed)" if missing else ".")
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ANIMATION ATLAS QA FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
