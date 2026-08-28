#!/usr/bin/env python3
"""Static release gate for the first official Unity character Sprite Atlases."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
UNITY = ROOT / "unity"
ART = UNITY / "Assets/FamilyForce/Art/Characters"
ATLASES = UNITY / "Assets/FamilyForce/Resources/Atlases"
APPROVED_COMMIT = "d6c317d"

SPECS = {
    "Essa": (ART / "Heroes/Essa", 132),
    "Adam": (ART / "Heroes/Adam", 88),
    "Grunt": (ART / "Stage1Enemies/Grunt", 36),
    "Skater": (ART / "Stage1Enemies/Skater", 36),
    "LanternCourier": (ART / "Stage1Enemies/LanternCourier", 36),
    "MarketEnforcer": (ART / "Stage1Enemies/MarketEnforcer", 42),
    "Keeper7": (ART / "Stage1Enemies/Keeper7", 36),
}

SOURCE_MAP = {
    ART / "Heroes/Essa": "android/app/src/main/assets/clips/heroes/parent",
    ART / "Heroes/Adam": "android/app/src/main/assets/clips/heroes/adam",
    ART / "Stage1Enemies/Grunt": "android/app/src/main/assets/clips/enemies/grunt",
    ART / "Stage1Enemies/LanternCourier":
        "android/app/src/main/assets/clips/enemies/lantern_courier",
    ART / "Stage1Enemies/MarketEnforcer":
        "android/app/src/main/assets/clips/enemies/market_enforcer",
    ART / "Stage1Enemies/Skater": "android/app/src/main/assets/enemies/skater_anim.png",
    ART / "Stage1Enemies/Keeper7": "android/app/src/main/assets/enemies/keeper_7_anim.png",
}


def git_blob(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{APPROVED_COMMIT}:{path}"], cwd=ROOT)


def assert_approved_sources() -> None:
    for local_root, source in SOURCE_MAP.items():
        images = sorted(local_root.glob("*.png"))
        assert images, local_root
        for image in images:
            remote = source if source.endswith(".png") else f"{source}/{image.name}"
            expected = hashlib.sha256(git_blob(remote)).digest()
            actual = hashlib.sha256(image.read_bytes()).digest()
            assert actual == expected, f"unapproved source: {image}"


def assert_import_contract() -> int:
    total = 0
    for actor, (folder, expected) in SPECS.items():
        actor_frames = 0
        for image_path in sorted(folder.glob("*.png")):
            with Image.open(image_path) as image:
                assert image.height in (192, 1152), (image_path, image.size)
                assert image.width % 192 == 0, (image_path, image.size)
            meta = image_path.with_suffix(".png.meta").read_text()
            assert "textureType: 8" in meta, image_path
            assert "spriteMode: 2" in meta, image_path
            assert "spritePixelsToUnits: 192" in meta, image_path
            assert "enableMipMap: 0" in meta, image_path
            assert "filterMode: 0" in meta, image_path
            assert "nPOTScale: 0" in meta, image_path
            actor_frames += meta.count(f"name: {actor}_")
        assert actor_frames == expected, (actor, actor_frames, expected)
        total += actor_frames
    return total


def assert_atlases() -> None:
    for actor in SPECS:
        atlas = (ATLASES / f"FF_{actor}.spriteatlas").read_text()
        assert "padding: 8" in atlas, actor
        assert "enableRotation: 0" in atlas, actor
        assert "enableTightPacking: 0" in atlas, actor
        assert "generateMipMaps: 0" in atlas, actor
        assert "filterMode: 0" in atlas, actor
        assert "m_MaxTextureSize: 2048" in atlas, actor
        assert "m_TextureFormat: 4" in atlas, actor  # Android RGBA32

    runtime = (UNITY / "Assets/FamilyForce/Scripts/Runtime/CharacterAtlasCatalog.cs").read_text()
    animator = (UNITY / "Assets/FamilyForce/Scripts/Runtime/SpriteStripAnimator.cs").read_text()
    assert 'Resources.Load<SpriteAtlas>' in runtime
    assert "StageOneEnemies" in runtime
    assert "Sprite.Create" not in animator


assert_approved_sources()
frame_total = assert_import_contract()
assert frame_total == 406, frame_total
assert_atlases()
print("Unity Sprite Atlas contract PASS: 7 actors, 406 approved sprites")
