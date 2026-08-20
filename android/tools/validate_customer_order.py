#!/usr/bin/env python3
"""Pre-delivery validation for Family Force commercial customer packs.

Uses only the Python standard library so it can run on an offline build machine.
It deliberately validates metadata rather than storing signatures or identity data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP_ASSETS = ROOT / "android/app/src/main/assets"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".heic", ".webp", ".tif", ".tiff"}
RAW_NAME_HINTS = re.compile(r"(^|[_-])(raw|source|reference|original|photo)([_-]|$)", re.I)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_object(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(errors, f"missing file: {path}")
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"cannot read {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(errors, f"{path} must contain a JSON object")
        return {}
    return value


def valid_date(value: object, field: str, errors: list[str]) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        fail(errors, f"{field} must be an ISO date (YYYY-MM-DD)")
        return None


def validate(pack: Path, delivery: bool) -> list[str]:
    errors: list[str] = []
    config = load_object(pack / "customer.json", errors)
    if config.get("schemaVersion") != 2:
        fail(errors, "customer.json schemaVersion must be 2 for commercial orders")

    order_id = config.get("orderId")
    if not isinstance(order_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,39}", order_id):
        fail(errors, "orderId must be 3-40 lowercase letters, digits, or hyphens")
    elif pack.name != "_template" and order_id != pack.name:
        fail(errors, "orderId must match the customer pack directory name")

    event = config.get("event")
    if not isinstance(event, dict):
        fail(errors, "event must be an object")
    else:
        name = event.get("displayName")
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
            fail(errors, "event.displayName must contain 1-80 characters")
        valid_date(event.get("date"), "event.date", errors)
        if not re.fullmatch(r"[a-z]{2}(?:-[A-Z]{2})?", str(event.get("locale", ""))):
            fail(errors, "event.locale must look like ar-KW or en")

    customer = config.get("customer")
    if not isinstance(customer, dict) or not str(customer.get("internalReference", "")).strip():
        fail(errors, "customer.internalReference is required")

    privacy = config.get("privacy")
    consent_path = None
    retention = None
    if not isinstance(privacy, dict):
        fail(errors, "privacy must be an object")
    else:
        if privacy.get("rawPhotosInApk") is not False:
            fail(errors, "privacy.rawPhotosInApk must be false")
        consent_rel = privacy.get("consentRecord", "")
        if not isinstance(consent_rel, str) or not re.fullmatch(r"consent/[A-Za-z0-9._-]+\.json", consent_rel):
            fail(errors, "privacy.consentRecord must be a JSON file inside consent/")
        else:
            consent_path = pack / consent_rel
        retention = valid_date(privacy.get("retentionUntil"), "privacy.retentionUntil", errors)
        if delivery:
            if privacy.get("consentStatus") != "granted":
                fail(errors, "delivery blocked: privacy.consentStatus must be granted")
            if privacy.get("aiUseDisclosed") is not True:
                fail(errors, "delivery blocked: AI use must be disclosed")
            if retention and retention < date.today():
                fail(errors, "delivery blocked: raw-photo retention date has passed")

    heroes = config.get("heroes")
    subject_ids: list[str] = []
    if not isinstance(heroes, list) or len(heroes) != 4:
        fail(errors, "exactly four heroes are required by the current engine")
        heroes = []
    stems: set[str] = set()
    for index, hero in enumerate(heroes, 1):
        if not isinstance(hero, dict):
            fail(errors, f"hero {index} must be an object")
            continue
        name = str(hero.get("displayName", "")).strip()
        stem = str(hero.get("assetStem", "")).strip()
        subject_id = str(hero.get("consentSubjectId", "")).strip()
        if not 1 <= len(name) <= 40:
            fail(errors, f"hero {index}: displayName must contain 1-40 characters")
        if not re.fullmatch(r"[a-z0-9_-]+", stem):
            fail(errors, f"hero {index}: invalid assetStem")
        if stem in stems:
            fail(errors, f"hero {index}: duplicate assetStem {stem}")
        stems.add(stem)
        if hero.get("subjectType") not in {"adult", "minor"}:
            fail(errors, f"hero {index}: subjectType must be adult or minor")
        if not re.fullmatch(r"[A-Za-z0-9_-]{3,64}", subject_id):
            fail(errors, f"hero {index}: invalid consentSubjectId")
        subject_ids.append(subject_id)
        if delivery:
            for suffix in (".png", "_portrait.png", "_anim.png"):
                rel = Path("heroes") / f"{stem}{suffix}"
                if not (pack / "assets" / rel).is_file() and not (APP_ASSETS / rel).is_file():
                    fail(errors, f"delivery asset missing: {rel}")

    consent = load_object(consent_path, errors) if consent_path else {}
    if consent:
        consent_subjects = consent.get("subjects")
        consent_by_id = {
            item.get("id"): item for item in consent_subjects
            if isinstance(consent_subjects, list) and isinstance(item, dict)
        } if isinstance(consent_subjects, list) else {}
        if delivery:
            if consent.get("status") != "granted" or not consent.get("grantedAt"):
                fail(errors, "delivery blocked: consent record is not granted and dated")
            permissions = consent.get("permissions", {})
            for permission in ("createAiCharacterAssets", "includeDerivedAssetsInApk", "deliverApkToCustomer"):
                if not isinstance(permissions, dict) or permissions.get(permission) is not True:
                    fail(errors, f"delivery blocked: consent permission {permission} is not granted")
        for hero, subject_id in zip(heroes, subject_ids):
            subject = consent_by_id.get(subject_id)
            if subject is None:
                fail(errors, f"consent has no subject {subject_id}")
            elif subject.get("type") != hero.get("subjectType"):
                fail(errors, f"subject type mismatch for {subject_id}")
            elif delivery and subject.get("authorized") is not True:
                fail(errors, f"delivery blocked: subject {subject_id} is not authorized")

    assets = pack / "assets"
    if assets.is_dir():
        for path in assets.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(assets)
            if path.suffix.lower() in IMAGE_SUFFIXES or RAW_NAME_HINTS.search(path.stem):
                fail(errors, f"possible raw/reference photo inside APK assets: {relative}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--delivery", action="store_true", help="require approved consent and final assets")
    args = parser.parse_args()
    pack = args.pack.resolve()
    errors = validate(pack, args.delivery)
    if errors:
        print("Customer order validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    mode = "delivery" if args.delivery else "draft"
    print(f"Customer order valid ({mode}): {pack.name}")


if __name__ == "__main__":
    main()
