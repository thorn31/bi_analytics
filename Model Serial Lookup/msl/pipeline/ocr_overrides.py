from __future__ import annotations

import csv
import json
import re
import subprocess
import tempfile
from pathlib import Path

MONTH_NAME_TO_NUM: dict[str, int] = {
    "JAN": 1,
    "JANUARY": 1,
    "FEB": 2,
    "FEBRUARY": 2,
    "MAR": 3,
    "MARCH": 3,
    "APR": 4,
    "APRIL": 4,
    "MAY": 5,
    "JUN": 6,
    "JUNE": 6,
    "JUL": 7,
    "JULY": 7,
    "AUG": 8,
    "AUGUST": 8,
    "SEP": 9,
    "SEPT": 9,
    "SEPTEMBER": 9,
    "OCT": 10,
    "OCTOBER": 10,
    "NOV": 11,
    "NOVEMBER": 11,
    "DEC": 12,
    "DECEMBER": 12,
}


def _load_image_log(path: Path) -> dict[str, str]:
    """
    Returns {url -> saved_path} for successfully downloaded images.
    """
    mapping: dict[str, str] = {}
    if not path.exists():
        return mapping
    with path.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            url = (row.get("url") or "").strip()
            saved = (row.get("saved_path") or "").strip()
            if url and saved:
                mapping[url] = saved
    return mapping


def _load_serial_rules(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["date_fields_obj"] = json.loads(row.get("date_fields") or "{}")
            row["image_urls_obj"] = json.loads(row.get("image_urls") or "[]")
            rows.append(row)
    return rows


def _load_existing_overrides(path: Path) -> tuple[list[dict], set[tuple]]:
    """
    Returns (rows, keys) for an existing JSONL override file.
    Key is (brand, style_name, field, mapping_json_sorted).
    """
    if not path.exists():
        return ([], set())
    rows: list[dict] = []
    keys: set[tuple] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            brand = (obj.get("brand") or "").strip()
            style = (obj.get("style_name") or "").strip()
            field = (obj.get("field") or "").strip()
            mapping = obj.get("mapping") if isinstance(obj.get("mapping"), dict) else {}
            key = (brand, style, field, json.dumps(mapping, sort_keys=True))
            if key in keys:
                continue
            keys.add(key)
            rows.append(obj)
    return (rows, keys)


def _extract_letter_mapping(text: str) -> tuple[dict[str, int], dict[str, int]]:
    """
    Returns (month_mapping, year_mapping) extracted from OCR text.
    """
    month_map: dict[str, int] = {}
    year_map: dict[str, int] = {}
    t = text.upper()

    # Patterns like "A=JAN", "A - JAN", "A : 2009", "A=1"
    for m in re.finditer(r"\b([A-Z])\s*[-:=]\s*([A-Z]{3,9}|\d{1,4})\b", t):
        key = m.group(1)
        val = m.group(2)
        if val.isdigit():
            n = int(val)
            if 1 <= n <= 12:
                month_map[key] = n
            elif 1900 <= n <= 2100:
                year_map[key] = n
            continue
        if val in MONTH_NAME_TO_NUM:
            month_map[key] = MONTH_NAME_TO_NUM[val]

    # Table-like patterns: "A JAN", "B FEB", etc.
    for m in re.finditer(
        r"\b([A-Z])\s+(JANUARY|JAN|FEBRUARY|FEB|MARCH|MAR|APRIL|APR|MAY|JUNE|JUN|JULY|JUL|AUGUST|AUG|SEPTEMBER|SEPT|SEP|OCTOBER|OCT|NOVEMBER|NOV|DECEMBER|DEC)\b",
        t,
    ):
        month_map[m.group(1)] = MONTH_NAME_TO_NUM[m.group(2)]

    # Loose year table patterns: "A 2010", "B 2011" (avoid small numbers that look like months)
    for m in re.finditer(r"\b([A-Z])\s+(19\d{2}|20\d{2})\b", t):
        year_map[m.group(1)] = int(m.group(2))

    return month_map, year_map


def _ocr_image(path: Path) -> str:
    """
    Preprocess with ImageMagick then OCR with tesseract.
    Returns OCR text (uppercase not forced).
    """
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        pre = td_path / "pre.png"

        # Preprocess for OCR: grayscale, upscale, mild sharpen.
        conv = subprocess.run(
            ["convert", str(path), "-colorspace", "Gray", "-resize", "200%", "-sharpen", "0x1", str(pre)],
            capture_output=True,
            text=True,
        )
        img_for_ocr = pre if conv.returncode == 0 and pre.exists() else path

        # OCR
        ocr = subprocess.run(
            ["tesseract", str(img_for_ocr), "stdout", "-l", "eng", "--psm", "6"],
            capture_output=True,
            text=True,
        )
        if ocr.returncode != 0:
            # Try a fallback segmentation mode.
            ocr = subprocess.run(
                ["tesseract", str(img_for_ocr), "stdout", "-l", "eng", "--psm", "11"],
                capture_output=True,
                text=True,
            )
        return (ocr.stdout or "") + ("\n" + (ocr.stderr or "") if ocr.stderr else "")


def cmd_ocr_overrides(args) -> int:
    ruleset_dir = Path(args.ruleset_dir)
    serial_csv = ruleset_dir / "SerialDecodeRule.csv"
    if not serial_csv.exists():
        raise SystemExit(f"Missing {serial_csv}")

    image_log = Path(args.images_log)
    url_to_path = _load_image_log(image_log)

    out_overrides = Path(args.out_overrides)
    out_overrides.parent.mkdir(parents=True, exist_ok=True)

    ocr_out_dir = Path(args.out_ocr_dir) if args.out_ocr_dir else (Path("data/ocr_text") / args.run_id)
    ocr_out_dir.mkdir(parents=True, exist_ok=True)

    rules = _load_serial_rules(serial_csv)

    max_images = int(args.max_images or 0)
    processed_images = 0
    existing_rows, seen_override_keys = _load_existing_overrides(out_overrides)
    new_rows: list[dict] = []

    overrides_written = 0

    for r in rules:
            date_fields = r.get("date_fields_obj") or {}
            if not isinstance(date_fields, dict):
                continue

            # Only target fields that are explicitly chart-required (most valuable guidance reducer).
            needs = [k for k, v in date_fields.items() if isinstance(v, dict) and v.get("requires_chart") is True]
            if not needs:
                continue

            image_urls = r.get("image_urls_obj") or []
            if not image_urls:
                continue

            # Prefer images that exist locally.
            local_images: list[tuple[str, Path]] = []
            for u in image_urls:
                p = url_to_path.get(u)
                if p and Path(p).exists():
                    local_images.append((u, Path(p)))
            if not local_images:
                continue

            brand = r.get("brand") or ""
            style_name = r.get("style_name") or ""

            # OCR up to N images per style until we find a useful mapping.
            month_map: dict[str, int] = {}
            year_map: dict[str, int] = {}
            used_image_url = ""
            for u, p in local_images[:3]:
                if max_images and processed_images >= max_images:
                    break
                processed_images += 1

                ocr_text = _ocr_image(p)
                (ocr_out_dir / f"{brand}__{re.sub(r'[^A-Za-z0-9]+','_',style_name)[:60]}__{p.name}.txt").write_text(
                    ocr_text, encoding="utf-8", errors="replace"
                )
                mm, yy = _extract_letter_mapping(ocr_text)
                if len(mm) >= 6 or len(yy) >= 6:
                    month_map = mm
                    year_map = yy
                    used_image_url = u
                    break

            if not month_map and not year_map:
                continue

            for field in needs:
                spec = date_fields.get(field) or {}
                if not isinstance(spec, dict):
                    continue

                # Only apply mapping if we know how to extract a code (positions/pattern).
                # If positions/pattern are missing, keep it chart_required (avoid guessing).
                if "positions" not in spec and "pattern" not in spec and "positions_list" not in spec:
                    continue

                mapping = None
                if field == "month" and month_map:
                    mapping = month_map
                elif field == "year" and year_map:
                    mapping = year_map
                elif field == "month" and year_map and not month_map:
                    # Sometimes charts show months as numbers without month names; treat 1..12 as month mapping.
                    if all(1 <= v <= 12 for v in year_map.values()):
                        mapping = year_map

                if not mapping:
                    continue

                key = (brand, style_name, field, json.dumps(mapping, sort_keys=True))
                if key in seen_override_keys:
                    continue
                seen_override_keys.add(key)

                new_rows.append(
                    {
                        "brand": brand,
                        "style_name": style_name,
                        "field": field,
                        "mapping": mapping,
                        "source_image_url": used_image_url,
                        "source_images_log": str(image_log),
                    }
                )
                overrides_written += 1

    # Rewrite file with existing + new rows, de-duped.
    with out_overrides.open("w", encoding="utf-8") as f_out:
        for obj in existing_rows + new_rows:
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(str(out_overrides))
    print(f"OCR images processed: {processed_images}")
    print(f"Overrides written: {overrides_written}")
    print(f"OCR text dir: {ocr_out_dir}")
    return 0
