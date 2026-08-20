#!/usr/bin/env python3
"""Build the Android vertical slice's deterministic base asset pack.

The script only writes under android/app/src/main/assets. Personalized family
masters are integrated afterward by integrate_family_assets.py. Existing
Higgsfield concepts and the procedural SNES art/audio are reused; new item, UI,
and VFX assets are drawn deterministically here.
"""

from __future__ import annotations

from array import array
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import struct
import subprocess
import tempfile
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "android" / "app" / "src" / "main" / "assets"

STYLE_FORMULA = (
    "High-detail retro arcade pixel art rendered at a modern 360p-to-720p game "
    "resolution, with fine 2–4 pixel clusters, crisp edges, selective dithering, "
    "and no oversized block pixels. Athletic readable silhouettes use dark navy "
    "outlines, expressive recognizable faces, dynamic foreshortening, and "
    "slightly exaggerated 1990s beat-’em-up proportions. Night streets use "
    "indigo, teal, and warm amber; heroes use distinct red-gold, green-purple, "
    "pink-ice, and blue-red palettes. Energetic family-friendly lighting and "
    "strong foreground contrast maintain a consistent three-quarter side-view "
    "belt-brawler perspective."
)

INK = (9, 15, 38, 255)
MIDNIGHT = (24, 31, 65, 255)
PANEL = (39, 42, 82, 238)
VIOLET = (85, 60, 112, 255)
CREAM = (248, 236, 202, 255)
CORAL = (231, 70, 75, 255)
ORANGE = (244, 132, 48, 255)
GOLD = (247, 202, 59, 255)
LIME = (137, 232, 73, 255)
TEAL = (40, 165, 169, 255)
CYAN = (61, 207, 224, 255)
BLUE = (54, 103, 194, 255)
PURPLE = (153, 78, 188, 255)
STEEL = (163, 176, 194, 255)


def ensure_directories() -> None:
    for relative in ("backgrounds", "ui", "heroes", "enemies", "items", "fx", "audio"):
        (OUT / relative).mkdir(parents=True, exist_ok=True)


def clean_transparent_rgb(image: Image.Image) -> Image.Image:
    """Zero RGB under fully transparent pixels to prevent Android filter halos."""
    rgba = image.convert("RGBA")
    rgba.putdata([
        (0, 0, 0, 0) if alpha == 0 else (red, green, blue, alpha)
        for red, green, blue, alpha in rgba.getdata()
    ])
    return rgba


def pixel_text_mask(text: str, scale: int) -> Image.Image:
    font = ImageFont.load_default()
    bounds = font.getbbox(text)
    width = max(1, bounds[2] - bounds[0] + 2)
    height = max(1, bounds[3] - bounds[1] + 2)
    small = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(small)
    draw.text((1 - bounds[0], 1 - bounds[1]), text, fill=255, font=font)
    return small.resize((width * scale, height * scale), Image.Resampling.NEAREST)


def paste_centered_mask(canvas: Image.Image, mask: Image.Image, y: int,
                        fill: tuple[int, int, int, int], outline: int = 0,
                        outline_fill: tuple[int, int, int, int] = INK) -> None:
    x = (canvas.width - mask.width) // 2
    if outline:
        size = outline * 2 + 1
        outlined = mask.filter(ImageFilter.MaxFilter(size))
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(outline_fill, (x, y), outlined)
        canvas.alpha_composite(layer)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(fill, (x, y), mask)
    canvas.alpha_composite(layer)


def draw_star(draw: ImageDraw.ImageDraw, center: tuple[float, float],
              outer: float, inner: float, fill, outline=INK,
              width: int = 4) -> None:
    points = []
    cx, cy = center
    for index in range(10):
        radius = outer if index % 2 == 0 else inner
        angle = -math.pi / 2 + index * math.pi / 5
        points.append((cx + math.cos(angle) * radius,
                       cy + math.sin(angle) * radius))
    draw.polygon(points, fill=fill, outline=outline, width=width)


def generate_logo() -> Image.Image:
    logo = Image.new("RGBA", (1024, 384), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    draw.rounded_rectangle((45, 48, 979, 324), radius=42,
                           fill=INK, outline=GOLD, width=12)
    draw.rounded_rectangle((66, 69, 958, 303), radius=32,
                           fill=MIDNIGHT, outline=TEAL, width=5)
    for x in range(92, 938, 34):
        draw.rectangle((x, 284 + (x // 34 & 1) * 4, x + 12, 290), fill=VIOLET)

    top = pixel_text_mask("FAMILY FORCE", 11)
    paste_centered_mask(logo, top, 93, CORAL, 11, GOLD)
    bottom = pixel_text_mask("NEON STREETS", 8)
    paste_centered_mask(logo, bottom, 228, CYAN, 8, BLUE)
    draw_star(draw, (512, 322), 35, 16, GOLD, INK, 5)
    draw.ellipse((495, 305, 529, 339), outline=CREAM, width=3)
    return logo


def generate_panel() -> Image.Image:
    panel = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((3, 3, 92, 92), radius=13, fill=PANEL,
                           outline=INK, width=6)
    draw.rounded_rectangle((9, 9, 86, 86), radius=9, outline=GOLD, width=3)
    for x, y in ((12, 12), (84, 12), (12, 84), (84, 84)):
        draw.rectangle((x - 4, y - 4, x + 4, y + 4), fill=CYAN, outline=INK, width=2)
    return panel


def generate_touch_buttons() -> Image.Image:
    sheet = Image.new("RGBA", (512, 128), (0, 0, 0, 0))
    labels = (("FIST", CORAL), ("HEAVY", GOLD), ("JUMP", CYAN), ("STAR", PURPLE))
    for index, (label, color) in enumerate(labels):
        x0 = index * 128
        draw = ImageDraw.Draw(sheet)
        draw.ellipse((x0 + 12, 14, x0 + 116, 118), fill=(7, 10, 28, 150),
                     outline=INK, width=7)
        draw.ellipse((x0 + 20, 22, x0 + 108, 110), fill=(*color[:3], 205),
                     outline=CREAM, width=3)
        if label == "STAR":
            draw_star(draw, (x0 + 64, 64), 28, 13, GOLD, INK, 4)
        elif label == "JUMP":
            draw.polygon(((x0 + 64, 38), (x0 + 90, 70), (x0 + 73, 70),
                          (x0 + 73, 91), (x0 + 55, 91), (x0 + 55, 70),
                          (x0 + 38, 70)), fill=CREAM, outline=INK)
        elif label == "HEAVY":
            draw.polygon(((x0 + 36, 42), (x0 + 78, 42), (x0 + 96, 64),
                          (x0 + 78, 86), (x0 + 36, 86), (x0 + 50, 64)),
                         fill=CREAM, outline=INK)
        else:
            draw.rounded_rectangle((x0 + 38, 43, x0 + 89, 88), radius=13,
                                   fill=CREAM, outline=INK, width=5)
            for finger in range(4):
                draw.rectangle((x0 + 42 + finger * 11, 34, x0 + 50 + finger * 11, 53),
                               fill=CREAM, outline=INK, width=3)
    return sheet


def item_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((20, 100, 108, 119), fill=(7, 10, 28, 90))
    return image, draw


def generate_food() -> Image.Image:
    image, draw = item_canvas()
    draw.polygon(((31, 81), (45, 34), (90, 31), (102, 78), (84, 104), (47, 101)),
                 fill=INK)
    draw.polygon(((39, 78), (50, 42), (84, 40), (94, 76), (79, 95), (52, 93)),
                 fill=CREAM)
    draw.polygon(((50, 42), (65, 26), (84, 40), (72, 58)), fill=ORANGE,
                 outline=INK)
    draw.rectangle((48, 68, 85, 82), fill=CORAL, outline=INK, width=4)
    draw_star(draw, (67, 75), 9, 4, GOLD, INK, 2)
    for x, y in ((43, 50), (89, 58), (55, 89)):
        draw.rectangle((x, y, x + 2, y + 2), fill=GOLD)
    return image


def generate_energy() -> Image.Image:
    image, draw = item_canvas()
    draw.rounded_rectangle((33, 28, 96, 105), radius=13, fill=INK)
    draw.rounded_rectangle((41, 36, 88, 97), radius=8, fill=TEAL,
                           outline=CREAM, width=3)
    draw.rectangle((51, 19, 78, 34), fill=STEEL, outline=INK, width=5)
    draw.rectangle((47, 59, 82, 90), fill=LIME)
    draw.polygon(((69, 42), (52, 67), (66, 67), (58, 89), (81, 59), (68, 59)),
                 fill=CREAM, outline=INK)
    for y in range(72, 91, 6):
        draw.rectangle((45, y, 48, y + 2), fill=CYAN)
    return image


def generate_token() -> Image.Image:
    image, draw = item_canvas()
    draw.ellipse((24, 21, 105, 105), fill=INK)
    draw.ellipse((31, 28, 98, 98), fill=GOLD, outline=CREAM, width=4)
    draw.ellipse((39, 36, 90, 90), fill=LIME, outline=INK, width=5)
    draw_star(draw, (64, 63), 23, 10, CREAM, INK, 4)
    for angle in range(0, 360, 45):
        x = int(64 + math.cos(math.radians(angle)) * 35)
        y = int(63 + math.sin(math.radians(angle)) * 35)
        draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=ORANGE)
    return image


def generate_bat() -> Image.Image:
    image, draw = item_canvas()
    draw.line((35, 98, 94, 31), fill=INK, width=27)
    draw.line((35, 98, 94, 31), fill=PURPLE, width=17)
    draw.line((45, 87, 83, 44), fill=CYAN, width=9)
    draw.line((34, 100, 48, 84), fill=INK, width=23)
    draw.line((34, 100, 48, 84), fill=CORAL, width=13)
    draw.ellipse((82, 19, 105, 42), fill=GOLD, outline=INK, width=5)
    for offset in (0, 14, 28):
        draw.line((55 + offset, 70 - offset, 61 + offset, 63 - offset),
                  fill=CREAM, width=3)
    return image


def keyed_enemy(source_path: Path) -> Image.Image:
    source = Image.open(source_path).convert("RGB")
    alpha = Image.new("L", source.size, 255)
    alpha.putdata([
        0 if (
            r >= 120 and b >= 120 and g <= 150 and abs(r - b) <= 90
            and ((r + b) // 2) - g >= 55
        ) else 255
        for r, g, b in source.getdata()
    ])
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError(f"No keyed subject in {source_path}")
    subject = source.crop(bbox).convert("RGBA")
    subject.putalpha(alpha.crop(bbox))
    subject.thumbnail((480, 488), Image.Resampling.NEAREST)
    output = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    x = (512 - subject.width) // 2
    y = 504 - subject.height
    output.alpha_composite(subject, (x, y))
    return clean_transparent_rgb(output)


def generate_hit_fx() -> Image.Image:
    sheet = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    rng = random.Random(0x46465821)
    palettes = ((GOLD, CORAL, CREAM), (CYAN, LIME, CREAM))
    for frame in range(16):
        x0 = (frame % 4) * 128
        y0 = (frame // 4) * 128
        draw = ImageDraw.Draw(sheet)
        local = frame % 8
        progress = local / 7.0
        radius = 13 + math.sin(progress * math.pi) * 39
        colors = palettes[frame // 8]
        center = (x0 + 64, y0 + 64)
        points = []
        for ray in range(16):
            angle = ray * math.pi / 8
            length = radius * (1.0 if ray % 2 == 0 else 0.48)
            jitter = rng.uniform(-3.0, 3.0)
            points.append((center[0] + math.cos(angle) * (length + jitter),
                           center[1] + math.sin(angle) * (length + jitter)))
        draw.polygon(points, fill=colors[0], outline=INK, width=4)
        inner = max(5, int(radius * 0.42))
        draw.ellipse((center[0] - inner, center[1] - inner,
                      center[0] + inner, center[1] + inner), fill=colors[2])
        for spark in range(8):
            angle = spark * math.pi / 4 + progress
            distance = radius + 11 + spark % 3 * 5
            sx = int(center[0] + math.cos(angle) * distance)
            sy = int(center[1] + math.sin(angle) * distance)
            size = 2 + (spark & 1)
            draw.rectangle((sx - size, sy - size, sx + size, sy + size), fill=colors[1])
    return sheet


def generate_special_fx() -> Image.Image:
    sheet = Image.new("RGBA", (512, 256), (0, 0, 0, 0))
    for frame in range(8):
        x0 = (frame % 4) * 128
        y0 = (frame // 4) * 128
        draw = ImageDraw.Draw(sheet)
        progress = frame / 7.0
        radius = 12 + progress * 45
        center = (x0 + 64, y0 + 64)
        draw.ellipse((center[0] - radius, center[1] - radius,
                      center[0] + radius, center[1] + radius),
                     fill=(*CYAN[:3], max(24, 170 - frame * 16)), outline=INK, width=4)
        draw_star(draw, center, max(8, radius * 0.65), max(4, radius * 0.28),
                  GOLD, INK, 3)
        for spark in range(4):
            angle = spark * math.pi / 2 + progress * math.pi
            sx = int(center[0] + math.cos(angle) * (radius + 9))
            sy = int(center[1] + math.sin(angle) * (radius + 9))
            draw.rectangle((sx - 3, sy - 3, sx + 3, sy + 3), fill=LIME)
    return sheet


NOTE_INDEX = {name: index for index, name in enumerate(
    ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
)}


def frequency(name: str, octave: int) -> float:
    midi = 12 * (octave + 1) + NOTE_INDEX[name]
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def render_stage_wav(path: Path) -> None:
    rate = 48_000
    bar_seconds = 1.6
    duration = 12.8
    count = int(rate * duration)
    left = [0.0] * count
    right = [0.0] * count

    melody = (
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
        (("A", 3), ("C", 4), ("E", 4)), (("F", 3), ("A", 3), ("C", 4)),
        (("D", 3), ("F", 3), ("A", 3)), (("E", 3), ("G#", 3), ("B", 3)),
        (("A", 3), ("C", 4), ("E", 4)), (("C", 3), ("E", 3), ("G", 3)),
        (("F", 3), ("A", 3), ("C", 4)), (("E", 3), ("G#", 3), ("B", 3)),
    )

    def add_tone(start: float, length: float, hz: float, gain: float,
                 wave_type: str, pan: float, attack: float = 0.008,
                 release: float = 0.08) -> None:
        first = int(start * rate)
        samples = min(int(length * rate), count - first)
        if samples <= 0:
            return
        for local in range(samples):
            time = local / rate
            tail = (samples - local - 1) / rate
            envelope = min(1.0, time / max(attack, 1e-5), tail / max(release, 1e-5))
            phase = math.tau * hz * time
            if wave_type == "pulse":
                value = 1.0 if math.sin(phase) >= 0.42 else -0.72
                value += 0.12 * math.sin(phase * 2.0)
            elif wave_type == "triangle":
                value = 2.0 / math.pi * math.asin(math.sin(phase))
            else:
                value = math.sin(phase) + 0.22 * math.sin(phase * 2.0)
            value *= gain * max(0.0, envelope)
            index = first + local
            left[index] += value * (1.0 - pan) * 0.5
            right[index] += value * (1.0 + pan) * 0.5

    rng = random.Random(0x4E454F4E)
    for bar in range(8):
        base = bar * bar_seconds
        for step, pitch in enumerate(melody[bar]):
            add_tone(base + step * 0.2, 0.18, frequency(*pitch), 0.19,
                     "pulse", 0.28 if step & 1 else 0.08, 0.006, 0.055)
        for beat in range(4):
            for chord_index, pitch in enumerate(chords[bar]):
                add_tone(base + beat * 0.4, 0.34, frequency(*pitch), 0.055,
                         "sine", -0.35 + chord_index * 0.16, 0.02, 0.10)
        for half in range(2):
            pitch = chords[bar][0 if half == 0 else 2]
            add_tone(base + half * 0.8, 0.72, frequency(*pitch) / 2.0,
                     0.24, "triangle", -0.05, 0.008, 0.10)

        for beat in range(4):
            start = base + beat * 0.4
            if beat in (0, 2):
                first = int(start * rate)
                for local in range(int(0.17 * rate)):
                    time = local / rate
                    hz = 155.0 - 105.0 * min(1.0, time / 0.17)
                    value = math.sin(math.tau * hz * time) * math.exp(-time * 25.0) * 0.56
                    left[first + local] += value * 0.5
                    right[first + local] += value * 0.5
            if beat in (1, 3):
                first = int(start * rate)
                previous = 0.0
                for local in range(int(0.16 * rate)):
                    time = local / rate
                    noise = rng.uniform(-1.0, 1.0)
                    high = noise - previous * 0.58
                    previous = noise
                    value = high * math.exp(-time * 22.0) * 0.24
                    left[first + local] += value * 0.58
                    right[first + local] += value * 0.42
        for eighth in range(8):
            first = int((base + eighth * 0.2) * rate)
            previous = 0.0
            for local in range(int(0.045 * rate)):
                time = local / rate
                noise = rng.uniform(-1.0, 1.0)
                high = noise - previous
                previous = noise
                value = high * math.exp(-time * 75.0) * 0.075
                left[first + local] += value * (0.35 if eighth & 1 else 0.55)
                right[first + local] += value * (0.55 if eighth & 1 else 0.35)

    peak = max(max(abs(value) for value in left), max(abs(value) for value in right), 1e-6)
    scale = 0.88 / peak
    pcm = array("h")
    for l_value, r_value in zip(left, right):
        pcm.append(max(-32767, min(32767, round(l_value * scale * 32767))))
        pcm.append(max(-32767, min(32767, round(r_value * scale * 32767))))
    with wave.open(str(path), "wb") as target:
        target.setnchannels(2)
        target.setsampwidth(2)
        target.setframerate(rate)
        target.writeframes(pcm.tobytes())


def render_special_wav(path: Path) -> None:
    rate = 44_100
    count = int(rate * 1.15)
    rng = random.Random(0x53544152)
    pcm = array("h")
    phase = 0.0
    for index in range(count):
        time = index / rate
        progress = index / count
        hz = 160.0 + 1040.0 * progress * progress
        phase += math.tau * hz / rate
        shimmer = math.sin(phase) + 0.35 * math.sin(phase * 1.997)
        noise = rng.uniform(-1.0, 1.0) * math.exp(-time * 18.0)
        envelope = math.sin(math.pi * progress) ** 0.7
        value = (shimmer * 0.52 + noise * 0.24) * envelope
        pcm.append(max(-32767, min(32767, round(value * 22000))))
    with wave.open(str(path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(rate)
        target.writeframes(pcm.tobytes())


def generate_audio() -> None:
    audio_out = OUT / "audio"
    generated_audio = ROOT / "assets" / "higgsfield" / "android"
    stage_source = generated_audio / "stage_theme.m4a"
    menu_source = generated_audio / "menu_theme.m4a"
    if stage_source.is_file():
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(stage_source),
            "-af", "loudnorm=I=-19:TP=-3:LRA=11", "-ar", "48000", "-ac", "2",
            "-c:a", "vorbis", "-strict", "experimental", "-q:a", "4",
            str(audio_out / "stage.ogg"),
        ], check=True)
    else:
        with tempfile.TemporaryDirectory(prefix="family-force-android-audio-") as temp_name:
            temp_dir = Path(temp_name)
            stage_wav = temp_dir / "stage.wav"
            render_stage_wav(stage_wav)
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error", "-i", str(stage_wav),
                "-ar", "48000", "-ac", "2", "-c:a", "vorbis", "-strict",
                "experimental", "-q:a", "5", "-metadata", "LOOPSTART=0",
                "-metadata", "LOOPEND=614400", str(audio_out / "stage.ogg"),
            ], check=True)

    if menu_source.is_file():
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(menu_source),
            "-af", "loudnorm=I=-20:TP=-3:LRA=11", "-ar", "48000", "-ac", "2",
            "-c:a", "vorbis", "-strict", "experimental", "-q:a", "4",
            str(audio_out / "menu.ogg"),
        ], check=True)
    else:
        shutil.copyfile(audio_out / "stage.ogg", audio_out / "menu.ogg")

    for name in ("punch", "damage", "pickup", "confirm", "victory", "jump"):
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(ROOT / "audio" / f"{name}.wav"),
            "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le",
            str(audio_out / f"{name}.wav"),
        ], check=True)
    render_special_wav(audio_out / "special.wav")
    shutil.copyfile(ROOT / "audio" / "LICENSE.txt", audio_out / "LICENSE.txt")


def generate_existing_art() -> None:
    shutil.copyfile(ROOT / "assets" / "higgsfield" / "street_background.png",
                    OUT / "backgrounds" / "street.png")
    street = Image.open(ROOT / "assets" / "higgsfield" / "street_background.png").convert("RGB")
    title = street.copy().convert("RGBA")
    title.alpha_composite(Image.new("RGBA", title.size, (7, 10, 28, 118)))
    title.convert("RGB").save(OUT / "backgrounds" / "title.png", optimize=True)
    high_detail_stage = ROOT / "assets" / "higgsfield" / "android" / "street_hd.png"
    if high_detail_stage.is_file():
        shutil.copyfile(high_detail_stage, OUT / "backgrounds" / "street_hd.png")
    retro_stage = (ROOT / "assets" / "higgsfield" / "android" / "retro_stage"
                   / "retro_stage_final.png")
    if retro_stage.is_file():
        shutil.copyfile(retro_stage, OUT / "backgrounds" / "street_retro.png")

    actor_atlas = clean_transparent_rgb(Image.open(ROOT / "assets" / "dev" / "actors.png"))
    portrait_atlas = clean_transparent_rgb(Image.open(ROOT / "assets" / "dev" / "portraits.png"))
    actor_atlas.save(OUT / "ui" / "actors.png", optimize=True)
    portrait_atlas.save(OUT / "ui" / "portraits.png", optimize=True)
    for hero in range(4):
        actions = actor_atlas.crop((0, hero * 64, 128, hero * 64 + 64))
        clean_transparent_rgb(actions.resize((512, 256), Image.Resampling.NEAREST)).save(
            OUT / "heroes" / f"hero_{hero + 1}_actions.png", optimize=True)
        idle = actions.crop((0, 0, 32, 64))
        clean_transparent_rgb(idle.resize((256, 512), Image.Resampling.NEAREST)).save(
            OUT / "heroes" / f"hero_{hero + 1}.png", optimize=True)
        px = (hero % 2) * 64
        py = (hero // 2) * 64
        clean_transparent_rgb(
            portrait_atlas.crop((px, py, px + 64, py + 64)).resize(
                (256, 256), Image.Resampling.NEAREST)
        ).save(OUT / "heroes" / f"hero_{hero + 1}_portrait.png", optimize=True)

    enemy_sources = {
        "grunt": "enemy_grunt.png",
        "skater": "enemy_skater.png",
        "brute": "enemy_brute.png",
        "boss": "boss_junk_king.png",
    }
    for output_name, source_name in enemy_sources.items():
        keyed_enemy(ROOT / "assets" / "higgsfield" / source_name).save(
            OUT / "enemies" / f"{output_name}.png", optimize=True)


def write_manifest() -> None:
    records = []
    for path in sorted(OUT.rglob("*")):
        if not path.is_file() or path.name == "asset_manifest.json":
            continue
        relative = path.relative_to(OUT).as_posix()
        record = {
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                record.update({"width": image.width, "height": image.height, "mode": image.mode})
        records.append(record)
    payload = {
        "project": "Family Force: Neon Streets",
        "status": "original placeholder pack; no family likeness claims",
        "visual_formula": STYLE_FORMULA,
        "files": records,
    }
    (OUT / "asset_manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ensure_directories()
    generate_existing_art()
    generate_logo().save(OUT / "ui" / "logo.png", optimize=True)
    generate_panel().save(OUT / "ui" / "panel_9slice.png", optimize=True)
    generate_touch_buttons().save(OUT / "ui" / "touch_buttons.png", optimize=True)
    items = {
        "food": generate_food(),
        "energy": generate_energy(),
        "token": generate_token(),
        "bat": generate_bat(),
    }
    for name, image in items.items():
        image.save(OUT / "items" / f"{name}.png", optimize=True)
    item_sheet = Image.new("RGBA", (512, 128), (0, 0, 0, 0))
    for index, image in enumerate(items.values()):
        item_sheet.alpha_composite(image, (index * 128, 0))
    item_sheet.save(OUT / "ui" / "item_icons.png", optimize=True)
    generate_hit_fx().save(OUT / "fx" / "hit_fx.png", optimize=True)
    generate_special_fx().save(OUT / "fx" / "special_fx.png", optimize=True)
    shadow = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((12, 19, 116, 51), fill=(7, 10, 28, 105))
    shadow.save(OUT / "fx" / "shadow.png", optimize=True)
    generate_audio()
    write_manifest()
    print(f"Generated {len(list(OUT.rglob('*')))} asset entries under {OUT}")


if __name__ == "__main__":
    main()
