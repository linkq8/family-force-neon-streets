#!/usr/bin/env python3
"""Require a complete human symbol audit and approvals for new art sources."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
AUDIT = json.loads((ASSETS / "asset_symbol_audit.json").read_text())

assert AUDIT["schema"] == 1
assert AUDIT["review_scope"] == "all 36 base-atlas frames per enemy"
approved = set(AUDIT["approved"])
rejected = set(AUDIT["rejected"])
enemies = {
    path.stem.removesuffix("_anim")
    for path in (ASSETS / "enemies").glob("*_anim.png")
}
assert approved.isdisjoint(rejected), approved & rejected
assert approved | rejected == enemies, sorted(enemies - approved - rejected)

source_root = ROOT.parent / "assets/imagegen/android/enemies"
new_sources = {
    f"quality-v4/{path.parent.name}"
    for path in (source_root / "quality-v4").glob("*/model_sheet.png")
}
source_approvals = set(AUDIT["new_source_approvals"])
assert new_sources <= source_approvals, sorted(new_sources - source_approvals)
assert not (rejected & {item.split("/", 1)[1] for item in source_approvals})

print(
    "Symbol-neutral contract: PASS "
    f"({len(approved)} approved, {len(rejected)} quarantined, "
    f"{len(source_approvals)} new source approval)"
)
