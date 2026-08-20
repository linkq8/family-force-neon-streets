#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_ASSETS = ROOT / "android/app/src/main/assets"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_for(pack: Path, relative: Path) -> Path:
    override = pack / "assets" / relative
    return override if override.is_file() else BASE_ASSETS / relative


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--aapt", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    apk, pack = args.apk.resolve(), args.pack.resolve()
    customer = json.loads((pack / "customer.json").read_text(encoding="utf-8"))
    expected_package = "com.familyforce.neonstreets.event." + re.sub(
        r"[^a-z0-9]", "", customer["orderId"])
    badging = subprocess.check_output(
        [str(args.aapt), "dump", "badging", str(apk)], text=True)
    package_match = re.search(r"package: name='([^']+)'", badging)
    if not package_match or package_match.group(1) != expected_package:
        raise SystemExit("APK package does not match customer order")
    checks = []
    with zipfile.ZipFile(apk) as archive:
        embedded_customer = archive.read("assets/customer.json")
        if json.loads(embedded_customer) != customer:
            raise SystemExit("Embedded customer.json differs from customer pack")
        for hero in customer["heroes"]:
            stem = hero["assetStem"]
            for name in (f"{stem}.png", f"{stem}_portrait.png", f"{stem}_anim.png"):
                relative = Path("heroes") / name
                source = source_for(pack, relative)
                expected = source.read_bytes()
                packaged = archive.read("assets/" + relative.as_posix())
                if expected != packaged:
                    raise SystemExit(f"APK asset mismatch: {relative}")
                checks.append({"path": relative.as_posix(), "sha256": sha256(packaged)})
    result = {
        "status": "PASS",
        "orderId": customer["orderId"],
        "package": expected_package,
        "apk": str(apk),
        "apkBytes": apk.stat().st_size,
        "apkSha256": sha256(apk.read_bytes()),
        "verifiedCustomerAssets": checks,
        "tvLauncher": "android.software.leanback" in badging,
        "touchscreenOptional": "uses-feature-not-required: name='android.hardware.touchscreen'" in badging,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Verified customer APK: {len(checks)} exact hero assets, package {expected_package}")


if __name__ == "__main__":
    main()
