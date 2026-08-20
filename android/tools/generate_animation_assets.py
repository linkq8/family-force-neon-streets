#!/usr/bin/env python3
"""Generate and package Family Force 2D animation atlases with Higgsfield.

The pipeline is resumable. Every submitted job is written to an audit JSON
before it is waited, and the completed response replaces that audit as soon as
the service returns. Re-running the script resumes completed and pending jobs
instead of submitting duplicates.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import urllib.request

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "assets" / "higgsfield" / "android" / "animation_v2"
JOB_DIR = WORK / "jobs"
SHEET_DIR = WORK / "model_sheets"
ACTOR_DIR = WORK / "actors"
GUIDE_DIR = WORK / "pose_guides"
APK_ASSETS = ROOT / "android" / "app" / "src" / "main" / "assets"

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

HERO_ACTIONS = (
    ("idle", 6, True, "smooth idle breathing cycle with a subtle weight shift"),
    ("walk", 9, True, "full walk cycle in place with a steady rhythmic stride"),
    ("punch", 6, False, "single fast straight punch with wind-up strike and follow-through"),
    ("kick", 6, False, "single fast front kick with chamber strike and recovery"),
    ("heavy_punch", 7, False, "single powerful heavy punch with deep wind-up impact and follow-through"),
    ("heavy_kick", 7, False, "single powerful heavy roundhouse kick with wind-up impact and recovery"),
    ("jump", 7, False, "single vertical combat jump with crouch takeoff apex and landing"),
    ("special", 8, False, "single joyful signature energy special attack with charge release and recovery"),
    ("link", 8, False, "single family link power attack with energy gathering burst and recovery"),
    ("hurt", 4, False, "single short hit recoil with clear impact and recovery"),
    ("knockdown", 7, False, "single knockdown fall ending safely on the ground"),
)

ENEMY_ACTIONS = (
    ("idle", 5, True, "smooth robot idle cycle with a subtle mechanical weight shift"),
    ("walk", 7, True, "full robot locomotion cycle in place with a steady rhythmic stride"),
    ("attack1", 6, False, "single fast primary robot attack with anticipation impact and recovery"),
    ("attack2", 6, False, "single powerful secondary robot special attack with anticipation impact and recovery"),
    ("hurt", 4, False, "single short robot hit recoil with parts rattling and recovery"),
    ("knockdown", 6, False, "single robot knockdown collapse ending safely on the ground"),
)

SAFE_SMALL_HERO_MOTIONS = {
    "idle": "subtle ready-stance breathing loop and gentle weight shift",
    "walk": "steady in-place arcade locomotion rehearsal with alternating arms and legs",
    "punch": "one athletic straight-arm motion rehearsal: draw back, extend once, and recover",
    "kick": "one athletic front-leg motion rehearsal: chamber, extend once, retract, and recover",
    "heavy_punch": "one slow powerful arm-motion rehearsal: deep wind-up, one extension, follow-through, and recovery",
    "heavy_kick": "one slow powerful turning-leg motion rehearsal: wind-up, one extension, retract, and recovery",
    "jump": "one safe vertical arcade jump rehearsal with crouch, takeoff, apex and landing",
    "special": "one joyful fantasy energy gesture with charge, release and recovery",
    "link": "one joyful family-link energy gesture with gathering, burst and recovery",
    "hurt": "one brief backward stagger rehearsal and complete recovery, no contact shown",
    "knockdown": "one safe staged arcade tumble ending in the supplied resting pose",
}


ACTORS = {
    "hero_1": {
        "kind": "hero", "name": "Essa", "key": "green #00FF00",
        "action_sheet_actions": {"punch", "kick", "hurt", "knockdown"},
        "action_sheet_version": "gpt_v1",
        "action_sheet_identity": "Essa must retain his exact recognizable adult face, beard, glasses and red-gold powered arcade suit in every frame",
        "action_sheet_prompt_extras": {
            "punch": "Exactly one straight punch only: idle guard, draw-back, one contact, follow-through, retract, full recovery. No arm-switching, flurry, second strike, detached effect, beam, ring or projectile.",
            "kick": "Exactly one front kick only: idle guard, one knee chamber, one extension, retraction, foot down, full recovery. No second kick, held pose, detached effect, beam, ring or projectile.",
            "hurt": "Exactly one clear backward defensive recoil: idle, torso and head snap back, arms shield naturally without a T-pose, one stagger step, balance returns, full recovery. No attack gesture, clapping, arms-horizontal pose or detached effect.",
            "knockdown": "Exactly one fall: idle, balance breaks, fall progresses, frame 6 reaches the ground, frames 7 and 8 remain fully grounded and settled. Never float, stand up or recover. No floor plane or detached effect.",
        },
        "master": ROOT / "assets/higgsfield/android/family/parent/master_keyed.png",
        "video_job_keys": {
            "punch": "video__hero_1__punch_semantic_v2",
            "kick": "video__hero_1__kick_semantic_v2",
            "heavy_punch": "video__hero_1__heavy_punch_semantic_v2",
            "hurt": "video__hero_1__hurt_semantic_v2",
            "knockdown": "video__hero_1__knockdown_semantic_v2",
        },
        "neutral_endpoint_actions": {"punch", "kick", "heavy_punch", "hurt"},
        "endpoint_overrides": {"knockdown": ("idle", "knockdown")},
        "motion_overrides": {
            "punch": "start idle, center exactly one action in the clip: clear fist-drawn-back anticipation, one fast straight-punch impact, complete recovery to the same idle; no second strike, held pose, block or idle wandering",
            "kick": "start idle, center exactly one action in the clip: clear knee-chamber anticipation, one fast front-kick impact, complete leg retraction and recovery to the same idle; no second strike, held kick or block",
            "heavy_punch": "start idle, center exactly one action in the clip: one slow deep wind-up, one powerful heavy-punch impact, complete follow-through and recovery to the same idle; no first-frame hit, second strike or held pose",
            "hurt": "start idle, center exactly one recoil in the clip: a sudden unseen chest impact makes torso and head snap backward, both arms fling defensively and one foot staggers back, then complete recovery to the same idle; no clapping, handshake, block, stretching or attack",
            "knockdown": "start fully visible in the supplied idle pose, perform exactly one coherent fall, finish in the supplied settled pose and remain down; keep the full body inside the fixed square at all times, no crop, no floor plane, no background change, no stand-up and no second fall",
        },
        "grid": (4, 3), "aspect": "4:3", "resolution": "4k",
        "cell": (192, 192), "row_cells": 8,
        "output": APK_ASSETS / "heroes/parent_anim.png",
    },
    "hero_2": {
        "kind": "hero", "name": "Adam", "key": "blue #0000FF",
        "animation_source": "action_sheet",
        "local_action_sheet_actions": {"walk"},
        "action_sheet_version": "gpt_v1",
        "action_sheet_identity": "Adam must remain an organic emerald-green fantasy powerhouse with a rounded strong soft-fabric silhouette, curly hair and purple torn-edge over-shorts; absolutely no armor, robot, metal or mechanical parts",
        "action_sheet_job_keys": {
            "walk": "action_sheet__hero_2__walk_flux_technical_v5",
            "punch": "action_sheet__hero_2__punch",
            "idle": "action_sheet__hero_2__breathing_safe_v2",
            "kick": "action_sheet__hero_2__leg_motion_safe_v2",
            "heavy_punch": "action_sheet__hero_2__heavy_punch_safe_guide_v4",
            "special": "action_sheet__hero_2__joyful_light_safe_v2",
            "link": "action_sheet__hero_2__link_contained_v2",
        },
        "action_sheet_remover_job_keys": {
            "walk": "remove_action_sheet__hero_2__walk_chatgpt_v7",
            "punch": "remove_action_sheet__hero_2__punch",
            "idle": "remove_action_sheet__hero_2__breathing_safe_v2",
            "kick": "remove_action_sheet__hero_2__leg_motion_safe_v2",
            "heavy_punch": "remove_action_sheet__hero_2__heavy_punch_safe_guide_v4",
            "special": "remove_action_sheet__hero_2__joyful_light_safe_v2",
            "link": "remove_action_sheet__hero_2__link_contained_v2",
        },
        "action_sheet_prompt_extras": {
            "walk": "Follow the supplied eight-panel TECHNICAL POSE GUIDE exactly for limb order while rendering Adam from the approved model sheet. The guide uses RED only to mark the screen-near limbs and CYAN only to mark the screen-far limbs; those are annotations and must not appear in the rendered costume. Frames 1 through 4 are the near-leg contact, down, passing and far-leg-lift half-cycle. Frames 5 through 8 unmistakably reverse the legs: far-leg contact, down, passing and near-leg-lift. Bottom-row leading feet must be the opposite depth leg from the corresponding top-row cells. Create one complete eight-pose alternating-leg cycle from scratch, with no repeated four-pose half-cycle and no labels or guide marks in the output.",
            "idle": "This is a calm breathing-loop design exercise. Feet stay planted in a narrow fixed stance; only tiny shoulder, hand, head and costume shifts; no action, contact, lunge or exposed areas.",
            "kick": "This is a non-contact athletic leg-motion rehearsal. Show chamber, one controlled forward leg extension, retraction and recovery; no opponent, collision, injury or impact effect.",
            "heavy_punch": "Follow the supplied eight-panel SAFE-BOX TECHNICAL POSE GUIDE for chronology and scale, while rendering Adam from the approved model sheet. Create the sequence from scratch. Every full figure including the extended fist occupies at most sixty-five percent of panel width, stays centered inside the dashed safe box shown by the guide, and has at least fifteen percent empty margin on every side. One slow wind-up, one compact contact, follow-through and full recovery. No glow, spark, beam, ring, projectile, guide marks or panel bleed.",
            "special": "This is a joyful fantasy light-gesture choreography with no contact or opponent. Use a small contained glow tight between the hands and body, then let it fade. No beam, projectile, detached spark, collision, injury or large burst; keep twelve percent safe margin.",
            "link": "EDIT the supplied current link sheet. Preserve identity and chronology, but replace the large aura and rays with one small contained glow tight between the hands and body. No beam, ring, projectile, detached spark or large burst. Keep every figure and glow at least twelve percent away from all panel and row boundaries.",
        },
        "action_sheet_action_names": {
            "special": "joyful fantasy light gesture",
        },
        "action_sheet_models": {
            "walk": "flux_2",
        },
        "action_sheet_extra_references": {
            "walk": GUIDE_DIR / "adam_walk_alternating_4x2.png",
            "heavy_punch": GUIDE_DIR / "adam_heavy_punch_safe_4x2.png",
            "link": ACTOR_DIR / "hero_2" / "action_sheets" / "link.png",
        },
        "video_safety": "small fully clothed family-friendly arcade hero; preserve the exact costume and face from the supplied illustration",
        "motion_overrides": SAFE_SMALL_HERO_MOTIONS,
        "video_model": "wan2_7", "video_version": "wan_v1",
        "video_duration": "5", "video_supports_audio": False,
        "endpoint_overrides": {
            "punch": ("idle", "idle"), "kick": ("idle", "idle"),
            "heavy_punch": ("idle", "idle"), "heavy_kick": ("idle", "idle"),
            "jump": ("idle", "idle"), "special": ("idle", "idle"),
            "link": ("idle", "idle"), "hurt": ("idle", "idle"),
            "knockdown": ("idle", "knockdown"),
        },
        "master": ROOT / "assets/higgsfield/android/family/adam/portrait.png",
        "references": [ROOT / "assets/higgsfield/android/family/adam/portrait.png"],
        "sheet_job_key": "model_sheet__hero_2_gpt_powerhouse",
        "sheet_model": "gpt_image_2",
        "redesign": (
            "preserve his recognizable cheerful illustrated face and curly black hair; "
            "make his face, neck and broad soft gloved hands clearly emerald green; "
            "redesign him as a clearly powerful organic fantasy powerhouse with a very "
            "large rounded muscle silhouette made entirely from soft padded fabric, an "
            "age-appropriate fully covering emerald stretch bodysuit, purple torn-edge "
            "style athletic over-shorts, opaque green leggings, and broad soft feet; "
            "no polo shirt, collar, regular trousers, shoes, exposed torso, "
            "shoes, armor plates, shoulder pads, knee pads, gauntlets, boots, panel "
            "lines, mechanical joints, robot parts, machinery, metal or hard surfaces"
        ),
        "grid": (4, 3), "aspect": "4:3", "resolution": "4k",
        "cell": (192, 192), "row_cells": 8,
        "output": APK_ASSETS / "heroes/adam_anim.png",
    },
    "hero_3": {
        "kind": "hero", "name": "Shaikha", "key": "green #00FF00",
        "animation_source": "action_sheet",
        "action_sheet_version": "gpt_v1",
        "action_sheet_identity": "Shaikha must retain her exact joyful pink ice-princess costume, pink cape and recognizable face in every frame",
        "action_sheet_prompt_extras": {
            "walk": "Eight UNIQUE successive poses; do not repeat the first half. Frames 5 through 8 must be opposite-leg in-betweens, and frame 8 approaches but is not identical to frame 1. At least six visibly distinct silhouettes.",
            "idle": "EDIT the supplied current idle sheet. Keep both feet planted in exactly one fixed stance and position across all eight frames. Create a subtle seamless breathing loop using only small shoulder, chest, cape, head and hand shifts. No lunge, no wide stance, no hands-on-hips pose, no stepping, no foot jitter. Frame 8 must flow gently into frame 1.",
            "punch": "EDIT the supplied current punch sheet. Preserve the approved anticipation, single contact and recovery sequence, face and costume. Fix the top-row fourth contact frame so the whole character, especially the rear boot, sits safely inside that fourth panel with at least twelve percent empty margin on every side; shift and narrow the pose inward. Every figure in every panel needs twelve percent safe margin. No limb or costume may touch or cross any panel boundary.",
            "heavy_punch": "EDIT the supplied current heavy-punch sheet. Preserve the motion sequence, face and costume, but keep the face, torso, hips and feet locked in the identical right-facing three-quarter side view in all eight frames; never back view, front view, profile, turn or rotate. Remove every detached spark, beam, ring and projectile. Read contact through pose and foreshortening only. Center each full figure with at least twelve percent empty margin on all sides.",
            "special": "EDIT the supplied current special sheet. Preserve the motion sequence, face and costume, but use only a small contained palm glow tight to the hands and body. No beam, detached spark, ring or projectile. Center each full figure and glow with at least twelve percent empty margin on all sides; nothing may cross a panel boundary.",
            "link": "EDIT the supplied current link sheet. Preserve the motion sequence, face and costume, but replace every large burst and ray with a small contained glow tight between the hands and body. No beam, detached spark, ring, ray or projectile. Center each figure and glow with at least twelve percent empty margin on all sides and away from the row boundary.",
        },
        "action_sheet_job_keys": {
            "idle": "action_sheet__hero_3__idle_semantic_v2",
            "punch": "action_sheet__hero_3__punch_margin_v2",
            "heavy_punch": "action_sheet__hero_3__heavy_punch_facing_v3",
            "special": "action_sheet__hero_3__special_contained_v2",
            "link": "action_sheet__hero_3__link_contained_v2",
        },
        "action_sheet_remover_job_keys": {
            "idle": "remove_action_sheet__hero_3__idle_semantic_v2",
            "punch": "remove_action_sheet__hero_3__punch_margin_v2",
            "heavy_punch": "remove_action_sheet__hero_3__heavy_punch_facing_v3",
            "special": "remove_action_sheet__hero_3__special_contained_v2",
            "link": "remove_action_sheet__hero_3__link_contained_v2",
        },
        "action_sheet_extra_references": {
            "idle": ACTOR_DIR / "hero_3" / "action_sheets" / "idle.png",
            "punch": ACTOR_DIR / "hero_3" / "action_sheets" / "punch.png",
            "heavy_punch": ACTOR_DIR / "hero_3" / "action_sheets" / "heavy_punch.png",
            "special": ACTOR_DIR / "hero_3" / "action_sheets" / "special.png",
            "link": ACTOR_DIR / "hero_3" / "action_sheets" / "link.png",
        },
        "video_safety": "small fully clothed family-friendly arcade hero; preserve the exact costume and face from the supplied illustration",
        "motion_overrides": SAFE_SMALL_HERO_MOTIONS,
        "video_model": "wan2_7", "video_version": "wan_v1",
        "video_duration": "5", "video_supports_audio": False,
        "endpoint_overrides": {
            "punch": ("idle", "idle"), "kick": ("idle", "idle"),
            "heavy_punch": ("idle", "idle"), "heavy_kick": ("idle", "idle"),
            "jump": ("idle", "idle"), "special": ("idle", "idle"),
            "link": ("idle", "idle"), "hurt": ("idle", "idle"),
            "knockdown": ("idle", "knockdown"),
        },
        "master": ROOT / "assets/higgsfield/android/family/shaikha/master_keyed.png",
        "grid": (4, 3), "aspect": "4:3", "resolution": "4k",
        "cell": (192, 192), "row_cells": 8,
        "output": APK_ASSETS / "heroes/shaikha_anim.png",
    },
    "hero_4": {
        "kind": "hero", "name": "Sulaiman", "key": "green #00FF00",
        "animation_source": "action_sheet",
        "action_sheet_version": "gpt_v1",
        "action_sheet_identity": "Sulaiman must retain his exact blue-and-red caped hero costume and the same large prominent S chest emblem, fully legible in every upright frame",
        "action_sheet_prompt_extras": {
            "walk": "Eight UNIQUE successive poses; do not repeat the first half. Frames 5 through 8 must be opposite-leg in-betweens, and frame 8 approaches but is not identical to frame 1. At least six visibly distinct silhouettes.",
            "heavy_punch": "EDIT the supplied current heavy-punch sheet. Preserve the large S emblem, identity and chronology, but shift the contact pose inward and keep the fist and any tiny glow at least twelve percent away from every panel edge. Remove detached sparks, beams, rings and projectiles; contact reads through pose and foreshortening only.",
            "special": "EDIT the supplied current special sheet. Preserve the large S emblem, identity and chronology, but remove every beam, projectile, detached spark and large blast. Use only a small contained hand or chest glow tight to the body, kept at least twelve percent from all panel boundaries.",
            "link": "EDIT the supplied current link sheet. Preserve the large S emblem, identity and chronology, but remove every blast, projectile, beam, ray, detached spark and large aura. Use only a small contained glow tight between the hands and chest, kept at least twelve percent from all panel and row boundaries.",
        },
        "action_sheet_job_keys": {
            "heavy_punch": "action_sheet__hero_4__heavy_punch_contained_v2",
            "special": "action_sheet__hero_4__special_contained_v2",
            "link": "action_sheet__hero_4__link_contained_v2",
        },
        "action_sheet_remover_job_keys": {
            "heavy_punch": "remove_action_sheet__hero_4__heavy_punch_contained_v2",
            "special": "remove_action_sheet__hero_4__special_contained_v2",
            "link": "remove_action_sheet__hero_4__link_contained_v2",
        },
        "action_sheet_extra_references": {
            "heavy_punch": ACTOR_DIR / "hero_4" / "action_sheets" / "heavy_punch.png",
            "special": ACTOR_DIR / "hero_4" / "action_sheets" / "special.png",
            "link": ACTOR_DIR / "hero_4" / "action_sheets" / "link.png",
        },
        "video_safety": "small fully clothed family-friendly arcade hero; preserve the exact costume and face from the supplied illustration",
        "motion_overrides": SAFE_SMALL_HERO_MOTIONS,
        "video_model": "wan2_7", "video_version": "wan_v1",
        "video_duration": "5", "video_supports_audio": False,
        "endpoint_overrides": {
            "punch": ("idle", "idle"), "kick": ("idle", "idle"),
            "heavy_punch": ("idle", "idle"), "heavy_kick": ("idle", "idle"),
            "jump": ("idle", "idle"), "special": ("idle", "idle"),
            "link": ("idle", "idle"), "hurt": ("idle", "idle"),
            "knockdown": ("idle", "knockdown"),
        },
        "master": WORK / "masters/sulaiman/master_keyed.png",
        "grid": (4, 3), "aspect": "4:3", "resolution": "4k",
        "cell": (192, 192), "row_cells": 8,
        "output": APK_ASSETS / "heroes/sulaiman_anim.png",
    },
    "enemy_grunt": {
        "kind": "enemy", "name": "trash-can robot", "key": "blue #0000FF",
        "action_sheet_actions": {"walk"},
        "action_sheet_version": "gpt_v1",
        "action_sheet_identity": "The trash-can robot must retain the exact same dumpster shell, limbs, colors and right-facing three-quarter silhouette in every frame",
        "action_sheet_prompt_extras": {
            "walk": "One fixed right-facing locomotion cycle only. The dumpster back and front remain on the identical sides in all eight frames; torso and head yaw are locked. Only alternating limbs move. Never front view, back view, opposite three-quarter view, turn, rotate or reverse.",
        },
        "video_job_keys": {
            "walk": "video__enemy_grunt__walk_semantic_v2",
            "knockdown": "video__enemy_grunt__knockdown_semantic_v2",
        },
        "endpoint_overrides": {
            "walk": ("walk", "walk"), "knockdown": ("idle", "knockdown"),
        },
        "motion_overrides": {
            "walk": "same right-facing three-quarter orientation throughout; only alternating legs and arms move in one steady locomotion loop; torso and head yaw stay locked, never profile, back view, turn or reverse",
            "knockdown": "start standing idle, perform exactly one robot fall, finish fully down in the supplied final pose and remain down; never begin prone, stand up, get up or fall twice",
        },
        "master": APK_ASSETS / "enemies/grunt.png",
        "grid": (3, 2), "aspect": "3:2", "resolution": "4k",
        "cell": (160, 192), "row_cells": 6,
        "output": APK_ASSETS / "enemies/grunt_anim.png",
    },
    "enemy_skater": {
        "kind": "enemy", "name": "traffic-cone skater robot", "key": "blue #0000FF",
        "video_job_keys": {
            "walk": "video__enemy_skater__walk_semantic_v2",
            "knockdown": "video__enemy_skater__knockdown_semantic_v2",
        },
        "endpoint_overrides": {
            "walk": ("walk", "walk"), "knockdown": ("idle", "knockdown"),
        },
        "motion_overrides": {
            "walk": "same right-facing three-quarter orientation throughout; only the rollers and limbs cycle in one steady locomotion loop; torso and cone head yaw stay locked, never profile, back view, turn or reverse",
            "knockdown": "start standing idle, perform exactly one robot fall, finish fully down in the supplied final pose and remain down; never begin prone, detach the cone, make an extra cone, stand up, get up or fall twice",
        },
        "master": APK_ASSETS / "enemies/skater.png",
        "grid": (3, 2), "aspect": "3:2", "resolution": "4k",
        "cell": (160, 192), "row_cells": 6,
        "output": APK_ASSETS / "enemies/skater_anim.png",
    },
    "enemy_brute": {
        "kind": "enemy", "name": "heavy recycling robot", "key": "blue #0000FF",
        "action_sheet_actions": {"hurt"},
        "local_action_sheet_actions": {"hurt"},
        "action_sheet_version": "gpt_v1",
        "action_sheet_job_keys": {
            "hurt": "action_sheet__enemy_brute__hurt_weapon_lock_v2",
        },
        "action_sheet_remover_job_keys": {
            "hurt": "remove_action_sheet__enemy_brute__hurt_rigid_recoil_v3",
        },
        "action_sheet_identity": "The heavy recycling robot must retain the exact same drill arm, wrecking-ball arm, shell, colors and right-facing three-quarter silhouette in every frame",
        "action_sheet_prompt_extras": {
            "hurt": "Follow the supplied WEAPON-LOCK TECHNICAL GUIDE. The same approved robot reference is intentionally repeated eight times because the identical blue drill arm and identical wrecking-ball arm must remain present, unchanged and inert in every panel. Only the torso and feet make one brief backward body recoil and stagger, then recover. Never replace the drill with a hand or fist, never hide or shorten either weapon, and never swing, raise, rotate, recolor or detach either weapon. No attack, spark, energy, effect, morph or extra part.",
        },
        "action_sheet_extra_references": {
            "hurt": GUIDE_DIR / "brute_hurt_weapon_lock_4x2.png",
        },
        "video_job_keys": {
            "idle": "video__enemy_brute__idle_semantic_v2",
            "hurt": "video__enemy_brute__hurt_semantic_v2",
            "knockdown": "video__enemy_brute__knockdown_semantic_v2",
        },
        "endpoint_overrides": {
            "idle": ("idle", "idle"), "hurt": ("idle", "idle"),
            "knockdown": ("idle", "knockdown"),
        },
        "motion_overrides": {
            "idle": "same right-facing three-quarter orientation throughout; subtle mechanical weight shift only; torso and head yaw stay locked, never profile, back view, turn or reverse",
            "hurt": "one short impact recoil and complete recovery; the drill arm remains the identical drill in every frame and never morphs into a hand, fist or other tool",
            "knockdown": "start standing idle, perform exactly one heavy robot fall, finish fully down in the supplied final pose and remain down; never begin falling, stand up, get up or fall twice",
        },
        "master": APK_ASSETS / "enemies/brute.png",
        "grid": (3, 2), "aspect": "3:2", "resolution": "4k",
        "cell": (160, 192), "row_cells": 6,
        "output": APK_ASSETS / "enemies/brute_anim.png",
    },
    "boss_junk_king": {
        "kind": "enemy", "name": "Junk King boss robot", "key": "blue #0000FF",
        "master": APK_ASSETS / "enemies/boss.png",
        "grid": (3, 2), "aspect": "3:2", "resolution": "4k",
        "cell": (160, 192), "row_cells": 6,
        "output": APK_ASSETS / "enemies/boss_anim.png",
    },
}

WRITE_LOCK = threading.Lock()


def actions_for(actor: dict) -> tuple:
    return HERO_ACTIONS if actor["kind"] == "hero" else ENEMY_ACTIONS


def uses_action_sheet(actor: dict, action: str) -> bool:
    return (
        actor.get("animation_source") == "action_sheet"
        or action in actor.get("action_sheet_actions", set())
    )


def parse_cli_json(text: str):
    decoder = json.JSONDecoder()
    starts = [index for index, char in enumerate(text) if char in "[{" ]
    for start in starts:
        try:
            value, _ = decoder.raw_decode(text[start:])
            return value
        except json.JSONDecodeError:
            continue
    raise RuntimeError(f"No JSON found in Higgsfield output: {text[-1000:]}")


def atomic_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def run_cli(args: list[str], *, check: bool = True,
            allow_no_json: bool = False) -> tuple[object | None, str, int]:
    result = subprocess.run(
        ["higgsfield", *args], cwd=ROOT, text=True, capture_output=True,
        timeout=60 * 30,
    )
    combined = result.stdout + result.stderr
    try:
        payload = parse_cli_json(combined)
    except RuntimeError:
        if not allow_no_json:
            raise
        payload = None
    if check and result.returncode != 0:
        raise RuntimeError(combined)
    return payload, combined, result.returncode


def normalize_job(payload) -> dict:
    if isinstance(payload, str):
        return {"id": payload, "status": "queued"}
    if isinstance(payload, list):
        if not payload:
            raise RuntimeError("Higgsfield returned an empty job list")
        return normalize_job(payload[0])
    if isinstance(payload, dict) and "id" in payload:
        return payload
    raise RuntimeError(f"Unexpected Higgsfield response: {payload!r}")


def download(url: str, path: Path, *, force: bool = False) -> None:
    if not force and path.is_file() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(
        path.suffix + f".download.{os.getpid()}.{threading.get_ident()}"
    )
    urllib.request.urlretrieve(url, temp)
    os.replace(temp, path)


def audit_path(job_key: str, attempt: int) -> Path:
    return JOB_DIR / f"{job_key}.attempt{attempt}.json"


def completed_from_audit(path: Path) -> dict | None:
    if not path.is_file():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    final = record.get("final") or record.get("initial")
    if isinstance(final, str):
        return None
    if final and final.get("status") == "completed" and final.get("result_url"):
        return final
    return None


def create_wait_job(job_key: str, job_type: str, flags: list[str], output: Path,
                    attempts: int = 2) -> dict:
    for attempt in range(1, attempts + 1):
        path = audit_path(job_key, attempt)
        done = completed_from_audit(path)
        if done:
            download(done["result_url"], output, force=True)
            return done

        record = {}
        if path.is_file():
            record = json.loads(path.read_text(encoding="utf-8"))
        initial = record.get("initial")
        if isinstance(initial, str):
            initial = {"id": initial, "status": "queued"}
            record["initial"] = initial
            with WRITE_LOCK:
                atomic_json(path, record)
        if not initial:
            payload = None
            for throttle_try in range(12):
                payload, raw, code = run_cli(
                    ["generate", "create", job_type, *flags, "--json"], check=False
                )
                if not (
                    isinstance(payload, dict)
                    and payload.get("error_type") == "rate_limit_reached"
                ):
                    break
                # The eight account slots are shared with other asset workers.
                # Back off without consuming an attempt or creating an audit hole.
                time.sleep(min(10 + throttle_try * 2, 30))
            initial = normalize_job(payload)
            record = {
                "job_key": job_key, "attempt": attempt, "job_type": job_type,
                "flags": flags, "initial": initial, "create_exit_code": code,
            }
            with WRITE_LOCK:
                atomic_json(path, record)

        job_id = initial["id"]
        if initial.get("status") in {"failed", "nsfw", "error"}:
            final = initial
        elif initial.get("status") == "completed":
            final = initial
        else:
            get_payload, _, _ = run_cli(
                ["generate", "get", job_id, "--json"], check=False
            )
            current = normalize_job(get_payload)
            if current.get("status") not in {"queued", "in_progress"}:
                final = current
                code = 0
            else:
                payload, raw, code = run_cli(
                    ["generate", "wait", job_id, "--json"], check=False,
                    allow_no_json=True,
                )
                if payload is None:
                    # Failed and NSFW waits return plain text. Fetch the record so the
                    # terminal state is audited and one safe retry can proceed.
                    get_payload, _, _ = run_cli(
                        ["generate", "get", job_id, "--json"], check=False
                    )
                    final = normalize_job(get_payload)
                else:
                    final = normalize_job(payload)
            record["wait_exit_code"] = code
        record["final"] = final
        with WRITE_LOCK:
            atomic_json(path, record)
        if final.get("status") == "completed" and final.get("result_url"):
            download(final["result_url"], output, force=True)
            return final
    raise RuntimeError(f"{job_key} failed after {attempts} attempts")


def run_batch(tasks: list[tuple], workers: int) -> dict[str, str]:
    failures: dict[str, str] = {}
    if not tasks:
        return failures
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(create_wait_job, *task): task[0] for task in tasks}
        for future in as_completed(futures):
            key = futures[future]
            try:
                job = future.result()
                print(f"completed {key}: {job['id']}", flush=True)
            except Exception as error:  # keep independent work moving
                failures[key] = str(error)
                print(f"FAILED {key}: {error}", file=sys.stderr, flush=True)
    return failures


def model_sheet_prompt(actor: dict) -> str:
    actions = actions_for(actor)
    cols, rows = actor["grid"]
    pose_descriptions = {
        "idle": "ready idle stance",
        "walk": "mid-stride walk pose with one leg forward",
        "punch": "straight-punch wind-up with fist drawn back",
        "kick": "front-kick chamber pose",
        "heavy_punch": "deep heavy-punch wind-up",
        "heavy_kick": "heavy roundhouse-kick wind-up",
        "jump": "low crouched jump anticipation",
        "special": "signature energy gathered for special release",
        "link": "family-link energy gathered at both hands",
        "hurt": "clear hit-recoil pose",
        "knockdown": "mid-fall knockdown pose",
        "attack1": "primary attack wind-up",
        "attack2": "secondary special attack wind-up",
    }
    ordered = "; ".join(
        f"panel {index + 1}: {pose_descriptions[action[0]]}"
        for index, action in enumerate(actions)
    )
    blank = cols * rows - len(actions)
    blank_clause = f"; leave the final {blank} panel completely empty" if blank else ""
    continuity = actor.get(
        "redesign",
        "preserve the identical face, outfit, colors, proportions and silhouette",
    )
    return (
        f"game sprite character model sheet of the same {actor['name']} from the "
        f"reference; {continuity} consistently in every "
        f"panel, one consistent full-body character per panel, facing right in the same "
        f"three-quarter side-view, arranged as a precise borderless {cols}-column by "
        f"{rows}-row grid of equal square panels, ordered left-to-right then top-to-bottom: "
        f"{ordered}{blank_clause}. Every pose has generous empty margin above the head, "
        f"below the feet, and around extended limbs. No labels, numbers, words, weapons, "
        f"extra people, duplicate figures within a panel, scenery, shadows or ground plane. "
        f"{STYLE_FORMULA}, on one solid uniform bright {actor['key']} background across "
        f"every panel, nothing cropped at any panel edge"
    )


ACTION_SHEET_SEQUENCES = {
    "idle": (
        "ready stance; gentle inhale with shoulders rising; settle with hands shifting; "
        "weight shift onto front foot; centered ready stance; weight shift onto rear "
        "foot; gentle exhale with shoulders lowering; exact ready stance loop closure"
    ),
    "walk": (
        "right-leg contact and left arm forward; right-leg down pose; passing pose; "
        "left-leg lift; left-leg contact and right arm forward; left-leg down pose; "
        "passing pose; right-leg lift returning into the first contact"
    ),
    "punch": (
        "idle guard; fist begins drawing behind chest; deep coiled anticipation; single "
        "straight-arm contact pose; follow-through; arm retracts; recovered guard; exact idle guard"
    ),
    "kick": (
        "idle guard; weight shifts to support leg; knee chambers with foot tucked; single "
        "front-leg contact pose; brief follow-through; knee retracts; foot lowers; exact idle guard"
    ),
    "heavy_punch": (
        "idle guard; slow shoulder turn; deepest fist-back wind-up; forward drive; one "
        "powerful arm contact pose; heavy follow-through; guarded recovery; exact idle guard"
    ),
    "heavy_kick": (
        "idle guard; turning wind-up; knee rises across body; powerful turning-leg contact "
        "pose; follow-through; leg retracts; stance recovers; exact idle guard"
    ),
    "jump": (
        "idle guard; deep crouch; takeoff stretch; rising pose; clear airborne apex; "
        "descending pose; soft crouched landing; recovered idle guard"
    ),
    "special": (
        "idle guard; hands gather joyful fantasy energy; energy grows; deepest charge; "
        "single bright energy release; follow-through glow; glow fades; exact idle guard"
    ),
    "link": (
        "idle guard; both hands gather family-link energy; two rings form; rings brighten; "
        "single joyful link burst; burst expands; energy fades; exact idle guard"
    ),
    "hurt": (
        "idle guard; startled anticipation; torso begins backward stagger; deepest defensive "
        "recoil with arms raised; one foot slides back; balance returns; guarded recovery; exact idle guard"
    ),
    "knockdown": (
        "idle guard; balance breaks; knees buckle; sideways falling pose; near-ground fall; "
        "first settled ground pose; same settled ground pose with slight secondary motion; final still ground pose"
    ),
}


def action_sheet_prompt(actor: dict, action: str) -> str:
    sequence = ACTION_SHEET_SEQUENCES[action]
    action_name = actor.get("action_sheet_action_names", {}).get(
        action, action.replace("_", " ")
    )
    prompt = (
        f"Sequential 2D game animation sheet for {actor['name']}, using the exact same "
        f"recognizable face, hair, costume, colors, proportions and silhouette as both "
        f"supplied illustrations. Show exactly eight chronological full-body frames of "
        f"one {action_name} animation, arranged as a precise borderless "
        f"4-column by 2-row grid of equal panels, read left-to-right across the top row "
        f"then left-to-right across the bottom row. Frame order: {sequence}. One and only "
        f"one character in each panel, always facing right in the identical three-quarter "
        f"arcade side view. Preserve face and costume exactly; make each adjacent frame a "
        f"clearly different readable pose with smooth authored timing. Full figure and all "
        f"limbs stay inside every panel with generous empty margin. No labels, numbers, "
        f"words, panel borders, extra people, props, scenery, shadows, floor or ground plane. "
        f"{STYLE_FORMULA} Solid perfectly uniform chroma blue #0000FF background in all "
        f"eight panels, no gradients, nothing cropped."
    )
    identity = actor.get("action_sheet_identity")
    if identity:
        prompt += f" {identity}."
    extra = actor.get("action_sheet_prompt_extras", {}).get(action)
    if extra:
        prompt += f" {extra}"
    return prompt


def generate_action_sheets(selected: list[str], selected_actions: set[str] | None,
                           workers: int) -> dict[str, str]:
    tasks = []
    for actor_id in selected:
        actor = ACTORS[actor_id]
        model_sheet = SHEET_DIR / f"{actor_id}.png"
        for action, _, _, _ in actions_for(actor):
            if not uses_action_sheet(actor, action):
                continue
            if action in actor.get("local_action_sheet_actions", set()):
                continue
            if selected_actions and action not in selected_actions:
                continue
            keypose = ACTOR_DIR / actor_id / "keyposes" / f"{action}.png"
            if not model_sheet.is_file() or not keypose.is_file():
                raise FileNotFoundError(model_sheet if not model_sheet.is_file() else keypose)
            output = ACTOR_DIR / actor_id / "action_sheets" / f"{action}.png"
            image_flags = [
                "--image", str(model_sheet), "--image", str(keypose),
            ]
            extra_reference = actor.get("action_sheet_extra_references", {}).get(action)
            if extra_reference:
                if not extra_reference.is_file():
                    raise FileNotFoundError(extra_reference)
                image_flags.extend(["--image", str(extra_reference)])
            default_key = f"action_sheet__{actor_id}__{action}"
            if actor.get("action_sheet_version"):
                default_key += f"__{actor['action_sheet_version']}"
            model = actor.get("action_sheet_models", {}).get(action, "gpt_image_2")
            render_flags = [
                "--aspect-ratio", "16:9", "--resolution", "2k",
            ]
            if model == "gpt_image_2":
                render_flags.extend(["--quality", "high"])
            elif model == "flux_2":
                render_flags.extend(["--variant", "pro"])
            tasks.append((
                actor.get("action_sheet_job_keys", {}).get(
                    action, default_key
                ),
                model,
                [*image_flags, "--prompt", action_sheet_prompt(actor, action),
                 *render_flags],
                output, 2,
            ))
    return run_batch(tasks, workers)


def remove_action_sheet_backgrounds(selected: list[str],
                                    selected_actions: set[str] | None,
                                    workers: int) -> dict[str, str]:
    tasks = []
    for actor_id in selected:
        actor = ACTORS[actor_id]
        for action, _, _, _ in actions_for(actor):
            if not uses_action_sheet(actor, action):
                continue
            if selected_actions and action not in selected_actions:
                continue
            source = ACTOR_DIR / actor_id / "action_sheets" / f"{action}.png"
            if not source.is_file():
                continue
            output = ACTOR_DIR / actor_id / "action_sheets_removed" / f"{action}.png"
            default_key = f"remove_action_sheet__{actor_id}__{action}"
            if actor.get("action_sheet_version"):
                default_key += f"__{actor['action_sheet_version']}"
            tasks.append((
                actor.get("action_sheet_remover_job_keys", {}).get(
                    action, default_key
                ),
                "image_background_remover", ["--image", str(source)], output, 2,
            ))
    return run_batch(tasks, workers)


def crop_action_sheet_frames(selected: list[str],
                             selected_actions: set[str] | None) -> None:
    for actor_id in selected:
        actor = ACTORS[actor_id]
        for action, _, _, _ in actions_for(actor):
            if not uses_action_sheet(actor, action):
                continue
            if selected_actions and action not in selected_actions:
                continue
            source = ACTOR_DIR / actor_id / "action_sheets_removed" / f"{action}.png"
            if not source.is_file():
                continue
            sheet = hard_alpha(Image.open(source))
            output_dir = ACTOR_DIR / actor_id / "removed" / action
            output_dir.mkdir(parents=True, exist_ok=True)
            for old in output_dir.glob("*.png"):
                old.unlink()
            for index in range(8):
                col, row = index % 4, index // 4
                left = round(col * sheet.width / 4)
                right = round((col + 1) * sheet.width / 4)
                top = round(row * sheet.height / 2)
                bottom = round((row + 1) * sheet.height / 2)
                cell = sheet.crop((left, top, right, bottom))
                inset = max(2, round(min(cell.size) * 0.004))
                cell = cell.crop((inset, inset, cell.width - inset, cell.height - inset))
                cell.save(output_dir / f"{index:02d}.png", optimize=True)
            print(f"cropped 8 authored frames for {actor_id}/{action}")


def _guide_limb(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]],
                color: str, width: int = 18) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    radius = max(4, width // 2)
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def _dashed_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                 color: str, width: int = 3, dash: int = 14) -> None:
    left, top, right, bottom = box
    for x in range(left, right, dash * 2):
        draw.line((x, top, min(x + dash, right), top), fill=color, width=width)
        draw.line((x, bottom, min(x + dash, right), bottom), fill=color, width=width)
    for y in range(top, bottom, dash * 2):
        draw.line((left, y, left, min(y + dash, bottom)), fill=color, width=width)
        draw.line((right, y, right, min(y + dash, bottom)), fill=color, width=width)


def create_adam_pose_guides() -> None:
    """Author unambiguous motion-only references; these guides are never shipped."""
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 2048, 1152
    cell_w, cell_h = width // 4, height // 2
    near, far = "#E43D3D", "#11AFCB"
    navy, paper, grid = "#17243F", "#F5F7FA", "#7A879D"

    walk = Image.new("RGB", (width, height), paper)
    draw = ImageDraw.Draw(walk)
    # (near foot, far foot, near hand, far hand), all offsets from hip/shoulder.
    walk_poses = [
        ((112, 190), (-82, 184), (-70, 92), (76, 76)),
        ((48, 198), (-98, 164), (-35, 98), (54, 82)),
        ((-52, 184), (18, 154), (28, 94), (-30, 92)),
        ((-90, 180), (88, 138), (66, 80), (-70, 76)),
        ((-82, 184), (112, 190), (76, 76), (-70, 92)),
        ((-98, 164), (48, 198), (54, 82), (-35, 98)),
        ((18, 154), (-52, 184), (-30, 92), (28, 94)),
        ((88, 138), (-90, 180), (-70, 76), (66, 80)),
    ]
    for index, (near_foot, far_foot, near_hand, far_hand) in enumerate(walk_poses):
        col, row = index % 4, index // 4
        ox, oy = col * cell_w, row * cell_h
        draw.rectangle((ox, oy, ox + cell_w - 1, oy + cell_h - 1), outline=grid, width=3)
        draw.text((ox + 18, oy + 14), f"FRAME {index + 1}", fill=navy)
        _dashed_rect(draw, (ox + 70, oy + 60, ox + cell_w - 70, oy + cell_h - 50), "#AAB3C2")
        hip = (ox + cell_w // 2, oy + 310)
        shoulder = (hip[0], hip[1] - 116)
        head = (shoulder[0] + 18, shoulder[1] - 54)
        # Far-side limbs first so depth is visually explicit.
        far_knee = (hip[0] + far_foot[0] // 2 - 12, hip[1] + far_foot[1] // 2)
        _guide_limb(draw, [hip, far_knee, (hip[0] + far_foot[0], hip[1] + far_foot[1])], far, 16)
        far_elbow = (shoulder[0] + far_hand[0] // 2, shoulder[1] + far_hand[1] // 2)
        _guide_limb(draw, [shoulder, far_elbow,
                           (shoulder[0] + far_hand[0], shoulder[1] + far_hand[1])], far, 14)
        draw.rounded_rectangle((shoulder[0] - 47, shoulder[1] - 6,
                                shoulder[0] + 47, hip[1] + 16), radius=30,
                               fill="#6A8B43", outline=navy, width=5)
        draw.ellipse((head[0] - 35, head[1] - 35, head[0] + 35, head[1] + 35),
                     fill="#79A653", outline=navy, width=5)
        near_knee = (hip[0] + near_foot[0] // 2 + 12, hip[1] + near_foot[1] // 2)
        _guide_limb(draw, [hip, near_knee,
                           (hip[0] + near_foot[0], hip[1] + near_foot[1])], near, 19)
        near_elbow = (shoulder[0] + near_hand[0] // 2, shoulder[1] + near_hand[1] // 2)
        _guide_limb(draw, [shoulder, near_elbow,
                           (shoulder[0] + near_hand[0], shoulder[1] + near_hand[1])], near, 17)
        draw.line((ox + 90, oy + cell_h - 45, ox + cell_w - 90, oy + cell_h - 45),
                  fill="#C7CDD8", width=3)
    draw.rectangle((12, 12, 336, 48), fill=paper)
    draw.text((18, 20), "RED = NEAR LIMBS   CYAN = FAR LIMBS", fill=navy)
    walk_path = GUIDE_DIR / "adam_walk_alternating_4x2.png"
    walk.save(walk_path, optimize=True)
    walk_cell_dir = GUIDE_DIR / "adam_walk_cells"
    walk_cell_dir.mkdir(parents=True, exist_ok=True)
    for index in range(8):
        col, row = index % 4, index // 4
        walk.crop((col * cell_w, row * cell_h,
                   (col + 1) * cell_w, (row + 1) * cell_h)).save(
            walk_cell_dir / f"{index:02d}.png", optimize=True
        )

    punch = Image.new("RGB", (width, height), paper)
    draw = ImageDraw.Draw(punch)
    # Striking-hand offsets trace idle -> wind-up -> contact -> recovery.
    hand_offsets = [(42, 30), (2, 16), (-82, 30), (44, 26),
                    (132, 22), (102, 36), (56, 32), (42, 30)]
    body_lean = [0, -6, -14, 8, 16, 12, 5, 0]
    for index, ((hand_x, hand_y), lean) in enumerate(zip(hand_offsets, body_lean)):
        col, row = index % 4, index // 4
        ox, oy = col * cell_w, row * cell_h
        draw.rectangle((ox, oy, ox + cell_w - 1, oy + cell_h - 1), outline=grid, width=3)
        draw.text((ox + 18, oy + 14), f"FRAME {index + 1}", fill=navy)
        safe = (ox + 88, oy + 76, ox + cell_w - 88, oy + cell_h - 62)
        _dashed_rect(draw, safe, "#D46B24", width=4)
        hip = (ox + cell_w // 2 + lean, oy + 330)
        shoulder = (hip[0], hip[1] - 122)
        head = (shoulder[0] + 16, shoulder[1] - 52)
        _guide_limb(draw, [hip, (hip[0] - 45, hip[1] + 86),
                           (hip[0] - 66, hip[1] + 175)], far, 16)
        _guide_limb(draw, [hip, (hip[0] + 44, hip[1] + 86),
                           (hip[0] + 62, hip[1] + 175)], near, 18)
        draw.rounded_rectangle((shoulder[0] - 48, shoulder[1] - 5,
                                shoulder[0] + 48, hip[1] + 16), radius=30,
                               fill="#6A8B43", outline=navy, width=5)
        draw.ellipse((head[0] - 34, head[1] - 34, head[0] + 34, head[1] + 34),
                     fill="#79A653", outline=navy, width=5)
        _guide_limb(draw, [shoulder, (shoulder[0] - 34, shoulder[1] + 54),
                           (shoulder[0] + 12, shoulder[1] + 88)], far, 14)
        elbow = (shoulder[0] + hand_x // 2, shoulder[1] + hand_y // 2 + 8)
        _guide_limb(draw, [shoulder, elbow,
                           (shoulder[0] + hand_x, shoulder[1] + hand_y)], near, 18)
        draw.text((ox + 112, oy + cell_h - 45), "ALL PIXELS STAY INSIDE SAFE BOX", fill="#A14D18")
    punch_path = GUIDE_DIR / "adam_heavy_punch_safe_4x2.png"
    punch.save(punch_path, optimize=True)
    atomic_json(GUIDE_DIR / "adam_pose_guides.json", {
        "purpose": "generation-only technical references; never packaged",
        "walk": {"path": walk_path.relative_to(ROOT).as_posix(),
                 "sha256": hashlib.sha256(walk_path.read_bytes()).hexdigest()},
        "heavy_punch": {"path": punch_path.relative_to(ROOT).as_posix(),
                        "sha256": hashlib.sha256(punch_path.read_bytes()).hexdigest()},
    })
    print(f"created Adam technical pose guides in {GUIDE_DIR}")


def generate_adam_walk_frames(workers: int) -> dict[str, str]:
    """Generate one referenced pose per job when a model cannot honor a 4x2 grid."""
    create_adam_pose_guides()
    actor_id = "hero_2"
    model_sheet = SHEET_DIR / f"{actor_id}.png"
    keypose = ACTOR_DIR / actor_id / "keyposes" / "walk.png"
    if not model_sheet.is_file() or not keypose.is_file():
        raise FileNotFoundError(model_sheet if not model_sheet.is_file() else keypose)
    descriptions = [
        "screen-near foot heel contact forward, screen-far foot trailing",
        "screen-near foot planted with body moving over it, far foot beginning to lift",
        "screen-far foot passing forward under the body, near foot trailing",
        "screen-far knee and foot lifted forward before contact",
        "screen-far foot heel contact forward, screen-near foot trailing",
        "screen-far foot planted with body moving over it, near foot beginning to lift",
        "screen-near foot passing forward under the body, far foot trailing",
        "screen-near knee and foot lifted forward toward the loop-closing contact",
    ]
    output_dir = ACTOR_DIR / actor_id / "action_frames" / "walk"
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = []
    for index, description in enumerate(descriptions):
        guide = GUIDE_DIR / "adam_walk_cells" / f"{index:02d}.png"
        prompt = (
            "Render exactly ONE full-body frame of Adam, the same fully clothed "
            "family-friendly arcade hero from the approved model illustration. Match "
            f"the supplied technical guide pose precisely: {description}. In the guide, "
            "RED marks only the screen-near limbs and CYAN marks only the screen-far "
            "limbs; do not copy those annotation colors, text, boxes or lines. Preserve "
            "the exact recognizable face, curly hair, organic emerald-green padded soft "
            "costume silhouette and purple torn-edge over-shorts from the approved model. "
            "Right-facing three-quarter arcade view, one character only, both feet and "
            "all limbs clearly visible, at least fifteen percent empty margin on every "
            "side. No label, text, border, guide mark, duplicate, scenery, shadow, floor "
            f"or ground plane. {STYLE_FORMULA} Solid perfectly uniform chroma blue "
            "#0000FF background, no gradient, nothing cropped."
        )
        tasks.append((
            f"action_frame__hero_2__walk_alt_v6__{index:02d}", "flux_2",
            ["--image", str(model_sheet), "--image", str(keypose),
             "--image", str(guide), "--prompt", prompt,
             "--aspect-ratio", "1:1", "--resolution", "2k", "--variant", "pro"],
            output_dir / f"{index:02d}.png", 2,
        ))
    return run_batch(tasks, workers)


def compose_adam_walk_frames() -> None:
    actor_id = "hero_2"
    source_dir = ACTOR_DIR / actor_id / "action_frames" / "walk"
    paths = [source_dir / f"{index:02d}.png" for index in range(8)]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing[0])
    width, height = 2688, 1520
    cell_w, cell_h = width // 4, height // 2
    sheet = Image.new("RGB", (width, height), (0, 0, 255))
    frame_records = []
    for index, path in enumerate(paths):
        source = Image.open(path).convert("RGB")
        alpha = Image.new("L", source.size, 0)
        alpha.putdata([
            0 if blue > 105 and blue > red * 1.20 and blue > green * 1.08 else 255
            for red, green, blue in source.getdata()
        ])
        alpha = alpha.filter(ImageFilter.MaxFilter(3))
        # FLUX occasionally copies detached guide labels/lines. Keep only the
        # character-connected component nearest the image center. Frame 7 once
        # attached three guide strokes beneath the shorts; clear only the empty
        # gap between its legs below the true costume before component tracing.
        if index == 6:
            erase = ImageDraw.Draw(alpha)
            erase.rectangle((round(source.width * 0.34), round(source.height * 0.73),
                             round(source.width * 0.55), round(source.height * 0.97)),
                            fill=0)
        center_x, center_y = source.width // 2, source.height // 2
        seed = None
        max_radius = max(source.size) // 2
        pixels = alpha.load()
        for radius in range(0, max_radius, 4):
            candidates = []
            for delta in range(-radius, radius + 1, 4):
                candidates.extend((
                    (center_x + delta, center_y - radius),
                    (center_x + delta, center_y + radius),
                    (center_x - radius, center_y + delta),
                    (center_x + radius, center_y + delta),
                ))
            for x, y in candidates:
                if 0 <= x < source.width and 0 <= y < source.height and pixels[x, y]:
                    seed = (x, y)
                    break
            if seed is not None:
                break
        if seed is None:
            raise RuntimeError(f"No central Adam figure in walk frame {index}")
        connected = alpha.copy()
        ImageDraw.floodfill(connected, seed, 128, thresh=0)
        alpha = connected.point(lambda value: 255 if value == 128 else 0)
        bbox = alpha.getbbox()
        if bbox is None:
            raise RuntimeError(f"Empty Adam walk frame {index}")
        figure = source.convert("RGBA").crop(bbox)
        figure.putalpha(alpha.crop(bbox))
        scale = min((cell_w * 0.72) / figure.width, (cell_h * 0.78) / figure.height)
        rendered = figure.resize(
            (max(1, round(figure.width * scale)), max(1, round(figure.height * scale))),
            Image.Resampling.NEAREST,
        )
        col, row = index % 4, index // 4
        x = col * cell_w + (cell_w - rendered.width) // 2
        y = row * cell_h + (cell_h - rendered.height) // 2
        sheet.paste(rendered.convert("RGB"), (x, y), rendered.getchannel("A"))
        frame_records.append({
            "index": index, "source": path.relative_to(ROOT).as_posix(),
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_bbox": bbox, "placed_bbox": [x, y, x + rendered.width, y + rendered.height],
        })
    output = ACTOR_DIR / actor_id / "action_sheets" / "walk.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    atomic_json(WORK / "adam_walk_v6_composition.json", {
        "method": "eight independently referenced FLUX.2 poses, locally keyed and composed",
        "style_formula": STYLE_FORMULA,
        "output": output.relative_to(ROOT).as_posix(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "frames": frame_records,
    })
    print(f"composed eight-frame Adam alternating walk sheet: {output}")


def compose_adam_walk_from_stable_sheet() -> None:
    """Turn one clean four-key half-cycle into a true opposite-leg full cycle."""
    actor_id = "hero_2"
    removed_path = ACTOR_DIR / actor_id / "action_sheets_removed" / "walk.png"
    snapshot = WORK / "approved_sources" / "adam_walk_clean_repeated_removed.png"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if not snapshot.is_file():
        if not removed_path.is_file():
            raise FileNotFoundError(removed_path)
        shutil.copy2(removed_path, snapshot)
    source = hard_alpha(Image.open(snapshot))
    source_cell_w, source_cell_h = source.width // 4, source.height // 2
    base_frames = []
    for index in range(4):
        cell = source.crop((index * source_cell_w, 0,
                            (index + 1) * source_cell_w, source_cell_h))
        bbox = cell.getchannel("A").getbbox()
        if bbox is None:
            raise RuntimeError(f"Empty stable Adam walk cell {index}")
        base_frames.append(cell.crop(bbox))

    def opposite_legs(figure: Image.Image) -> Image.Image:
        width, height = figure.size
        # Detect the bottom edge of Adam's purple over-shorts and flip only the
        # legs below it. This preserves face/torso/arms and hides the join under
        # the torn costume edge instead of slicing through the body or gloves.
        rgb = figure.convert("RGB")
        purple = Image.new("L", figure.size, 0)
        purple.putdata([
            255 if red > 55 and blue > 50
            and red > green * 1.18 and blue > green * 1.10 else 0
            for red, green, blue in rgb.getdata()
        ])
        purple_bbox = purple.getbbox()
        split = (
            max(round(height * 0.56), purple_bbox[3] + 3)
            if purple_bbox else round(height * 0.60)
        )
        split = min(split, round(height * 0.72))
        result = Image.new("RGBA", figure.size, (0, 0, 0, 0))
        lower_top = min(height - 1, split + max(6, round(height * 0.025)))
        lower = figure.crop((0, lower_top, width, height)).transpose(
            Image.Transpose.FLIP_LEFT_RIGHT
        )
        result.paste(lower, (0, lower_top), lower)
        upper_bottom = min(height, lower_top + 2)
        upper = figure.crop((0, 0, width, upper_bottom))
        result.paste(upper, (0, 0), upper)
        return result

    frames = [*base_frames, *(opposite_legs(frame) for frame in base_frames)]
    width, height = 2688, 1520
    cell_w, cell_h = width // 4, height // 2
    sheet = Image.new("RGB", (width, height), (0, 0, 255))
    common_scale = min(
        (cell_w * 0.70) / max(frame.width for frame in frames),
        (cell_h * 0.78) / max(frame.height for frame in frames),
    )
    records = []
    for index, frame in enumerate(frames):
        rendered = frame.resize(
            (max(1, round(frame.width * common_scale)),
             max(1, round(frame.height * common_scale))),
            Image.Resampling.NEAREST,
        )
        col, row = index % 4, index // 4
        x = col * cell_w + (cell_w - rendered.width) // 2
        y = row * cell_h + cell_h - round(cell_h * 0.09) - rendered.height
        sheet.paste(rendered.convert("RGB"), (x, y), rendered.getchannel("A"))
        records.append({
            "index": index, "source_top_cell": index % 4,
            "opposite_leg_transform": index >= 4,
            "placed_bbox": [x, y, x + rendered.width, y + rendered.height],
        })
    output = ACTOR_DIR / actor_id / "action_sheets" / "walk.png"
    sheet.save(output, optimize=True)
    atomic_json(WORK / "adam_walk_local_mirrored_v7.json", {
        "method": "clean stable four-key top cycle plus locally mirrored lower-body opposite-leg cycle",
        "source": snapshot.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "output": output.relative_to(ROOT).as_posix(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "frames": records,
    })
    print(f"composed stable opposite-leg Adam walk sheet: {output}")


def adopt_adam_walk_candidate() -> None:
    source = ACTOR_DIR / "hero_2" / "action_sheets" / "walk_chatgpt_v7.png"
    output = ACTOR_DIR / "hero_2" / "action_sheets" / "walk.png"
    if not source.is_file():
        raise FileNotFoundError(source)
    shutil.copy2(source, output)
    with Image.open(output) as image:
        size, mode = image.size, image.mode
    atomic_json(WORK / "adam_walk_chatgpt_v7_adoption.json", {
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output": output.relative_to(ROOT).as_posix(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "width": size[0], "height": size[1], "mode": mode,
        "qa": "strict semantic pre-remover PASS; true near/far leg swap",
    })
    print(f"adopted QA-approved Adam walk candidate: {output}")


def create_brute_hurt_pose_guide() -> None:
    """Repeat the approved brute silhouette so both weapon arms remain immutable."""
    source_path = ACTOR_DIR / "enemy_brute" / "keyposes" / "idle.png"
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(source_path).convert("RGB")
    alpha = Image.new("L", source.size, 0)
    alpha.putdata([
        0 if blue > 140 and blue > red * 1.30 and blue > green * 1.15 else 255
        for red, green, blue in source.getdata()
    ])
    alpha = alpha.filter(ImageFilter.MaxFilter(5))
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("Brute idle keypose has no foreground")
    figure = source.convert("RGBA").crop(bbox)
    figure.putalpha(alpha.crop(bbox))

    width, height = 2048, 1152
    cell_w, cell_h = width // 4, height // 2
    paper, navy, grid = "#F5F7FA", "#17243F", "#7A879D"
    guide = Image.new("RGB", (width, height), paper)
    draw = ImageDraw.Draw(guide)
    shifts = [(0, 0), (-5, 0), (-13, 2), (-22, 5),
              (-16, 4), (-8, 2), (-3, 0), (0, 0)]
    for index, (shift_x, shift_y) in enumerate(shifts):
        col, row = index % 4, index // 4
        ox, oy = col * cell_w, row * cell_h
        draw.rectangle((ox, oy, ox + cell_w - 1, oy + cell_h - 1), outline=grid, width=3)
        draw.text((ox + 18, oy + 14), f"FRAME {index + 1}: WEAPONS LOCKED", fill=navy)
        _dashed_rect(draw, (ox + 52, oy + 58, ox + cell_w - 52, oy + cell_h - 50), "#AAB3C2")
        scale = min((cell_w * 0.76) / figure.width, (cell_h * 0.76) / figure.height)
        rendered = figure.resize(
            (max(1, round(figure.width * scale)), max(1, round(figure.height * scale))),
            Image.Resampling.NEAREST,
        )
        x = ox + (cell_w - rendered.width) // 2 + shift_x
        y = oy + (cell_h - rendered.height) // 2 + shift_y
        guide.paste(rendered, (x, y), rendered)
        if 1 <= index <= 5:
            draw.line((ox + cell_w - 84, oy + 170,
                       ox + cell_w - 84 + shift_x * 3, oy + 170 + shift_y * 2),
                      fill="#D46B24", width=8)
    draw.rectangle((12, 12, 430, 48), fill=paper)
    draw.text((18, 20), "COPY THE SAME DRILL + WRECKING BALL IN ALL 8 FRAMES", fill=navy)
    output = GUIDE_DIR / "brute_hurt_weapon_lock_4x2.png"
    guide.save(output, optimize=True)
    atomic_json(GUIDE_DIR / "brute_hurt_weapon_lock.json", {
        "purpose": "generation-only weapon identity lock; never packaged",
        "source": source_path.relative_to(ROOT).as_posix(),
        "output": output.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    })
    print(f"created brute weapon-lock guide: {output}")


def compose_brute_hurt_sheet() -> None:
    """Author a rigid recoil while keeping both approved weapon silhouettes intact."""
    actor_id = "enemy_brute"
    source_path = ACTOR_DIR / actor_id / "keyposes" / "idle.png"
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    source = Image.open(source_path).convert("RGB")
    alpha = Image.new("L", source.size, 0)
    alpha.putdata([
        0 if blue > 140 and blue > red * 1.30 and blue > green * 1.15 else 255
        for red, green, blue in source.getdata()
    ])
    alpha = alpha.filter(ImageFilter.MaxFilter(3))
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("Brute idle keypose has no foreground")
    figure = source.convert("RGBA").crop(bbox)
    figure.putalpha(alpha.crop(bbox))

    width, height = 2688, 1520
    cell_w, cell_h = width // 4, height // 2
    sheet = Image.new("RGB", (width, height), (0, 0, 255))
    angles = [0, 1, 3, 6, 4, 2, 1, 0]
    x_shifts = [0, -4, -12, -22, -16, -8, -3, 0]
    y_shifts = [0, 0, 2, 5, 4, 2, 0, 0]
    records = []
    base_scale = min((cell_w * 0.73) / figure.width, (cell_h * 0.78) / figure.height)
    base = figure.resize(
        (max(1, round(figure.width * base_scale)),
         max(1, round(figure.height * base_scale))),
        Image.Resampling.NEAREST,
    )
    for index, (angle, shift_x, shift_y) in enumerate(zip(angles, x_shifts, y_shifts)):
        rendered = base.rotate(
            angle, resample=Image.Resampling.NEAREST, expand=True,
            fillcolor=(0, 0, 0, 0),
        )
        col, row = index % 4, index // 4
        baseline = row * cell_h + cell_h - round(cell_h * 0.10) + shift_y
        x = col * cell_w + (cell_w - rendered.width) // 2 + shift_x
        y = baseline - rendered.height
        sheet.paste(rendered.convert("RGB"), (x, y), rendered.getchannel("A"))
        records.append({
            "index": index, "angle_degrees": angle,
            "x_shift": shift_x, "y_shift": shift_y,
            "placed_bbox": [x, y, x + rendered.width, y + rendered.height],
        })
    output = ACTOR_DIR / actor_id / "action_sheets" / "hurt.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    atomic_json(WORK / "brute_hurt_rigid_recoil_v3.json", {
        "method": "rigid transform of approved idle silhouette; no generated limb morphing",
        "source": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "output": output.relative_to(ROOT).as_posix(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "frames": records,
    })
    print(f"composed rigid brute hurt sheet: {output}")


def generate_model_sheets(selected: list[str], workers: int) -> dict[str, str]:
    tasks = []
    for actor_id in selected:
        actor = ACTORS[actor_id]
        if not actor["master"].is_file():
            raise FileNotFoundError(actor["master"])
        output = SHEET_DIR / f"{actor_id}.png"
        references = actor.get("references", [actor["master"]])
        image_flags = []
        for reference in references:
            if not reference.is_file():
                raise FileNotFoundError(reference)
            image_flags.extend(["--image", str(reference)])
        tasks.append((
            actor.get("sheet_job_key", f"model_sheet__{actor_id}"),
            actor.get("sheet_model", "nano_banana_flash"),
            [*image_flags, "--prompt", model_sheet_prompt(actor),
             "--aspect-ratio", actor["aspect"], "--resolution", actor["resolution"]],
            output, 2,
        ))
    return run_batch(tasks, workers)


def extract_pose_cells(selected: list[str]) -> None:
    for actor_id in selected:
        actor = ACTORS[actor_id]
        sheet_path = SHEET_DIR / f"{actor_id}.png"
        if not sheet_path.is_file():
            print(f"skip cells for missing sheet {actor_id}", file=sys.stderr)
            continue
        sheet = Image.open(sheet_path).convert("RGB")
        cols, rows = actor["grid"]
        actions = actions_for(actor)
        cell_dir = ACTOR_DIR / actor_id / "keyposes"
        cell_dir.mkdir(parents=True, exist_ok=True)
        for index, (action, _, _, _) in enumerate(actions):
            col, row = index % cols, index // cols
            left = round(col * sheet.width / cols)
            right = round((col + 1) * sheet.width / cols)
            top = round(row * sheet.height / rows)
            bottom = round((row + 1) * sheet.height / rows)
            cell = sheet.crop((left, top, right, bottom))
            # Model sheets commonly draw a thin separator even when asked for a
            # borderless grid. Remove it before the cell is used as a video key.
            inset = max(4, round(min(cell.size) * 0.006))
            cell = cell.crop((inset, inset, cell.width - inset, cell.height - inset))
            # Seedance receives square cells with the model-sheet key background intact.
            side = max(cell.size)
            square = Image.new("RGB", (side, side), key_rgb(actor["key"]))
            square.paste(cell, ((side - cell.width) // 2, (side - cell.height) // 2))
            square.save(cell_dir / f"{action}.png", optimize=True)
        print(f"extracted {len(actions)} cells for {actor_id}")


def key_rgb(key: str) -> tuple[int, int, int]:
    if "#00FF00" in key:
        return 0, 255, 0
    if "#0000FF" in key:
        return 0, 0, 255
    return 255, 0, 255


NEGATIVE = (
    "Camera locked, no camera movement, no zoom, subject stays fully in frame, "
    "plain static background. The character performs ONLY this action; nothing else "
    "happens. Any carried or attached prop stays inert unless the requested action is "
    "its attack. The subject keeps facing the SAME direction for the entire video — "
    "never turns around, never rotates toward or away from the camera, no head turns "
    "past the shoulder."
)


def generate_videos(selected: list[str], workers: int,
                    selected_actions: set[str] | None = None) -> dict[str, str]:
    tasks = []
    for actor_id in selected:
        actor = ACTORS[actor_id]
        for action, _, loop, motion in actions_for(actor):
            if uses_action_sheet(actor, action):
                continue
            if selected_actions and action not in selected_actions:
                continue
            start_action = action
            end_action = action if loop else None
            endpoint = actor.get("endpoint_overrides", {}).get(action)
            if endpoint:
                start_action, end_action = endpoint
            keypose = ACTOR_DIR / actor_id / "keyposes" / f"{start_action}.png"
            if not keypose.is_file():
                continue
            neutral_endpoints = actor.get("neutral_endpoint_actions", set())
            if action in neutral_endpoints:
                keypose = ACTOR_DIR / actor_id / "keyposes" / "idle.png"
                end_action = "idle"
            video = ACTOR_DIR / actor_id / "videos" / f"{action}.mp4"
            motion = actor.get("motion_overrides", {}).get(action, motion)
            safety = actor.get("video_safety")
            prompt = f"{motion}. {NEGATIVE}"
            if safety:
                prompt = f"{safety}. {prompt}"
            model = actor.get("video_model", "seedance1_5")
            flags = [
                "--start-image", str(keypose), "--prompt", prompt,
                "--duration", actor.get("video_duration", "4"),
                "--resolution", actor.get("video_resolution", "720p"),
                "--aspect-ratio", "1:1",
            ]
            if actor.get("video_supports_audio", True):
                flags.extend(["--generate-audio", "false"])
            if end_action:
                end_keypose = ACTOR_DIR / actor_id / "keyposes" / f"{end_action}.png"
                flags[2:2] = ["--end-image", str(end_keypose)]
            default_key = f"video__{actor_id}__{action}"
            if actor.get("video_version"):
                default_key += f"__{actor['video_version']}"
            tasks.append((
                actor.get("video_job_keys", {}).get(
                    action, default_key
                ),
                model, flags, video, 2,
            ))
    return run_batch(tasks, workers)


def extraction_indices(total: int, count: int) -> list[int]:
    if count <= 1:
        return [0]
    values = [round(index * (total - 1) / (count - 1)) for index in range(count)]
    result = []
    for value in values:
        if not result or value != result[-1]:
            result.append(value)
    return result


def motion_indices(frames: list[Path], count: int) -> list[int]:
    """Choose chronological frames by cumulative edge motion.

    Generated clips sometimes hold the starting or ending pose. Edge-space
    differences discount uniform key-background drift while retaining the
    anticipation, contact, follow-through and silhouette changes the atlas needs.
    """
    if len(frames) <= count:
        return list(range(len(frames)))
    signatures = []
    for path in frames:
        image = Image.open(path).convert("L")
        width, height = image.size
        image = image.crop((
            width // 10, height // 20, width * 9 // 10, height * 19 // 20,
        ))
        image.thumbnail((96, 96), Image.Resampling.BILINEAR)
        signatures.append(image.filter(ImageFilter.FIND_EDGES))
    changes = [0.0]
    for before, after in zip(signatures, signatures[1:]):
        changes.append(ImageStat.Stat(ImageChops.difference(before, after)).mean[0])
    positive = [value for value in changes[1:] if value > 0]
    floor = (sum(positive) / len(positive) * 0.08) if positive else 1.0
    cumulative = []
    running = 0.0
    for change in changes:
        running += max(change, floor)
        cumulative.append(running)
    targets = [
        cumulative[0] + index * (cumulative[-1] - cumulative[0]) / (count - 1)
        for index in range(count)
    ]
    selected = []
    for target in targets:
        choice = min(
            range(len(cumulative)), key=lambda index: abs(cumulative[index] - target)
        )
        if choice not in selected:
            selected.append(choice)
    for choice in extraction_indices(len(frames), count):
        if len(selected) >= count:
            break
        if choice not in selected:
            selected.append(choice)
    return sorted(selected[:count])


def extract_selected_frames(selected: list[str]) -> None:
    for actor_id in selected:
        for action, count, _, _ in actions_for(ACTORS[actor_id]):
            if uses_action_sheet(ACTORS[actor_id], action):
                continue
            video = ACTOR_DIR / actor_id / "videos" / f"{action}.mp4"
            if not video.is_file():
                continue
            raw_dir = ACTOR_DIR / actor_id / "raw" / action
            selected_dir = ACTOR_DIR / actor_id / "selected" / action
            selected_dir.mkdir(parents=True, exist_ok=True)
            raw_dir.mkdir(parents=True, exist_ok=True)
            if not list(raw_dir.glob("*.png")):
                subprocess.run([
                    "ffmpeg", "-v", "error", "-i", str(video),
                    "-fps_mode", "passthrough",
                    str(raw_dir / "%04d.png"),
                ], check=True)
            frames = sorted(raw_dir.glob("*.png"))
            if not frames:
                raise RuntimeError(f"No extracted frames for {actor_id}/{action}")
            indices = motion_indices(frames, count)
            for old in selected_dir.glob("*.png"):
                old.unlink()
            for order, frame_index in enumerate(indices):
                shutil.copy2(frames[frame_index], selected_dir / f"{order:02d}.png")
            print(f"selected {len(indices)}/{len(frames)} frames for {actor_id}/{action}")


def remove_frame_backgrounds(selected: list[str], workers: int) -> dict[str, str]:
    tasks = []
    for actor_id in selected:
        for action, _, _, _ in actions_for(ACTORS[actor_id]):
            if uses_action_sheet(ACTORS[actor_id], action):
                continue
            selected_dir = ACTOR_DIR / actor_id / "selected" / action
            for frame in sorted(selected_dir.glob("*.png")):
                output = ACTOR_DIR / actor_id / "removed" / action / frame.name
                tasks.append((
                    f"remove__{actor_id}__{action}__{frame.stem}",
                    "image_background_remover", ["--image", str(frame)], output, 2,
                ))
    return run_batch(tasks, workers)


def hard_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = []
    for red, green, blue, alpha in rgba.getdata():
        if alpha < 128:
            pixels.append((0, 0, 0, 0))
        else:
            pixels.append((red, green, blue, 255))
    rgba.putdata(pixels)
    return rgba


def duplicate_to_count(frames: list[Image.Image], count: int) -> list[Image.Image]:
    if not frames:
        return []
    if len(frames) == count:
        return frames
    if len(frames) > count:
        indices = extraction_indices(len(frames), count)
        return [frames[index] for index in indices]
    return [frames[round(index * (len(frames) - 1) / (count - 1))] for index in range(count)]


def assemble_actor(actor_id: str) -> None:
    actor = ACTORS[actor_id]
    loaded: dict[str, list[Image.Image]] = {}
    row_bboxes: dict[str, list[tuple[int, int, int, int]]] = {}
    row_unions: dict[str, tuple[int, int, int, int]] = {}
    for action, _, loop, _ in actions_for(actor):
        paths = sorted((ACTOR_DIR / actor_id / "removed" / action).glob("*.png"))
        frames = [hard_alpha(Image.open(path)) for path in paths]
        if loop and len(frames) > actor["row_cells"]:
            frames = frames[:-1]
        if not frames:
            raise RuntimeError(f"Missing removed frames for {actor_id}/{action}")
        loaded[action] = frames
        bboxes = [frame.getchannel("A").getbbox() for frame in frames]
        bboxes = [bbox for bbox in bboxes if bbox]
        if not bboxes:
            raise RuntimeError(f"All removed frames are empty for {actor_id}/{action}")
        row_bboxes[action] = bboxes
        row_unions[action] = (
            min(box[0] for box in bboxes), min(box[1] for box in bboxes),
            max(box[2] for box in bboxes), max(box[3] for box in bboxes),
        )
    cell_w, cell_h = actor["cell"]
    row_cells = actor["row_cells"]
    actions = actions_for(actor)
    atlas = Image.new("RGBA", (cell_w * row_cells, cell_h * len(actions)), (0, 0, 0, 0))
    # Keep the full authored resolution in the runtime cell.  The previous
    # half-size intermediate followed by nearest-neighbour enlargement made
    # every two source pixels become a large square on Fold/high-density
    # screens, hiding faces and costume details during motion.
    logical_w, logical_h = cell_w, cell_h
    for row, (action, _, _, _) in enumerate(actions):
        union = row_unions[action]
        bboxes = row_bboxes[action]
        if action == "jump":
            crop_w, crop_h = union[2] - union[0], union[3] - union[1]
        else:
            crop_w = max(box[2] - box[0] for box in bboxes)
            crop_h = max(box[3] - box[1] for box in bboxes)
        # Package every action independently. Upright rows fill about 90% of
        # the 192px cell height, while extended attacks/knockdowns scale down
        # only as much as needed to keep a true four-pixel final margin.
        scale = min((logical_w - 8) / crop_w, (logical_h * 0.92) / crop_h)
        target_w = max(1, round(crop_w * scale))
        target_h = max(1, round(crop_h * scale))
        row_frames = duplicate_to_count(loaded[action], row_cells)
        for col, frame in enumerate(row_frames):
            if action == "jump":
                crop = frame.crop(union)
                frame_w, frame_h = target_w, target_h
            else:
                bbox = frame.getchannel("A").getbbox()
                if bbox is None:
                    raise RuntimeError(f"Empty assembly frame for {actor_id}/{action}")
                crop = frame.crop(bbox)
                frame_w = max(1, round(crop.width * scale))
                frame_h = max(1, round(crop.height * scale))
            # The source frames are high-resolution Higgsfield mattes.  A
            # high-quality reduction preserves facial features while keeping
            # the limited-palette retro silhouette.
            small = crop.resize((frame_w, frame_h), Image.Resampling.LANCZOS)
            logical = Image.new("RGBA", (logical_w, logical_h), (0, 0, 0, 0))
            x = (logical_w - frame_w) // 2
            y = logical_h - frame_h - 2
            logical.alpha_composite(small, (x, y))
            cell = logical
            atlas.alpha_composite(cell, (col * cell_w, row * cell_h))
    # Enforce zero RGB below clear pixels and exact hard-alpha 2px clusters.
    atlas = hard_alpha(atlas)
    actor["output"].parent.mkdir(parents=True, exist_ok=True)
    atlas.save(actor["output"], optimize=True)
    print(f"assembled {actor_id}: {actor['output']} {atlas.size}")


def assemble_all(selected: list[str]) -> None:
    for actor_id in selected:
        assemble_actor(actor_id)


def record_existing(ids: list[str]) -> None:
    for job_id in ids:
        payload, _, _ = run_cli(["generate", "get", job_id, "--json"])
        job = normalize_job(payload)
        atomic_json(JOB_DIR / f"existing__{job_id}.json", {"final": job})
        print(f"recorded {job_id}")


def adopt_existing(mappings: list[str]) -> None:
    """Attach a remotely-created job to its deterministic local task key."""
    for mapping in mappings:
        if "=" not in mapping:
            raise ValueError(f"Expected JOB_KEY=JOB_ID, got {mapping!r}")
        job_key, job_id = mapping.split("=", 1)
        payload, _, _ = run_cli(["generate", "get", job_id, "--json"])
        job = normalize_job(payload)
        atomic_json(audit_path(job_key, 1), {
            "job_key": job_key,
            "attempt": 1,
            "job_type": job.get("job_type"),
            "adopted": True,
            "initial": {"id": job_id, "status": "queued"},
            "final": job,
        })
        parts = job_key.split("__")
        if len(parts) == 3 and parts[0] == "video" and parts[1] in ACTORS:
            output = ACTOR_DIR / parts[1] / "videos" / f"{parts[2]}.mp4"
            if job.get("status") == "completed" and job.get("result_url"):
                download(job["result_url"], output, force=True)
        elif len(parts) >= 3 and parts[0] in {
            "action_sheet", "remove_action_sheet"
        } and parts[1] in ACTORS:
            actor_id = parts[1]
            action = next(
                (name for name, _, _, _ in actions_for(ACTORS[actor_id])
                 if parts[2] == name or parts[2].startswith(name + "_")),
                None,
            )
            if action and job.get("status") == "completed" and job.get("result_url"):
                folder = (
                    "action_sheets" if parts[0] == "action_sheet"
                    else "action_sheets_removed"
                )
                output = ACTOR_DIR / actor_id / folder / f"{action}.png"
                download(job["result_url"], output, force=True)
        print(f"adopted {job_key}: {job_id} ({job.get('status')})")


def write_summary(selected: list[str], failures: dict[str, str]) -> None:
    records = []
    for path in sorted(JOB_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        final = payload.get("final") or payload.get("initial") or {}
        if isinstance(final, str):
            final = {"id": final, "status": "queued"}
        records.append({
            "audit": path.relative_to(ROOT).as_posix(),
            "id": final.get("id"), "job_type": final.get("job_type"),
            "status": final.get("status"), "result_url": final.get("result_url"),
        })
    outputs = []
    for actor_id in selected:
        path = ACTORS[actor_id]["output"]
        if path.is_file():
            outputs.append({
                "actor": actor_id, "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
    atomic_json(WORK / "generation_audit.json", {
        "style_formula": STYLE_FORMULA,
        "actors": selected, "jobs": records, "outputs": outputs,
        "failures": failures,
    })


def refresh_asset_manifest() -> None:
    manifest_path = APK_ASSETS / "asset_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = []
    for path in sorted(APK_ASSETS.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        record = {
            "path": path.relative_to(APK_ASSETS).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                record.update({
                    "width": image.width, "height": image.height,
                    "mode": image.mode,
                })
        records.append(record)
    payload["files"] = records
    atomic_json(manifest_path, payload)
    print(f"refreshed exact asset manifest: {len(records)} files")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actors", nargs="*", choices=sorted(ACTORS), default=sorted(ACTORS))
    parser.add_argument("--actions", nargs="*", choices=sorted({
        action[0] for action in HERO_ACTIONS + ENEMY_ACTIONS
    }))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--record", nargs="*")
    parser.add_argument("--adopt", nargs="*")
    parser.add_argument("--sheets", action="store_true")
    parser.add_argument("--cells", action="store_true")
    parser.add_argument("--videos", action="store_true")
    parser.add_argument("--pose-guides", action="store_true")
    parser.add_argument("--adopt-adam-walk-candidate", action="store_true")
    parser.add_argument("--compose-brute-hurt", action="store_true")
    parser.add_argument("--action-sheets", action="store_true")
    parser.add_argument("--remove-action-sheets", action="store_true")
    parser.add_argument("--crop-action-sheets", action="store_true")
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--refresh-manifest", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    JOB_DIR.mkdir(parents=True, exist_ok=True)
    selected = args.actors
    failures: dict[str, str] = {}
    if args.record:
        record_existing(args.record)
    if args.adopt:
        adopt_existing(args.adopt)
    if args.all or args.sheets:
        failures.update(generate_model_sheets(selected, args.workers))
    if args.all or args.cells:
        extract_pose_cells(selected)
    if args.all or args.videos:
        failures.update(generate_videos(
            selected, args.workers, set(args.actions) if args.actions else None
        ))
    if args.pose_guides or args.all or args.action_sheets:
        requested_actions = set(args.actions) if args.actions else None
        if "hero_2" in selected and (
            requested_actions is None
            or {"walk", "heavy_punch"} & requested_actions
        ):
            create_adam_pose_guides()
        if "enemy_brute" in selected and (
            requested_actions is None or "hurt" in requested_actions
        ):
            create_brute_hurt_pose_guide()
    if args.adopt_adam_walk_candidate:
        adopt_adam_walk_candidate()
    if args.compose_brute_hurt:
        compose_brute_hurt_sheet()
    if args.all or args.action_sheets:
        failures.update(generate_action_sheets(
            selected, set(args.actions) if args.actions else None, args.workers
        ))
    if args.all or args.remove_action_sheets:
        failures.update(remove_action_sheet_backgrounds(
            selected, set(args.actions) if args.actions else None, args.workers
        ))
    if args.all or args.crop_action_sheets:
        crop_action_sheet_frames(
            selected, set(args.actions) if args.actions else None
        )
    if args.all or args.extract:
        extract_selected_frames(selected)
    if args.all or args.remove:
        failures.update(remove_frame_backgrounds(selected, args.workers))
    if args.all or args.assemble:
        assemble_all(selected)
    if args.refresh_manifest:
        refresh_asset_manifest()
    write_summary(selected, failures)
    if failures:
        print(json.dumps(failures, indent=2), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
