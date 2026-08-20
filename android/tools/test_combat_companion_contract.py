#!/usr/bin/env python3
from pathlib import Path

source = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/familyforce/neonstreets/GameView.java").read_text()

required = {
    "independent P1 companion": "selectedCompanion1",
    "independent P2 companion": "selectedCompanion2",
    "P1 Link owner": "startAssist(0)",
    "P2 Link owner": "startAssist(1)",
    "team combo gate": "triggerTeamCombo(enemy)",
    "mixed kick finisher": "punchChainStep == 3 ? 1.41f",
    "dash strike": "dashAttackActive = true",
    "co-op revive": "updateCoopRevives()",
    "correct Link threshold": "if (linkMeter >= 50)",
}

missing = [name for name, token in required.items() if token not in source]
if missing:
    raise SystemExit("Missing combat/companion contracts: " + ", ".join(missing))
if "assist.hero = (selectedHero + 1)" in source:
    raise SystemExit("Legacy automatic companion selection is still active")
print("Combat/companion contract tests passed")
