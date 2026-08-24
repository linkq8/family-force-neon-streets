#!/usr/bin/env python3
"""Static release gate for the deliberately dependency-free in-app updater."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text()
MANAGER = (ROOT / "app/src/main/java/com/familyforce/neonstreets/UpdateManager.java").read_text()
PROVIDER = (ROOT / "app/src/main/java/com/familyforce/neonstreets/UpdateFileProvider.java").read_text()
GAME = (ROOT / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()

checks = {
    "internet permission": 'android.permission.INTERNET' in MANIFEST,
    "install permission": 'android.permission.REQUEST_INSTALL_PACKAGES' in MANIFEST,
    "private provider": 'android:exported="false"' in MANIFEST and '.UpdateFileProvider' in MANIFEST,
    "official permission screen": 'ACTION_MANAGE_UNKNOWN_APP_SOURCES' in MANAGER,
    "official package installer": 'ACTION_INSTALL_PACKAGE' in MANAGER,
    "content URI grant": 'FLAG_GRANT_READ_URI_PERMISSION' in MANAGER,
    "GitHub HTTPS API": 'https://api.github.com/repos/linkq8/family-force-neon-streets/releases/latest' in MANAGER,
    "GitHub release digest": 'digest.startsWith("sha256:")' in MANAGER,
    "versioned APK fallback": 'isCompatibleApkName' in MANAGER
        and 'family-force-neon-streets-' in MANAGER,
    "download size cap": 'MAX_APK_BYTES' in MANAGER and 'total > expectedSize' in MANAGER,
    "package identity": 'activity.getPackageName().equals(archive.packageName)' in MANAGER,
    "upgrade only": 'archiveVersion <= installedVersion' in MANAGER,
    "certificate equality": 'archiveCerts.equals(installedCerts)' in MANAGER,
    "optional certificate pin": 'EXPECTED_CERT_SHA256' in MANAGER,
    "HTTPS host allowlist": 'requireAllowedUrl' in MANAGER and 'githubusercontent.com' in MANAGER,
    "read-only provider": 'MODE_READ_ONLY' in PROVIDER and 'UnsupportedOperationException("Read only")' in PROVIDER,
    "canonical cache boundary": 'getCanonicalFile().getParentFile().equals' in PROVIDER,
    "controller-selectable row": 'settingsOption == 6' in GAME and 'requestUpdateCheck();' in GAME,
    "separate back row": 'settingsOption == 7' in GAME and 'clampInt(settingsOption, 0, 7)' in GAME,
}

failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("FAIL: " + ", ".join(failed))
print(f"in-app update contract: PASS ({len(checks)}/{len(checks)})")
