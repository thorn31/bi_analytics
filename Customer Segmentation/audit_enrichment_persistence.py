#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

import customer_processing as cp


REPO_ROOT = cp.repo_root()


@dataclass(frozen=True)
class AuditItem:
    source_type: str
    source_file: str
    raw_name: str
    expected_status: str  # Verified / Deferred / ApprovedWebsite


def _iter_enrichment_log_items(path: Path) -> list[AuditItem]:
    """
    Parse output/enrichment_logs/Batch_*.md.

    Expected patterns (examples):
    - *   **10% Cabinetry**: 238350 - Finish Carpentry Contractors
    - *   **3665 Mallory Jv**
    """
    items: list[AuditItem] = []
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    section = ""
    for line in text:
        s = line.strip()
        if s.startswith("## "):
            if s.startswith("## ✅ Enriched"):
                section = "enriched"
            elif s.startswith("## ⚠️ Deferred"):
                section = "deferred"
            else:
                # Don't treat other sections (e.g. Notes) as signals for persistence.
                section = ""
            continue
        if not section:
            continue
        name = ""
        if section == "enriched":
            m = re.match(r"^\*\s+\*\*\s*([^*]+?)\s*\*\*\s*:", s)
            if m:
                name = m.group(1).strip()
        else:
            m = re.match(r"^\*\s+\*\*\s*([^*]+?)\s*\*\*\s*$", s)
            if m:
                name = m.group(1).strip()
            else:
                # Some deferred bullets include a trailing ':' too; accept them.
                m2 = re.match(r"^\*\s+\*\*\s*([^*]+?)\s*\*\*\s*:", s)
                if m2:
                    name = m2.group(1).strip()
        if not name:
            continue
        if name.lower() in {"rationale", "narrative", "notes"}:
            continue
        if not name or name.lower() == "customer":
            continue
        expected = "Verified" if section == "enriched" else "Deferred"
        items.append(AuditItem("enrichment_log", path.name, name, expected))
    return items


def _canonicalize_against_master(raw_name: str, master_canonicals: set[str]) -> str:
    """
    Prefer mapping to the *current* master canonical list to avoid drift in tokenization.
    """
    if not raw_name:
        return ""

    # First try direct canonicalizer.
    guess = cp.get_master_name(raw_name)
    if guess in master_canonicals:
        return guess

    # Normalized matching: collapse to alnum only (handles 10% vs 10 % etc).
    def norm(s: str) -> str:
        return "".join(ch for ch in (s or "").upper() if ch.isalnum())

    master_by_norm: dict[str, str] = {}
    for c in master_canonicals:
        master_by_norm.setdefault(norm(c), c)

    alt = master_by_norm.get(norm(guess)) or master_by_norm.get(norm(raw_name))
    if alt:
        return alt

    return guess


def _iter_batch_enrichment_table_items(path: Path) -> list[AuditItem]:
    """
    Parse data/batches/Batch_Enrichment*.md table rows.
    These represent website-focused enrichment decisions.
    """
    items: list[AuditItem] = []
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in text:
        s = line.strip()
        if not s.startswith("|") or s.startswith("|---"):
            continue
        cols = [c.strip() for c in s.strip("|").split("|")]
        if len(cols) < 5:
            continue
        customer = cols[0]
        if not customer or customer.lower() == "customer":
            continue
        items.append(AuditItem("batch_enrichment_md", path.name, customer, "ApprovedWebsite"))
    return items


def _load_master_enrichment(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            canon = (row.get("Master Customer Name Canonical") or "").strip()
            if not canon or canon.startswith("#"):
                continue
            out[canon] = row
    return out


def _load_master_websites(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            canon = (row.get("Master Customer Name Canonical") or "").strip()
            if not canon or canon.startswith("#"):
                continue
            out[canon] = (row.get("Company Website") or "").strip()
    return out


def _load_apply_reports(paths: list[Path]) -> set[str]:
    applied: set[str] = set()
    for p in paths:
        try:
            with p.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    canon = (row.get("Master Customer Name Canonical") or "").strip()
                    if canon:
                        applied.add(canon)
        except Exception:
            continue
    return applied


def main() -> None:
    paths = cp.default_paths()
    master_enrichment_path = paths.get("master_enrichment", REPO_ROOT / "data" / "enrichment" / "MasterEnrichment.csv")
    master_websites_path = paths.get("master_websites", REPO_ROOT / "data" / "enrichment" / "MasterWebsites.csv")

    enrich_by = _load_master_enrichment(master_enrichment_path)
    websites_by = _load_master_websites(master_websites_path)

    apply_reports = sorted((REPO_ROOT / "output" / "work" / "enrichment").glob("MasterEnrichmentApplyReport_*.csv"))
    applied_canons = _load_apply_reports(apply_reports)

    # Load current master canonical list for robust matching.
    master_output = paths.get("master_segmentation_output", REPO_ROOT / "output" / "final" / "MasterCustomerSegmentation.csv")
    master_canonicals: set[str] = set()
    if master_output.exists():
        with master_output.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                c = (row.get("Master Customer Name Canonical") or "").strip()
                if c:
                    master_canonicals.add(c)

    items: list[AuditItem] = []
    for p in sorted((REPO_ROOT / "output" / "enrichment_logs").glob("Batch_*.md")):
        items.extend(_iter_enrichment_log_items(p))
    for p in sorted((REPO_ROOT / "data" / "batches").glob("Batch_Enrichment*.md")):
        items.extend(_iter_batch_enrichment_table_items(p))

    out_dir = REPO_ROOT / "output" / "work" / "enrichment"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "EnrichmentPersistenceAudit.csv"
    missing_path = out_dir / "EnrichmentPersistenceAudit_missing.csv"

    rows_out: list[dict[str, str]] = []
    missing_out: list[dict[str, str]] = []

    for item in items:
        canon = _canonicalize_against_master(item.raw_name, master_canonicals)
        e = enrich_by.get(canon)
        w = websites_by.get(canon, "")

        in_enrichment = bool(e)
        in_websites = bool(w)
        in_apply_reports = canon in applied_canons

        enrich_status = (e.get("Enrichment Status") or "").strip() if e else ""
        enrich_site = (e.get("Company Website") or "").strip() if e else ""
        enrich_naics = (e.get("NAICS") or "").strip() if e else ""
        enrich_detail = (e.get("Industry Detail") or "").strip() if e else ""

        row = {
            "Source Type": item.source_type,
            "Source File": item.source_file,
            "Raw Name": item.raw_name,
            "Canonical": canon,
            "Expected Status": item.expected_status,
            "In MasterEnrichment": "TRUE" if in_enrichment else "FALSE",
            "MasterEnrichment Status": enrich_status,
            "MasterEnrichment Website": enrich_site,
            "MasterEnrichment NAICS": enrich_naics,
            "MasterEnrichment Industry Detail": enrich_detail,
            "In MasterWebsites": "TRUE" if in_websites else "FALSE",
            "MasterWebsites Website": w,
            "Appears In Apply Reports": "TRUE" if in_apply_reports else "FALSE",
        }
        rows_out.append(row)

        # Missing persistence: log says enriched/deferred, but we don't have a row in MasterEnrichment.
        if item.expected_status in {"Verified", "Deferred"} and not in_enrichment:
            missing_out.append(row)

    fieldnames = [
        "Source Type",
        "Source File",
        "Raw Name",
        "Canonical",
        "Expected Status",
        "In MasterEnrichment",
        "MasterEnrichment Status",
        "MasterEnrichment Website",
        "MasterEnrichment NAICS",
        "MasterEnrichment Industry Detail",
        "In MasterWebsites",
        "MasterWebsites Website",
        "Appears In Apply Reports",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_out)

    with missing_path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(missing_out)

    print(f"Wrote audit: {out_path} (rows={len(rows_out)})")
    print(f"Wrote missing persistence list: {missing_path} (rows={len(missing_out)})")


if __name__ == "__main__":
    main()
