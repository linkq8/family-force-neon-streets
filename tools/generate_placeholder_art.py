#!/usr/bin/env python3
"""Generate original, temporary SNES-sized art for the family beat-'em-up.

The generated PNGs are deliberately indexed and tile-aligned so the game can
be built before photo-derived final characters are available.  All drawing is
performed directly on the target pixel grid; contact-sheet enlargement uses
nearest-neighbour resampling only.

Outputs:
    assets/dev/actors.png        64 sequential 32x32 sprite blocks (128x512)
    assets/dev/portraits.png     four 64x64 character-select portraits
    assets/dev/enemy_wave0.png   wave-local 8-pose enemy atlas (8 KiB 4bpp)
    assets/dev/enemy_wave1.png   wave-local 8-pose enemy atlas (8 KiB 4bpp)
    assets/dev/enemy_wave2.png   wave-local 8-pose enemy atlas (8 KiB 4bpp)
    assets/dev/street.png        64 x 32 map of 8x8 indexed tiles
    assets/dev/select_bg.png     static 256x224 indexed character-select BG
    assets/dev/select_screen.png graphical four-character select mock-up
    assets/dev/contact_sheet.png enlarged visual-review sheet
    assets/dev/font.png          verbatim PVSnesLib MIT example font copy
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "dev"
FONT_SOURCE = Path(
    "/Users/essa/.codex/tools/pvsneslib-4.6.0/pvsneslib/snes-examples/"
    "graphics/Sprites/DynamicEngineMetaSprite/pvsneslibfont.png"
)
ENEMY_CONCEPT_SOURCES = (
    ROOT / "assets" / "higgsfield" / "enemy_grunt.png",
    ROOT / "assets" / "higgsfield" / "enemy_skater.png",
    ROOT / "assets" / "higgsfield" / "enemy_brute.png",
    ROOT / "assets" / "higgsfield" / "boss_junk_king.png",
)

STYLE_FORMULA = (
    "Authentic 16-bit SNES pixel art with crisp hand-placed pixels, compact "
    "color ramps, and energetic arcade-era animation. Bold readable "
    "silhouettes use dark navy outlines, chunky heroic proportions, and "
    "expressive faces. Nighttime neighborhood streets use indigo, sandstone, "
    "and teal, while family heroes wear distinct warm red, gold, cyan, and "
    "violet accents; hazards and pickups glow lime. The mood is adventurous, "
    "playful, and family-friendly under warm streetlights. High "
    "foreground-background contrast and a consistent side-view perspective "
    "keep every action readable."
)

BLOCK_SIZE = 32
FRAME_WIDTH = 32
FRAME_HEIGHT = 64
ACTIONS = ("IDLE", "WALK", "ATTACK", "HURT")
PACKED_BLOCK_COLUMNS = 4
PACKED_BLOCK_ROWS = 16

# Every wave atlas is 128x128: two four-pose banks. Within a bank the top
# halves are one 4-block row and the corresponding bottom halves are the next
# row. A None entry is a deliberately transparent spare pose.
ENEMY_WAVE_LAYOUTS = (
    (
        ("grunt", "idle"), ("grunt", "walk"),
        ("grunt", "attack"), ("grunt", "hurt"),
        ("grunt", "idle"), ("grunt", "walk"), None, None,
    ),
    (
        ("skater", "idle"), ("skater", "walk"), ("skater", "attack"),
        ("grunt", "idle"), ("grunt", "attack"),
        ("brute", "idle"), ("brute", "walk"), ("brute", "attack"),
    ),
    (
        ("grunt", "idle"), ("grunt", "attack"),
        ("boss", "idle"), ("boss", "walk"),
        ("boss", "attack"), ("boss", "hurt"),
        ("skater", "idle"), ("skater", "attack"),
    ),
)
ENEMY_ACTOR_INDEX = {"grunt": 4, "skater": 5, "brute": 6, "boss": 7}
ACTION_INDEX = {name.lower(): index for index, name in enumerate(ACTIONS)}

# One global 16-colour sprite palette. Index 0 is an explicit key colour and
# is also stored as PNG transparency. Every visible pixel uses indices 1..15.
ACTOR_PALETTE = (
    (255, 0, 255),   # 0 transparent/key magenta
    (10, 15, 35),    # 1 ink
    (29, 35, 67),    # 2 midnight cloth
    (72, 55, 91),    # 3 violet-brown shade
    (246, 211, 164), # 4 light skin
    (201, 139, 98),  # 5 warm skin
    (121, 75, 64),   # 6 deep skin
    (242, 235, 204), # 7 cream
    (218, 61, 68),   # 8 red
    (241, 132, 47),  # 9 orange
    (240, 200, 59),  # 10 yellow
    (59, 187, 104),  # 11 green
    (37, 158, 168),  # 12 teal
    (52, 91, 181),   # 13 blue
    (139, 71, 176),  # 14 purple
    (158, 166, 184), # 15 steel
)

# A separate 16-colour environment palette. Index 0 is opaque ink here.
STREET_PALETTE = (
    (7, 10, 24),     # 0 ink
    (14, 20, 45),    # 1 night
    (35, 31, 73),    # 2 violet sky/glass
    (62, 44, 86),    # 3 distant purple
    (77, 53, 72),    # 4 brick shadow
    (116, 66, 78),   # 5 brick light
    (41, 46, 65),    # 6 asphalt
    (72, 76, 89),    # 7 paving
    (126, 126, 120), # 8 concrete
    (209, 201, 161), # 9 warm pale light
    (244, 198, 76),  # 10 amber
    (231, 101, 62),  # 11 coral
    (51, 171, 157),  # 12 teal
    (56, 117, 169),  # 13 blue
    (153, 82, 175),  # 14 neon purple
    (231, 233, 213), # 15 paper white
)


def _flat_palette(colors: tuple[tuple[int, int, int], ...]) -> list[int]:
    """Expand 16 RGB triples to the 256-entry table required by PNG P mode."""
    assert len(colors) == 16
    flat = [channel for rgb in colors for channel in rgb]
    return flat + [0] * (768 - len(flat))


def indexed_image(
    size: tuple[int, int],
    palette: tuple[tuple[int, int, int], ...],
    fill: int = 0,
) -> Image.Image:
    image = Image.new("P", size, fill)
    image.putpalette(_flat_palette(palette))
    return image


@dataclass(frozen=True)
class Actor:
    label: str
    skin: int
    shirt: int
    pants: int
    shoes: int
    hair: int
    accent: int
    style: str
    head_top: int
    shoulder: int
    hip: int


ACTORS = (
    # The four heroes are original placeholders, not likeness claims. Their
    # enlarged heads intentionally reserve enough pixels for readable brows,
    # eye whites, pupils, noses and mouths at native SNES resolution.
    Actor("FAMILY HERO 1", 5, 8, 13, 7, 1, 8, "jacket", 3, 21, 42),
    Actor("FAMILY HERO 2", 4, 12, 13, 9, 3, 12, "cap", 5, 23, 43),
    Actor("FAMILY HERO 3", 5, 10, 11, 13, 3, 10, "headband", 6, 24, 44),
    Actor("FAMILY HERO 4", 6, 14, 8, 12, 1, 14, "hood", 5, 23, 43),
    Actor("ALLEY GRUNT", 5, 11, 2, 15, 1, 11, "bandana", 3, 21, 42),
    Actor("NIGHT SKATER", 4, 13, 14, 7, 3, 12, "skater", 5, 23, 43),
    Actor("MARKET BRUTE", 6, 9, 3, 1, 1, 9, "brute", 2, 21, 42),
    Actor("NEON BOSS", 4, 14, 2, 15, 15, 14, "boss", 2, 21, 42),
)


def stroke_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    color: int,
    width: int = 3,
) -> None:
    draw.line(points, fill=1, width=width + 2)
    draw.line(points, fill=color, width=width)


def outlined_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: int,
) -> None:
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=1)
    if x1 - x0 >= 2 and y1 - y0 >= 2:
        draw.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=fill)


def _leg_points(
    action: int,
    cx: int,
    hip: int,
    baseline: int,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    if action == 1:  # broad arcade walk pose
        return (
            [(cx - 4, hip), (cx - 7, baseline - 12), (cx - 9, baseline - 2)],
            [(cx + 3, hip), (cx + 6, baseline - 10), (cx + 9, baseline - 2)],
        )
    if action == 2:  # planted attack stance
        return (
            [(cx - 4, hip), (cx - 7, baseline - 10), (cx - 9, baseline - 2)],
            [(cx + 3, hip), (cx + 7, baseline - 9), (cx + 10, baseline - 2)],
        )
    if action == 3:  # hurt: stagger away from right-facing threat
        return (
            [(cx - 4, hip), (cx - 8, baseline - 10), (cx - 10, baseline - 2)],
            [(cx + 2, hip), (cx + 5, baseline - 12), (cx + 3, baseline - 2)],
        )
    return (
        [(cx - 4, hip), (cx - 5, baseline - 10), (cx - 5, baseline - 2)],
        [(cx + 3, hip), (cx + 5, baseline - 10), (cx + 6, baseline - 2)],
    )


def _draw_foot(
    draw: ImageDraw.ImageDraw,
    end: tuple[int, int],
    shoe: int,
) -> None:
    x, y = end
    # Toe points right in every frame, reinforcing the facing direction.
    outlined_box(draw, (max(1, x - 2), y - 2, min(30, x + 4), min(62, y + 1)), shoe)


def draw_actor(actor: Actor, action: int) -> Image.Image:
    """Draw one original, tall right-facing 32x64 arcade-brawler frame."""
    image = indexed_image((FRAME_WIDTH, FRAME_HEIGHT), ACTOR_PALETTE, 0)
    draw = ImageDraw.Draw(image)

    is_hurt = action == 3
    is_attack = action == 2
    bob = 1 if action == 1 else 0
    cx = 16 - (2 if is_hurt else 0)
    head_top = actor.head_top + bob + (1 if is_attack else 0)
    head_bottom = head_top + 15
    shoulder = actor.shoulder + bob
    hip = actor.hip
    baseline = 61
    leg_width = 5
    arm_width = 4 if actor.style in {"brute", "boss"} else 3

    # Cape, skateboard and other silhouette-defining pieces go behind limbs.
    if actor.style == "boss":
        draw.polygon(
            [(cx - 7, shoulder), (cx - 11, hip + 7), (cx - 3, hip + 5),
             (cx - 2, shoulder + 2)],
            fill=1,
        )
        draw.polygon(
            [(cx - 6, shoulder + 1), (cx - 9, hip + 5), (cx - 4, hip + 3),
             (cx - 3, shoulder + 2)],
            fill=14,
        )
    if actor.style == "hood":
        draw.rectangle((cx - 8, head_top + 3, cx - 5, shoulder + 9), fill=1)
        draw.rectangle((cx - 7, head_top + 4, cx - 5, shoulder + 8), fill=14)

    back_leg, front_leg = _leg_points(action, cx, hip, baseline)
    stroke_line(draw, back_leg, actor.pants, leg_width)
    stroke_line(draw, front_leg, actor.pants, leg_width)
    _draw_foot(draw, back_leg[-1], actor.shoes)
    _draw_foot(draw, front_leg[-1], actor.shoes)

    # Back arm is drawn before the torso.
    if is_attack:
        back_arm = [(cx - 5, shoulder + 3), (cx - 8, shoulder + 10), (cx - 2, hip - 2)]
    elif is_hurt:
        back_arm = [(cx - 5, shoulder + 3), (cx - 9, shoulder - 3), (cx - 10, shoulder - 8)]
    elif action == 1:
        back_arm = [(cx - 5, shoulder + 3), (cx - 9, shoulder + 11), (cx - 6, hip - 1)]
    else:
        back_arm = [(cx - 5, shoulder + 3), (cx - 7, shoulder + 12), (cx - 5, hip - 1)]
    stroke_line(draw, back_arm[:-1], actor.shirt, arm_width)
    stroke_line(draw, back_arm[-2:], actor.skin, max(2, arm_width - 1))

    body_half = 8 if actor.style in {"brute", "boss"} else 7
    body_x0 = cx - body_half
    body_x1 = cx + body_half
    if is_hurt:
        outer_body = [
            (body_x0 + 2, shoulder), (body_x1 + 2, shoulder),
            (body_x1, hip), (body_x0 - 1, hip),
        ]
        inner_body = [
            (body_x0 + 3, shoulder + 2), (body_x1 + 1, shoulder + 2),
            (body_x1 - 1, hip - 2), (body_x0, hip - 2),
        ]
    else:
        outer_body = [
            (body_x0 + 2, shoulder), (body_x1 - 2, shoulder),
            (body_x1, shoulder + 4), (body_x1 - 1, hip),
            (body_x0 + 1, hip), (body_x0, shoulder + 4),
        ]
        inner_body = [
            (body_x0 + 3, shoulder + 2), (body_x1 - 3, shoulder + 2),
            (body_x1 - 1, shoulder + 5), (body_x1 - 2, hip - 2),
            (body_x0 + 2, hip - 2), (body_x0 + 1, shoulder + 5),
        ]
    draw.polygon(outer_body, fill=1)
    draw.polygon(inner_body, fill=actor.shirt)

    # Character-specific costume marks make silhouettes and teams readable.
    if actor.style == "jacket":
        draw.line((cx, shoulder + 2, cx, hip - 2), fill=7)
        draw.rectangle((cx + 3, shoulder + 5, cx + 4, shoulder + 6), fill=15)
    elif actor.style == "cap":
        draw.rectangle((body_x0 + 2, shoulder + 6, body_x1 - 2, shoulder + 8), fill=10)
    elif actor.style == "headband":
        draw.rectangle((body_x0 + 2, hip - 5, body_x1 - 2, hip - 3), fill=13)
    elif actor.style == "hood":
        draw.rectangle((body_x0 + 1, shoulder + 4, body_x1 - 1, shoulder + 6), fill=12)
    elif actor.style == "bandana":
        draw.rectangle((body_x0 + 1, hip - 5, body_x1 - 1, hip - 3), fill=8)
    elif actor.style == "skater":
        draw.line((body_x0 + 1, shoulder + 4, body_x1 - 1, hip - 3), fill=12, width=2)
    elif actor.style == "brute":
        draw.rectangle((body_x0 + 2, shoulder + 6, body_x1 - 2, shoulder + 8), fill=8)
        draw.rectangle((body_x0 + 3, hip - 5, body_x1 - 3, hip - 3), fill=10)
    elif actor.style == "boss":
        draw.polygon([(cx, shoulder + 4), (cx + 3, shoulder + 7),
                      (cx, shoulder + 10), (cx - 3, shoulder + 7)], fill=10)
        draw.rectangle((body_x0 + 1, hip - 5, body_x1 - 1, hip - 3), fill=15)

    # Front arm and hand. Attack reaches x=30 while remaining in its cell.
    if is_attack:
        front_arm = [(cx + 5, shoulder + 3), (cx + 10, shoulder + 1), (28, shoulder + 2)]
        stroke_line(draw, front_arm[:2], actor.shirt, arm_width)
        stroke_line(draw, front_arm[1:], actor.skin, arm_width)
        outlined_box(draw, (27, shoulder - 1, 30, shoulder + 4), actor.skin)
    elif is_hurt:
        front_arm = [(cx + 5, shoulder + 3), (cx + 8, shoulder - 3), (cx + 10, shoulder - 8)]
        stroke_line(draw, front_arm[:2], actor.shirt, arm_width)
        stroke_line(draw, front_arm[1:], actor.skin, max(2, arm_width - 1))
        # Small impact spark uses the heroes/enemies' common signal yellow.
        sx, sy = min(29, cx + 12), max(2, shoulder - 10)
        draw.point((sx, sy), fill=10)
        draw.point((sx - 1, sy - 1), fill=10)
        draw.point((sx + 1, sy - 1), fill=10)
    elif action == 1:
        front_arm = [(cx + 5, shoulder + 3), (cx + 9, shoulder + 11), (cx + 7, hip - 1)]
        stroke_line(draw, front_arm[:2], actor.shirt, arm_width)
        stroke_line(draw, front_arm[1:], actor.skin, max(2, arm_width - 1))
    else:
        front_arm = [(cx + 5, shoulder + 3), (cx + 8, shoulder + 12), (cx + 6, hip - 1)]
        stroke_line(draw, front_arm[:2], actor.shirt, arm_width)
        stroke_line(draw, front_arm[1:], actor.skin, max(2, arm_width - 1))

    # Large three-quarter face: two eye whites/pupils, brow, nose and mouth
    # all survive native-resolution gameplay instead of reading as a blank dot.
    face_cx = cx + (1 if is_hurt else 0)
    outer_head = [
        (face_cx - 7, head_top + 3), (face_cx - 3, head_top),
        (face_cx + 4, head_top + 1), (face_cx + 7, head_top + 5),
        (face_cx + 7, head_bottom - 4), (face_cx + 4, head_bottom),
        (face_cx - 4, head_bottom), (face_cx - 7, head_bottom - 4),
    ]
    inner_head = [
        (face_cx - 6, head_top + 4), (face_cx - 2, head_top + 2),
        (face_cx + 3, head_top + 2), (face_cx + 6, head_top + 6),
        (face_cx + 6, head_bottom - 5), (face_cx + 3, head_bottom - 2),
        (face_cx - 3, head_bottom - 2), (face_cx - 6, head_bottom - 5),
    ]
    draw.polygon(outer_head, fill=1)
    draw.polygon(inner_head, fill=actor.skin)
    nose_y = head_top + 8
    draw.rectangle((face_cx + 4, nose_y, face_cx + 8, nose_y + 3), fill=1)
    draw.rectangle((face_cx + 4, nose_y, face_cx + 7, nose_y + 2), fill=actor.skin)

    # Hair/headwear treatments remain clear at native resolution.
    if actor.style == "cap":
        draw.rectangle((face_cx - 7, head_top, face_cx + 5, head_top + 4), fill=1)
        draw.rectangle((face_cx - 6, head_top + 1, face_cx + 5, head_top + 3), fill=12)
        draw.rectangle((face_cx + 4, head_top + 4, face_cx + 9, head_top + 5), fill=1)
        draw.rectangle((face_cx + 4, head_top + 4, face_cx + 8, head_top + 4), fill=12)
    elif actor.style == "headband":
        draw.rectangle((face_cx - 7, head_top + 2, face_cx + 6, head_top + 4), fill=13)
        draw.rectangle((face_cx - 10, head_top + 2, face_cx - 7, head_top + 3), fill=13)
        draw.point((face_cx - 10, head_top + 4), fill=13)
    elif actor.style == "hood":
        draw.line((face_cx - 7, head_top + 4, face_cx - 3, head_top,
                   face_cx + 5, head_top + 2), fill=14, width=3)
    elif actor.style == "bandana":
        draw.rectangle((face_cx - 7, head_top + 2, face_cx + 7, head_top + 4), fill=8)
        draw.line((face_cx - 7, head_top + 4, face_cx - 11, head_top + 7), fill=8, width=2)
    elif actor.style == "skater":
        draw.rectangle((face_cx - 7, head_top, face_cx + 5, head_top + 4), fill=12)
        draw.rectangle((face_cx + 4, head_top + 4, face_cx + 9, head_top + 5), fill=1)
        draw.rectangle((face_cx + 4, head_top + 4, face_cx + 8, head_top + 4), fill=12)
    elif actor.style == "brute":
        draw.polygon([(face_cx - 4, head_top + 2), (face_cx, max(1, head_top - 2)),
                      (face_cx + 4, head_top + 2)], fill=8)
    elif actor.style == "boss":
        draw.polygon([(face_cx - 5, head_top + 2), (face_cx - 3, max(1, head_top - 2)),
                      (face_cx, head_top), (face_cx + 3, max(1, head_top - 3)),
                      (face_cx + 6, head_top + 2)], fill=10)
        draw.line((face_cx - 5, head_top + 2, face_cx + 6, head_top + 2), fill=1)
    else:
        draw.rectangle((face_cx - 6, head_top + 1, face_cx + 4, head_top + 4), fill=actor.hair)
        draw.rectangle((face_cx - 6, head_top + 4, face_cx - 4, head_top + 9), fill=actor.hair)

    eye_y = head_top + 7
    # Eye whites and pupils are deliberately two-pixel motifs.
    draw.rectangle((face_cx - 1, eye_y, face_cx + 1, eye_y + 1), fill=7)
    draw.point((face_cx + 1, eye_y + 1), fill=1)
    draw.rectangle((face_cx + 4, eye_y, face_cx + 5, eye_y + 1), fill=7)
    draw.point((face_cx + 5, eye_y + 1), fill=1)
    draw.line((face_cx - 2, eye_y - 2, face_cx + 1, eye_y - 2), fill=1)
    draw.line((face_cx + 3, eye_y - 2, face_cx + 5, eye_y - 2), fill=1)
    mouth_y = head_bottom - 3
    draw.line((face_cx + 1, mouth_y, face_cx + 5, mouth_y), fill=1)
    draw.point((face_cx + 4, mouth_y + 1), fill=8)
    if actor.style == "jacket":
        # Two-pixel beard/sideburn, distinct from the other family heroes.
        draw.line((face_cx - 4, head_bottom - 4, face_cx + 1, head_bottom - 2), fill=3, width=2)

    if actor.style == "skater":
        # Board and wheels sit below the elevated foot line with a clear
        # transparent row at the cell edge.
        draw.line((3, 59, 29, 59), fill=1, width=3)
        draw.line((4, 58, 28, 58), fill=12)
        draw.rectangle((7, 61, 9, 62), fill=15)
        draw.rectangle((24, 61, 26, 62), fill=15)

    return image


def _nearest_actor_color(rgb: tuple[int, int, int]) -> int:
    """Map a concept pixel to the shared visible palette (never key index 0)."""
    r, g, b = rgb
    return min(
        range(1, 16),
        key=lambda index: (
            3 * (r - ACTOR_PALETTE[index][0]) ** 2
            + 4 * (g - ACTOR_PALETTE[index][1]) ** 2
            + 2 * (b - ACTOR_PALETTE[index][2]) ** 2
        ),
    )


def concept_to_sprite(path: Path) -> Image.Image:
    """Key and reduce a Higgsfield concept into a tall 32x64 runtime cell."""
    with Image.open(path) as source_file:
        source = source_file.convert("RGB")

    # Generated concepts use a hot-magenta key with small sampling variation.
    alpha_bytes = bytearray()
    for r, g, b in source.getdata():
        is_key = r >= 180 and b >= 180 and g <= 125 and r - g >= 75 and b - g >= 75
        alpha_bytes.append(0 if is_key else 255)
    alpha = Image.frombytes("L", source.size, bytes(alpha_bytes))
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError(f"No keyed subject found in {path}")

    subject = source.crop(bbox)
    subject_alpha = alpha.crop(bbox)

    # The concepts were intentionally composed as chunky square designs. A
    # controlled vertical arcade stretch makes them share the 32x64 gameplay
    # scale with the heroes while preserving the generated silhouettes,
    # costumes and faces. Nearest-neighbour keeps their pixel clusters crisp.
    natural_height = round(subject.height * 28 / subject.width)
    target_height = max(50, min(59, natural_height * 2))
    reduced_size = (28, target_height)
    subject = subject.resize(reduced_size, Image.Resampling.NEAREST)
    subject_alpha = subject_alpha.resize(reduced_size, Image.Resampling.NEAREST)

    sprite = indexed_image((FRAME_WIDTH, FRAME_HEIGHT), ACTOR_PALETTE, 0)
    x0 = (FRAME_WIDTH - reduced_size[0]) // 2
    y0 = 62 - reduced_size[1]
    color_cache: dict[tuple[int, int, int], int] = {}
    src_pixels = list(subject.getdata())
    mask_pixels = list(subject_alpha.getdata())
    dst = sprite.load()
    for y in range(reduced_size[1]):
        for x in range(reduced_size[0]):
            offset = y * reduced_size[0] + x
            if mask_pixels[offset] == 0:
                continue
            rgb = src_pixels[offset]
            if rgb not in color_cache:
                color_cache[rgb] = _nearest_actor_color(rgb)
            dst[x0 + x, y0 + y] = color_cache[rgb]

    if sum(1 for pixel in sprite.getdata() if pixel) < 250:
        raise ValueError(f"Concept reduction became unreadable: {path}")
    return sprite


def _shift_indexed(source: Image.Image, dx: int, dy: int) -> Image.Image:
    shifted = indexed_image(source.size, ACTOR_PALETTE, 0)
    shifted.paste(source, (dx, dy))
    return shifted


def concept_pose(base: Image.Image, action: int) -> Image.Image:
    """Create readable tall poses while retaining Higgsfield concept identity."""
    if action == 0:
        return base.copy()

    posed = indexed_image((FRAME_WIDTH, FRAME_HEIGHT), ACTOR_PALETTE, 0)
    src = base.load()
    dst = posed.load()
    dy = -1 if action == 1 else (1 if action == 3 else 0)
    for y in range(FRAME_HEIGHT):
        if action == 1:
            row_shift = 1 if y < 32 else (-1 if y > 47 else 0)
        elif action == 2:
            row_shift = 2 if y < 34 else (1 if y < 49 else 0)
        else:  # hurt: recoil away from the right-facing threat
            row_shift = -2 if y < 34 else (-1 if y < 49 else 0)
        for x in range(FRAME_WIDTH):
            pixel = src[x, y]
            tx, ty = x + row_shift, y + dy
            if pixel and 0 <= tx < FRAME_WIDTH and 0 <= ty < FRAME_HEIGHT:
                dst[tx, ty] = pixel

    mask = posed.point(lambda pixel: 255 if pixel else 0, mode="1")
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError("Empty concept pose")
    dx = 1 - bbox[0] if bbox[0] < 1 else (31 - bbox[2] if bbox[2] > 31 else 0)
    dy_fix = 1 - bbox[1] if bbox[1] < 1 else (63 - bbox[3] if bbox[3] > 63 else 0)
    return _shift_indexed(posed, dx, dy_fix) if dx or dy_fix else posed


def build_actor_sheet() -> tuple[Image.Image, list[str]]:
    """Pack 32 logical 32x64 frames as 64 sequential 32x32 blocks.

    Raster block order is:
      actor 0 idle/walk/attack/hurt TOP halves,
      actor 0 idle/walk/attack/hurt BOTTOM halves, then actor 1, etc.

    The 128x512 source therefore converts into exactly 64 row-major blocks.
    Runtime indexes are ``actor * 8 + action`` for the top and ``+4`` for the
    bottom. This layout lets the renderer select a state without repacking.
    """
    sheet = indexed_image(
        (BLOCK_SIZE * PACKED_BLOCK_COLUMNS, BLOCK_SIZE * PACKED_BLOCK_ROWS),
        ACTOR_PALETTE,
        0,
    )
    concepts_used: list[str] = []
    for row, actor in enumerate(ACTORS):
        concept_base: Image.Image | None = None
        if row >= 4:
            concept_path = ENEMY_CONCEPT_SOURCES[row - 4]
            if concept_path.exists():
                try:
                    concept_base = concept_to_sprite(concept_path)
                    concepts_used.append(concept_path.name)
                except (OSError, ValueError) as error:
                    print(f"warning: using procedural fallback for {actor.label}: {error}")
        for col in range(len(ACTIONS)):
            frame = concept_pose(concept_base, col) if concept_base is not None else draw_actor(actor, col)
            sheet.paste(frame.crop((0, 0, 32, 32)), (col * BLOCK_SIZE, row * FRAME_HEIGHT))
            sheet.paste(frame.crop((0, 32, 32, 64)), (col * BLOCK_SIZE, row * FRAME_HEIGHT + BLOCK_SIZE))
    sheet.info["transparency"] = 0
    return sheet, concepts_used


def unpack_actor_frame(sheet: Image.Image, actor: int, action: int) -> Image.Image:
    """Reconstruct one 32x64 frame from the actor's top/bottom block rows."""
    frame = indexed_image((FRAME_WIDTH, FRAME_HEIGHT), ACTOR_PALETTE, 0)
    x = action * BLOCK_SIZE
    y = actor * FRAME_HEIGHT
    frame.paste(sheet.crop((x, y, x + BLOCK_SIZE, y + FRAME_HEIGHT)), (0, 0))
    return frame


def build_portrait_sheet(actor_sheet: Image.Image) -> Image.Image:
    """Build four expressive 64x64 hero portraits in a 128x128 sheet."""
    portraits = indexed_image((128, 128), ACTOR_PALETTE, 0)
    draw = ImageDraw.Draw(portraits)
    for hero in range(4):
        x0 = (hero % 2) * 64
        y0 = (hero // 2) * 64
        accent = ACTORS[hero].accent
        draw.rectangle((x0 + 1, y0 + 1, x0 + 62, y0 + 62), fill=1)
        draw.rectangle((x0 + 3, y0 + 3, x0 + 60, y0 + 60), fill=3)
        draw.rectangle((x0 + 5, y0 + 5, x0 + 58, y0 + 58), outline=accent, width=2)
        frame = unpack_actor_frame(actor_sheet, hero, 0)
        crop = frame.crop((4, 0, 30, 27)).resize((52, 54), Image.Resampling.NEAREST)
        # Index 0 remains transparent over the violet portrait panel.
        mask = crop.point(lambda pixel: 255 if pixel else 0, mode="1")
        portraits.paste(crop, (x0 + 6, y0 + 7), mask)
    portraits.info["transparency"] = 0
    return portraits


def build_enemy_wave_atlas(actor_sheet: Image.Image, wave: int) -> Image.Image:
    """Build one 8-pose, 128x128 wave atlas (exactly 8 KiB at SNES 4bpp)."""
    layout = ENEMY_WAVE_LAYOUTS[wave]
    atlas = indexed_image((128, 128), ACTOR_PALETTE, 0)
    for pose_index, entry in enumerate(layout):
        if entry is None:
            continue
        enemy_name, state_name = entry
        frame = unpack_actor_frame(
            actor_sheet,
            ENEMY_ACTOR_INDEX[enemy_name],
            ACTION_INDEX[state_name],
        )
        bank = pose_index // 4
        column = pose_index % 4
        atlas.paste(frame.crop((0, 0, 32, 32)), (column * 32, bank * 64))
        atlas.paste(frame.crop((0, 32, 32, 64)), (column * 32, bank * 64 + 32))
    atlas.info["transparency"] = 0
    return atlas


def make_street_tile(kind: str, variant: int = 0) -> Image.Image:
    """Return a reusable 8x8 tile. Variants are intentionally bounded."""
    tile = indexed_image((8, 8), STREET_PALETTE, 0)
    d = ImageDraw.Draw(tile)

    if kind == "sky":
        d.rectangle((0, 0, 7, 7), fill=1)
        if variant == 1:
            d.point((2, 2), fill=15)
        elif variant == 2:
            d.point((6, 3), fill=10)
        elif variant == 3:
            d.point((3, 6), fill=13)
            d.point((4, 6), fill=13)
    elif kind.startswith("moon_"):
        d.rectangle((0, 0, 7, 7), fill=1)
        pieces = {
            "moon_tl": (3, 3, 7, 7), "moon_tr": (0, 2, 4, 7),
            "moon_bl": (3, 0, 7, 4), "moon_br": (0, 0, 4, 4),
        }
        d.rectangle(pieces[kind], fill=9)
        if kind == "moon_tr":
            d.rectangle((3, 2, 5, 5), fill=1)
        if kind == "moon_br":
            d.rectangle((3, 0, 5, 2), fill=1)
    elif kind == "roof":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((0, 5, 7, 7), fill=8)
        d.line((0, 4, 7, 4), fill=15)
    elif kind == "roof_teal":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((0, 4, 7, 7), fill=12)
        d.line((0, 4, 7, 4), fill=15)
    elif kind == "brick":
        d.rectangle((0, 0, 7, 7), fill=4)
        d.line((0, 3, 7, 3), fill=5)
        d.point(((variant * 3) % 7, 1), fill=5)
        d.line((2 if variant == 0 else 5, 4, 2 if variant == 0 else 5, 7), fill=5)
    elif kind == "purple_wall":
        d.rectangle((0, 0, 7, 7), fill=3)
        d.line((7, 0, 7, 7), fill=14 if variant else 2)
        d.point((2 + variant, 2), fill=14)
    elif kind == "teal_wall":
        d.rectangle((0, 0, 7, 7), fill=13)
        d.rectangle((0, 6, 7, 7), fill=12)
        if variant:
            d.line((1, 1, 6, 1), fill=12)
    elif kind == "alley":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((1, 0, 6, 7), fill=2)
        if variant:
            d.line((1, 6, 6, 6), fill=3)
    elif kind in {"window", "window_lit", "window_teal"}:
        glass = {"window": 2, "window_lit": 10, "window_teal": 12}[kind]
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((1, 1, 6, 6), fill=glass)
        d.line((3, 1, 3, 6), fill=8)
        d.line((1, 4, 6, 4), fill=8)
        if kind == "window_lit":
            d.point((5, 2), fill=15)
    elif kind == "balcony":
        d.rectangle((0, 0, 7, 7), fill=3)
        d.line((0, 2, 7, 2), fill=0, width=2)
        d.line((1, 2, 1, 7), fill=8)
        d.line((6, 2, 6, 7), fill=8)
    elif kind == "door":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((2, 0, 6, 7), fill=3)
        d.line((2, 0, 2, 7), fill=8)
        d.point((5, 4), fill=10)
    elif kind == "shutter":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((1, 0, 7, 7), fill=7)
        for y in (1, 3, 5, 7):
            d.line((1, y, 7, y), fill=8)
    elif kind == "sign_coral":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((1, 1, 6, 6), fill=11)
        d.line((2, 5, 5, 2), fill=15)
    elif kind == "sign_neon":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((1, 1, 6, 6), outline=14)
        d.line((2, 4, 3, 2, 5, 4, 5, 5), fill=15)
    elif kind == "sign_teal":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((0, 1, 7, 6), fill=12)
        d.line((1, 4, 3, 2, 6, 4), fill=9)
    elif kind == "awning_coral":
        d.rectangle((0, 0, 7, 7), fill=0)
        for x in range(0, 8, 4):
            d.rectangle((x, 1, x + 1, 6), fill=11)
            d.rectangle((x + 2, 1, x + 3, 6), fill=9)
        d.line((0, 0, 7, 0), fill=15)
    elif kind == "awning_teal":
        d.rectangle((0, 0, 7, 7), fill=0)
        for x in range(8):
            d.line((x, 1, x, 6), fill=12 if x % 4 < 2 else 15)
        d.line((0, 0, 7, 0), fill=9)
    elif kind == "stall_post":
        d.rectangle((0, 0, 7, 7), fill=0)
        d.rectangle((3, 0, 4, 7), fill=10)
        d.point((2, variant % 7), fill=11)
    elif kind == "stall_goods":
        d.rectangle((0, 0, 7, 7), fill=4)
        d.rectangle((0, 5, 7, 7), fill=10)
        goods = (11, 12, 10, 14)
        for x in (1, 3, 5):
            d.rectangle((x, 2 + ((x + variant) % 2), x + 1, 4), fill=goods[(x + variant) % 4])
    elif kind == "crate":
        d.rectangle((0, 0, 7, 7), fill=4)
        d.rectangle((1, 1, 6, 6), outline=10)
        d.line((1, 1, 6, 6), fill=5)
        d.line((6, 1, 1, 6), fill=5)
    elif kind == "lamp_top":
        d.rectangle((0, 0, 7, 7), fill=1)
        d.polygon([(2, 1), (5, 1), (7, 5), (6, 7), (1, 7), (0, 5)], fill=0)
        d.rectangle((2, 2, 5, 5), fill=10)
        d.point((3, 2), fill=15)
    elif kind == "lamp_post":
        d.rectangle((0, 0, 7, 7), fill=1 if variant == 0 else 7)
        d.rectangle((3, 0, 4, 7), fill=8)
        d.line((2, 0, 2, 7), fill=0)
    elif kind == "sidewalk":
        d.rectangle((0, 0, 7, 7), fill=7)
        d.line((0, 3, 7, 3), fill=8)
        x = 2 if variant == 0 else 6
        d.line((x, 0, x, 3), fill=6)
        d.line((7 - x, 4, 7 - x, 7), fill=6)
    elif kind == "curb":
        d.rectangle((0, 0, 7, 7), fill=6)
        d.rectangle((0, 0, 7, 3), fill=8)
        d.line((0, 4, 7, 4), fill=0)
        if variant:
            d.line((1, 1, 5, 1), fill=9)
    elif kind == "road":
        d.rectangle((0, 0, 7, 7), fill=6)
        if variant == 1:
            d.point((2, 2), fill=7)
            d.point((6, 6), fill=7)
        elif variant == 2:
            d.line((0, 5, 7, 5), fill=7)
        elif variant == 3:
            d.rectangle((2, 3, 5, 4), fill=8)
    elif kind == "puddle":
        d.rectangle((0, 0, 7, 7), fill=6)
        d.line((1, 4, 6, 4), fill=13)
        d.line((2, 5, 5, 5), fill=2)
        d.point((5, 3), fill=12)
    elif kind == "poster":
        d.rectangle((0, 0, 7, 7), fill=4)
        d.rectangle((2, 1, 6, 6), fill=9)
        d.rectangle((3, 2, 5, 3), fill=14)
        d.line((3, 5, 5, 5), fill=0)
    elif kind == "pipe":
        d.rectangle((0, 0, 7, 7), fill=3)
        d.rectangle((5, 0, 7, 7), fill=0)
        d.line((6, 0, 6, 7), fill=8)
    else:
        raise ValueError(f"Unknown tile kind: {kind}")

    return tile


def build_street() -> tuple[Image.Image, int]:
    # gfx4snes SC_64x32 paged maps require a complete 32-row page. The game
    # camera uses the composed top 28 rows (224 px); rows 28..31 are safe road
    # padding for conversion and offscreen scroll clamping.
    width_tiles, height_tiles = 64, 32
    grid: list[list[tuple[str, int]]] = [
        [("sky", (x * 5 + y * 3) % 4 if (x + y) % 7 == 0 else 0)
         for x in range(width_tiles)]
        for y in range(height_tiles)
    ]

    def put(x: int, y: int, kind: str, variant: int = 0) -> None:
        if 0 <= x < width_tiles and 0 <= y < height_tiles:
            grid[y][x] = (kind, variant)

    def rect(x0: int, y0: int, x1: int, y1: int, kind: str) -> None:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                put(x, y, kind, (x + y) & 1)

    # Moon and stars are themselves tile-aligned, not free-painted overlays.
    put(55, 1, "moon_tl")
    put(56, 1, "moon_tr")
    put(55, 2, "moon_bl")
    put(56, 2, "moon_br")

    # Four original neighbourhood facades frame an open market alley.
    rect(0, 6, 14, 17, "brick")
    for x in range(0, 15):
        put(x, 5, "roof")
    rect(15, 3, 30, 17, "teal_wall")
    for x in range(15, 31):
        put(x, 2, "roof_teal")
    rect(31, 8, 37, 17, "alley")
    rect(38, 6, 49, 17, "purple_wall")
    for x in range(38, 50):
        put(x, 5, "roof")
    rect(50, 4, 63, 17, "brick")
    for x in range(50, 64):
        put(x, 3, "roof")

    # Windows, signs and balconies repeat a small, converter-friendly kit.
    for x in (2, 6, 10):
        put(x, 8, "window_lit" if x != 6 else "window")
        put(x, 9, "balcony")
    put(1, 11, "poster")
    put(13, 12, "pipe")
    for x in (17, 21, 25, 29):
        put(x, 5, "window_teal" if x in (17, 25) else "window")
        put(x, 9, "window_lit" if x == 21 else "window")
    put(18, 12, "sign_teal")
    put(19, 12, "sign_teal")
    put(27, 13, "door")
    for x in (40, 44, 48):
        put(x, 8, "window" if x != 44 else "window_lit")
    put(41, 11, "sign_neon")
    put(42, 11, "sign_neon")
    for x in (52, 56, 60):
        put(x, 6, "window_lit" if x == 56 else "window")
        put(x, 10, "window")
    put(60, 12, "sign_coral")
    put(61, 12, "sign_coral")

    # Market stalls occupy the playfield edge without obscuring the fighters.
    for x in range(3, 13):
        put(x, 13, "awning_coral")
        put(x, 16, "stall_goods", x % 4)
    put(2, 14, "stall_post")
    put(13, 14, "stall_post", 1)
    put(2, 15, "stall_post", 2)
    put(13, 15, "stall_post", 3)
    for x in range(39, 49):
        put(x, 13, "awning_teal")
        put(x, 16, "stall_goods", (x + 1) % 4)
    put(38, 14, "stall_post")
    put(49, 14, "stall_post", 2)
    put(38, 15, "stall_post", 1)
    put(49, 15, "stall_post", 3)
    put(54, 16, "crate")
    put(55, 16, "crate")
    put(58, 15, "shutter")
    put(59, 15, "shutter")

    # Sidewalk and road are repeated 8x8 gameplay tiles.
    for y in range(18, 21):
        for x in range(width_tiles):
            put(x, y, "sidewalk", (x + y) & 1)
    for x in range(width_tiles):
        put(x, 21, "curb", 1 if x % 9 == 0 else 0)
    for y in range(22, 28):
        for x in range(width_tiles):
            put(x, y, "road", (x * 3 + y) % 3)
    for x in range(5, 63, 13):
        put(x, 26, "road", 3)
    for x in (18, 19, 44, 45):
        put(x, 23, "puddle", x & 1)

    for y in range(28, 32):
        for x in range(width_tiles):
            put(x, y, "road", (x * 3 + y) % 3)

    # One central lamp gives a readable pool of light and vertical landmark.
    put(34, 13, "lamp_top")
    for y in range(14, 22):
        put(34, y, "lamp_post", 1 if y >= 18 else 0)

    image = indexed_image((width_tiles * 8, height_tiles * 8), STREET_PALETTE, 0)
    tile_cache: dict[tuple[str, int], Image.Image] = {}
    for y, row in enumerate(grid):
        for x, key in enumerate(row):
            if key not in tile_cache:
                tile_cache[key] = make_street_tile(*key)
            image.paste(tile_cache[key], (x * 8, y * 8))

    unique_tiles = {
        bytes(image.crop((x, y, x + 8, y + 8)).getdata())
        for y in range(0, image.height, 8)
        for x in range(0, image.width, 8)
    }
    assert len(unique_tiles) <= 256
    return image, len(unique_tiles)


def transparent_rgba(frame: Image.Image) -> Image.Image:
    """Convert an indexed actor frame to RGBA using palette index 0 as key."""
    rgba = frame.convert("RGBA")
    alpha = Image.new("L", frame.size, 255)
    alpha.putdata([0 if pixel == 0 else 255 for pixel in frame.getdata()])
    rgba.putalpha(alpha)
    return rgba


def _centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text_value: str,
    fill: int | tuple[int, int, int],
    font: ImageFont.ImageFont,
) -> None:
    x0, y0, x1, y1 = box
    bounds = draw.textbbox((0, 0), text_value, font=font)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    draw.text(
        (x0 + (x1 - x0 + 1 - width) // 2, y0 + (y1 - y0 + 1 - height) // 2),
        text_value,
        fill=fill,
        font=font,
    )


def _tile_text(
    image: Image.Image,
    tile_y: int,
    text_value: str,
    fill: int,
    tile_x: int | None = None,
) -> None:
    """Draw one bitmap character per 8x8 cell for SNES tile reuse."""
    assert image.mode == "P"
    if tile_x is None:
        tile_x = (image.width // 8 - len(text_value)) // 2
    assert tile_x >= 0 and tile_x + len(text_value) <= image.width // 8
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for index, character in enumerate(text_value):
        draw.text(
            ((tile_x + index) * 8 + 1, tile_y * 8),
            character,
            fill=fill,
            font=font,
        )


def build_select_background(portrait_sheet: Image.Image) -> Image.Image:
    """Build the static indexed BG0 art for character selection.

    Player markers and selection highlights are deliberately absent. Runtime
    text/sprites can draw P1 and P2 independently without erasing this map.
    All four cards share the same geometry; accent colors identify characters
    but do not imply a selected card.
    """
    screen = indexed_image((256, 224), ACTOR_PALETTE, 1)
    draw = ImageDraw.Draw(screen)
    draw.rectangle((3, 3, 252, 220), outline=10, width=2)
    draw.rectangle((7, 7, 248, 31), fill=2, outline=12)
    _tile_text(screen, 2, "CHOOSE YOUR FAMILY HERO", 7)

    role_labels = ("POW", "SPD", "BAL", "TEC")
    card_accents = (8, 12, 10, 14)
    for hero in range(4):
        # A constant x modulo 8 makes corresponding card tiles reusable.
        x0 = 4 + hero * 64
        x1 = x0 + 55
        accent = card_accents[hero]
        draw.rectangle((x0, 38, x1, 163), fill=2, outline=3, width=2)
        draw.line((x0 + 2, 40, x1 - 2, 40), fill=accent, width=2)
        draw.rectangle((x0 + 3, 43, x1 - 3, 101), fill=3)

        portrait_x = (hero % 2) * 64
        portrait_y = (hero // 2) * 64
        portrait = portrait_sheet.crop((portrait_x, portrait_y, portrait_x + 64, portrait_y + 64))
        portrait = portrait.resize((32, 32), Image.Resampling.NEAREST)
        mask = portrait.point(lambda pixel: 255 if pixel else 0, mode="1")
        screen.paste(portrait, (x0 + 12, 56), mask)

        draw.line((x0 + 4, 102, x1 - 4, 102), fill=accent)
        _tile_text(screen, 14, f"HERO {hero + 1}", 7, hero * 8 + 1)
        _tile_text(screen, 16, role_labels[hero], accent, hero * 8 + 2)
        for pip in range(4):
            px = x0 + 9 + pip * 10
            color = accent if pip <= hero % 3 + 1 else 3
            draw.rectangle((px, 144, px + 6, 149), fill=color)
        # Confirm/back controls live in the shared instruction panel below;
        # keeping cards uncluttered also lets their lower tiles repeat.

    draw.rectangle((7, 171, 248, 215), fill=2, outline=3)
    _tile_text(screen, 22, "D-PAD CHOOSE  A CONFIRM", 7)
    _tile_text(screen, 25, "P2 START JOIN  B BACK", 12)
    return screen


def build_select_screen(actor_sheet: Image.Image, portrait_sheet: Image.Image) -> Image.Image:
    """Preview the static select BG with example dynamic P1/P2 markers."""
    _ = actor_sheet
    screen = build_select_background(portrait_sheet).convert("RGB")
    draw = ImageDraw.Draw(screen)
    font = ImageFont.load_default()

    # P1/P2 cursor ribbons preview local co-op character selection.
    draw.polygon([(7, 36), (24, 36), (28, 41), (24, 46), (7, 46)], fill=ACTOR_PALETTE[8])
    draw.text((10, 37), "P1", fill=ACTOR_PALETTE[7], font=font)
    draw.polygon([(199, 158), (216, 158), (220, 163), (216, 168), (199, 168)], fill=ACTOR_PALETTE[12])
    draw.text((202, 159), "P2", fill=ACTOR_PALETTE[7], font=font)
    return screen


def build_contact_sheet(
    actor_sheet: Image.Image,
    portrait_sheet: Image.Image,
    street: Image.Image,
) -> Image.Image:
    width, height = 1280, 3220
    contact = Image.new("RGB", (width, height), (10, 15, 35))
    draw = ImageDraw.Draw(contact)
    font = ImageFont.load_default()
    draw.text((20, 14), "FAMILY FORCE - TALL ARCADE FIGHTER ART REVIEW", fill=(242, 235, 204), font=font)
    draw.text((20, 29), "32x64 LOGICAL FRAMES / FOUR STATES / 64 SEQUENTIAL 32x32 SNES BLOCKS", fill=(158, 166, 184), font=font)

    # Lead with the requested graphical selection screen at 4x nearest scale.
    select_screen = build_select_screen(actor_sheet, portrait_sheet)
    select_large = select_screen.resize((1024, 896), Image.Resampling.NEAREST)
    contact.paste(select_large, (128, 52))
    draw.rectangle((0, 956, 1279, 959), fill=(241, 132, 47))
    draw.text((20, 970), "NATIVE 256x224 CHARACTER SELECT PREVIEW (SHOWN AT 4x)", fill=(240, 200, 59), font=font)

    # Review only the 224px visible camera composition; the final 32px is
    # converter padding for the complete 64x32 map page.
    street_visible = street.crop((0, 0, 512, 224))
    street_large = street_visible.convert("RGB").resize((1024, 448), Image.Resampling.NEAREST)
    contact.paste(street_large, (128, 995))
    draw.rectangle((0, 1451, 1279, 1454), fill=(241, 132, 47))
    draw.text((20, 1466), "32x64 GAMEPLAY CELLS (SHOWN AT 3x) - HEROES ARE PLACEHOLDERS", fill=(240, 200, 59), font=font)

    start_x, start_y = 300, 1510
    slot_w, slot_h = 224, 204
    for col, action in enumerate(ACTIONS):
        _centered_text(
            draw,
            (start_x + col * slot_w, 1485, start_x + col * slot_w + 95, 1504),
            action,
            (242, 235, 204),
            font,
        )

    for row, actor in enumerate(ACTORS):
        y = start_y + row * slot_h
        draw.text((20, y + 76), actor.label, fill=ACTOR_PALETTE[actor.accent], font=font)
        if row < 4:
            draw.text((20, y + 91), "ORIGINAL PLACEHOLDER", fill=ACTOR_PALETTE[15], font=font)
        else:
            draw.text((20, y + 91), "HIGGSFIELD-DERIVED", fill=ACTOR_PALETTE[12], font=font)
        for col in range(len(ACTIONS)):
            x = start_x + col * slot_w
            # Pixel checker makes the index-0 transparency easy to review.
            cell = Image.new("RGB", (96, 192), (35, 31, 73))
            cd = ImageDraw.Draw(cell)
            for yy in range(0, 192, 12):
                for xx in range(0, 96, 12):
                    if (xx // 12 + yy // 12) & 1:
                        cd.rectangle((xx, yy, xx + 11, yy + 11), fill=(29, 35, 67))
            frame = transparent_rgba(unpack_actor_frame(actor_sheet, row, col)).resize((96, 192), Image.Resampling.NEAREST)
            cell.paste(frame, (0, 0), frame)
            contact.paste(cell, (x, y))

    palette_y = 3202
    draw.text((20, palette_y - 14), "ACTOR PALETTE", fill=(242, 235, 204), font=font)
    for i, color in enumerate(ACTOR_PALETTE):
        x = 130 + i * 28
        draw.rectangle((x, palette_y - 10, x + 23, palette_y + 9), fill=color)
        draw.text((x + 7, palette_y - 8), f"{i:X}", fill=(255, 255, 255) if sum(color) < 330 else (0, 0, 0), font=font)
    return contact


def used_indices(image: Image.Image) -> list[int]:
    colors = image.getcolors(maxcolors=image.width * image.height)
    assert colors is not None
    return sorted(index for _count, index in colors)


def unique_8x8_tile_count(image: Image.Image) -> int:
    assert image.width % 8 == 0 and image.height % 8 == 0
    return len({
        bytes(image.crop((x, y, x + 8, y + 8)).getdata())
        for y in range(0, image.height, 8)
        for x in range(0, image.width, 8)
    })


def validate_actor_frames(sheet: Image.Image) -> None:
    assert sheet.mode == "P"
    assert sheet.size == (128, 512)
    assert sheet.info.get("transparency") == 0
    assert max(used_indices(sheet)) < 16
    assert sheet.width // 32 * (sheet.height // 32) == 64
    for row in range(8):
        for col in range(4):
            frame = unpack_actor_frame(sheet, row, col)
            visible = sum(1 for px in frame.getdata() if px != 0)
            assert visible >= 240, (row, col, visible)
            bbox = frame.point(lambda pixel: 255 if pixel else 0, mode="1").getbbox()
            assert bbox is not None
            assert bbox[0] > 0 and bbox[1] > 0 and bbox[2] < 32 and bbox[3] < 64, (row, col, bbox)

    # Byte-for-byte unpack validation guards the exact top/bottom ordering.
    for actor in range(8):
        for action in range(4):
            expected = (
                concept_pose(concept_to_sprite(ENEMY_CONCEPT_SOURCES[actor - 4]), action)
                if actor >= 4 and ENEMY_CONCEPT_SOURCES[actor - 4].exists()
                else draw_actor(ACTORS[actor], action)
            )
            assert bytes(unpack_actor_frame(sheet, actor, action).getdata()) == bytes(expected.getdata())


def validate_auxiliary_actor_art(
    portraits: Image.Image,
    wave_atlases: list[Image.Image],
) -> None:
    assert portraits.mode == "P" and portraits.size == (128, 128)
    assert portraits.info.get("transparency") == 0
    assert max(used_indices(portraits)) < 16
    for hero in range(4):
        x = (hero % 2) * 64
        y = (hero // 2) * 64
        portrait = portraits.crop((x, y, x + 64, y + 64))
        assert sum(1 for pixel in portrait.getdata() if pixel) >= 900

    assert len(wave_atlases) == 3
    for wave, atlas in enumerate(wave_atlases):
        assert atlas.mode == "P" and atlas.size == (128, 128)
        assert atlas.info.get("transparency") == 0
        assert atlas.width // 32 * (atlas.height // 32) == 16
        assert max(used_indices(atlas)) < 16
        for pose, entry in enumerate(ENEMY_WAVE_LAYOUTS[wave]):
            bank = pose // 4
            column = pose % 4
            top = atlas.crop((column * 32, bank * 64, column * 32 + 32, bank * 64 + 32))
            bottom = atlas.crop((column * 32, bank * 64 + 32, column * 32 + 32, bank * 64 + 64))
            visible = sum(1 for pixel in top.getdata() if pixel) + sum(1 for pixel in bottom.getdata() if pixel)
            assert (visible == 0) == (entry is None), (wave, pose, entry, visible)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    actors, concepts_used = build_actor_sheet()
    portraits = build_portrait_sheet(actors)
    wave_atlases = [build_enemy_wave_atlas(actors, wave) for wave in range(3)]
    select_background = build_select_background(portraits)
    select_preview = build_select_screen(actors, portraits)
    street, tile_count = build_street()
    validate_actor_frames(actors)
    validate_auxiliary_actor_art(portraits, wave_atlases)
    assert street.mode == "P" and street.size == (512, 256)
    assert max(used_indices(street)) < 16
    select_tile_count = unique_8x8_tile_count(select_background)
    assert select_background.mode == "P" and select_background.size == (256, 224)
    assert select_background.info.get("transparency") is None
    assert max(used_indices(select_background)) < 16
    assert select_tile_count <= 256
    # The RGB review preview may differ from the runtime BG only inside the
    # two example dynamic marker ribbons. This proves cursors are not baked in.
    base_rgb = select_background.convert("RGB")
    for y in range(224):
        for x in range(256):
            if base_rgb.getpixel((x, y)) == select_preview.getpixel((x, y)):
                continue
            in_p1_marker = 7 <= x <= 28 and 36 <= y <= 46
            in_p2_marker = 199 <= x <= 220 and 158 <= y <= 168
            assert in_p1_marker or in_p2_marker, (x, y)

    actor_path = OUT_DIR / "actors.png"
    portrait_path = OUT_DIR / "portraits.png"
    wave_paths = [OUT_DIR / f"enemy_wave{wave}.png" for wave in range(3)]
    street_path = OUT_DIR / "street.png"
    select_bg_path = OUT_DIR / "select_bg.png"
    select_path = OUT_DIR / "select_screen.png"
    contact_path = OUT_DIR / "contact_sheet.png"
    font_path = OUT_DIR / "font.png"

    actors.save(actor_path, transparency=0, optimize=False)
    portraits.save(portrait_path, transparency=0, optimize=False)
    for atlas, path in zip(wave_atlases, wave_paths):
        atlas.save(path, transparency=0, optimize=False)
    street.save(street_path, optimize=False)
    select_background.save(select_bg_path, optimize=False)
    select_preview.save(select_path, optimize=False)
    build_contact_sheet(actors, portraits, street).save(contact_path, optimize=False)
    if not FONT_SOURCE.exists():
        raise FileNotFoundError(f"Bundled PVSnesLib font not found: {FONT_SOURCE}")
    shutil.copyfile(FONT_SOURCE, font_path)

    actor_indices = used_indices(actors)
    street_indices = used_indices(street)
    print(f"{actor_path}: {actors.size[0]}x{actors.size[1]}, P, "
          f"64 blocks / 32 tall frames, indices={actor_indices}, transparent=0")
    print("actor block order: top=actor*8+state; bottom=actor*8+4+state")
    print(f"{portrait_path}: 128x128 P, four 64x64 portraits, transparent=0")
    for wave, path in enumerate(wave_paths):
        mapping = ", ".join(
            f"{pose}={'blank' if entry is None else entry[0] + '/' + entry[1]}"
            for pose, entry in enumerate(ENEMY_WAVE_LAYOUTS[wave])
        )
        print(f"{path}: 128x128 P, 16 blocks = 8192 SNES 4bpp bytes; {mapping}")
    print(f"Higgsfield enemy concept rows: {', '.join(concepts_used) if concepts_used else 'procedural fallbacks'}")
    print(f"{street_path}: {street.size[0]}x{street.size[1]}, P, "
          f"indices={street_indices}, unique_8x8_tiles={tile_count}")
    print(f"{select_bg_path}: 256x224 P, indices={used_indices(select_background)}, "
          f"unique_8x8_tiles={select_tile_count}, no baked player markers")
    with Image.open(contact_path) as contact:
        print(f"{contact_path}: {contact.size[0]}x{contact.size[1]}, {contact.mode}")
    with Image.open(select_path) as select:
        print(f"{select_path}: {select.size[0]}x{select.size[1]}, {select.mode}")
    with Image.open(font_path) as font_image:
        print(f"{font_path}: {font_image.size[0]}x{font_image.size[1]}, "
              f"{font_image.mode}, colors={len(font_image.getcolors() or [])}")


if __name__ == "__main__":
    main()
