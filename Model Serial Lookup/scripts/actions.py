#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_BASE_DIR = REPO_ROOT / "data" / "rules_normalized"
REPORTS_BASE_DIR = REPO_ROOT / "data" / "reports"
DISCOVERED_BASE_DIR = REPO_ROOT / "data" / "rules_discovered"
MANUAL_ADDITIONS_DIR = DISCOVERED_BASE_DIR / "manual_additions"

# Allow importing `msl` when this script is executed directly from `scripts/`.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


def _utc_compact_ts() -> str:
    # Windows-safe, filesystem-safe.
    return _utc_now().strftime("%Y%m%dT%H%M%SZ")


def _today() -> str:
    return _utc_now().date().isoformat()


def _sanitize_token(value: str) -> str:
    v = (value or "").strip()
    v = re.sub(r"[^A-Za-z0-9._-]+", "_", v)
    v = re.sub(r"_+", "_", v).strip("_")
    return v or "run"


def _default_run_id(action: str, tag: str) -> str:
    return "__".join([_today(), _sanitize_token(action), _sanitize_token(tag or "default"), _utc_compact_ts()])


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _resolve_current_ruleset_dir() -> Path:
    from msl.pipeline.ruleset_manager import read_current_ruleset

    ruleset = read_current_ruleset(RULES_BASE_DIR)
    if not ruleset:
        raise SystemExit(f"CURRENT ruleset not resolvable from {RULES_BASE_DIR / 'CURRENT.txt'}")
    return ruleset


def _resolve_ruleset_dir(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if p.exists() and p.is_dir():
            return p
        # Allow passing a ruleset id (folder name) too.
        p2 = RULES_BASE_DIR / Path(explicit).name
        if p2.exists() and p2.is_dir():
            return p2
        raise SystemExit(f"--ruleset-dir not found: {explicit}")
    return _resolve_current_ruleset_dir()


def _run_cmd(
    cmd: list[str],
    *,
    cwd: Path,
    stdout_path: Path,
    stderr_path: Path,
    env: dict[str, str] | None = None,
) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("w", encoding="utf-8") as f_out, stderr_path.open("w", encoding="utf-8") as f_err:
        p = subprocess.run(cmd, cwd=str(cwd), stdout=f_out, stderr=f_err, env=env)
    return int(p.returncode)


def _action_meta_base(*, action: str, run_id: str, ruleset_dir: Path | None, inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": action,
        "run_id": run_id,
        "timestamp_utc": _utc_now().isoformat().replace("+00:00", "Z"),
        "ruleset_dir": str(ruleset_dir) if ruleset_dir else "",
        "ruleset_id": ruleset_dir.name if ruleset_dir else "",
        "inputs": inputs,
        "python": sys.version,
        "cwd": str(REPO_ROOT),
    }


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _jsonl_read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def _validate_candidates_hard_fail(candidates_dir: Path) -> None:
    """
    Hard gate for promotion: candidate rows must be structurally valid.
    Policy (minimum):
    - Serial decode candidates must include non-empty example_serials and regex must match at least one example.
    - Attribute decode candidates must include a non-empty value_extraction dict.
    """
    import re as _re

    errors: list[dict[str, Any]] = []

    serial_path = candidates_dir / "SerialDecodeRule.candidates.jsonl"
    for obj in _jsonl_read(serial_path):
        if (obj.get("rule_type") or "decode") != "decode":
            continue
        brand = (obj.get("brand") or "").strip()
        style = (obj.get("style_name") or "").strip()
        rx_s = (obj.get("serial_regex") or "").strip()
        examples = obj.get("example_serials") or obj.get("examples") or []
        if not rx_s:
            errors.append({"type": "SerialDecodeRule", "brand": brand, "style_name": style, "issue": "missing_serial_regex"})
            continue
        try:
            rx = _re.compile(rx_s)
        except Exception as e:
            errors.append({"type": "SerialDecodeRule", "brand": brand, "style_name": style, "issue": f"bad_regex:{e}"})
            continue
        if not isinstance(examples, list) or not examples:
            errors.append({"type": "SerialDecodeRule", "brand": brand, "style_name": style, "issue": "missing_example_serials"})
            continue
        matched_any = False
        for ex in examples[:50]:
            if isinstance(ex, str) and rx.search(ex):
                matched_any = True
                break
        if not matched_any:
            errors.append({"type": "SerialDecodeRule", "brand": brand, "style_name": style, "issue": "examples_do_not_match_regex"})

    attr_path = candidates_dir / "AttributeDecodeRule.candidates.jsonl"
    for obj in _jsonl_read(attr_path):
        if (obj.get("rule_type") or "decode") != "decode":
            continue
        brand = (obj.get("brand") or "").strip()
        attr = (obj.get("attribute_name") or "").strip()
        ve = obj.get("value_extraction")
        if not isinstance(ve, dict) or not ve:
            errors.append({"type": "AttributeDecodeRule", "brand": brand, "attribute_name": attr, "issue": "missing_value_extraction"})

    if errors:
        raise SystemExit(
            "Promotion blocked: candidate validation failed. "
            f"Fix candidates and retry. First error: {errors[0]}"
        )


def _merge_candidates_dirs(
    *,
    primary_dir: Path,
    out_dir: Path,
    include_manual_additions: bool,
) -> Path:
    """
    Create a deterministic "effective candidates" directory.

    Policy:
    - Always include `primary_dir`.
    - Optionally include `data/rules_discovered/manual_additions/`.
    - If a manual candidate collides with a non-manual candidate by key, manual wins and the non-manual is dropped.
      - Serial key: (brand, style_name)
      - Attribute key: (brand, attribute_name, model_regex, equipment_types_key)
    - Output ordering: manual candidates first, then remaining primary candidates; both sorted stably.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    manual_dir = MANUAL_ADDITIONS_DIR if include_manual_additions else None

    def read_serial(dir_path: Path, is_manual: bool) -> list[tuple[bool, dict[str, Any]]]:
        p = dir_path / "SerialDecodeRule.candidates.jsonl"
        return [(is_manual, obj) for obj in _jsonl_read(p)]

    def read_attr(dir_path: Path, is_manual: bool) -> list[tuple[bool, dict[str, Any]]]:
        p = dir_path / "AttributeDecodeRule.candidates.jsonl"
        return [(is_manual, obj) for obj in _jsonl_read(p)]

    serial_items: list[tuple[bool, dict[str, Any]]] = []
    attr_items: list[tuple[bool, dict[str, Any]]] = []

    if manual_dir and manual_dir.exists():
        serial_items.extend(read_serial(manual_dir, True))
        attr_items.extend(read_attr(manual_dir, True))
    if primary_dir.exists():
        serial_items.extend(read_serial(primary_dir, False))
        attr_items.extend(read_attr(primary_dir, False))

    # Dedup policy: if manual exists for key, drop non-manual with same key.
    manual_serial_keys = {
        ((obj.get("brand") or "").strip(), (obj.get("style_name") or "").strip())
        for is_manual, obj in serial_items
        if is_manual
    }

    def _equipment_types_key(obj: dict[str, Any]) -> str:
        # Support legacy single-valued `equipment_type` in addition to `equipment_types`.
        et_list = obj.get("equipment_types")
        if et_list is None:
            et_list = []
        if not isinstance(et_list, list):
            et_list = []
        legacy = (obj.get("equipment_type") or "").strip()
        if legacy:
            et_list = list(et_list) + [legacy]
        cleaned = sorted({str(x).strip() for x in et_list if str(x).strip()})
        return ",".join(cleaned)

    manual_attr_keys = {
        (
            (obj.get("brand") or "").strip(),
            (obj.get("attribute_name") or "").strip(),
            (obj.get("model_regex") or "").strip(),
            _equipment_types_key(obj),
        )
        for is_manual, obj in attr_items
        if is_manual
    }

    def serial_key(obj: dict[str, Any]) -> tuple[str, str, str]:
        return (
            (obj.get("brand") or "").strip(),
            (obj.get("style_name") or "").strip(),
            (obj.get("serial_regex") or "").strip(),
        )

    def attr_key(obj: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            (obj.get("brand") or "").strip(),
            (obj.get("attribute_name") or "").strip(),
            (obj.get("model_regex") or "").strip(),
            _equipment_types_key(obj),
            (obj.get("source_url") or "").strip(),
        )

    serial_kept: list[tuple[bool, dict[str, Any]]] = []
    for is_manual, obj in serial_items:
        k = ((obj.get("brand") or "").strip(), (obj.get("style_name") or "").strip())
        if (not is_manual) and k in manual_serial_keys:
            continue
        serial_kept.append((is_manual, obj))

    attr_kept: list[tuple[bool, dict[str, Any]]] = []
    for is_manual, obj in attr_items:
        k = (
            (obj.get("brand") or "").strip(),
            (obj.get("attribute_name") or "").strip(),
            (obj.get("model_regex") or "").strip(),
            _equipment_types_key(obj),
        )
        if (not is_manual) and k in manual_attr_keys:
            continue
        attr_kept.append((is_manual, obj))

    # Write JSONL (manual first, then others).
    def write_jsonl(items: list[tuple[bool, dict[str, Any]]], path: Path, sort_fn) -> None:
        manual = [obj for is_manual, obj in items if is_manual]
        non = [obj for is_manual, obj in items if not is_manual]
        manual = sorted(manual, key=sort_fn)
        non = sorted(non, key=sort_fn)
        lines = [json.dumps(o, ensure_ascii=False) for o in (manual + non)]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    write_jsonl(serial_kept, out_dir / "SerialDecodeRule.candidates.jsonl", lambda o: serial_key(o))
    write_jsonl(attr_kept, out_dir / "AttributeDecodeRule.candidates.jsonl", lambda o: attr_key(o))

    # Brand normalize candidates: merge CSVs (union by (raw_make, canonical)).
    def read_brand_csv(path: Path) -> list[dict[str, str]]:
        if not path.exists():
            return []
        return _load_csv_rows(path)

    brand_rows: list[dict[str, str]] = []
    if manual_dir and manual_dir.exists():
        brand_rows.extend(read_brand_csv(manual_dir / "BrandNormalizeRule.candidates.csv"))
    brand_rows.extend(read_brand_csv(primary_dir / "BrandNormalizeRule.candidates.csv"))

    if brand_rows:
        seen: set[tuple[str, str]] = set()
        merged: list[dict[str, str]] = []
        for r in brand_rows:
            raw = (r.get("raw_make") or r.get("raw_make_normalized") or "").strip()
            canon = (r.get("canonical_brand") or r.get("suggested_brand") or "").strip()
            k = (raw, canon)
            if not raw or not canon:
                continue
            if k in seen:
                continue
            seen.add(k)
            merged.append(r)
        out_csv = out_dir / "BrandNormalizeRule.candidates.csv"
        # Preserve original header if possible; else write a stable minimal set.
        fieldnames = list(merged[0].keys()) if merged else ["raw_make", "canonical_brand"]
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in merged:
                w.writerow({k: r.get(k, "") for k in fieldnames})

    return out_dir


def _enrich_serial_candidates_with_examples(
    *,
    candidates_dir: Path,
    labeled_csv: Path,
    out_dir: Path,
    max_examples_per_rule: int = 5,
) -> Path:
    """
    Deterministically enrich SerialDecodeRule candidates by adding example serials when missing.

    Phase 3 mining can produce candidates without example values. This helper derives examples directly
    from the labeled dataset used for mining/audit:
    - filter rows to the candidate brand
    - normalize serials
    - keep the first N unique matches in sorted order

    If a candidate has no matching examples in the labeled dataset, this fails (promotion should not proceed).
    """
    import shutil
    import re as _re

    from msl.decoder.normalize import normalize_brand, normalize_serial
    from msl.pipeline.phase3_baseline import infer_column_map

    if not labeled_csv.exists():
        raise SystemExit(f"Missing labeled dataset: {labeled_csv}")
    if not candidates_dir.exists():
        raise SystemExit(f"Missing candidates dir: {candidates_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy non-candidate files through for completeness.
    for p in candidates_dir.iterdir():
        if p.is_file() and p.name not in {"SerialDecodeRule.candidates.jsonl"}:
            shutil.copy2(p, out_dir / p.name)

    # Load labeled dataset once.
    with labeled_csv.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        fns = reader.fieldnames or []
        cmap = infer_column_map(fns)
        if not cmap.make or not cmap.serial:
            raise SystemExit("Cannot enrich candidates: labeled CSV missing Make/Serial columns")
        rows = list(reader)

    # Index candidate brand -> matching serials.
    serials_by_brand: dict[str, set[str]] = {}
    for row in rows:
        make_raw = (row.get(cmap.make) or "").strip()
        brand = normalize_brand(make_raw)
        serial_raw = (row.get(cmap.serial) or "").strip()
        s = normalize_serial(serial_raw)
        if not brand or not s:
            continue
        serials_by_brand.setdefault(brand, set()).add(s)

    src_path = candidates_dir / "SerialDecodeRule.candidates.jsonl"
    dst_path = out_dir / "SerialDecodeRule.candidates.jsonl"
    out_lines: list[str] = []
    for obj in _jsonl_read(src_path):
        if (obj.get("rule_type") or "decode") != "decode":
            out_lines.append(json.dumps(obj, ensure_ascii=False))
            continue
        if obj.get("example_serials") or obj.get("examples"):
            out_lines.append(json.dumps(obj, ensure_ascii=False))
            continue

        brand = (obj.get("brand") or "").strip()
        rx_s = (obj.get("serial_regex") or "").strip()
        if not brand or not rx_s:
            out_lines.append(json.dumps(obj, ensure_ascii=False))
            continue

        try:
            rx = _re.compile(rx_s)
        except Exception:
            out_lines.append(json.dumps(obj, ensure_ascii=False))
            continue

        candidates = sorted(serials_by_brand.get(brand, set()))
        examples: list[str] = []
        for s in candidates:
            if rx.search(s):
                examples.append(s)
                if len(examples) >= max_examples_per_rule:
                    break

        if not examples:
            raise SystemExit(
                "Cannot enrich serial candidate with examples from labeled dataset. "
                f"brand={brand} serial_regex={rx_s}"
            )

        obj2 = dict(obj)
        obj2["example_serials"] = examples
        out_lines.append(json.dumps(obj2, ensure_ascii=False))

    dst_path.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")
    return out_dir


def action_ruleset_validate(args: argparse.Namespace) -> int:
    action = "ruleset.validate"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_dir = _ensure_dir(REPORTS_BASE_DIR / run_id / action)

    ruleset_dir = _resolve_ruleset_dir(args.ruleset_dir)

    meta = _action_meta_base(
        action=action,
        run_id=run_id,
        ruleset_dir=ruleset_dir,
        inputs={"ruleset_dir": str(ruleset_dir)},
    )
    _write_json(run_dir / "meta.json", meta)

    # Capture `msl report` output (human-friendly counts).
    cmd = [sys.executable, "-m", "msl", "report", "--ruleset-dir", str(ruleset_dir)]
    rc = _run_cmd(
        cmd,
        cwd=REPO_ROOT,
        stdout_path=run_dir / "stdout.log",
        stderr_path=run_dir / "stderr.log",
    )
    if rc != 0:
        raise SystemExit(f"{action} failed (msl report). See: {run_dir}")

    # Structural validation issues (machine-readable).
    from msl.decoder.io import load_attribute_rules_csv, load_serial_rules_csv
    from msl.decoder.equipment_type import load_equipment_type_vocab
    from msl.decoder.validate import validate_attribute_rules, validate_serial_rules

    serial_rules = load_serial_rules_csv(ruleset_dir / "SerialDecodeRule.csv")
    _serial_acc, serial_issues = validate_serial_rules(serial_rules)

    attr_issues: list[Any] = []
    attr_rows_n = 0
    attr_path = ruleset_dir / "AttributeDecodeRule.csv"
    if attr_path.exists():
        attr_rules = load_attribute_rules_csv(attr_path)
        attr_rows_n = len(attr_rules)
        _attr_acc, attr_issues = validate_attribute_rules(attr_rules)

    # Warn-only: rules may declare equipment types not present in the canonical vocab.
    vocab = load_equipment_type_vocab(REPO_ROOT / "data" / "static" / "equipment_types.csv")
    vocab_keys = set(vocab.keys())
    type_warnings: list[dict[str, Any]] = []
    for r in serial_rules:
        for t in (r.equipment_types or []):
            if t and t not in vocab_keys:
                type_warnings.append({"type": "SerialDecodeRule", "brand": r.brand, "key": r.style_name, "issue": f"unknown_equipment_type:{t}"})
    if attr_path.exists():
        for r in attr_rules:
            for t in (r.equipment_types or []):
                if t and t not in vocab_keys:
                    type_warnings.append({"type": "AttributeDecodeRule", "brand": r.brand, "key": r.attribute_name, "issue": f"unknown_equipment_type:{t}"})

    issues_path = run_dir / "ruleset_issues.jsonl"
    with issues_path.open("w", encoding="utf-8") as f:
        for i in serial_issues:
            f.write(json.dumps({"severity": "error", "type": i.rule_type, "brand": i.brand, "key": i.style_name, "issue": i.issue}, ensure_ascii=False) + "\n")
        for i in attr_issues:
            f.write(json.dumps({"severity": "error", "type": i.rule_type, "brand": i.brand, "key": i.style_name, "issue": i.issue}, ensure_ascii=False) + "\n")
        for w in type_warnings:
            f.write(json.dumps({"severity": "warning", **w}, ensure_ascii=False) + "\n")

    # Quick counts as JSON.
    counts = {
        "ruleset_id": ruleset_dir.name,
        "serial": {"issues_n": len(serial_issues), "rows_n": len(serial_rules)},
        "attribute": {"issues_n": len(attr_issues), "rows_n": attr_rows_n},
        "warnings": {"equipment_types_unknown_n": len(type_warnings)},
    }
    _write_json(run_dir / "ruleset_counts.json", counts)

    return 0


def action_decode_run(args: argparse.Namespace) -> int:
    action = "decode.run"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_dir = _ensure_dir(REPORTS_BASE_DIR / run_id / action)

    ruleset_dir = _resolve_ruleset_dir(args.ruleset_dir)
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input CSV: {input_path}")

    out_decoded = run_dir / "decoded.csv"
    out_attrs = run_dir / "attributes_long.csv"

    meta = _action_meta_base(
        action=action,
        run_id=run_id,
        ruleset_dir=ruleset_dir,
        inputs={
            "input": str(input_path),
            "min_manufacture_year": int(getattr(args, "min_manufacture_year", 1980)),
        },
    )
    _write_json(run_dir / "meta.json", meta)

    cmd = [
        sys.executable,
        "-m",
        "msl",
        "decode",
        "--ruleset-dir",
        str(ruleset_dir),
        "--input",
        str(input_path),
        "--output",
        str(out_decoded),
        "--attributes-output",
        str(out_attrs),
        "--min-manufacture-year",
        str(int(getattr(args, "min_manufacture_year", 1980))),
    ]
    rc = _run_cmd(cmd, cwd=REPO_ROOT, stdout_path=run_dir / "stdout.log", stderr_path=run_dir / "stderr.log")
    if rc != 0:
        raise SystemExit(f"{action} failed. See: {run_dir}")

    # Summary counts.
    rows = _load_csv_rows(out_decoded)
    by_status: dict[str, int] = {}
    by_brand: dict[str, dict[str, int]] = {}
    for r in rows:
        status = (r.get("DecodeStatus") or "").strip() or "Unknown"
        brand = (r.get("DetectedBrand") or "").strip() or "UNKNOWN"
        by_status[status] = by_status.get(status, 0) + 1
        b = by_brand.setdefault(brand, {})
        b[status] = b.get(status, 0) + 1
    _write_json(run_dir / "decode_summary.json", {"rows": len(rows), "by_status": by_status, "by_brand": by_brand})

    return 0


def _has_labeled_year(input_path: Path) -> bool:
    with input_path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        r = csv.DictReader(f)
        fns = r.fieldnames or []
    # Mirror phase3_baseline inference candidates.
    norm = {re.sub(r"\s+", "", (c or "").lower()) for c in fns}
    return ("knownmanufactureyear" in norm) or ("manuf.year" in norm) or ("installyear" in norm)


def action_eval_truth(args: argparse.Namespace) -> int:
    action = "eval.truth"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_dir = _ensure_dir(REPORTS_BASE_DIR / run_id / action)

    ruleset_dir = _resolve_ruleset_dir(args.ruleset_dir)
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input CSV: {input_path}")

    meta = _action_meta_base(action=action, run_id=run_id, ruleset_dir=ruleset_dir, inputs={"input": str(input_path)})
    _write_json(run_dir / "meta.json", meta)

    cmd = [
        sys.executable,
        "-m",
        "msl",
        "phase3-baseline",
        "--input",
        str(input_path),
        "--ruleset-dir",
        str(ruleset_dir),
        "--run-id",
        action,
        "--out-dir",
        str(REPORTS_BASE_DIR / run_id),
    ]
    rc = _run_cmd(cmd, cwd=REPO_ROOT, stdout_path=run_dir / "stdout.log", stderr_path=run_dir / "stderr.log")
    if rc != 0:
        raise SystemExit(f"{action} failed. See: {run_dir}")

    # phase3-baseline writes artifacts to data/reports/<run_id>/eval.truth/
    out_dir = REPORTS_BASE_DIR / run_id / action
    # Point CURRENT_BASELINE to this run if requested by workflow wrapper (set by caller).
    if getattr(args, "update_baseline_pointer", False):
        _ensure_dir(REPORTS_BASE_DIR)
        _write_text(REPORTS_BASE_DIR / "CURRENT_BASELINE.txt", f"{run_id}\n")

    # Small wrapper summary.
    summary_path = out_dir / "phase3_baseline_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    lines = [
        f"# Truth Evaluation — {run_id}\n\n",
        f"- Input: `{input_path}`\n",
        f"- Ruleset: `{ruleset_dir.name}`\n",
        "\n## Outputs\n",
    ]
    outputs = (summary.get("outputs") or {}) if isinstance(summary, dict) else {}
    for k in [
        "baseline_scorecard",
        "baseline_scorecard_by_type",
        "next_targets_markdown",
        "next_targets_by_type_markdown",
        "training_data_profile",
    ]:
        if k in outputs:
            lines.append(f"- {k}: `{outputs[k]}`\n")
    _write_text(out_dir / "truth_summary.md", "".join(lines))

    return 0


def action_eval_coverage(args: argparse.Namespace) -> int:
    action = "eval.coverage"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_dir = _ensure_dir(REPORTS_BASE_DIR / run_id / action)

    ruleset_dir = _resolve_ruleset_dir(args.ruleset_dir)
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input CSV: {input_path}")

    meta = _action_meta_base(action=action, run_id=run_id, ruleset_dir=ruleset_dir, inputs={"input": str(input_path)})
    _write_json(run_dir / "meta.json", meta)

    if _has_labeled_year(input_path):
        # Delegate to truth evaluation (coverage is part of scorecards).
        args2 = argparse.Namespace(**vars(args))
        setattr(args2, "run_id", run_id)
        setattr(args2, "tag", args.tag)
        setattr(args2, "update_baseline_pointer", getattr(args, "update_baseline_pointer", False))
        return action_eval_truth(args2)

    # Unlabeled: use gap-report.
    out_csv = run_dir / "gap_report.csv"
    cmd = [
        sys.executable,
        "-m",
        "msl",
        "gap-report",
        "--ruleset-dir",
        str(ruleset_dir),
        "--input",
        str(input_path),
        "--output",
        str(out_csv),
    ]
    rc = _run_cmd(cmd, cwd=REPO_ROOT, stdout_path=run_dir / "stdout.log", stderr_path=run_dir / "stderr.log")
    if rc != 0:
        raise SystemExit(f"{action} failed. See: {run_dir}")

    summary_path = out_csv.with_suffix(".summary.json")
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    totals = summary.get("totals_by_reason") if isinstance(summary, dict) else {}
    lines = [
        f"# Coverage Report (Unlabeled) — {run_id}\n\n",
        f"- Input: `{input_path}`\n",
        f"- Ruleset: `{ruleset_dir.name}`\n\n",
        "## Totals by Reason\n",
    ]
    if isinstance(totals, dict):
        for k, v in sorted(totals.items(), key=lambda kv: (-int(kv[1]), kv[0])):
            lines.append(f"- {k}: {v}\n")
    _write_text(run_dir / "coverage_report.md", "".join(lines))
    return 0


def action_mine_rules(args: argparse.Namespace) -> int:
    action = "mine.rules"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_dir = _ensure_dir(REPORTS_BASE_DIR / run_id / action)

    ruleset_dir = _resolve_ruleset_dir(args.ruleset_dir)
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input CSV: {input_path}")

    meta = _action_meta_base(
        action=action,
        run_id=run_id,
        ruleset_dir=ruleset_dir,
        inputs={
            "input": str(input_path),
            "min_brand_similarity": float(args.min_brand_similarity),
            "min_serial_support": int(args.min_serial_support),
            "min_model_support": int(args.min_model_support),
            "min_model_match_rate": float(args.min_model_match_rate),
            "min_model_train_accuracy": float(args.min_model_train_accuracy),
            "min_model_holdout_accuracy": float(args.min_model_holdout_accuracy),
            "capacity_tolerance_tons": float(args.capacity_tolerance_tons),
        },
    )
    _write_json(run_dir / "meta.json", meta)

    # Candidates go to data/rules_discovered/<run_id>/candidates
    cmd = [
        sys.executable,
        "-m",
        "msl",
        "phase3-mine",
        "--input",
        str(input_path),
        "--ruleset-dir",
        str(ruleset_dir),
        "--run-id",
        run_id,
        "--out-candidates-dir",
        str(DISCOVERED_BASE_DIR),
        "--out-reports-dir",
        str(REPORTS_BASE_DIR),
    ]
    cmd += ["--min-brand-similarity", str(float(args.min_brand_similarity))]
    cmd += ["--min-serial-support", str(int(args.min_serial_support))]
    cmd += ["--min-model-support", str(int(args.min_model_support))]
    cmd += ["--min-model-match-rate", str(float(args.min_model_match_rate))]
    cmd += ["--min-model-train-accuracy", str(float(args.min_model_train_accuracy))]
    cmd += ["--min-model-holdout-accuracy", str(float(args.min_model_holdout_accuracy))]
    cmd += ["--capacity-tolerance-tons", str(float(args.capacity_tolerance_tons))]

    rc = _run_cmd(cmd, cwd=REPO_ROOT, stdout_path=run_dir / "stdout.log", stderr_path=run_dir / "stderr.log")
    if rc != 0:
        raise SystemExit(f"{action} failed. See: {run_dir}")

    cand_dir = DISCOVERED_BASE_DIR / run_id / "candidates"
    _write_json(run_dir / "candidates_ref.json", {"candidates_dir": str(cand_dir)})
    _write_text(run_dir / "mine_summary.md", f"# Mined Candidates — {run_id}\n\n- Candidates: `{cand_dir}`\n")
    return 0


def action_eval_candidates(args: argparse.Namespace) -> int:
    action = "eval.candidates"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_dir = _ensure_dir(REPORTS_BASE_DIR / run_id / action)

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input CSV: {input_path}")
    candidates_dir = Path(args.candidates_dir)
    if not candidates_dir.exists():
        raise SystemExit(f"Missing candidates dir: {candidates_dir}")

    meta = _action_meta_base(
        action=action,
        run_id=run_id,
        ruleset_dir=_resolve_ruleset_dir(args.ruleset_dir),
        inputs={"input": str(input_path), "candidates_dir": str(candidates_dir), "capacity_tolerance_tons": float(args.capacity_tolerance_tons)},
    )
    _write_json(run_dir / "meta.json", meta)

    cmd = [
        sys.executable,
        "-m",
        "msl",
        "phase3-audit",
        "--input",
        str(input_path),
        "--candidates-dir",
        str(candidates_dir),
        "--run-id",
        action,
        "--out-dir",
        str(REPORTS_BASE_DIR / run_id),
        "--capacity-tolerance-tons",
        str(float(args.capacity_tolerance_tons)),
    ]
    rc = _run_cmd(cmd, cwd=REPO_ROOT, stdout_path=run_dir / "stdout.log", stderr_path=run_dir / "stderr.log")
    if rc != 0:
        raise SystemExit(f"{action} failed. See: {run_dir}")

    _write_text(
        run_dir / "candidates_audit_summary.md",
        f"# Candidate Audit — {run_id}\n\n- Audit outputs: `{REPORTS_BASE_DIR / run_id / action}`\n",
    )
    return 0


def action_ruleset_promote(args: argparse.Namespace) -> int:
    action = "ruleset.promote"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_dir = _ensure_dir(REPORTS_BASE_DIR / run_id / action)

    base_ruleset_dir = _resolve_ruleset_dir(args.base_ruleset_dir)
    candidates_dir = Path(args.candidates_dir)
    if not candidates_dir.exists():
        raise SystemExit(f"Missing candidates dir: {candidates_dir}")

    include_manual = not bool(getattr(args, "no_manual_additions", False))
    effective_candidates_dir = candidates_dir
    if include_manual and MANUAL_ADDITIONS_DIR.exists():
        effective_candidates_dir = _merge_candidates_dirs(
            primary_dir=candidates_dir,
            out_dir=(REPORTS_BASE_DIR / run_id / action / "candidates_effective"),
            include_manual_additions=True,
        )
    candidates_dir = effective_candidates_dir

    # Hard gate: malformed candidates block promotion.
    _validate_candidates_hard_fail(candidates_dir)

    new_ruleset_id = args.new_ruleset_id
    if not new_ruleset_id:
        raise SystemExit("--new-ruleset-id is required (e.g., 2026-01-28-sdi-master-v4)")
    new_ruleset_id = _sanitize_token(new_ruleset_id)

    meta = _action_meta_base(
        action=action,
        run_id=run_id,
        ruleset_dir=base_ruleset_dir,
        inputs={
            "base_ruleset_dir": str(base_ruleset_dir),
            "candidates_dir": str(candidates_dir),
            "new_ruleset_id": new_ruleset_id,
            "audit_dir": str(args.audit_dir or ""),
            "include_manual_additions": bool(include_manual),
        },
    )
    _write_json(run_dir / "meta.json", meta)

    audit_dir = str(args.audit_dir or "")
    if getattr(args, "promote_all", False):
        audit_dir = ""

    cmd = [
        sys.executable,
        "-m",
        "msl",
        "phase3-promote",
        "--base-ruleset-dir",
        str(base_ruleset_dir),
        "--candidates-dir",
        str(candidates_dir),
        "--run-id",
        new_ruleset_id,
        "--out-dir",
        str(RULES_BASE_DIR),
    ]
    # Audit gating is optional. If provided, `msl phase3-promote` will only promote candidates
    # that pass its thresholds. If omitted, it will promote all candidates (still deduped + safety-checked).
    if audit_dir:
        cmd += ["--audit-dir", str(Path(audit_dir))]
    if args.no_cleanup:
        cmd += ["--no-cleanup"]
    rc = _run_cmd(cmd, cwd=REPO_ROOT, stdout_path=run_dir / "stdout.log", stderr_path=run_dir / "stderr.log")
    if rc != 0:
        raise SystemExit(f"{action} failed (msl phase3-promote). See: {run_dir}")

    new_ruleset_dir = RULES_BASE_DIR / new_ruleset_id

    # Apply post-promote manual fix registry (supported today).
    fix_stdout = run_dir / "post_promote_fix_stdout.log"
    fix_stderr = run_dir / "post_promote_fix_stderr.log"
    fix_cmd = [sys.executable, "scripts/apply_manual_serial_fixes.py", "--ruleset-dir", str(new_ruleset_dir)]
    rc2 = _run_cmd(fix_cmd, cwd=REPO_ROOT, stdout_path=fix_stdout, stderr_path=fix_stderr)
    if rc2 != 0:
        raise SystemExit(f"{action} failed (apply_manual_serial_fixes). See: {run_dir}")

    # Keep ruleset folders clean: move backups into the promotion run folder.
    backup_in_ruleset = new_ruleset_dir / "SerialDecodeRule.csv.before_manual_fixes"
    if backup_in_ruleset.exists():
        backup_dest = run_dir / backup_in_ruleset.name
        backup_dest.parent.mkdir(parents=True, exist_ok=True)
        backup_dest.write_bytes(backup_in_ruleset.read_bytes())
        backup_in_ruleset.unlink()

    # Ruleset diff summary (always).
    diff_json, diff_md = _ruleset_diff(base_ruleset_dir, new_ruleset_dir)
    _write_json(run_dir / "ruleset_diff.json", diff_json)
    _write_text(run_dir / "ruleset_diff.md", diff_md)

    _write_json(run_dir / "promoted_ruleset_ref.json", {"ruleset_id": new_ruleset_id, "ruleset_dir": str(new_ruleset_dir)})
    return 0


def _read_scorecard(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = _load_csv_rows(path)
    out: dict[str, dict[str, str]] = {}
    for r in rows:
        b = (r.get("Brand") or "").strip()
        if b:
            out[b] = r
    return out


def _write_delta_scorecard(before: Path, after: Path, out_csv: Path) -> None:
    b = _read_scorecard(before)
    a = _read_scorecard(after)
    brands = sorted(set(b) | set(a))
    fields = [
        "Brand",
        "Before_YearCoveragePct",
        "After_YearCoveragePct",
        "Delta_YearCoveragePct",
        "Before_YearAccuracyPct",
        "After_YearAccuracyPct",
        "Delta_YearAccuracyPct",
    ]
    out_rows = []
    for brand in brands:
        br = b.get(brand, {})
        ar = a.get(brand, {})
        def fnum(x: str) -> float | None:
            t = (x or "").strip()
            if not t:
                return None
            try:
                return float(t)
            except Exception:
                return None
        bc = fnum(br.get("YearCoveragePct", ""))
        ac = fnum(ar.get("YearCoveragePct", ""))
        ba = fnum(br.get("YearAccuracyPct", ""))
        aa = fnum(ar.get("YearAccuracyPct", ""))
        out_rows.append(
            {
                "Brand": brand,
                "Before_YearCoveragePct": br.get("YearCoveragePct", ""),
                "After_YearCoveragePct": ar.get("YearCoveragePct", ""),
                "Delta_YearCoveragePct": f"{(ac - bc):.1f}" if (ac is not None and bc is not None) else "",
                "Before_YearAccuracyPct": br.get("YearAccuracyPct", ""),
                "After_YearAccuracyPct": ar.get("YearAccuracyPct", ""),
                "Delta_YearAccuracyPct": f"{(aa - ba):.1f}" if (aa is not None and ba is not None) else "",
            }
        )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    return True


def _read_csv_keyed(path: Path, key_fields: list[str]) -> dict[tuple[str, ...], dict[str, str]]:
    if not path.exists():
        return {}
    rows = _load_csv_rows(path)
    out: dict[tuple[str, ...], dict[str, str]] = {}
    for r in rows:
        key = tuple((r.get(k) or "").strip() for k in key_fields)
        out[key] = r
    return out


def _ruleset_diff(base_ruleset: Path, new_ruleset: Path) -> tuple[dict[str, Any], str]:
    """
    Deterministically summarize how a promotion changed a ruleset.

    This is not a full semantic diff; it compares row identity keys per file and reports adds/removes.
    """
    files = {
        "SerialDecodeRule.csv": ["brand", "rule_type", "style_name", "serial_regex", "source_url"],
        "AttributeDecodeRule.csv": ["brand", "rule_type", "attribute_name", "model_regex", "source_url"],
        "BrandNormalizeRule.csv": ["raw_make_normalized", "canonical_brand", "source_url"],
    }

    diff: dict[str, Any] = {
        "base_ruleset_id": base_ruleset.name,
        "new_ruleset_id": new_ruleset.name,
        "base_ruleset_dir": str(base_ruleset),
        "new_ruleset_dir": str(new_ruleset),
        "files": {},
    }

    md_lines: list[str] = []
    md_lines.append(f"# Ruleset Diff — {base_ruleset.name} → {new_ruleset.name}\n\n")

    for fname, keys in files.items():
        base_path = base_ruleset / fname
        new_path = new_ruleset / fname
        base_rows = _read_csv_keyed(base_path, keys)
        new_rows = _read_csv_keyed(new_path, keys)

        base_set = set(base_rows.keys())
        new_set = set(new_rows.keys())
        added = sorted(new_set - base_set)
        removed = sorted(base_set - new_set)

        diff["files"][fname] = {
            "file": fname,
            "key_fields": keys,
            "base_rows_n": len(base_set),
            "new_rows_n": len(new_set),
            "added_n": len(added),
            "removed_n": len(removed),
        }

        md_lines.append(f"## {fname}\n")
        md_lines.append(f"- base rows: {len(base_set)}\n")
        md_lines.append(f"- new rows: {len(new_set)}\n")
        md_lines.append(f"- added: {len(added)}\n")
        md_lines.append(f"- removed: {len(removed)}\n\n")

        if added:
            md_lines.append("### Added (sample)\n")
            for key in added[:25]:
                md_lines.append(f"- {key}\n")
            if len(added) > 25:
                md_lines.append(f"- ... and {len(added) - 25} more\n")
            md_lines.append("\n")

    return diff, "".join(md_lines)


def action_workflow_improve(args: argparse.Namespace) -> int:
    action = "workflow.improve"
    run_id = args.run_id or _default_run_id(action, args.tag)
    run_root = _ensure_dir(REPORTS_BASE_DIR / run_id)

    ruleset_dir_before = _resolve_ruleset_dir(args.ruleset_dir)
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing input CSV: {input_path}")

    # 1) ruleset.validate (current)
    action_ruleset_validate(argparse.Namespace(**{**vars(args), "run_id": run_id, "tag": args.tag, "ruleset_dir": str(ruleset_dir_before)}))

    # 2) decode.run
    action_decode_run(argparse.Namespace(**{**vars(args), "run_id": run_id, "tag": args.tag, "ruleset_dir": str(ruleset_dir_before)}))

    # 3-4) eval.truth (labeled expected)
    if not _has_labeled_year(input_path):
        raise SystemExit("workflow.improve requires a labeled dataset (KnownManufactureYear column).")

    truth_args = argparse.Namespace(**{**vars(args), "run_id": run_id, "tag": args.tag, "ruleset_dir": str(ruleset_dir_before), "update_baseline_pointer": True})
    action_eval_truth(truth_args)

    score_before = run_root / "eval.truth" / "baseline_decoder_scorecard.csv"
    _copy_if_exists(run_root / "eval.truth" / "next_targets.md", run_root / "NEXT_TARGETS.md")
    _copy_if_exists(run_root / "eval.truth" / "next_targets_by_type.md", run_root / "NEXT_TARGETS_BY_TYPE.md")

    # 5) mine.rules
    action_mine_rules(argparse.Namespace(**{**vars(args), "run_id": run_id, "tag": args.tag, "ruleset_dir": str(ruleset_dir_before)}))
    mined_candidates_dir = DISCOVERED_BASE_DIR / run_id / "candidates"

    # Always build an "effective candidates" directory for reporting and (optional) promotion.
    include_manual = not bool(getattr(args, "no_manual_additions", False))
    effective_candidates_dir = _merge_candidates_dirs(
        primary_dir=mined_candidates_dir,
        out_dir=(run_root / "candidates_effective"),
        include_manual_additions=include_manual,
    )

    # 6) eval.candidates
    action_eval_candidates(
        argparse.Namespace(
            **{
                **vars(args),
                "run_id": run_id,
                "tag": args.tag,
                "ruleset_dir": str(ruleset_dir_before),
                "candidates_dir": str(effective_candidates_dir),
            }
        )
    )

    promoted_ruleset_id = ""
    if args.promote:
        # 7) ruleset.promote
        if not args.new_ruleset_id:
            raise SystemExit("--new-ruleset-id is required when using --promote")
        promote_candidates_dir = effective_candidates_dir
        if getattr(args, "promote_all", False):
            # Enrich candidates to satisfy promotion gates (example_serials required for serial decode rules).
            enriched_dir = run_root / "candidates_enriched"
            promote_candidates_dir = _enrich_serial_candidates_with_examples(
                candidates_dir=effective_candidates_dir,
                labeled_csv=input_path,
                out_dir=enriched_dir,
            )

        promote_args = argparse.Namespace(
            **{
                **vars(args),
                "run_id": run_id,
                "tag": args.tag,
                "base_ruleset_dir": str(ruleset_dir_before),
                "candidates_dir": str(promote_candidates_dir),
                # If --promote-all is set, skip audit gating and promote all candidates.
                "audit_dir": ("" if getattr(args, "promote_all", False) else str(REPORTS_BASE_DIR / run_id / "eval.candidates")),
            }
        )
        action_ruleset_promote(promote_args)
        promoted_ruleset_id = _sanitize_token(args.new_ruleset_id)

        # 8) re-run truth after promotion, compute delta
        ruleset_dir_after = RULES_BASE_DIR / promoted_ruleset_id
        truth_after_args = argparse.Namespace(
            **{
                **vars(args),
                "run_id": run_id,
                "tag": args.tag,
                "ruleset_dir": str(ruleset_dir_after),
                "update_baseline_pointer": True,
            }
        )
        # Reuse same action dir for after? Keep separate.
        # Run baseline into eval.truth_after/
        action2 = "eval.truth_after"
        run_dir2 = _ensure_dir(REPORTS_BASE_DIR / run_id / action2)
        cmd = [
            sys.executable,
            "-m",
            "msl",
            "phase3-baseline",
            "--input",
            str(input_path),
            "--ruleset-dir",
            str(ruleset_dir_after),
            "--run-id",
            action2,
            "--out-dir",
            str(REPORTS_BASE_DIR / run_id),
        ]
        _run_cmd(cmd, cwd=REPO_ROOT, stdout_path=run_dir2 / "stdout.log", stderr_path=run_dir2 / "stderr.log")
        score_after = run_root / action2 / "baseline_decoder_scorecard.csv"
        delta_csv = run_root / "delta_scorecard.csv"
        _write_delta_scorecard(score_before, score_after, delta_csv)
        _copy_if_exists(run_root / action2 / "next_targets.md", run_root / "NEXT_TARGETS_AFTER.md")
        _copy_if_exists(run_root / action2 / "next_targets_by_type.md", run_root / "NEXT_TARGETS_BY_TYPE_AFTER.md")

        # Promotion diff summary (always write for promoted workflow runs).
        diff_json, diff_md = _ruleset_diff(ruleset_dir_before, ruleset_dir_after)
        _write_json(run_root / "RULESET_DIFF.json", diff_json)
        _write_text(run_root / "RULESET_DIFF.md", diff_md)

    # Consolidated workflow report.
    lines = [
        f"# Workflow Improve Report — {run_id}\n\n",
        f"- Input: `{input_path}`\n",
        f"- Ruleset (before): `{ruleset_dir_before.name}`\n",
        f"- Promote: `{str(bool(args.promote)).lower()}`\n",
    ]
    if promoted_ruleset_id:
        lines.append(f"- Ruleset (after): `{promoted_ruleset_id}`\n")
    lines.append("\n## Artifacts\n")
    for a in ["ruleset.validate", "decode.run", "eval.truth", "mine.rules", "eval.candidates", "ruleset.promote", "eval.truth_after"]:
        p = run_root / a
        if p.exists():
            lines.append(f"- `{a}`: `{p}`\n")
    if (run_root / "delta_scorecard.csv").exists():
        lines.append(f"- delta_scorecard: `{run_root / 'delta_scorecard.csv'}`\n")
    if (run_root / "NEXT_TARGETS.md").exists():
        lines.append(f"- next_targets: `{run_root / 'NEXT_TARGETS.md'}`\n")
    if (run_root / "NEXT_TARGETS_AFTER.md").exists():
        lines.append(f"- next_targets_after: `{run_root / 'NEXT_TARGETS_AFTER.md'}`\n")
    if (run_root / "RULESET_DIFF.md").exists():
        lines.append(f"- ruleset_diff: `{run_root / 'RULESET_DIFF.md'}`\n")
    _write_text(run_root / "WORKFLOW_REPORT.md", "".join(lines))

    # Update CURRENT_RUN pointer.
    _ensure_dir(REPORTS_BASE_DIR)
    _write_text(REPORTS_BASE_DIR / "CURRENT_RUN.txt", f"{run_id}\n")

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="actions", description="Action-driven workflow wrapper for model-serial-lookup")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--run-id", default="", help="Run folder name under data/reports (default: autogenerated)")
        sp.add_argument("--tag", default="default", help="Free-form tag for run-id generation (default: default)")
        sp.add_argument("--ruleset-dir", default="", help="Ruleset dir or ruleset id (defaults to CURRENT)")

    rsv = sub.add_parser("ruleset.validate", help="Resolve CURRENT ruleset, validate, and summarize")
    add_common(rsv)
    rsv.set_defaults(func=action_ruleset_validate)

    dec = sub.add_parser("decode.run", help="Run engine decode on a dataset")
    add_common(dec)
    dec.add_argument("--input", required=True, help="Input asset CSV")
    dec.add_argument("--min-manufacture-year", type=int, default=1980)
    dec.set_defaults(func=action_decode_run)

    cov = sub.add_parser("eval.coverage", help="Coverage report (labeled routes to eval.truth)")
    add_common(cov)
    cov.add_argument("--input", required=True, help="Input asset CSV")
    cov.set_defaults(func=action_eval_coverage)

    truth = sub.add_parser("eval.truth", help="Truth evaluation on labeled dataset (baseline scorecards)")
    add_common(truth)
    truth.add_argument("--input", required=True, help="Labeled asset CSV")
    truth.set_defaults(func=action_eval_truth)

    mine = sub.add_parser("mine.rules", help="Mine candidate rules from labeled dataset")
    add_common(mine)
    mine.add_argument("--input", required=True, help="Labeled asset CSV")
    mine.add_argument("--min-brand-similarity", type=float, default=0.90)
    mine.add_argument("--min-serial-support", type=int, default=50)
    mine.add_argument("--min-model-support", type=int, default=50)
    mine.add_argument("--min-model-match-rate", type=float, default=0.50)
    mine.add_argument("--min-model-train-accuracy", type=float, default=0.95)
    mine.add_argument("--min-model-holdout-accuracy", type=float, default=0.95)
    mine.add_argument("--capacity-tolerance-tons", type=float, default=0.5)
    mine.set_defaults(func=action_mine_rules)

    audit = sub.add_parser("eval.candidates", help="Audit mined candidates against labeled dataset")
    add_common(audit)
    audit.add_argument("--input", required=True, help="Labeled asset CSV")
    audit.add_argument("--candidates-dir", required=True, help="Candidates dir (contains *.candidates.* files)")
    audit.add_argument("--capacity-tolerance-tons", type=float, default=0.5)
    audit.set_defaults(func=action_eval_candidates)

    promote = sub.add_parser("ruleset.promote", help="Promote candidates into a new ruleset folder")
    promote.add_argument("--run-id", default="", help="Run folder name under data/reports (default: autogenerated)")
    promote.add_argument("--tag", default="default")
    promote.add_argument("--base-ruleset-dir", default="", help="Base ruleset dir or ruleset id (defaults to CURRENT)")
    promote.add_argument("--candidates-dir", required=True, help="Candidates dir")
    promote.add_argument("--audit-dir", default="", help="Optional audit dir")
    promote.add_argument("--new-ruleset-id", required=True, help="New ruleset folder name under data/rules_normalized")
    promote.add_argument(
        "--promote-all",
        action="store_true",
        help="Promote all candidates (skip audit gating even if --audit-dir is provided)",
    )
    promote.add_argument(
        "--no-manual-additions",
        action="store_true",
        help="Do not include data/rules_discovered/manual_additions during promotion",
    )
    promote.add_argument("--no-cleanup", action="store_true", help="Skip ruleset cleanup in msl phase3-promote")
    promote.set_defaults(func=action_ruleset_promote)

    wf = sub.add_parser("workflow.improve", help="Run validate→decode→truth→mine→audit→(optional promote)→truth delta")
    add_common(wf)
    wf.add_argument("--input", required=True, help="Labeled asset CSV")
    wf.add_argument("--min-manufacture-year", type=int, default=1980)
    wf.add_argument("--promote", action="store_true", help="Promote passing candidates into a new ruleset")
    wf.add_argument(
        "--promote-all",
        action="store_true",
        help="Promote all candidates (skip audit gating)",
    )
    wf.add_argument(
        "--no-manual-additions",
        action="store_true",
        help="Do not include data/rules_discovered/manual_additions during this workflow run",
    )
    wf.add_argument("--new-ruleset-id", default="", help="Required with --promote")
    wf.add_argument("--no-cleanup", action="store_true", help="Skip ruleset cleanup during promotion")
    wf.add_argument("--min-brand-similarity", type=float, default=0.90)
    wf.add_argument("--min-serial-support", type=int, default=50)
    wf.add_argument("--min-model-support", type=int, default=50)
    wf.add_argument("--min-model-match-rate", type=float, default=0.50)
    wf.add_argument("--min-model-train-accuracy", type=float, default=0.95)
    wf.add_argument("--min-model-holdout-accuracy", type=float, default=0.95)
    wf.add_argument("--capacity-tolerance-tons", type=float, default=0.5)
    wf.set_defaults(func=action_workflow_improve)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
