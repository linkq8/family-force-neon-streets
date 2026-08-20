#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android/app/src/main/assets"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", type=Path)
    args = parser.parse_args()
    pack = args.pack.resolve()
    config_path = pack / "customer.json"
    if not config_path.is_file():
        raise SystemExit(f"Missing {config_path}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schemaVersion") not in (1, 2):
        raise SystemExit("customer.json schemaVersion must be 1 or 2")
    order = config.get("orderId", "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,39}", order):
        raise SystemExit("orderId must be 3-40 lowercase letters, digits, or hyphens")
    heroes = config.get("heroes")
    if not isinstance(heroes, list) or len(heroes) != 4:
        raise SystemExit("Exactly four hero slots are required by the current engine")
    for index, hero in enumerate(heroes, 1):
        name = str(hero.get("displayName", "")).strip()
        stem = str(hero.get("assetStem", "")).strip()
        if not name or len(name) > 40:
            raise SystemExit(f"Hero {index}: invalid displayName")
        if not re.fullmatch(r"[a-z0-9_-]+", stem):
            raise SystemExit(f"Hero {index}: invalid assetStem")
        relative = [
            Path(f"heroes/{stem}.png"),
            Path(f"heroes/{stem}_portrait.png"),
            Path(f"heroes/{stem}_anim.png"),
        ]
        missing = [str(path) for path in relative
                   if not (pack / "assets" / path).is_file()
                   and not (ASSETS / path).is_file()]
        if missing:
            raise SystemExit("Missing hero assets:\n" + "\n".join(missing))
    print(f"Customer pack valid: {order} ({len(heroes)} heroes)")


if __name__ == "__main__":
    main()
