#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the private local order dashboard")
    parser.add_argument("--customers", type=Path, default=ROOT / "customers")
    parser.add_argument("--dist", type=Path, default=ROOT / "dist/customers")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "dist/customer-orders-dashboard.html")
    args = parser.parse_args()
    rows = []
    for config_path in sorted(args.customers.glob("*/customer.json")):
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        order = config.get("orderId", config_path.parent.name)
        apk = args.dist / order / f"family-force-{order}.apk"
        consent = config.get("consent", {})
        rows.append({
            "order": order,
            "event": config.get("eventName", ""),
            "heroes": ", ".join(h.get("displayName", "") for h in config.get("heroes", [])),
            "consent": "READY" if consent.get("status") == "approved" else "REVIEW",
            "apk": "BUILT" if apk.is_file() else "PENDING",
            "sha": digest(apk)[:16] if apk.is_file() else "—",
        })
    body = "\n".join(
        "<tr>" + "".join(f"<td>{html.escape(str(row[key]))}</td>" for key in
                           ("order", "event", "heroes", "consent", "apk", "sha")) + "</tr>"
        for row in rows)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    document = f"""<!doctype html><html><head><meta charset=\"utf-8\"><title>Family Force Orders</title>
<style>body{{font:16px system-ui;background:#071329;color:#eef4ff;padding:28px}}h1{{color:#7eeaff}}
table{{width:100%;border-collapse:collapse;background:#101f3d}}th,td{{padding:12px;border:1px solid #30446b;text-align:left}}
th{{color:#ffcf58}}small{{color:#9ab0cf}}</style></head><body><h1>Family Force — Customer Orders</h1>
<small>Generated {timestamp}. Local production report; contains no reference photos.</small>
<table><thead><tr><th>Order</th><th>Event</th><th>Heroes</th><th>Consent</th><th>APK</th><th>SHA-256</th></tr></thead>
<tbody>{body}</tbody></table></body></html>"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    print(f"Dashboard: {args.output} ({len(rows)} orders)")


if __name__ == "__main__":
    main()
