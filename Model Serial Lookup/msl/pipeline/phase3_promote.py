from __future__ import annotations

import csv
import json
from pathlib import Path

from msl.pipeline.common import ensure_dir
from msl.pipeline.ruleset_manager import cleanup_old_rulesets, update_current_pointer


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def _read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
        return (r.fieldnames or []), rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def cmd_phase3_promote(args) -> int:
    from msl.decoder.normalize import normalize_text

    base_ruleset = Path(args.base_ruleset_dir)
    if not base_ruleset.exists():
        raise SystemExit(f"Missing base ruleset: {base_ruleset}")
    candidates_dir = Path(args.candidates_dir)
    if not candidates_dir.exists():
        raise SystemExit(f"Missing candidates dir: {candidates_dir}")

    out_ruleset = ensure_dir(Path(args.out_dir) / args.run_id)

    # Copy + load base CSVs
    base_serial = base_ruleset / "SerialDecodeRule.csv"
    base_attr = base_ruleset / "AttributeDecodeRule.csv"
    if not base_serial.exists() or not base_attr.exists():
        raise SystemExit("Base ruleset must contain SerialDecodeRule.csv and AttributeDecodeRule.csv")

    serial_fields, serial_rows = _read_csv(base_serial)
    attr_fields, attr_rows = _read_csv(base_attr)
    base_brands = {normalize_text(r.get("brand")) for r in serial_rows} | {normalize_text(r.get("brand")) for r in attr_rows}
    base_decode_brands = {
        normalize_text(r.get("brand"))
        for r in serial_rows
        if (r.get("rule_type") or "decode") == "decode" and (r.get("brand") or "").strip()
    } | {
        normalize_text(r.get("brand"))
        for r in attr_rows
        if (r.get("rule_type") or "decode") == "decode" and (r.get("brand") or "").strip()
    }

    # Optional audit gating
    audited_ok_attr: set[tuple[str, str]] = set()  # (brand, pattern_regex)
    audited_ok_serial: set[tuple[str, str]] = set()  # (brand, serial_regex)
    if getattr(args, "audit_dir", ""):
        audit_dir = Path(args.audit_dir)
        holdout_path = audit_dir / "holdout_validation_results.csv"
        fp_path = audit_dir / "false_positive_audit.csv"
        if holdout_path.exists():
            with holdout_path.open("r", newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    ctype = row.get("candidate_type", "")
                    brand = (row.get("brand", "") or "").strip()
                    pat = (row.get("pattern_regex", "") or "").strip()
                    acc = float(row.get("accuracy_on_matches") or 0.0)
                    cov = float(row.get("coverage_on_truth") or 0.0)
                    if ctype == "AttributeDecodeRule":
                        if acc >= float(args.min_accuracy) and cov >= float(args.min_coverage):
                            audited_ok_attr.add((brand, pat))
                    if ctype == "SerialDecodeRule":
                        if acc >= float(args.min_accuracy) and cov >= float(args.min_coverage):
                            audited_ok_serial.add((brand, pat))
        # Apply false-positive gate for attributes only (serial rules are brand-filtered at decode time).
        if fp_path.exists():
            with fp_path.open("r", newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    if row.get("candidate_type") != "AttributeDecodeRule":
                        continue
                    brand = (row.get("brand", "") or "").strip()
                    pat = (row.get("pattern_regex", "") or "").strip()
                    rate = float(row.get("other_brand_match_rate") or 0.0)
                    if rate > float(args.max_false_positive_rate):
                        audited_ok_attr.discard((brand, pat))

    # Load candidates
    serial_cands = _load_jsonl(candidates_dir / "SerialDecodeRule.candidates.jsonl")
    attr_cands = _load_jsonl(candidates_dir / "AttributeDecodeRule.candidates.jsonl")
    brand_cand_csv = candidates_dir / "BrandNormalizeRule.candidates.csv"

    # Append candidates conservatively (no schema changes; store extra metadata in evidence/limitations).
    existing_serial_keys = {
        (r.get("brand", ""), r.get("style_name", ""), r.get("serial_regex", ""), r.get("source_url", "")) for r in serial_rows
    }
    for c in serial_cands:
        if audited_ok_serial:
            if (c.get("brand", ""), c.get("serial_regex", "")) not in audited_ok_serial:
                continue
        key = (c.get("brand", ""), c.get("style_name", ""), c.get("serial_regex", ""), c.get("source_url", ""))
        if key in existing_serial_keys:
            continue
        existing_serial_keys.add(key)
        serial_rows.append(
            {
                "rule_type": c.get("rule_type", "decode"),
                "brand": c.get("brand", ""),
                "style_name": c.get("style_name", ""),
                "serial_regex": c.get("serial_regex", ""),
                "date_fields": json.dumps(c.get("date_fields", {}), ensure_ascii=False),
                "example_serials": json.dumps(c.get("example_serials", []), ensure_ascii=False),
                "decade_ambiguity": json.dumps(c.get("decade_ambiguity", {}), ensure_ascii=False),
                "guidance_action": c.get("guidance_action", ""),
                "guidance_text": c.get("guidance_text", ""),
                "evidence_excerpt": c.get("evidence_excerpt", ""),
                "source_url": c.get("source_url", "internal_asset_reports"),
                "retrieved_on": c.get("retrieved_on", ""),
                "image_urls": json.dumps(c.get("image_urls", []), ensure_ascii=False),
            }
        )

    existing_attr_keys = {
        (r.get("brand", ""), r.get("attribute_name", ""), r.get("model_regex", ""), r.get("value_extraction", ""), r.get("source_url", ""))
        for r in attr_rows
    }
    for c in attr_cands:
        ve_obj = c.get("value_extraction", {}) or {}
        pat = ((ve_obj.get("pattern") or {}).get("regex") or "").strip()
        if audited_ok_attr:
            if (c.get("brand", ""), pat) not in audited_ok_attr:
                continue
        ve = json.dumps(c.get("value_extraction", {}), ensure_ascii=False)
        key = (c.get("brand", ""), c.get("attribute_name", ""), c.get("model_regex", ""), ve, c.get("source_url", ""))
        if key in existing_attr_keys:
            continue
        existing_attr_keys.add(key)
        limitations = c.get("limitations", "") or ""
        # Preserve some metrics in limitations (keeps CSV schema stable).
        metrics = []
        for k in ["equipment_type", "support_n", "match_n", "train_accuracy", "holdout_accuracy"]:
            if k in c:
                metrics.append(f"{k}={c.get(k)}")
        if metrics:
            limitations = (limitations + " " + ("[" + ", ".join(metrics) + "]")).strip()

        attr_rows.append(
            {
                "rule_type": c.get("rule_type", "decode"),
                "brand": c.get("brand", ""),
                "model_regex": c.get("model_regex", ""),
                "attribute_name": c.get("attribute_name", ""),
                "value_extraction": ve,
                "units": c.get("units", ""),
                "examples": json.dumps(c.get("examples", []), ensure_ascii=False),
                "limitations": limitations,
                "guidance_action": c.get("guidance_action", ""),
                "guidance_text": c.get("guidance_text", ""),
                "evidence_excerpt": c.get("evidence_excerpt", ""),
                "source_url": c.get("source_url", "internal_asset_reports"),
                "retrieved_on": c.get("retrieved_on", ""),
                "image_urls": json.dumps(c.get("image_urls", []), ensure_ascii=False),
            }
        )

    # Write out merged ruleset
    _write_csv(out_ruleset / "SerialDecodeRule.csv", serial_fields, serial_rows)
    _write_csv(out_ruleset / "AttributeDecodeRule.csv", attr_fields, attr_rows)

    # Promote BrandNormalizeRule.csv (optional)
    base_brand_rules = base_ruleset / "BrandNormalizeRule.csv"
    brand_fields: list[str] = [
        "raw_make_normalized",
        "canonical_brand",
        "support_n",
        "similarity",
        "examples",
        "source_url",
        "retrieved_on",
    ]
    brand_rows: list[dict] = []
    if base_brand_rules.exists():
        _f, brand_rows = _read_csv(base_brand_rules)

    existing_brand_keys = {(normalize_text(r.get("raw_make_normalized") or ""), normalize_text(r.get("canonical_brand") or "")) for r in brand_rows}
    if brand_cand_csv.exists():
        _cand_fields, cand_rows = _read_csv(brand_cand_csv)
        print(f"DEBUG: Found {len(cand_rows)} brand candidates.")
        for c in cand_rows:
            raw = normalize_text(c.get("raw_make") or c.get("raw_make_normalized") or "")
            canonical = normalize_text(c.get("canonical_brand") or c.get("suggested_brand") or "")
            if not raw or not canonical or raw == canonical:
                continue
            try:
                support_n = int(str(c.get("support_n") or "0").strip() or "0")
            except Exception:
                support_n = 0
            try:
                similarity = float(str(c.get("similarity") or "0").strip() or "0")
            except Exception:
                similarity = 0.0

            if support_n < int(getattr(args, "min_brand_support", 1)):
                print(f"DEBUG: Skip {raw}->{canonical}: support {support_n} < {getattr(args, 'min_brand_support', 1)}")
                continue
            if similarity < float(getattr(args, "min_brand_similarity", 0.80)):
                print(f"DEBUG: Skip {raw}->{canonical}: sim {similarity} < {getattr(args, 'min_brand_similarity', 0.80)}")
                continue
            # Safety: only promote mappings to brands already present in the base ruleset.
            if canonical not in base_brands:
                print(f"DEBUG: Skip {raw}->{canonical}: canonical brand '{canonical}' not in base ruleset.")
                continue
            # Safety: don't override an already-recognized brand token in the ruleset.
            if raw in base_decode_brands:
                print(f"DEBUG: Skip {raw}->{canonical}: raw brand '{raw}' is already a decoding brand.")
                continue

            key = (raw, canonical)
            if key in existing_brand_keys:
                continue
            existing_brand_keys.add(key)
            print(f"DEBUG: Promoting {raw} -> {canonical}")
            brand_rows.append(
                {
                    "raw_make_normalized": raw,
                    "canonical_brand": canonical,
                    "support_n": str(support_n),
                    "similarity": f"{similarity:.3f}",
                    "examples": c.get("examples") or "",
                    "source_url": c.get("source_url") or "internal_asset_reports",
                    "retrieved_on": c.get("retrieved_on") or "",
                }
            )

    if brand_rows:
        _write_csv(out_ruleset / "BrandNormalizeRule.csv", brand_fields, brand_rows)

    # Update CURRENT.txt pointer to this new ruleset
    update_current_pointer(out_ruleset)
    print(f"Updated CURRENT.txt -> {out_ruleset}")

    # Auto-cleanup old rulesets unless --no-cleanup specified
    if not getattr(args, "no_cleanup", False):
        cleanup_old_rulesets()

    print(str(out_ruleset))
    return 0
