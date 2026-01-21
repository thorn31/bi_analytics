from __future__ import annotations

import csv
import os
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

from customer_processing import (
    build_master_segmentation_rows,
    confidence_for_method,
    default_paths,
    load_master_enrichment,
    load_master_display_name_overrides,
    load_master_logos,
    load_master_segmentation_overrides,
    load_master_websites,
    load_naics_titles_2022,
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


def _set_if_blank(row: dict, key: str, value: str) -> None:
    if not (row.get(key) or "").strip():
        row[key] = value


def _build_apistemic_logo_url(domain: str) -> str:
    d = (domain or "").strip()
    if not d:
        return ""
    return f"https://logos-api.apistemic.com/domain:{d}"


def _build_logo_dev_url(domain: str) -> str:
    d = (domain or "").strip()
    if not d:
        return ""
    token = (os.environ.get("LOGO_DEV_PUBLISHABLE_KEY") or "").strip()
    base = f"https://img.logo.dev/{d}"
    params = "size=256&format=png&retina=true"
    if token:
        return f"{base}?token={token}&{params}"
    return f"{base}?{params}"


def _normalize_naics_single(value: str) -> tuple[str, str]:
    raw = (value or "").strip()
    if not raw:
        return "", ""
    if raw in {"31-33", "44-45", "48-49"}:
        return "", raw
    if "-" in raw:
        return "", raw
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        return "", raw
    return digits, raw


def _naics_sector_code(naics_digits: str) -> str:
    d = (naics_digits or "").strip()
    if len(d) < 2:
        return ""
    first2 = d[:2]
    if first2 in {"31", "32", "33"}:
        return "31-33"
    if first2 in {"44", "45"}:
        return "44-45"
    if first2 in {"48", "49"}:
        return "48-49"
    return first2


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
    display_overrides_path = paths.get("master_display_name_overrides", Path("data/governance/MasterDisplayNameOverrides.csv"))
    master_seg_overrides_path = paths["master_segmentation_overrides"]
    naics_codes_path = paths.get("naics_codes_2022") or (Path("data") / "sources" / "NAICS 2-6 Digit_2022_Codes.csv")

    output_segmentation = paths["segmentation_output"]
    output_master_segmentation = paths["master_segmentation_output"]
    output_dir = output_master_segmentation.parent  # final output folder

    if not master_map_path.exists():
        raise SystemExit(
            f"Error: Master map not found at {master_map_path}. Run dedupe first: `python3 dedupe_customers.py`"
        )

    overrides = load_overrides(overrides_path)
    websites = load_master_websites(websites_path)
    display_name_overrides = load_master_display_name_overrides(display_overrides_path)
    enrichment = load_master_enrichment(paths.get("master_enrichment", Path("data/enrichment/MasterEnrichment.csv")))
    logos = load_master_logos(paths.get("master_logos", Path("data/enrichment/MasterLogos.csv")))
    master_seg_overrides = load_master_segmentation_overrides(master_seg_overrides_path)
    naics_titles = load_naics_titles_2022(naics_codes_path)
    master_rows = read_csv_dicts(master_map_path)

    master_segmentation_rows = build_master_segmentation_rows(master_rows)
    for row in master_segmentation_rows:
        row.setdefault("Status", "")
        canonical = (row.get("Master Customer Name Canonical") or "").strip()
        if canonical and canonical.upper() in display_name_overrides:
            row["Master Customer Name"] = display_name_overrides[canonical.upper()]

        _set_if_blank(row, "Industrial Group Source", "Segmentation Logic")
        _set_if_blank(row, "Industry Detail Source", "Segmentation Logic" if (row.get("Industry Detail") or "").strip() else "")
        _set_if_blank(row, "NAICS Source", "Segmentation Logic" if (row.get("NAICS") or "").strip() else "")
        _set_if_blank(row, "Support Category Source", "Segmentation Logic" if (row.get("Support Category") or "").strip() else "")
        _set_if_blank(row, "Company Website Source", "Segmentation Logic" if (row.get("Company Website") or "").strip() else "")

        row.setdefault("Company Logo URL", "")
        row.setdefault("Company Logo URL Source", "")
        row.setdefault("Company Logo URL (Apistemic)", "")
        row.setdefault("Company Logo URL (Apistemic) Source", "")
        row.setdefault("Company Logo URL (Logo.dev)", "")
        row.setdefault("Company Logo URL (Logo.dev) Source", "")

        row.setdefault("Enrichment Status", "")
        row.setdefault("Enrichment Rationale", "")

        e = enrichment.get(canonical) if canonical else None
        if e:
            row["Enrichment Status"] = (e.get("Enrichment Status") or "").strip()
            row["Enrichment Rationale"] = (e.get("Enrichment Rationale") or "").strip()

        if canonical in master_seg_overrides:
            o = master_seg_overrides[canonical]
            if o.get("Industrial Group"):
                row["Industrial Group"] = o["Industrial Group"]
                row["Industrial Group Source"] = "Master Override"
            if o.get("Industry Detail"):
                row["Industry Detail"] = o["Industry Detail"]
                row["Industry Detail Source"] = "Master Override"
            if o.get("NAICS"):
                row["NAICS"] = o["NAICS"]
                row["NAICS Source"] = "Master Override"
            if o.get("Method"):
                row["Method"] = _normalize_override_method(o["Method"])
            if o.get("Status"):
                row["Status"] = o["Status"]
            if o.get("Support Category"):
                row["Support Category"] = o["Support Category"]
                row["Support Category Source"] = "Master Override"
            if o.get("Company Website"):
                row["Company Website"] = o["Company Website"]
                row["Company Website Source"] = "Master Override"

            status = (row.get("Status") or "").strip() or "Final"
            row["Status"] = status
            method = (row.get("Method") or "").strip()
            if status == "Queued":
                row["Confidence"] = "Low"
                row["Rationale"] = "Queued for AI analyst research" if method == "AI Analyst Research" else "Queued for review"
            else:
                row["Confidence"] = _confidence_for_status(status) or "High"
                base = "Analyst-approved" if status == "Final" else "Analyst draft"
                row["Rationale"] = f"{base} override (method: {method})" if method else f"{base} override"

        if e and (e.get("Enrichment Status") or "").strip() == "Verified":
            updated_fields: list[str] = []
            o = master_seg_overrides.get(canonical) if canonical else None
            if (e.get("NAICS") or "").strip() and not (o and (o.get("NAICS") or "").strip()):
                row["NAICS"] = (e.get("NAICS") or "").strip()
                row["NAICS Source"] = "Verified Enrichment"
                updated_fields.append("NAICS")
            if (e.get("Industry Detail") or "").strip() and not (o and (o.get("Industry Detail") or "").strip()):
                row["Industry Detail"] = (e.get("Industry Detail") or "").strip()
                row["Industry Detail Source"] = "Verified Enrichment"
                updated_fields.append("Industry Detail")
            if (e.get("Company Website") or "").strip() and not (o and (o.get("Company Website") or "").strip()):
                row["Company Website"] = (e.get("Company Website") or "").strip()
                row["Company Website Source"] = "Verified Enrichment"
                updated_fields.append("Company Website")

            if updated_fields:
                conf = (e.get("Enrichment Confidence") or "").strip()
                rationale = (e.get("Enrichment Rationale") or "").strip()
                if conf:
                    row["Confidence"] = conf
                if rationale:
                    row["Rationale"] = f"Verified enrichment updated: {', '.join(updated_fields)} — {rationale}"
                else:
                    row["Rationale"] = f"Verified enrichment updated: {', '.join(updated_fields)}"

        if not (row.get("Company Website") or "").strip():
            fallback = websites.get(canonical, "")
            if fallback:
                row["Company Website"] = fallback
                row["Company Website Source"] = "Approved Website"

        if not (row.get("Company Logo URL") or "").strip():
            hosted = (logos.get(canonical, {}).get("Hosted Logo URL") or "").strip() if canonical else ""
            if hosted:
                row["Company Logo URL"] = hosted
                row["Company Logo URL Source"] = "Master Logos"

        domain = (row.get("Company Website") or "").strip()
        if not (row.get("Company Logo URL (Apistemic)") or "").strip() and domain:
            row["Company Logo URL (Apistemic)"] = _build_apistemic_logo_url(domain)
            if (row.get("Company Logo URL (Apistemic)") or "").strip():
                row["Company Logo URL (Apistemic) Source"] = "Computed from Company Website"
        if not (row.get("Company Logo URL (Logo.dev)") or "").strip() and domain:
            row["Company Logo URL (Logo.dev)"] = _build_logo_dev_url(domain)
            if (row.get("Company Logo URL (Logo.dev)") or "").strip():
                row["Company Logo URL (Logo.dev) Source"] = "Computed from Company Website"

        naics_norm, naics_raw = _normalize_naics_single(row.get("NAICS") or "")
        row["NAICS Raw"] = naics_raw
        row["NAICS"] = naics_norm
        if not naics_norm:
            row["NAICS Source"] = ""

        row["NAICS 2 Digit"] = naics_norm[:2] if len(naics_norm) >= 2 else ""
        row["NAICS 4 Digit"] = naics_norm[:4] if len(naics_norm) >= 4 else ""
        row["NAICS 6 Digit"] = naics_norm[:6] if len(naics_norm) >= 6 else ""
        row["NAICS 2 Digit Title"] = naics_titles.get(row["NAICS 2 Digit"], "") if row["NAICS 2 Digit"] else ""
        row["NAICS 4 Digit Title"] = naics_titles.get(row["NAICS 4 Digit"], "") if row["NAICS 4 Digit"] else ""
        row["NAICS 6 Digit Title"] = naics_titles.get(row["NAICS 6 Digit"], "") if row["NAICS 6 Digit"] else ""

        row["NAICS Sector Code"] = _naics_sector_code(naics_norm)
        row["NAICS Sector Title"] = naics_titles.get(row["NAICS Sector Code"], "") if row["NAICS Sector Code"] else ""
        row["NAICS Subsector Code"] = naics_norm[:3] if len(naics_norm) >= 3 else ""
        row["NAICS Subsector Title"] = naics_titles.get(row["NAICS Subsector Code"], "") if row["NAICS Subsector Code"] else ""
        row["NAICS Industry Group Code"] = naics_norm[:4] if len(naics_norm) >= 4 else ""
        row["NAICS Industry Group Title"] = (
            naics_titles.get(row["NAICS Industry Group Code"], "") if row["NAICS Industry Group Code"] else ""
        )
        row["NAICS Industry Code"] = naics_norm[:5] if len(naics_norm) >= 5 else ""
        row["NAICS Industry Title"] = naics_titles.get(row["NAICS Industry Code"], "") if row["NAICS Industry Code"] else ""
        row["NAICS National Industry Code"] = naics_norm[:6] if len(naics_norm) >= 6 else ""
        row["NAICS National Industry Title"] = (
            naics_titles.get(row["NAICS National Industry Code"], "") if row["NAICS National Industry Code"] else ""
        )

    master_dim_by_canonical = {
        (r.get("Master Customer Name Canonical") or "").strip(): r for r in master_segmentation_rows
    }

    segmentation_rows: list[dict] = []
    for row in master_rows:
        customer_key = row["Customer Key"]
        master_canonical = (row.get("Master Customer Name Canonical") or "").strip()
        dim = master_dim_by_canonical.get(master_canonical) or {}

        seg_row: dict[str, str] = {
            "Customer Key": customer_key,
            "Original Name": row.get("Original Name", ""),
            # Prefer the master-dimension display name (includes MasterDisplayNameOverrides).
            "Master Customer Name": dim.get("Master Customer Name", row.get("Master Customer Name", "")),
            "Master Customer Name Canonical": master_canonical,
            "Industrial Group": dim.get("Industrial Group", ""),
            "Industry Detail": dim.get("Industry Detail", ""),
            "NAICS": dim.get("NAICS", ""),
            "NAICS Raw": dim.get("NAICS Raw", ""),
            "NAICS Source": dim.get("NAICS Source", ""),
            "NAICS Sector Code": dim.get("NAICS Sector Code", ""),
            "NAICS Sector Title": dim.get("NAICS Sector Title", ""),
            "NAICS Subsector Code": dim.get("NAICS Subsector Code", ""),
            "NAICS Subsector Title": dim.get("NAICS Subsector Title", ""),
            "NAICS Industry Group Code": dim.get("NAICS Industry Group Code", ""),
            "NAICS Industry Group Title": dim.get("NAICS Industry Group Title", ""),
            "NAICS Industry Code": dim.get("NAICS Industry Code", ""),
            "NAICS Industry Title": dim.get("NAICS Industry Title", ""),
            "NAICS National Industry Code": dim.get("NAICS National Industry Code", ""),
            "NAICS National Industry Title": dim.get("NAICS National Industry Title", ""),
            "Method": dim.get("Method", ""),
            "Status": dim.get("Status", ""),
            "Confidence": dim.get("Confidence", ""),
            "Rationale": dim.get("Rationale", ""),
            "Support Category": dim.get("Support Category", ""),
            "Company Website": dim.get("Company Website", ""),
            "Company Logo URL": dim.get("Company Logo URL", ""),
            "Company Logo URL (Apistemic)": dim.get("Company Logo URL (Apistemic)", ""),
            "Company Logo URL (Logo.dev)": dim.get("Company Logo URL (Logo.dev)", ""),
            "Source": row.get("Source", ""),
        }

        # IMPORTANT: CustomerSegmentation is a master-derived join output. To keep it
        # perfectly aligned with MasterCustomerSegmentation, we do not apply key-level
        # Manual Segment overrides here.
        #
        # If you need to change a segmentation decision, do it at master-grain via:
        # - data/governance/MasterSegmentationOverrides.csv (segmentation)
        # - data/enrichment/MasterEnrichment.csv (website/NAICS/detail enrichment)

        segmentation_rows.append(seg_row)

    master_seg_written = write_csv_dicts(
        output_master_segmentation,
        master_segmentation_rows,
        fieldnames=[
            "Master Customer Name",
            "Master Customer Name Canonical",
            "Industrial Group",
            "Industrial Group Source",
            "Industry Detail",
            "Industry Detail Source",
            "NAICS",
            "NAICS Raw",
            "NAICS Source",
            "NAICS Sector Code",
            "NAICS Sector Title",
            "NAICS Subsector Code",
            "NAICS Subsector Title",
            "NAICS Industry Group Code",
            "NAICS Industry Group Title",
            "NAICS Industry Code",
            "NAICS Industry Title",
            "NAICS National Industry Code",
            "NAICS National Industry Title",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Support Category Source",
            "Company Website",
            "Company Website Source",
            "Company Logo URL",
            "Company Logo URL Source",
            "Company Logo URL (Apistemic)",
            "Company Logo URL (Apistemic) Source",
            "Company Logo URL (Logo.dev)",
            "Company Logo URL (Logo.dev) Source",
            "Enrichment Status",
            "Enrichment Rationale",
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
            "Master Customer Name Canonical",
            "Industrial Group",
            "Industry Detail",
            "NAICS",
            "NAICS Raw",
            "NAICS Source",
            "NAICS Sector Code",
            "NAICS Sector Title",
            "NAICS Subsector Code",
            "NAICS Subsector Title",
            "NAICS Industry Group Code",
            "NAICS Industry Group Title",
            "NAICS Industry Code",
            "NAICS Industry Title",
            "NAICS National Industry Code",
            "NAICS National Industry Title",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Company Website",
            "Company Logo URL",
            "Company Logo URL (Apistemic)",
            "Company Logo URL (Logo.dev)",
            "Source",
        ],
    )

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
            "Industrial Group Source",
            "Industry Detail",
            "Industry Detail Source",
            "NAICS",
            "NAICS Raw",
            "NAICS Source",
            "NAICS Sector Code",
            "NAICS Sector Title",
            "NAICS Subsector Code",
            "NAICS Subsector Title",
            "NAICS Industry Group Code",
            "NAICS Industry Group Title",
            "NAICS Industry Code",
            "NAICS Industry Title",
            "NAICS National Industry Code",
            "NAICS National Industry Title",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Support Category Source",
            "Company Website",
            "Company Website Source",
            "Company Logo URL",
            "Company Logo URL Source",
            "Company Logo URL (Apistemic)",
            "Company Logo URL (Apistemic) Source",
            "Company Logo URL (Logo.dev)",
            "Company Logo URL (Logo.dev) Source",
            "Enrichment Status",
            "Enrichment Rationale",
            "IsMerge",
            "MergeGroupSize",
        ],
    )

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
            "NAICS Sector Code",
            "NAICS Subsector Code",
            "NAICS Industry Group Code",
            "NAICS Industry Code",
            "NAICS National Industry Code",
            "Method",
            "Status",
            "Confidence",
            "Rationale",
            "Support Category",
            "Company Website",
            "Company Logo URL",
            "Company Logo URL (Apistemic)",
            "Company Logo URL (Logo.dev)",
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
