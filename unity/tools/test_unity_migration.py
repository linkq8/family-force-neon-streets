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

    atlas_root = UNITY / "Assets/FamilyForce/Resources/Atlases"
    for actor in ("Essa", "Adam", "Grunt", "Skater", "LanternCourier",
                  "MarketEnforcer", "Keeper7"):
        atlas = (atlas_root / f"FF_{actor}.spriteatlas").read_text()
        assert "enableRotation: 0" in atlas, actor
        assert "enableTightPacking: 0" in atlas, actor
        assert "generateMipMaps: 0" in atlas, actor
        assert "filterMode: 0" in atlas, actor

    apk = PRODUCTION_APK if PRODUCTION_APK.is_file() else DEVELOPMENT_APK
    assert apk.is_file(), "Build the Unity Android prototype first"
    aapt = sorted((SDK / "build-tools").glob("*/aapt2"))[-1]
    badging = subprocess.check_output([str(aapt), "dump", "badging", str(apk)], text=True)
    assert "com.familyforce.neonstreets.unityprototype" in badging
    assert "leanback-launchable-activity" in badging
    assert "android.hardware.touchscreen" in badging and "not-required" in badging
    assert "arm64-v8a" in badging and "armeabi-v7a" in badging
    assert "uses-gl-es: '0x30000'" in badging
    print("Unity migration contract PASS: engine, input, sprites, Android TV, ABIs")


if __name__ == "__main__":
    main()
