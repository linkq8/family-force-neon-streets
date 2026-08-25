#!/usr/bin/env python3
"""Build crisp enemy variants directly from the two user-approved atlases.

Market Enforcer inherits Shield Guard's shield/baton silhouettes and motion.
Keeper-7 inherits Striker's large-glove silhouettes and motion.  Every output
tier is transformed from the matching approved tier, never from a reduced copy.
"""

from __future__ import annotations

import argparse
import colorsys
from pathlib import Path

from PIL import Image, ImageDraw


COLS = ROWS = 6
TIER_PATHS = {
    "base": "enemies/{actor}_anim.png",
    "runtime": "runtime/enemies/{actor}_anim.png",
    "tv": "tv/enemies/{actor}_anim.png",
}
TARGET_CELLS = {
    "base": (224, 192),
    "runtime": (336, 288),
    "tv": (196, 168),
}
SAFE_GUTTERS = {"base": 8, "runtime": 12, "tv": 7}


def shift_palette(image: Image.Image, actor: str) -> Image.Image:
    rgba = image.convert("RGBA")
    output = []
    for red, green, blue, alpha in rgba.getdata():
        if not alpha:
            output.append((0, 0, 0, 0))
            continue
        hue, saturation, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
        degrees = hue * 360
        if actor == "market_enforcer":
            # Cyan/teal armor and green shield energy become readable copper,
            # orange and amber while the approved navy joints remain intact.
            if 145 <= degrees <= 220 and saturation >= .28 and value >= .18:
                hue = 26 / 360
                saturation = min(1.0, saturation * 1.08)
                value = min(1.0, value * 1.04)
            elif 65 <= degrees < 145 and saturation >= .25:
                hue = 39 / 360
                saturation = min(1.0, saturation * .92)
                value = min(1.0, value * 1.10)
        else:
            # Striker teal becomes darker jade; coral accents become aged gold.
            if 145 <= degrees <= 220 and saturation >= .25:
                hue = 166 / 360
                saturation = min(1.0, saturation * .90)
                value = value * .78
            elif (degrees <= 55 or degrees >= 335) and saturation >= .28:
                hue = 42 / 360
                saturation = min(1.0, saturation * .82)
                value = min(1.0, value * 1.08)
        nr, ng, nb = colorsys.hsv_to_rgb(hue, saturation, value)
        output.append((round(nr * 255), round(ng * 255), round(nb * 255), 255))
    rgba.putdata(output)
    return rgba


def remove_white_edge_pixels(image: Image.Image, actor: str) -> Image.Image:
    """Replace only near-white silhouette pixels that touch transparency.

    Interior eye, armor and energy highlights are preserved. This specifically
    removes the pale halo that becomes conspicuous after TV filtering.
    """
    pixels = image.load()
    source = image.copy()
    original = source.load()
    edge_color = (35, 18, 25, 255) if actor == "market_enforcer" else (8, 29, 39, 255)
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = original[x, y]
            # Generated masters also contain medium-grey fringe pixels (roughly
            # RGB 120–190), which read as a white seam once filtered on TV.
            if alpha == 0 or min(red, green, blue) < 96 or max(red, green, blue) - min(red, green, blue) > 28:
                continue
            touches_clear = False
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    nx, ny = x + ox, y + oy
                    if nx < 0 or ny < 0 or nx >= image.width or ny >= image.height \
                            or original[nx, ny][3] == 0:
                        touches_clear = True
                        break
                if touches_clear:
                    break
            if touches_clear:
                pixels[x, y] = edge_color
    return image


def draw_keeper_identity(cell: Image.Image, clustered: bool) -> Image.Image:
    """Add a bold chest core and seven compact lanterns inside the safe box."""
    alpha_box = cell.getchannel("A").getbbox()
    if not alpha_box:
        return cell
    left, top, right, bottom = alpha_box
    width, height = right - left, bottom - top
    unit = 2 if clustered else max(1, round(cell.height / 96))
    draw = ImageDraw.Draw(cell)

    # The core is intentionally broad and geometric so it survives TV scaling.
    core_x = (left + right) // 2
    core_y = top + round(height * .39)
    radius = max(3 * unit, round(min(width, height) * .055))
    outline = max(unit, radius // 3)
    draw.ellipse((core_x-radius-outline, core_y-radius-outline,
                  core_x+radius+outline, core_y+radius+outline), fill=(10, 35, 42, 255))
    draw.ellipse((core_x-radius, core_y-radius, core_x+radius, core_y+radius),
                 fill=(64, 245, 226, 255))
    draw.rectangle((core_x-unit, core_y-radius, core_x+unit, core_y+radius),
                   fill=(205, 255, 205, 255))

    # Seven lanterns form one strong crown silhouette.  On grounded frames they
    # stay compact rather than forcing the whole actor to shrink dramatically.
    crown_width = max(14 * unit, round(width * .62))
    crown_left = max(4 * unit, core_x - crown_width // 2)
    crown_right = min(cell.width - 4 * unit, core_x + crown_width // 2)
    crown_top = max(4 * unit, top - 7 * unit)
    spacing = (crown_right - crown_left) / 6
    stem_y = crown_top + 5 * unit
    draw.line((crown_left, stem_y, crown_right, stem_y), fill=(70, 43, 12, 255), width=unit)
    for index in range(7):
        x = round(crown_left + index * spacing)
        lift = (3 - abs(3 - index)) * unit // 2
        y = crown_top - lift
        draw.line((x, stem_y, x, y + 4 * unit), fill=(118, 73, 18, 255), width=unit)
        draw.rectangle((x-2*unit, y, x+2*unit, y+4*unit), fill=(70, 43, 12, 255))
        draw.rectangle((x-unit, y+unit, x+unit, y+3*unit), fill=(255, 181, 35, 255))
    return cell


def remix_atlas(source: Image.Image, actor: str, tier: str) -> Image.Image:
    source = source.convert("RGBA")
    source_width, source_height = source.width // COLS, source.height // ROWS
    cell_width, cell_height = TARGET_CELLS[tier]
    gutter = SAFE_GUTTERS[tier]
    output = Image.new("RGBA", (cell_width * COLS, cell_height * ROWS), (0, 0, 0, 0))
    for row in range(ROWS):
        for column in range(COLS):
            source_box = (column * source_width, row * source_height,
                          (column + 1) * source_width, (row + 1) * source_height)
            remixed = shift_palette(source.crop(source_box), actor)
            alpha_box = remixed.getchannel("A").getbbox()
            if not alpha_box:
                raise ValueError(f"empty reference frame {tier} {row}:{column}")
            figure = remixed.crop(alpha_box)
            if figure.width > cell_width - gutter * 2 or figure.height > cell_height - gutter * 2:
                raise ValueError(
                    f"reference frame exceeds target safe box: {tier} {row}:{column} "
                    f"{figure.size} in {cell_width}x{cell_height}"
                )
            cell = Image.new("RGBA", (cell_width, cell_height), (0, 0, 0, 0))
            # Preserve every approved source pixel. Only placement changes:
            # horizontally centred and baseline-locked inside the target cell.
            x = (cell_width - figure.width) // 2
            y = cell_height - gutter - figure.height
            cell.alpha_composite(figure, (x, y))
            if actor == "keeper_7":
                cell = draw_keeper_identity(cell, tier == "base")
            cell = remove_white_edge_pixels(cell, actor)
            output.alpha_composite(cell, (column * cell_width, row * cell_height))
    return output


def fallback(runtime: Image.Image) -> Image.Image:
    cell = runtime.crop((0, 0, runtime.width // COLS, runtime.height // ROWS))
    box = cell.getchannel("A").getbbox()
    if not box:
        raise ValueError("empty idle frame")
    actor = cell.crop(box)
    scale = min(440 / actor.width, 464 / actor.height)
    actor = actor.resize((round(actor.width * scale), round(actor.height * scale)),
                         Image.Resampling.NEAREST)
    result = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    result.alpha_composite(actor, ((512 - actor.width) // 2, 496 - actor.height))
    return result


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True, compress_level=9)


def build(actor: str, assets: Path, output: Path) -> None:
    reference = "shield_guard" if actor == "market_enforcer" else "striker"
    built = {}
    for tier, pattern in TIER_PATHS.items():
        source_path = assets / pattern.format(actor=reference)
        built[tier] = remix_atlas(Image.open(source_path), actor, tier)
        save(built[tier], output / pattern.format(actor=actor))
    save(fallback(built["runtime"]), output / f"enemies/{actor}.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--actor", choices=("market_enforcer", "keeper_7", "all"),
                        default="all")
    args = parser.parse_args()
    actors = ("market_enforcer", "keeper_7") if args.actor == "all" else (args.actor,)
    for actor in actors:
        build(actor, args.assets, args.output)
        print(f"built reference remix: {actor}")


if __name__ == "__main__":
    main()
