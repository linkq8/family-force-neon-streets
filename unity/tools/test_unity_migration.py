#!/usr/bin/env python3
"""Static and APK contract for the first Unity migration milestone."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
UNITY = ROOT / "unity"
APK = UNITY / "Builds/Android/FamilyForceUnityPrototype.apk"
SDK = Path("/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer/SDK")


def main() -> None:
    version = (UNITY / "ProjectSettings/ProjectVersion.txt").read_text()
    assert "6000.3.22f1" in version
    manifest = (UNITY / "Packages/manifest.json").read_text()
    assert '"com.unity.inputsystem": "1.17.0"' in manifest
    settings = (UNITY / "ProjectSettings/ProjectSettings.asset").read_text()
    assert "activeInputHandler: 2" in settings

    for name in ("parent_idle.png", "parent_walk.png"):
        path = UNITY / "Assets/FamilyForce/Resources/Heroes" / name
        with Image.open(path) as image:
            assert image.width % 12 == 0, (path, image.size)
            assert image.height > 0
        meta = path.with_suffix(path.suffix + ".meta").read_text()
        assert "nPOTScale: 0" in meta, path
        assert "enableMipMap: 0" in meta, path

    assert APK.is_file(), "Build the Unity Android prototype first"
    aapt = sorted((SDK / "build-tools").glob("*/aapt2"))[-1]
    badging = subprocess.check_output([str(aapt), "dump", "badging", str(APK)], text=True)
    assert "com.familyforce.neonstreets.unityprototype" in badging
    assert "leanback-launchable-activity" in badging
    assert "android.hardware.touchscreen" in badging and "not-required" in badging
    assert "arm64-v8a" in badging and "armeabi-v7a" in badging
    assert "uses-gl-es: '0x30000'" in badging
    print("Unity migration contract PASS: engine, input, sprites, Android TV, ABIs")


if __name__ == "__main__":
    main()
