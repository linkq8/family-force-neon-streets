#!/usr/bin/env python3
"""Guard full Canvas UI localization coverage and Arabic/English parity."""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORY = ROOT / "app/src/main/assets/story"
SOURCE = (ROOT / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text(encoding="utf-8")

with (STORY / "story_ar.json").open(encoding="utf-8") as file:
    ar = json.load(file)["ui"]
with (STORY / "story_en.json").open(encoding="utf-8") as file:
    en = json.load(file)["ui"]

assert set(ar) == set(en), "Arabic and English UI dictionaries must have identical keys"

required = {
    "tap_to_start", "menu_heading", "continue_game", "one_player", "two_players",
    "training", "settings", "choose_hero", "build_coop", "link_ready", "sp_ready",
    "route_locked", "clear_wave", "route_paused", "resume_route", "restart_stage",
    "settings_heading", "music", "sound_effects", "difficulty", "language",
    "game_update", "campaign_clear", "arcade_top", "play_again", "game_over_title",
    "gallery_heading", "stage_0", "stage_1", "stage_2", "stage_3", "stage_4",
}
required.update({f"location_{index}" for index in range(14)})
required.update({f"role_{index}" for index in range(4)})
required.update({f"move_{index}" for index in range(4)})
required.update({f"action_{index}" for index in range(8)})
missing = sorted(required - set(ar))
assert not missing, f"missing required UI keys: {missing}"

for key in required:
    assert ar[key].strip() and en[key].strip(), f"empty translation: {key}"
    assert re.search(r"[\u0600-\u06ff]", ar[key]), f"Arabic letters missing: {key}"

for key in ("menu_heading", "choose_hero", "route_paused", "settings_heading",
            "campaign_clear", "game_over_title", "gallery_heading"):
    assert f'ui("{key}"' in SOURCE, f"major screen does not consume localized key: {key}"

assert 'localizedUpdateStatus()' in SOURCE, "updater status must be localized"
assert 'stageName(' in SOURCE and 'locationName(' in SOURCE, "stage/location helpers missing"
assert 'safeHeroRole(' in SOURCE and 'safeHeroMove(' in SOURCE, "hero metadata localization missing"

print(f"UI localization contract: PASS ({len(ar)} bilingual keys)")
