"""Educational/research use only; not investment advice.

Reconstruct CPI knowledge for ONE decision date from the full vintage history.
Run separately for every trade date in a backtest. Standard library only.
"""

# Example from Lab 16 only; choose the actual Lab 17 trade date in lab.
DECISION_DATE = "2026-03-31"

import argparse
import csv
import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
COLUMNS = ["Series name", "Month measured", "Published on", "Value"]


def select_asof(rows, decision, prior_day_only=False):
    """Filter availability BEFORE selecting the most recent version per month."""
    indexed = list(enumerate(rows, start=1))
    latest = {}
    for number, row in indexed:
        month = date.fromisoformat(row["Month measured"] + "-01")
        published = date.fromisoformat(row["Published on"])
        if month > published:
            raise ValueError(f"Data row {number}: publication precedes measured month")
        if row["Value"] != ".":
            value = Decimal(row["Value"])
            if not value.is_finite() or value <= 0:
                raise ValueError(f"Data row {number}: invalid CPI index value")
        available = published < decision if prior_day_only else published <= decision
        if not available:
            continue
        key = (row["Series name"], row["Month measured"])
        old = latest.get(key)
        if old is not None and old[1]["Published on"] == row["Published on"]:
            raise ValueError(f"Duplicate/ambiguous month and publication at row {number}")
        if old is None or row["Published on"] > old[1]["Published on"]:
            latest[key] = (number, row)
    selected_ids = {number for number, _ in latest.values()}
    audit = []
    for number, row in indexed:
        pub = date.fromisoformat(row["Published on"])
        available = pub < decision if prior_day_only else pub <= decision
        if not available:
            status = "excluded: not published by cutoff"
        elif number not in selected_ids:
            status = "excluded: superseded by another knowable publication"
        elif row["Value"] == ".":
            status = "retained: missing marker, not a tradable numeric value"
        else:
            status = "selected: latest knowable numeric value"
        audit.append({"source_data_row": number, **row, "status": status})
    panel = [row for _, row in sorted(latest.values(),
                                     key=lambda item: (item[1]["Series name"],
                                                       item[1]["Month measured"]))]
    return panel, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-date", default=DECISION_DATE,
                        help="YYYY-MM-DD; default is an illustrative Lab 16 example: %(default)s")
    parser.add_argument("--prior-day-only", action="store_true",
                        help="Exclude same-day publications when release time is unknown")
    args = parser.parse_args()
    decision = date.fromisoformat(args.decision_date)
    manifest = json.loads((FOLDER / "sources/manifest.json").read_text())
    if decision > date.fromisoformat(manifest["publication_cutoff"]):
        parser.error("Decision date is beyond this saved archive's cutoff; refresh first")
    source = FOLDER / "CPIAUCSL_all_vintages.csv"
    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise ValueError("Unexpected input columns")
        rows = list(reader)
    panel, audit = select_asof(rows, decision, args.prior_day_only)
    label = decision.isoformat() + ("_prior_day" if args.prior_day_only else "")
    output = FOLDER / f"CPIAUCSL_asof_{label}.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(panel)
    counts = {"input_rows": len(rows),
              "future_publications_excluded": sum(a["status"].startswith("excluded: not") for a in audit),
              "superseded_versions_excluded": sum(a["status"].startswith("excluded: superseded") for a in audit),
              "selected_numeric_values": sum(r["Value"] != "." for r in panel),
              "retained_missing_markers": sum(r["Value"] == "." for r in panel),
              "same_day_numeric_values": sum(r["Value"] != "." and r["Published on"] == decision.isoformat() for r in panel)}
    report = {"decision_date": decision.isoformat(),
              "cutoff_rule": "published < decision date" if args.prior_day_only else "published <= decision date",
              "archive_cutoff": manifest["publication_cutoff"],
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "counts": counts,
              "timing_limit": "Daily availability only. Verify release time before any same-day trade; use --prior-day-only otherwise.",
              "rows": audit}
    (FOLDER / "sources" / f"asof_audit_{label}.json").write_text(json.dumps(report, indent=2))
    print(f"Decision date: {decision}; {report['cutoff_rule']}")
    for name, count in counts.items():
        print(f"{name}: {count}")
    numeric = [r for r in panel if r["Value"] != "."]
    if numeric:
        latest = max(numeric, key=lambda r: r["Month measured"])
        print(f"Latest known month: {latest['Month measured']}; "
              f"published {latest['Published on']}; CPI {latest['Value']}")
    else:
        print("No numeric CPI observations were available in this window.")
    if counts["same_day_numeric_values"]:
        print("RELEASE TIME NOT VERIFIED: same-day rows require an intraday release check before trading.")
    print(f"Saved: {output.name}")
    print("Rebuild for every trade date. Missing values must never be filled from the future.")


if __name__ == "__main__":
    main()
