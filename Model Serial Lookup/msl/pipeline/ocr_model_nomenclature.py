from __future__ import annotations

import csv
import json
import re
import subprocess
import tempfile
from pathlib import Path


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


def _load_attribute_rules(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                row["image_urls_obj"] = json.loads(row.get("image_urls") or "[]")
            except Exception:
                row["image_urls_obj"] = []
            rows.append(row)
    return rows


def _ocr_image(path: Path) -> str:
    """
    Preprocess with ImageMagick then OCR with tesseract.
    Returns OCR text (best-effort).
    """
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        pre = td_path / "pre.png"

        conv = subprocess.run(
            ["convert", str(path), "-colorspace", "Gray", "-resize", "200%", "-sharpen", "0x1", str(pre)],
            capture_output=True,
            text=True,
        )
        img_for_ocr = pre if conv.returncode == 0 and pre.exists() else path

        ocr = subprocess.run(
            ["tesseract", str(img_for_ocr), "stdout", "-l", "eng", "--psm", "6"],
            capture_output=True,
            text=True,
        )
        if ocr.returncode != 0:
            ocr = subprocess.run(
                ["tesseract", str(img_for_ocr), "stdout", "-l", "eng", "--psm", "11"],
                capture_output=True,
                text=True,
            )
        return (ocr.stdout or "") + ("\n" + (ocr.stderr or "") if ocr.stderr else "")


def cmd_ocr_model_nomenclature(args) -> int:
    ruleset_dir = Path(args.ruleset_dir)
    attr_csv = ruleset_dir / "AttributeDecodeRule.csv"
    if not attr_csv.exists():
        raise SystemExit(f"Missing {attr_csv}")

    image_log = Path(args.images_log)
    url_to_path = _load_image_log(image_log)

    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    ocr_out_dir = Path(args.out_ocr_dir) if args.out_ocr_dir else (Path("data/ocr_text") / args.run_id / "model_nomenclature")
    ocr_out_dir.mkdir(parents=True, exist_ok=True)

    rules = _load_attribute_rules(attr_csv)

    max_images = int(args.max_images or 0)
    processed_images = 0
    written = 0

    with out_csv.open("w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(
            f_out,
            fieldnames=[
                "brand",
                "attribute_name",
                "source_url",
                "image_url",
                "saved_path",
                "ocr_text_path",
                "ocr_excerpt",
            ],
        )
        w.writeheader()

        for r in rules:
            if (r.get("rule_type") or "") != "guidance":
                continue
            if (r.get("attribute_name") or "") != "ModelNomenclature":
                continue
            image_urls = r.get("image_urls_obj") or []
            if not image_urls:
                continue

            brand = r.get("brand") or ""
            src = r.get("source_url") or ""

            for image_url in image_urls:
                if max_images and processed_images >= max_images:
                    break
                saved = url_to_path.get(image_url) or ""
                if not saved or not Path(saved).exists():
                    continue
                processed_images += 1

                text = _ocr_image(Path(saved))
                safe_brand = re.sub(r"[^A-Za-z0-9]+", "_", brand)[:40] or "UNKNOWN"
                name = Path(saved).name
                out_txt = ocr_out_dir / f"{safe_brand}__{name}.txt"
                out_txt.write_text(text, encoding="utf-8", errors="replace")
                excerpt = " ".join((text or "").split())
                excerpt = excerpt[:400]

                w.writerow(
                    {
                        "brand": brand,
                        "attribute_name": "ModelNomenclature",
                        "source_url": src,
                        "image_url": image_url,
                        "saved_path": saved,
                        "ocr_text_path": str(out_txt),
                        "ocr_excerpt": excerpt,
                    }
                )
                written += 1

            if max_images and processed_images >= max_images:
                break

    print(str(out_csv))
    return 0

