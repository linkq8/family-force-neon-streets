#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "android/tools/validate_customer_order.py"
TEMPLATE = ROOT / "customers/_template"


class ValidatorTests(unittest.TestCase):
    def run_validator(self, pack: Path, delivery: bool = False) -> subprocess.CompletedProcess:
        command = ["python3", str(VALIDATOR), str(pack)]
        if delivery:
            command.append("--delivery")
        return subprocess.run(command, text=True, capture_output=True)

    def test_template_is_valid_draft(self):
        result = self.run_validator(TEMPLATE)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_template_is_blocked_from_delivery(self):
        result = self.run_validator(TEMPLATE, delivery=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("consentStatus must be granted", result.stderr)

    def test_raw_photo_in_assets_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "order-100"
            (pack / "consent").mkdir(parents=True)
            (pack / "assets/heroes").mkdir(parents=True)
            config = json.loads((TEMPLATE / "customer.json").read_text())
            config["orderId"] = "order-100"
            (pack / "customer.json").write_text(json.dumps(config))
            (pack / "consent/consent-record.json").write_text(
                (TEMPLATE / "consent/consent-record.json").read_text()
            )
            (pack / "assets/heroes/source_photo.jpg").write_bytes(b"not an image")
            result = self.run_validator(pack)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("raw/reference photo", result.stderr)

    def test_fully_approved_order_passes_delivery(self):
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "order-101"
            (pack / "consent").mkdir(parents=True)
            config = json.loads((TEMPLATE / "customer.json").read_text())
            config["orderId"] = "order-101"
            config["privacy"].update({
                "consentStatus": "granted",
                "aiUseDisclosed": True,
                "retentionUntil": "2099-04-01",
            })
            for hero, stem in zip(config["heroes"], ("parent", "adam", "shaikha", "sulaiman")):
                hero["assetStem"] = stem
            (pack / "customer.json").write_text(json.dumps(config))
            consent = json.loads((TEMPLATE / "consent/consent-record.json").read_text())
            consent["status"] = "granted"
            consent["grantedAt"] = "2098-12-01T10:00:00Z"
            consent["permissions"] = {key: True for key in consent["permissions"]}
            for subject in consent["subjects"]:
                subject["authorized"] = True
            (pack / "consent/consent-record.json").write_text(json.dumps(consent))
            result = self.run_validator(pack, delivery=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
