#!/usr/bin/env python3
"""Validate bilingual campaign data without Android or network access."""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORY = ROOT / "app" / "src" / "main" / "assets" / "story"
REQUIRED = ["prologue", "ending"] + [
    f"stage_{stage}_{part}"
    for stage in range(1, 6)
    for part in ("intro", "mid", "boss", "outro")
]


def load(language):
    with (STORY / f"story_{language}.json").open(encoding="utf-8") as source:
        return json.load(source)


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    ar = load("ar")
    en = load("en")
    if ar.get("language") != "ar" or ar.get("direction") != "rtl":
        fail("Arabic metadata must be ar/rtl")
    if en.get("language") != "en" or en.get("direction") != "ltr":
        fail("English metadata must be en/ltr")
    if set(ar.get("ui", {})) != set(en.get("ui", {})):
        fail("UI key mismatch")
    if set(ar.get("scenes", {})) != set(en.get("scenes", {})):
        fail("scene key mismatch")
    for scene in REQUIRED:
        if scene not in ar["scenes"]:
            fail(f"missing required scene {scene}")
        ar_lines, en_lines = ar["scenes"][scene], en["scenes"][scene]
        if len(ar_lines) != len(en_lines) or not ar_lines:
            fail(f"line-count mismatch in {scene}")
        for index, (ar_line, en_line) in enumerate(zip(ar_lines, en_lines)):
            for field in ("speaker", "emotion", "text"):
                if not str(ar_line.get(field, "")).strip() or not str(en_line.get(field, "")).strip():
                    fail(f"empty {field} in {scene}[{index}]")
            if ar_line["speaker"] != en_line["speaker"]:
                fail(f"speaker mismatch in {scene}[{index}]")
            if ar_line["emotion"] != en_line["emotion"]:
                fail(f"emotion mismatch in {scene}[{index}]")
            if not re.search(r"[\u0600-\u06ff]", ar_line["text"]):
                fail(f"Arabic text missing Arabic letters in {scene}[{index}]")
    joined_en = " ".join(line["text"] for lines in en["scenes"].values() for line in lines)
    for token in ("Shadow Code", "Essa", "evidence", "protect"):
        if token.lower() not in joined_en.lower():
            fail(f"canon token missing: {token}")
    print(f"PASS: {len(REQUIRED)} bilingual scenes, "
          f"{sum(len(lines) for lines in en['scenes'].values())} lines per language")


if __name__ == "__main__":
    main()
