from __future__ import annotations

import csv
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

from customer_processing import (
    build_master_segmentation_rows,
    confidence_for_method,
    default_paths,
    load_master_enrichment,
    load_master_websites,
    load_master_segmentation_overrides,
    load_overrides,
    map_legacy_segment_to_industrial_group,
    read_csv_dicts,
    write_csv_dicts,
)

REVIEW_METHODS = {"Unclassified"}
REVIEW_GROUPS = {"Unknown / Needs Review"}
REVIEW_STATUSES = {"Queued", "Draft"}


def _normalize_override_method(method: str) -> str:
    m = (method or "").strip()
    if m == "AI-Assisted Search":
        return "AI Analyst Research"
    return m


def _confidence_for_status(status: str) -> str:
    s = (status or "").strip()
    if s == "Final":
        return "High"
    if s == "Draft":
        return "Medium"
    if s == "Queued":
        return "Low"
    return ""


def _latest_override_mismatch_report(output_dir: Path) -> Path | None:
    candidates = sorted(output_dir.glob("OverrideMismatchReport*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _copy_if_possible(src: Path, dest: Path) -> None:
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    except Exception as exc:
        print(f"Warning: could not copy {src} to {dest}: {exc}")


def _write_run_summary(path: Path, metrics: dict[str, int | str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=["Metric", "Value"])
        w.writeheader()
        for k, v in metrics.items():
            w.writerow({"Metric": k, "Value": v})


def _append_run_history(path: Path, row: dict[str, int | str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    fieldnames = [
        "Run Timestamp",
        "Masters",
        "Worklist Masters",
        "Unknown / Needs Review",
        "Method=Unclassified",
        "Method=AI-Assisted Search",
        "Override Mismatch Canonicals",
        "Input Customer Keys",
        "Output Customer Keys",
        "Missing Customer Keys",
        "Extra Customer Keys",
    ]
    # If the file exists but has an older header, avoid corrupting it; start a v2 file.
    target = path
    if exists:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                first = handle.readline().strip("\n\r")
            existing_fields = [c.strip() for c in first.split(",")] if first else []
            if existing_fields and existing_fields != fieldnames:
                target = path.with_name("RunHistory_v2.csv")
                exists = target.exists()
                print(f"Warning: {path} has a different header; appending to {target} instead.")
        except Exception:
            target = path.with_name("RunHistory_v2.csv")
            exists = target.exists()
            print(f"Warning: could not read {path} header; appending to {target} instead.")

    with target.open("a", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in fieldnames})


def main() -> None:
    paths = default_paths()
    output_root = paths.get("output_root") or Path("output")
    work_dir = paths.get("work_dir") or (output_root / "work")

    master_map_path = paths["dedupe_output"]
    input_customers_path = paths["input_customers"]
    overrides_path = paths["manual_overrides"]
    websites_path = paths["master_websites"]
    master_seg_overrides_path = paths["master_segmentation_overrides"]
    output_segmentation = paths["segmentation_output"]
    output_master_segmentation = paths["master_segmentation_output"]
    output_dir = output_master_segmentation.parent  # final output folder

    if not master_map_path.exists():
        raise SystemExit(
            f"Error: Master map not found at {master_map_path}. Run dedupe first: `python3 dedupe_customers.py`"
        )

    overrides = load_overrides(overrides_path)
    websites = load_master_websites(websites_path)
    enrichment = load_master_enrichment(paths.get("master_enrichment", Path("data/enrichment/MasterEnrichment.csv")))
    master_seg_overrides = load_master_segmentation_overrides(master_seg_overrides_path)
    master_rows = read_csv_dicts(master_map_path)

    master_segmentation_rows = build_master_segmentation_rows(master_rows)
    for row in master_segmentation_rows:
        row.setdefault("Status", "")
        canonical = (row.get("Master Customer Name Canonical") or "").strip()
        if canonical in master_seg_overrides:
            o = master_seg_overrides[canonical]
            if o.get("Industrial Group"):
                row["Industrial Group"] = o["Industrial Group"]
            if o.get("Industry Detail"):
                row["Industry Detail"] = o["Industry Detail"]
            if o.get("NAICS"):
                row["NAICS"] = o["NAICS"]
            if o.get("Method"):
                row["Method"] = _normalize_override_method(o["Method"])
            if o.get("Status"):
                row["Status"] = o["Status"]
            if o.get("Support Category"):
                row["Support Category"] = o["Support Category"]
            if o.get("Company Website"):
                row["Company Website"] = o["Company Website"]

            # Confidence/rationale should reflect governance posture (Status first).
            status = (row.get("Status") or "").strip() or "Final"
            row["Status"] = status
            method = (row.get("Method") or "").strip()
            if status == "Queued":
                row["Confidence"] = "Low"
                row["Rationale"] = "Queued for AI analyst research" if method == "AI Analyst Research" else "Queued for review"
            else:
                row["Confidence"] = _confidence_for_status(status) or "High"
                base = "Analyst-approved" if status == "Final" else "Analyst draft"
                if method:
                    row["Rationale"] = f"{base} override (method: {method})"
                else:
                    row["Rationale"] = f"{base} override"

        # Apply verified enrichment (website/NAICS/industry detail), without overriding governance overrides.
        e = enrichment.get(canonical) if canonical else None
        if e and (e.get("Enrichment Status") or "").strip() == "Verified":
            updated_fields: list[str] = []

            # Governance override always wins per field.
            o = master_seg_overrides.get(canonical) if canonical else None
            if (e.get("NAICS") or "").strip() and not (o and (o.get("NAICS") or "").strip()):
                row["NAICS"] = (e.get("NAICS") or "").strip()
                updated_fields.append("NAICS")
            if (e.get("Industry Detail") or "").strip() and not (o and (o.get("Industry Detail") or "").strip()):
                row["Industry Detail"] = (e.get("Industry Detail") or "").strip()
                updated_fields.append("Industry Detail")
            if (e.get("Company Website") or "").strip() and not (o and (o.get("Company Website") or "").strip()):
                row["Company Website"] = (e.get("Company Website") or "").strip()
                updated_fields.append("Company Website")

            # If enrichment materially affected the output, adopt its confidence/rationale.
            if updated_fields:
                conf = (e.get("Enrichment Confidence") or "").strip()
                rationale = (e.get("Enrichment Rationale") or "").strip()
                if conf:
                    row["Confidence"] = conf
                if rationale:
                    row["Rationale"] = f"Verified enrichment updated: {', '.join(updated_fields)} — {rationale}"
                else:
                    row["Rationale"] = f"Verified enrichment updated: {', '.join(updated_fields)}"

        # Fill remaining website gaps from the approved websites table.
        if not row.get("Company Website"):
            row["Company Website"] = websites.get(canonical, "")

    master_dim_by_canonical = {
        (r.get("Master Customer Name Canonical") or "").strip(): r for r in master_segmentation_rows
    }

    # Customer-grain output should inherit master-grain segmentation (after overrides),
    # then optionally apply any legacy key-level segment overrides.
    segmentation_rows: list[dict] = []
    for row in master_rows:
        customer_key = row["Customer Key"]
        master_canonical = (row.get("Master Customer Name Canonical") or "").strip()
        dim = master_dim_by_canonical.get(master_canonical) or {}

        seg_row: dict[str, str] = {
            "Customer Key": customer_key,
            "Original Name": row.get("Original Name", ""),
            "Master Customer Name": row.get("Master Customer Name", ""),
            "Industrial Group": dim.get("Industrial Group", ""),
            "Industry Detail": dim.get("Industry Detail", ""),
            "NAICS": dim.get("NAICS", ""),
            "Method": dim.get("Method", ""),
            "Status": dim.get("Status", ""),
            "Confidence": dim.get("Confidence", ""),
            "Rationale": dim.get("Rationale", ""),
            "Support Category": dim.get("Support Category", ""),
            "Company Website": dim.get("Company Website", ""),
            "Source": row.get("Source", ""),
        }

        # Key-level manual segment override (legacy behavior). This can cause
        # inconsistency within a master; long-term, prefer master-level overrides.
        segment_override = overrides.get(customer_key).segment if customer_key in overrides else ""
        if segment_override.strip():
            group = (segment_override or "").strip()
            mapped_group = map_legacy_segment_to_industrial_group(group)
            method = "Manual Override"
            conf, rationale = confidence_for_method(method)
            if mapped_group:
                seg_row["Industrial Group"] = mapped_group
                seg_row["Industry Detail"] = ""
                seg_row["NAICS"] = ""
            else:
                seg_row["Industrial Group"] = "Unknown / Needs Review"
                seg_row["Industry Detail"] = f"Override: {group}"
                seg_row["NAICS"] = ""
            seg_row["Method"] = method
            seg_row["Status"] = (seg_row.get("Status") or "").strip() or "Final"
            seg_row["Confidence"] = conf
            seg_row["Rationale"] = rationale
            seg_row["Support Category"] = ""
            seg_row["Company Website"] = ""

        segmentation_rows.append(seg_row)

    master_seg_written = write_csv_dicts(
        output_master_segmentation,
        master_segmentation_rows,
        fieldnames=[
            "Master Customer Name",
            "Master Customer Name Canonical",
            "Industrial Group",
            "Industry Detail",
            "NAICS",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Company Website",
            "IsMerge",
            "MergeGroupSize",
        ],
    )
    seg_written = write_csv_dicts(
        output_segmentation,
        segmentation_rows,
        fieldnames=[
            "Customer Key",
            "Original Name",
            "Master Customer Name",
            "Industrial Group",
            "Industry Detail",
            "NAICS",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Company Website",
            "Source",
        ],
    )

    # Review worklist (masters still needing segmentation attention).
    worklist_rows = [
        r
        for r in master_segmentation_rows
        if (r.get("Method") or "").strip() in REVIEW_METHODS
        or (r.get("Industrial Group") or "").strip() in REVIEW_GROUPS
        or (r.get("Status") or "").strip() in REVIEW_STATUSES
    ]
    worklist_written = write_csv_dicts(
        output_dir / "SegmentationReviewWorklist.csv",
        worklist_rows,
        fieldnames=[
            "Master Customer Name",
            "Master Customer Name Canonical",
            "Industrial Group",
            "Industry Detail",
            "NAICS",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Company Website",
            "IsMerge",
            "MergeGroupSize",
        ],
    )

    # Per-run snapshot folder and trend logging.
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    runs_dir = output_root / "runs" / run_ts
    runs_dir.mkdir(parents=True, exist_ok=True)
    write_csv_dicts(
        runs_dir / "SegmentationReviewWorklist.csv",
        worklist_rows,
        fieldnames=[
            "Master Customer Name",
            "Master Customer Name Canonical",
            "Industrial Group",
            "Industry Detail",
            "NAICS",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Company Website",
            "IsMerge",
            "MergeGroupSize",
        ],
    )

    mismatch_report = _latest_override_mismatch_report(work_dir)
    mismatch_count = 0
    if mismatch_report:
        _copy_if_possible(mismatch_report, runs_dir / "OverrideMismatchReport.csv")
        try:
            with mismatch_report.open("r", encoding="utf-8-sig", newline="") as handle:
                mismatch_count = sum(1 for _ in csv.DictReader(handle))
        except Exception:
            mismatch_count = 0

    group_counts = Counter((r.get("Industrial Group") or "").strip() for r in master_segmentation_rows)
    method_counts = Counter((r.get("Method") or "").strip() for r in master_segmentation_rows)

    summary = {
        "Run Timestamp": run_ts,
        "Masters": len(master_segmentation_rows),
        "Worklist Masters": len(worklist_rows),
        "Unknown / Needs Review": group_counts.get("Unknown / Needs Review", 0),
        "Method=Unclassified": method_counts.get("Unclassified", 0),
        "Method=AI-Assisted Search": method_counts.get("AI-Assisted Search", 0),
        "Method=AI Analyst Research": method_counts.get("AI Analyst Research", 0),
        "Override Mismatch Canonicals": mismatch_count,
    }
    # Key coverage verification: output CustomerSegmentation should cover all input Customer Keys.
    try:
        with input_customers_path.open("r", encoding="utf-8-sig", newline="") as handle:
            input_keys = {row.get("Customer Key", "").strip() for row in csv.DictReader(handle) if row.get("Customer Key")}
        with Path(seg_written).open("r", encoding="utf-8-sig", newline="") as handle:
            output_keys = {row.get("Customer Key", "").strip() for row in csv.DictReader(handle) if row.get("Customer Key")}
        summary["Input Customer Keys"] = len(input_keys)
        summary["Output Customer Keys"] = len(output_keys)
        summary["Missing Customer Keys"] = len(input_keys - output_keys)
        summary["Extra Customer Keys"] = len(output_keys - input_keys)
    except Exception as exc:
        print(f"Warning: could not compute Customer Key coverage metrics: {exc}")
    _write_run_summary(runs_dir / "RunSummary.csv", summary)
    _append_run_history(output_root / "RunHistory.csv", summary)

    print(f"Loaded {len(overrides)} manual overrides from {overrides_path}.")
    print(f"Loaded {len(websites)} master websites from {websites_path}.")
    print(f"Loaded {len(master_seg_overrides)} master segmentation overrides from {master_seg_overrides_path}.")
    print(f"Processed {len(segmentation_rows)} rows.")
    print(f"Saved master segmentation to {master_seg_written}")
    print(f"Saved segmentation output to {seg_written}")
    print(f"Saved review worklist to {worklist_written}")
    print(f"Wrote run snapshot to {runs_dir}")
    print(f"Appended run history to {output_root / 'RunHistory.csv'}")


if __name__ == "__main__":
    main()
