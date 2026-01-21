from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys
import shutil

# Ensure repo-root imports work when executed as `python3 enrichment/...`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from customer_processing import default_paths, normalize_company_website, write_csv_dicts  # noqa: E402


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _normalize_naics(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return ""
    # Allow common shorthand like 31-33; otherwise digits only.
    if v in {"31-33", "44-45", "48-49"}:
        return v
    digits = "".join(ch for ch in v if ch.isdigit())
    return digits


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply approved master enrichment values into data/enrichment/MasterEnrichment.csv."
    )
    parser.add_argument(
        "--queue-path",
        default="output/work/enrichment/MasterEnrichmentQueue.csv",
        help="Queue CSV path (default: output/work/enrichment/MasterEnrichmentQueue.csv).",
    )
    parser.add_argument(
        "--enrichment-path",
        default="data/enrichment/MasterEnrichment.csv",
        help="Enrichment CSV path (default: data/enrichment/MasterEnrichment.csv).",
    )
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Overwrite existing enrichment values when queue supplies a value (default: false).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing files.",
    )
    parser.add_argument(
        "--allow-shrink",
        action="store_true",
        help="Allow MasterEnrichment.csv row count to shrink significantly (default: false).",
    )
    args = parser.parse_args()

    queue_path = Path(args.queue_path).resolve()
    enrichment_path = Path(args.enrichment_path).resolve()
    if not queue_path.exists():
        raise SystemExit(f"Missing queue file: {queue_path}")

    rows = _read_csv(queue_path)
    if not rows:
        raise SystemExit(f"No rows found in queue: {queue_path}")

    required = {
        "Master Customer Name Canonical",
        "Company Website (Approved)",
        "NAICS (Approved)",
        "Industry Detail (Approved)",
        "Enrichment Status",
        "Enrichment Confidence",
        "Enrichment Rationale",
        "Enrichment Source",
        "Attempt Outcome",
        "Notes",
    }
    if not required.issubset(set(rows[0].keys())):
        missing = sorted(required - set(rows[0].keys()))
        raise SystemExit(f"Queue missing required columns {missing}: {queue_path}")

    existing_rows: list[dict] = []
    existing: dict[str, dict[str, str]] = {}
    if enrichment_path.exists():
        existing_rows = _read_csv(enrichment_path)
        for r in existing_rows:
            canonical = (r.get("Master Customer Name Canonical") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            existing[canonical] = r

    prior_row_count = len(existing)

    adds = 0
    updates = 0
    skipped = 0
    changes: list[dict[str, str]] = []

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for r in rows:
        canonical = (r.get("Master Customer Name Canonical") or "").strip()
        if not canonical or canonical.startswith("#"):
            continue

        approved_website = normalize_company_website(r.get("Company Website (Approved)") or "")
        approved_naics = _normalize_naics(r.get("NAICS (Approved)") or "")
        approved_detail = (r.get("Industry Detail (Approved)") or "").strip()

        status = (r.get("Enrichment Status") or "").strip() or "Verified"
        confidence = (r.get("Enrichment Confidence") or "").strip()
        rationale = (r.get("Enrichment Rationale") or "").strip()
        source = (r.get("Enrichment Source") or "").strip() or "Analyst"
        attempt_outcome = (r.get("Attempt Outcome") or "").strip()
        notes = (r.get("Notes") or "").strip()

        has_approved_values = bool(approved_website or approved_naics or approved_detail)
        is_deferred = status.lower() == "deferred"
        has_attempt_signal = bool(has_approved_values or attempt_outcome or rationale or notes or is_deferred)

        # No-op rows: keep the queue clean; don't mutate MasterEnrichment.
        if not has_attempt_signal:
            continue

        # Guardrail: a Verified row must supply at least one approved value.
        if status.lower() == "verified" and not has_approved_values:
            continue

        base = dict(existing.get(canonical, {}))
        if not base:
            base = {
                "Master Customer Name Canonical": canonical,
                "Company Website": "",
                "NAICS": "",
                "Industry Detail": "",
                "Enrichment Status": "",
                "Enrichment Confidence": "",
                "Enrichment Rationale": "",
                "Enrichment Source": "",
                "Attempt Count": "0",
                "Last Attempted At": "",
                "Attempt Outcome": "",
                "Notes": "",
                "Updated At": "",
            }
            adds += 1

        before = {
            "Company Website": (base.get("Company Website") or "").strip(),
            "NAICS": (base.get("NAICS") or "").strip(),
            "Industry Detail": (base.get("Industry Detail") or "").strip(),
            "Enrichment Status": (base.get("Enrichment Status") or "").strip(),
            "Enrichment Confidence": (base.get("Enrichment Confidence") or "").strip(),
            "Enrichment Rationale": (base.get("Enrichment Rationale") or "").strip(),
            "Enrichment Source": (base.get("Enrichment Source") or "").strip(),
            "Attempt Count": (base.get("Attempt Count") or "").strip(),
            "Last Attempted At": (base.get("Last Attempted At") or "").strip(),
            "Attempt Outcome": (base.get("Attempt Outcome") or "").strip(),
        }

        # Safety: don't allow a Deferred attempt to overwrite an existing Verified record unless explicitly asked.
        base_status = (base.get("Enrichment Status") or "").strip().lower()
        if is_deferred and base_status == "verified" and not args.overwrite_existing:
            continue

        def set_if_allowed(field: str, value: str) -> None:
            if not value:
                return
            if (base.get(field) or "").strip() and not args.overwrite_existing:
                return
            base[field] = value

        set_if_allowed("Company Website", approved_website)
        set_if_allowed("NAICS", approved_naics)
        set_if_allowed("Industry Detail", approved_detail)
        set_if_allowed("Enrichment Status", status)
        set_if_allowed("Enrichment Confidence", confidence)
        set_if_allowed("Enrichment Rationale", rationale)
        set_if_allowed("Enrichment Source", source)

        # Track attempts when the row is actively processed.
        if has_attempt_signal:
            try:
                current_attempts = int((base.get("Attempt Count") or "0").strip() or "0")
            except ValueError:
                current_attempts = 0
            base["Attempt Count"] = str(current_attempts + 1)
            base["Last Attempted At"] = now
            if attempt_outcome:
                base["Attempt Outcome"] = attempt_outcome
            if notes:
                base["Notes"] = notes

        base["Updated At"] = now

        after = {
            "Company Website": (base.get("Company Website") or "").strip(),
            "NAICS": (base.get("NAICS") or "").strip(),
            "Industry Detail": (base.get("Industry Detail") or "").strip(),
            "Enrichment Status": (base.get("Enrichment Status") or "").strip(),
            "Enrichment Confidence": (base.get("Enrichment Confidence") or "").strip(),
            "Enrichment Rationale": (base.get("Enrichment Rationale") or "").strip(),
            "Enrichment Source": (base.get("Enrichment Source") or "").strip(),
            "Attempt Count": (base.get("Attempt Count") or "").strip(),
            "Last Attempted At": (base.get("Last Attempted At") or "").strip(),
            "Attempt Outcome": (base.get("Attempt Outcome") or "").strip(),
        }

        if before != after:
            updates += 1
            changes.append(
                {
                    "Master Customer Name Canonical": canonical,
                    "Old Website": before["Company Website"],
                    "New Website": after["Company Website"],
                    "Old NAICS": before["NAICS"],
                    "New NAICS": after["NAICS"],
                    "Old Industry Detail": before["Industry Detail"],
                    "New Industry Detail": after["Industry Detail"],
                    "Enrichment Status": after["Enrichment Status"],
                    "Enrichment Confidence": after["Enrichment Confidence"],
                    "Enrichment Source": after["Enrichment Source"],
                    "Attempt Count": after["Attempt Count"],
                    "Last Attempted At": after["Last Attempted At"],
                    "Attempt Outcome": after["Attempt Outcome"],
                }
            )

        existing[canonical] = base

    if args.dry_run:
        print(f"Queue: {queue_path}")
        print(f"Enrichment: {enrichment_path}")
        print(f"Would add rows: {adds}")
        print(f"Would update rows: {updates}")
        print(f"Skipped rows (no approved values): {skipped}")
        for c in changes[:20]:
            print(c)
        raise SystemExit(0)

    # Preserve comment/example rows if present.
    out_rows: list[dict[str, str]] = []
    for r in existing_rows:
        canonical = (r.get("Master Customer Name Canonical") or "").strip()
        if canonical.startswith("#"):
            out_rows.append(
                {
                    "Master Customer Name Canonical": canonical,
                    "Company Website": (r.get("Company Website") or "").strip(),
                    "NAICS": (r.get("NAICS") or "").strip(),
                    "Industry Detail": (r.get("Industry Detail") or "").strip(),
                    "Enrichment Status": (r.get("Enrichment Status") or "").strip(),
                    "Enrichment Confidence": (r.get("Enrichment Confidence") or "").strip(),
                    "Enrichment Rationale": (r.get("Enrichment Rationale") or "").strip(),
                    "Enrichment Source": (r.get("Enrichment Source") or "").strip(),
                    "Attempt Count": (r.get("Attempt Count") or "").strip(),
                    "Last Attempted At": (r.get("Last Attempted At") or "").strip(),
                    "Attempt Outcome": (r.get("Attempt Outcome") or "").strip(),
                    "Notes": (r.get("Notes") or "").strip(),
                    "Updated At": (r.get("Updated At") or "").strip(),
                }
            )

    if not out_rows:
        out_rows.append(
            {
                "Master Customer Name Canonical": "# Example row (verified):",
                "Company Website": "",
                "NAICS": "",
                "Industry Detail": "",
                "Enrichment Status": "",
                "Enrichment Confidence": "",
                "Enrichment Rationale": "",
                "Enrichment Source": "",
                "Attempt Count": "",
                "Last Attempted At": "",
                "Attempt Outcome": "",
                "Notes": "",
                "Updated At": "",
            }
        )

    for canonical in sorted(existing.keys()):
        r = existing[canonical]
        out_rows.append(
            {
                "Master Customer Name Canonical": canonical,
                "Company Website": normalize_company_website(r.get("Company Website") or ""),
                "NAICS": _normalize_naics(r.get("NAICS") or ""),
                "Industry Detail": (r.get("Industry Detail") or "").strip(),
                "Enrichment Status": (r.get("Enrichment Status") or "").strip(),
                "Enrichment Confidence": (r.get("Enrichment Confidence") or "").strip(),
                "Enrichment Rationale": (r.get("Enrichment Rationale") or "").strip(),
                "Enrichment Source": (r.get("Enrichment Source") or "").strip(),
                "Attempt Count": (r.get("Attempt Count") or "").strip(),
                "Last Attempted At": (r.get("Last Attempted At") or "").strip(),
                "Attempt Outcome": (r.get("Attempt Outcome") or "").strip(),
                "Notes": (r.get("Notes") or "").strip(),
                "Updated At": (r.get("Updated At") or "").strip(),
            }
        )

    # Safety rail: we should almost never shrink this file materially during apply.
    # Shrinks can happen if the existing file had duplicate canonicals that are now de-duped.
    # But catastrophic shrink is usually a signal of a bad read/write or wrong input.
    new_row_count = len(out_rows)
    if prior_row_count > 0 and new_row_count < int(prior_row_count * 0.95) and not args.allow_shrink:
        raise SystemExit(
            f"Refusing to shrink {enrichment_path} from {prior_row_count} -> {new_row_count} rows. "
            f"Re-run with --allow-shrink if intentional."
        )

    # Backup before write (cheap insurance against accidental truncation or user error).
    backup_path: Path | None = None
    if enrichment_path.exists() and not args.dry_run:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = enrichment_path.with_name(f"{enrichment_path.stem}_backup_before_apply_{ts}{enrichment_path.suffix}")
        shutil.copy2(enrichment_path, backup_path)

    write_csv_dicts(
        enrichment_path,
        out_rows,
        fieldnames=[
            "Master Customer Name Canonical",
            "Company Website",
            "NAICS",
            "Industry Detail",
            "Enrichment Status",
            "Enrichment Confidence",
            "Enrichment Rationale",
            "Enrichment Source",
            "Attempt Count",
            "Last Attempted At",
            "Attempt Outcome",
            "Notes",
            "Updated At",
        ],
    )
    if backup_path:
        print(f"Backed up {enrichment_path} to {backup_path}")

    paths = default_paths()
    work_dir = paths.get("work_dir") or Path("output/work")
    report_dir = Path(work_dir) / "enrichment"
    report_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"MasterEnrichmentApplyReport_{report_ts}.csv"
    write_csv_dicts(
        report_path,
        changes,
        fieldnames=[
            "Master Customer Name Canonical",
            "Old Website",
            "New Website",
            "Old NAICS",
            "New NAICS",
            "Old Industry Detail",
            "New Industry Detail",
            "Enrichment Status",
            "Enrichment Confidence",
            "Enrichment Source",
            "Attempt Count",
            "Last Attempted At",
            "Attempt Outcome",
        ],
    )

    print(f"Applied enrichment queue to {enrichment_path} (adds={adds}, updates={updates})")
    print(f"Wrote apply report to {report_path}")


if __name__ == "__main__":
    main()
