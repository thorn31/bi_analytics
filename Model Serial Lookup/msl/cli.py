from __future__ import annotations

import argparse

from msl.pipeline.discover import cmd_discover
from msl.pipeline.decode_run import cmd_decode
from msl.pipeline.extract_sections import cmd_extract
from msl.pipeline.fetch_html import cmd_fetch
from msl.pipeline.fetch_images import cmd_fetch_images
from msl.pipeline.gap_report import cmd_gap_report
from msl.pipeline.normalize_rules import cmd_normalize
from msl.pipeline.ocr_overrides import cmd_ocr_overrides
from msl.pipeline.ocr_model_nomenclature import cmd_ocr_model_nomenclature
from msl.pipeline.mine_model_ocr_attributes import cmd_mine_model_ocr_attributes
from msl.pipeline.phase3_baseline import cmd_phase3_baseline
from msl.pipeline.phase3_audit import cmd_phase3_audit
from msl.pipeline.phase3_mine import cmd_phase3_mine
from msl.pipeline.phase3_promote import cmd_phase3_promote
from msl.pipeline.report_rules import cmd_report
from msl.pipeline.ruleset_manager import cmd_cleanup_rulesets
from msl.pipeline.validate_export import cmd_validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="msl", description="Model/serial rule dictionary builder")
    sub = parser.add_subparsers(dest="command", required=True)

    discover = sub.add_parser("discover", help="Discover Building-Center pages from TOC seeds")
    discover.add_argument("--seed-url", action="append", required=True, help="Seed TOC URL (repeatable)")
    discover.add_argument("--run-date", default=None, help="YYYY-MM-DD (default: today)")
    discover.add_argument("--out-dir", default="data/page_index", help="Base output dir")
    discover.set_defaults(func=cmd_discover)

    fetch = sub.add_parser("fetch", help="Fetch and archive raw HTML for discovered pages")
    fetch.add_argument("--page-index", required=True, help="Path to page_index.csv")
    fetch.add_argument("--run-date", default=None, help="YYYY-MM-DD (default: inferred from page_index path or today)")
    fetch.add_argument("--out-raw-dir", default="data/raw_html", help="Base raw HTML dir")
    fetch.add_argument("--out-log-dir", default="data/logs", help="Base logs dir")
    fetch.add_argument("--delay-seconds", type=float, default=1.5, help="Delay between requests")
    fetch.add_argument("--timeout-seconds", type=float, default=30.0, help="HTTP timeout")
    fetch.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip fetching if the target HTML file already exists (recommended for iterative runs)",
    )
    fetch.add_argument(
        "--force",
        action="store_true",
        help="Force re-fetch even if the target HTML file already exists (overrides --skip-existing)",
    )
    fetch.set_defaults(func=cmd_fetch)

    fetch_images = sub.add_parser("fetch-images", help="Download and archive referenced images from extracted sections")
    fetch_images.add_argument("--extracted-file", required=True, help="Path to extracted_sections.jsonl")
    fetch_images.add_argument("--run-date", default=None, help="YYYY-MM-DD (default: inferred from extracted file path)")
    fetch_images.add_argument("--out-dir", default="data/raw_images", help="Base output dir for images")
    fetch_images.add_argument("--out-log-dir", default="data/logs_images", help="Base output dir for image fetch logs")
    fetch_images.add_argument("--delay-seconds", type=float, default=0.5, help="Delay between image requests")
    fetch_images.add_argument("--timeout-seconds", type=float, default=30.0, help="HTTP timeout")
    fetch_images.set_defaults(func=cmd_fetch_images)

    extract = sub.add_parser("extract", help="Extract style sections/examples into JSONL")
    extract.add_argument("--raw-dir", required=True, help="Path like data/raw_html/YYYY-MM-DD")
    extract.add_argument("--run-date", default=None, help="YYYY-MM-DD (default: inferred from raw-dir)")
    extract.add_argument("--out-dir", default="data/extracted_sections", help="Base extracted output dir")
    extract.add_argument("--out-file", default="extracted_sections.jsonl", help="Output filename within run folder")
    extract.add_argument("--max-files", type=int, default=0, help="Limit HTML files processed (0 = no limit)")
    extract.set_defaults(func=cmd_extract)

    normalize = sub.add_parser("normalize", help="LLM-assisted normalization into strict rule JSONL")
    normalize.add_argument("--extracted-dir", required=True, help="Path like data/extracted_sections/YYYY-MM-DD")
    normalize.add_argument("--run-date", default=None, help="YYYY-MM-DD (default: inferred from extracted-dir)")
    normalize.add_argument("--out-dir", default="data/rules_staged", help="Base staged rules dir")
    normalize.add_argument("--provider", choices=["openai", "manual", "heuristic"], default="manual")
    normalize.add_argument(
        "--input-file",
        default=None,
        help="Specific extracted JSONL filename to process (default: extracted_sections.jsonl if present, else all *.jsonl)",
    )
    normalize.add_argument(
        "--include-brand",
        action="append",
        default=[],
        help="Only process extracted records matching this brand value (repeatable)",
    )
    normalize.add_argument("--openai-model", default="gpt-4.1-mini", help="OpenAI model name")
    normalize.add_argument("--openai-api-key", default=None, help="OpenAI API key (or set OPENAI_API_KEY)")
    normalize.add_argument("--max-sections", type=int, default=0, help="Limit sections processed (0 = no limit)")
    normalize.set_defaults(func=cmd_normalize)

    validate = sub.add_parser("validate", help="Validate staged rules and export normalized CSVs + reports")
    validate.add_argument("--staged-dir", required=True, help="Path like data/rules_staged/YYYY-MM-DD")
    validate.add_argument("--run-date", default=None, help="YYYY-MM-DD (default: inferred from staged-dir)")
    validate.add_argument("--out-normalized-dir", default="data/rules_normalized", help="Base normalized output dir")
    validate.add_argument("--out-reports-dir", default="data/reports", help="Base reports output dir")
    validate.add_argument("--no-cleanup", action="store_true", help="Skip automatic cleanup of old rulesets")
    validate.set_defaults(func=cmd_validate)

    decode = sub.add_parser("decode", help="Decode a sample asset file using SerialDecodeRule.csv")
    decode.add_argument("--ruleset-dir", default="", help="Directory containing SerialDecodeRule.csv/ModelDecodeRule.csv (defaults to CURRENT.txt)")
    decode.add_argument("--serial-rules-csv", default="", help="Path to SerialDecodeRule.csv (overrides --ruleset-dir)")
    decode.add_argument(
        "--attribute-rules-csv", default="", help="Path to AttributeDecodeRule.csv (overrides --ruleset-dir)"
    )
    decode.add_argument("--input", required=True, help="Input CSV with AssetID, Make, SerialNumber columns")
    decode.add_argument("--output", required=True, help="Output CSV path")
    decode.add_argument(
        "--attributes-output",
        default="",
        help="Optional row-per-attribute output CSV (useful for Excel/Power Query)",
    )
    decode.add_argument(
        "--min-manufacture-year",
        type=int,
        default=1980,
        help="Skip decoded years earlier than this (0 disables the check; helps avoid false decodes on obsolete styles)",
    )
    decode.add_argument("--write-rejected", default="", help="Optional path to write rejected rules report (JSONL)")
    decode.set_defaults(func=cmd_decode)

    report = sub.add_parser("report", help="Summarize ruleset coverage (brands, decode vs guidance, etc.)")
    report.add_argument("--ruleset-dir", default="", help="Directory containing SerialDecodeRule.csv/AttributeDecodeRule.csv")
    report.add_argument(
        "--rules-base-dir",
        default="data/rules_normalized",
        help="Base directory used to auto-select the newest ruleset (default: data/rules_normalized)",
    )
    report.add_argument("--serial-rules-csv", default="", help="Path to SerialDecodeRule.csv (overrides --ruleset-dir)")
    report.add_argument(
        "--attribute-rules-csv", default="", help="Path to AttributeDecodeRule.csv (overrides --ruleset-dir)"
    )
    report.set_defaults(func=cmd_report)

    gap = sub.add_parser("gap-report", help="Analyze asset file gaps vs current ruleset")
    gap.add_argument("--ruleset-dir", default="", help="Directory containing SerialDecodeRule.csv/AttributeDecodeRule.csv (defaults to CURRENT.txt)")
    gap.add_argument("--serial-rules-csv", default="", help="Optional override path to SerialDecodeRule.csv")
    gap.add_argument("--attribute-rules-csv", default="", help="Optional override path to AttributeDecodeRule.csv")
    gap.add_argument("--input", required=True, help="Input asset CSV (AssetID/Make/SerialNumber/ModelNumber columns)")
    gap.add_argument("--output", required=True, help="Output CSV path for gap report")
    gap.set_defaults(func=cmd_gap_report)

    ocr = sub.add_parser("ocr-overrides", help="OCR chart images to generate serial mapping overrides (reduces chart_required)")
    ocr.add_argument("--ruleset-dir", required=True, help="Ruleset dir containing SerialDecodeRule.csv")
    ocr.add_argument(
        "--images-log",
        default="data/logs_images/2026-01-25/fetch_images_log.csv",
        help="Path to fetch_images_log.csv mapping image URLs to saved files",
    )
    ocr.add_argument(
        "--out-overrides",
        default="data/manual_overrides/serial_overrides.jsonl",
        help="Output overrides JSONL path (consumed by `msl validate` if present)",
    )
    ocr.add_argument("--run-id", default="ocr", help="Run identifier used for OCR text output folder naming")
    ocr.add_argument("--out-ocr-dir", default="", help="Optional OCR text output directory (default: data/ocr_text/<run-id>)")
    ocr.add_argument("--max-images", type=int, default=0, help="Limit OCR images processed (0 = no limit)")
    ocr.set_defaults(func=cmd_ocr_overrides)

    ocr_model = sub.add_parser(
        "ocr-model-nomenclature",
        help="OCR model nomenclature images (ModelNomenclature guidance rows) into text files for later rule transcription",
    )
    ocr_model.add_argument("--ruleset-dir", required=True, help="Ruleset dir containing AttributeDecodeRule.csv")
    ocr_model.add_argument(
        "--images-log",
        default="data/logs_images/2026-01-25/fetch_images_log.csv",
        help="Path to fetch_images_log.csv mapping image URLs to saved files",
    )
    ocr_model.add_argument(
        "--output-csv",
        default="data/manual_overrides/model_nomenclature_ocr.csv",
        help="Output CSV mapping model nomenclature images to OCR text files",
    )
    ocr_model.add_argument("--run-id", default="ocr-model", help="Run identifier used for OCR text output folder naming")
    ocr_model.add_argument("--out-ocr-dir", default="", help="Optional OCR text output directory")
    ocr_model.add_argument("--max-images", type=int, default=0, help="Limit OCR images processed (0 = no limit)")
    ocr_model.set_defaults(func=cmd_ocr_model_nomenclature)

    mine_ocr_attr = sub.add_parser(
        "mine-ocr-attributes",
        help="Mine deterministic AttributeDecodeRule overrides from OCR model nomenclature text (voltage + limited other attributes)",
    )
    mine_ocr_attr.add_argument("--input-csv", required=True, help="CSV output from `msl ocr-model-nomenclature`")
    mine_ocr_attr.add_argument(
        "--out-overrides",
        default="data/manual_overrides/attribute_overrides.jsonl",
        help="Output JSONL file of AttributeDecodeRule override objects",
    )
    mine_ocr_attr.add_argument("--max-rows", type=int, default=0, help="Limit input rows processed (0 = no limit)")
    mine_ocr_attr.set_defaults(func=cmd_mine_model_ocr_attributes)

    phase3 = sub.add_parser("phase3-baseline", help="Phase 3: profile labeled asset report + baseline decode scorecard")
    phase3.add_argument("--input", required=True, help="Labeled asset report CSV")
    phase3.add_argument("--ruleset-dir", default="", help="Ruleset dir containing SerialDecodeRule.csv/AttributeDecodeRule.csv (defaults to CURRENT.txt)")
    phase3.add_argument("--run-id", default="", help="Run identifier (default: autogenerated UTC timestamp)")
    phase3.add_argument("--out-dir", default="data/reports", help="Base output dir (default: data/reports)")
    phase3.set_defaults(func=cmd_phase3_baseline)

    phase3_mine = sub.add_parser("phase3-mine", help="Phase 3: mine candidate rules from labeled asset report")
    phase3_mine.add_argument("--input", required=True, help="Labeled asset report CSV")
    phase3_mine.add_argument("--ruleset-dir", default="", help="Ruleset dir containing SerialDecodeRule.csv/AttributeDecodeRule.csv (defaults to CURRENT.txt)")
    phase3_mine.add_argument("--run-id", default="", help="Run identifier (default: autogenerated UTC timestamp)")
    phase3_mine.add_argument("--out-candidates-dir", default="data/rules_discovered", help="Base dir for discovered candidates")
    phase3_mine.add_argument("--out-reports-dir", default="data/reports", help="Base dir for Phase 3 mining reports")
    phase3_mine.add_argument("--min-brand-similarity", type=float, default=0.90, help="Min similarity to suggest brand mapping")
    phase3_mine.add_argument("--min-serial-support", type=int, default=50, help="Min rows per brand/signature group for serial mining")
    phase3_mine.add_argument("--min-model-support", type=int, default=50, help="Min rows per brand/type group for capacity mining")
    phase3_mine.add_argument("--min-model-match-rate", type=float, default=0.50, help="Min match rate for a model pattern within group")
    phase3_mine.add_argument("--min-model-train-accuracy", type=float, default=0.95, help="Min training accuracy for capacity candidates")
    phase3_mine.add_argument("--min-model-holdout-accuracy", type=float, default=0.95, help="Min holdout accuracy for capacity candidates")
    phase3_mine.add_argument("--capacity-tolerance-tons", type=float, default=0.5, help="Allowed tons error for capacity match")
    phase3_mine.set_defaults(func=cmd_phase3_mine)

    phase3_audit = sub.add_parser("phase3-audit", help="Phase 3: audit mined candidates against labeled dataset")
    phase3_audit.add_argument("--input", required=True, help="Labeled asset report CSV")
    phase3_audit.add_argument("--candidates-dir", required=True, help="Candidates dir (contains *.candidates.* files)")
    phase3_audit.add_argument("--run-id", default="", help="Run identifier (default: inferred from candidates dir)")
    phase3_audit.add_argument("--out-dir", default="data/reports", help="Base output dir for audit reports")
    phase3_audit.add_argument("--capacity-tolerance-tons", type=float, default=0.5, help="Allowed tons error for capacity match")
    phase3_audit.set_defaults(func=cmd_phase3_audit)

    phase3_promote = sub.add_parser("phase3-promote", help="Phase 3: promote candidate rules into a new versioned ruleset")
    phase3_promote.add_argument("--base-ruleset-dir", required=True, help="Existing ruleset dir to merge into")
    phase3_promote.add_argument("--candidates-dir", required=True, help="Candidates dir containing *.candidates.* files")
    phase3_promote.add_argument("--audit-dir", default="", help="Optional audit dir (holdout_validation_results.csv, false_positive_audit.csv)")
    phase3_promote.add_argument("--min-accuracy", type=float, default=0.98, help="Min accuracy_on_matches to promote")
    phase3_promote.add_argument("--min-coverage", type=float, default=0.60, help="Min coverage_on_truth to promote")
    phase3_promote.add_argument("--max-false-positive-rate", type=float, default=0.01, help="Max other_brand_match_rate to promote attribute rules")
    phase3_promote.add_argument("--min-brand-support", type=int, default=10, help="Min support_n to promote brand mappings")
    phase3_promote.add_argument("--min-brand-similarity", type=float, default=0.95, help="Min similarity to promote brand mappings")
    phase3_promote.add_argument("--run-id", required=True, help="New ruleset folder name under --out-dir")
    phase3_promote.add_argument("--out-dir", default="data/rules_normalized", help="Base output dir for promoted ruleset")
    phase3_promote.add_argument("--no-cleanup", action="store_true", help="Skip automatic cleanup of old rulesets")
    phase3_promote.set_defaults(func=cmd_phase3_promote)

    cleanup = sub.add_parser("cleanup-rulesets", help="Remove old rulesets beyond retention count (protects CURRENT.txt target)")
    cleanup.add_argument("--retention", type=int, default=5, help="Number of rulesets to keep (default: 5)")
    cleanup.add_argument("--dry-run", action="store_true", help="Preview what would be removed without deleting")
    cleanup.add_argument(
        "--rules-base-dir",
        default="data/rules_normalized",
        help="Base directory containing rulesets (default: data/rules_normalized)",
    )
    cleanup.set_defaults(func=cmd_cleanup_rulesets)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
