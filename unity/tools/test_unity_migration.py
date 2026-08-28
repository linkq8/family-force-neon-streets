#!/usr/bin/env python3
"""Static and APK contract for the first Unity migration milestone."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UNITY = ROOT / "unity"
PRODUCTION_APK = UNITY / "Builds/Android/FamilyForceUnityAtlasPrototype.apk"
DEVELOPMENT_APK = UNITY / "Builds/Android/FamilyForceUnityPrototype.apk"
SDK = Path("/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK")


def main() -> None:
    version = (UNITY / "ProjectSettings/ProjectVersion.txt").read_text()
    assert "6000.3.22f1" in version
    manifest = (UNITY / "Packages/manifest.json").read_text()
    assert '"com.unity.inputsystem": "1.17.0"' in manifest
    settings = (UNITY / "ProjectSettings/ProjectSettings.asset").read_text()
    assert "activeInputHandler: 2" in settings

    runtime = UNITY / "Assets/FamilyForce/Scripts/Runtime"
    touch = (runtime / "TouchInputOverlay.cs").read_text()
    unified = (runtime / "UnifiedInput.cs").read_text()
    flow = (runtime / "PrototypeFlow.cs").read_text()
    combat = (runtime / "CombatDirector.cs").read_text()
    enemy = (runtime / "EnemyCombatant.cs").read_text()
    assert "Input.touchSupported" in touch
    assert "Input.multiTouchEnabled = true" in touch
    for action in ("PUNCH", "KICK", "HEAVY", "SPECIAL", "GRAB", "TEAM", "JUMP", "WEAPON", "THROW"):
        assert action in touch, action
    assert "TouchInputOverlay.Move" in unified
    assert "TouchInputOverlay.PunchPressedThisFrame" in unified
    assert "TouchInputOverlay.BeganInside(OptionRect(index))" in flow
    assert "BOTH PLAYERS MUST CONFIRM" in flow
    assert "FF_STAGE1_HIGH_SCORE" in flow and "STAGE CLEAR!" in flow
    assert "TryPlayerAction(PlayerMotor actor, CombatAction action)" in combat
    assert "TeamCombo(PlayerMotor partner)" in combat and "ApplyTeamCombo()" in enemy
    assert "CharacterAtlasCatalog.Adam" in combat
    assert "CharacterAtlasCatalog.Grunt" in combat
    assert "Gamepad.all.Count > playerIndex" in unified
    assert "START — 2 PLAYERS" in flow
    assert "SetCombatActive(true, twoPlayersRequested)" in flow
    assert "ClosestActivePlayer" in combat
    assert "enemy.Grabber != actor" in combat
    assert "MarketEnforcer" in combat and "MINI-BOSS" in combat
    assert "HitStop" in combat and "comboUntil" in combat
    assert "WeaponPickup" in combat and "OverlapsAttack" in combat
    assert "bufferedUntil" in (runtime / "PlayerMotor.cs").read_text()
    assert (runtime / "CombatHurtbox.cs").is_file()
    assert (runtime / "WeaponPickup.cs").is_file()

    atlas_root = UNITY / "Assets/FamilyForce/Resources/Atlases"
    for actor in ("Essa", "Adam", "Grunt", "Skater", "LanternCourier",
                  "MarketEnforcer", "Keeper7"):
        atlas = (atlas_root / f"FF_{actor}.spriteatlas").read_text()
        assert "enableRotation: 0" in atlas, actor
        assert "enableTightPacking: 0" in atlas, actor
        assert "generateMipMaps: 0" in atlas, actor
        assert "filterMode: 0" in atlas, actor
    props_atlas = (atlas_root / "FF_Stage1Props.spriteatlas").read_text()
    assert "enableRotation: 0" in props_atlas
    assert "filterMode: 0" in props_atlas
    assert (UNITY / "Assets/FamilyForce/Art/Stage1Props/bat.png").is_file()

    apk = PRODUCTION_APK if PRODUCTION_APK.is_file() else DEVELOPMENT_APK
    assert apk.is_file(), "Build the Unity Android prototype first"
    aapt = sorted((SDK / "build-tools").glob("*/aapt2"))[-1]
    badging = subprocess.check_output([str(aapt), "dump", "badging", str(apk)], text=True)
    assert "com.familyforce.neonstreets.unityprototype" in badging
    assert "versionName='0.5.0-stage-one-slice'" in badging
    assert "leanback-launchable-activity" in badging
    assert "android.hardware.touchscreen" in badging and "not-required" in badging
    assert "arm64-v8a" in badging and "armeabi-v7a" in badging
    assert "uses-gl-es: '0x30000'" in badging
    print("Unity migration contract PASS: engine, input, sprites, Android TV, ABIs")


if __name__ == "__main__":
    main()
