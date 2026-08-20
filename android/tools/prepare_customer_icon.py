#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path

from PIL import Image

DENSITIES = {
    "mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216),
    "xxhdpi": (144, 324), "xxxhdpi": (192, 432),
}


def fit(source: Image.Image, size: int, safe: float = 1.0) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    limit = max(1, round(size * safe))
    image = source.copy()
    image.thumbnail((limit, limit), Image.Resampling.LANCZOS)
    canvas.alpha_composite(image, ((size - image.width) // 2, (size - image.height) // 2))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", type=Path)
    args = parser.parse_args()
    pack = args.pack.resolve()
    config = json.loads((pack / "customer.json").read_text(encoding="utf-8"))
    reference = config.get("branding", {}).get("appIconRef", "default")
    output = pack / ".generated/res"
    if output.exists():
        shutil.rmtree(output)
    if reference == "default":
        print("Customer icon: default")
        return
    candidates = (pack / reference, pack / "assets" / reference)
    source_path = next((path for path in candidates if path.is_file()), None)
    if source_path is None:
        raise SystemExit(f"Missing branding.appIconRef: {reference}")
    source = Image.open(source_path).convert("RGBA")
    if source.width < 512 or source.height < 512:
        raise SystemExit("Custom launcher icon must be at least 512x512")
    for density, (legacy_size, foreground_size) in DENSITIES.items():
        directory = output / f"mipmap-{density}"
        directory.mkdir(parents=True, exist_ok=True)
        legacy = fit(source, legacy_size, 0.88)
        legacy.save(directory / "ic_launcher.png", optimize=True)
        legacy.save(directory / "ic_launcher_round.png", optimize=True)
        fit(source, foreground_size, 0.62).save(
            directory / "ic_launcher_foreground.png", optimize=True)
    print(f"Customer icon generated: {source_path}")


if __name__ == "__main__":
    main()
