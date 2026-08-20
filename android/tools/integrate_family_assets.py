#!/usr/bin/env python3
"""Convert Higgsfield family masters into fine-cluster Android pixel assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "higgsfield" / "android" / "family"
ANIMATION = ROOT / "assets" / "higgsfield" / "android" / "animation_v2"
OUTPUT = ROOT / "android" / "app" / "src" / "main" / "assets"
NAMES = ("parent", "adam", "shaikha", "sulaiman")
DISPLAY_NAMES = ("ESSA", "ADAM", "SHAIKHA", "SULAIMAN")
HEIGHTS_CM = (177, 108, 108, 124)
ACCENTS = ((255, 76, 74), (83, 220, 92), (255, 110, 190), (69, 142, 255))
MASTER_CANDIDATES = ("master.png", "transparent.png", "fullbody.png")
MASTER_OVERRIDES = {
    "adam": ANIMATION / "actors" / "hero_2" / "removed" / "punch" / "00.png",
    "sulaiman": ANIMATION / "masters" / "sulaiman" / "master.png",
}
PORTRAIT_OVERRIDES = {
    "adam": ANIMATION / "actors" / "hero_2" / "removed" / "punch" / "00.png",
    "sulaiman": ANIMATION / "masters" / "sulaiman" / "portrait.png",
}


def quantize_rgba(image: Image.Image, colors: int = 96) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    rgb = rgba.convert("RGB").quantize(
        colors=colors,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.FLOYDSTEINBERG,
    ).convert("RGB")
    rgb.putalpha(alpha)
    return clean_transparent_rgb(rgb)


def clean_transparent_rgb(image: Image.Image) -> Image.Image:
    """Keep fully transparent pixels black so Android scaling cannot make halos."""
    rgba = image.convert("RGBA")
    rgba.putdata([
        (0, 0, 0, 0) if opacity == 0 else (red, green, blue, opacity)
        for red, green, blue, opacity in rgba.getdata()
    ])
    return rgba


def despill_key_edge(image: Image.Image) -> Image.Image:
    """Neutralize a saturated chroma-key fringe without touching interior color."""
    rgba = image.convert("RGBA")
    key = rgba.getpixel((0, 0))
    key_rgb = key[:3]
    dominant = max(range(3), key=lambda index: key_rgb[index])
    others = [key_rgb[index] for index in range(3) if index != dominant]
    if key[3] != 0 or key_rgb[dominant] - max(others) < 70:
        return rgba

    alpha = rgba.getchannel("A")
    clear = alpha.point(lambda opacity: 255 if opacity == 0 else 0)
    edge = clear.filter(ImageFilter.MaxFilter(5))
    output = []
    for (red, green, blue, opacity), edge_value in zip(rgba.getdata(), edge.getdata()):
        channels = [red, green, blue]
        other_max = max(channels[index] for index in range(3) if index != dominant)
        excess = channels[dominant] - other_max
        if opacity > 0 and (opacity < 250 or edge_value > 0) and excess > 28:
            channels[dominant] = min(channels[dominant], other_max + 18)
        output.append((*channels, opacity))
    rgba.putdata(output)
    return rgba


def build_master(path: Path) -> Image.Image:
    source = despill_key_edge(Image.open(path))
    bbox = source.getchannel("A").point(
        lambda opacity: 255 if opacity >= 128 else 0
    ).getbbox()
    if bbox is None:
        raise ValueError(f"No visible character in {path}")
    character = source.crop(bbox)
    low = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    scale = min(116 / character.width, 180 / character.height)
    size = (max(1, round(character.width * scale)), max(1, round(character.height * scale)))
    character = character.resize(size, Image.Resampling.NEAREST)
    x = (low.width - character.width) // 2
    y = low.height - character.height - 4
    low.alpha_composite(character, (x, y))
    low.putalpha(low.getchannel("A").point(lambda opacity: 255 if opacity >= 128 else 0))
    low = quantize_rgba(low, 96)
    return low.resize((256, 384), Image.Resampling.NEAREST)


def build_portrait(path: Path, *, upper_body: bool = False) -> Image.Image:
    source = clean_transparent_rgb(Image.open(path).convert("RGBA"))
    bbox = source.getchannel("A").point(
        lambda opacity: 255 if opacity >= 128 else 0
    ).getbbox()
    if bbox is None:
        raise ValueError(f"No visible portrait subject in {path}")
    if upper_body:
        # Adam's approved organic source is a full-body authored animation cell.
        # Crop head/shoulders/upper torso for the character-select portrait.
        height = bbox[3] - bbox[1]
        bbox = (bbox[0], bbox[1], bbox[2], min(bbox[3], bbox[1] + round(height * 0.64)))
    subject = source.crop(bbox)
    low = Image.new("RGBA", (128, 128), (42, 46, 104, 255))
    scale = min(120 / subject.width, 122 / subject.height)
    size = (max(1, round(subject.width * scale)), max(1, round(subject.height * scale)))
    subject = subject.resize(size, Image.Resampling.NEAREST)
    x = (low.width - subject.width) // 2
    y = low.height - subject.height
    low.alpha_composite(subject, (x, y))
    portrait_mask = Image.new("L", low.size, 0)
    ImageDraw.Draw(portrait_mask).rounded_rectangle(
        (1, 1, 126, 126), radius=14, fill=255
    )
    low.putalpha(portrait_mask)
    low = quantize_rgba(low, 112)
    return clean_transparent_rgb(low.resize((256, 256), Image.Resampling.NEAREST))


def write_manifest() -> None:
    records = []
    for path in sorted(OUTPUT.rglob("*")):
        if not path.is_file() or path.name == "asset_manifest.json":
            continue
        record = {
            "path": path.relative_to(OUTPUT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                record.update({"width": image.width, "height": image.height, "mode": image.mode})
        records.append(record)
    prior = json.loads((OUTPUT / "asset_manifest.json").read_text(encoding="utf-8"))
    prior["files"] = records
    prior["status"] = (
        "direct-reference family character pack; likeness quality is provisional "
        "until five or more photos per person enable Soul training"
    )
    (OUTPUT / "asset_manifest.json").write_text(
        json.dumps(prior, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def find_master(name: str) -> Path:
    override = MASTER_OVERRIDES.get(name)
    if override is not None:
        if not override.is_file():
            raise FileNotFoundError(f"Missing generated master override for {name}: {override}")
        return override
    directory = SOURCE / name
    for filename in MASTER_CANDIDATES:
        candidate = directory / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(str(directory / filename) for filename in MASTER_CANDIDATES)
    raise FileNotFoundError(f"Missing generated master for {name}; checked {expected}")


def main() -> None:
    hero_out = OUTPUT / "heroes"
    hero_out.mkdir(parents=True, exist_ok=True)
    sources = []
    for name in NAMES:
        master_path = find_master(name)
        portrait_path = PORTRAIT_OVERRIDES.get(name, SOURCE / name / "portrait.png")
        if not portrait_path.is_file():
            raise FileNotFoundError(
                f"Missing generated assets for {name}: {master_path}, {portrait_path}"
            )
        sources.append((name, master_path, portrait_path))

    final_masters = []
    final_portraits = []
    for name, master_path, portrait_path in sources:
        final_masters.append(build_master(master_path))
        final_portraits.append(build_portrait(
            portrait_path, upper_body=(name == "adam")
        ))

    for (name, _, _), master, portrait in zip(
            sources, final_masters, final_portraits):
        master.save(hero_out / f"{name}.png", optimize=True)
        portrait.save(hero_out / f"{name}_portrait.png", optimize=True)

    sheet = Image.new("RGB", (1280, 720), (11, 12, 35))
    draw = ImageDraw.Draw(sheet)
    parent_visible_bbox = final_masters[0].getchannel("A").getbbox()
    if parent_visible_bbox is None:
        raise ValueError("Integrated Essa master has no visible pixels")
    parent_visible_height = parent_visible_bbox[3] - parent_visible_bbox[1]
    for index, (name, display_name, height_cm, accent, master, portrait) in enumerate(
            zip(NAMES, DISPLAY_NAMES, HEIGHTS_CM, ACCENTS, final_masters, final_portraits)):
        x = 24 + index * 312
        draw.rounded_rectangle((x, 24, x + 288, 690), radius=18,
                               fill=(22, 24, 59), outline=accent, width=5)
        portrait_preview = portrait.resize((240, 240), Image.Resampling.NEAREST)
        visible_bbox = master.getchannel("A").getbbox()
        if visible_bbox is None:
            raise ValueError(f"Integrated {display_name} master has no visible pixels")
        visible_height = visible_bbox[3] - visible_bbox[1]
        relative_scale = (
            (height_cm / HEIGHTS_CM[0])
            * (parent_visible_height / visible_height)
        )
        master_preview = master.resize(
            (round(220 * relative_scale), round(330 * relative_scale)),
            Image.Resampling.NEAREST,
        )
        sheet.paste(portrait_preview, (x + 24, 50), portrait_preview)
        master_x = x + (288 - master_preview.width) // 2
        master_y = 640 - master_preview.height
        sheet.paste(master_preview, (master_x, master_y), master_preview)
        draw.text(
            (x + 144, 672), f"{display_name}  •  {height_cm} CM",
            anchor="mm", fill=accent,
        )
    sheet.save(SOURCE / "family_contact_sheet.png", optimize=True)
    write_manifest()
    print(f"Integrated {len(NAMES)} personalized hero masters and portraits.")


if __name__ == "__main__":
    main()
