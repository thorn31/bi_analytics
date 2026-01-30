#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _utc_compact_ts() -> str:
    import datetime as dt

    return dt.datetime.now(dt.UTC).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")


def _sanitize_filename(value: str) -> str:
    v = (value or "").strip()
    v = re.sub(r"[^\w.\- ]+", "", v)
    v = re.sub(r"\s+", " ", v).strip()
    v = v.replace(" ", "_")
    return v or "spec"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _extract_text_pypdf(pdf_path: Path) -> tuple[str, dict[str, Any]]:
    try:
        from pypdf import PdfReader
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: pypdf. Install with: python3 -m pip install -r requirements.txt"
        ) from e

    reader = PdfReader(str(pdf_path))
    pages = []
    chars = 0
    for i, page in enumerate(reader.pages):
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        t = t.replace("\r\n", "\n").replace("\r", "\n")
        pages.append(t)
        chars += len(t)
        # Keep deterministic + avoid pathological huge docs.
        if chars > 5_000_000:
            break

    text = "\n\n".join(pages).strip() + "\n"
    meta = {
        "pages_total": len(reader.pages),
        "pages_extracted": len(pages),
        "chars": chars,
    }
    return text, meta


@dataclass(frozen=True)
class ExtractedSpec:
    input_pdf: str
    output_txt: str
    sha256: str
    pages_total: int
    pages_extracted: int
    chars: int


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_specs_extract_text(args: argparse.Namespace) -> int:
    inbox_dir = Path(args.inbox_dir)
    if not inbox_dir.exists():
        raise SystemExit(f"Missing inbox dir: {inbox_dir}")

    out_base = Path(args.out_base_dir)
    snapshot_id = (args.snapshot_id or "").strip() or _utc_compact_ts()
    out_dir = out_base / snapshot_id
    out_txt_dir = out_dir / "text"
    out_txt_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted([p for p in inbox_dir.rglob("*.pdf") if p.is_file()])
    if not pdfs:
        raise SystemExit(f"No PDFs found under: {inbox_dir}")

    extracted: list[ExtractedSpec] = []
    for pdf in pdfs:
        sha = _sha256_file(pdf)
        stem = _sanitize_filename(pdf.stem)
        out_txt = out_txt_dir / f"{stem}__{sha[:12]}.txt"

        text, meta = _extract_text_pypdf(pdf)
        out_txt.write_text(text, encoding="utf-8")

        extracted.append(
            ExtractedSpec(
                input_pdf=str(pdf),
                output_txt=str(out_txt),
                sha256=sha,
                pages_total=int(meta.get("pages_total") or 0),
                pages_extracted=int(meta.get("pages_extracted") or 0),
                chars=int(meta.get("chars") or 0),
            )
        )

    manifest = {
        "snapshot_id": snapshot_id,
        "inbox_dir": str(inbox_dir),
        "out_dir": str(out_dir),
        "n_pdfs": len(pdfs),
        "extracted": [e.__dict__ for e in extracted],
    }
    _write_json(out_dir / "manifest.json", manifest)

    print(str(out_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Extract text from spec sheet PDFs into a versioned snapshot folder.")
    p.add_argument(
        "--inbox-dir",
        default=str(REPO_ROOT / "data" / "external_sources" / "specs"),
        help="Folder containing input PDFs (default: data/external_sources/specs)",
    )
    p.add_argument(
        "--out-base-dir",
        default=str(REPO_ROOT / "data" / "external_sources" / "specs_snapshots"),
        help="Base output folder for snapshots (default: data/external_sources/specs_snapshots)",
    )
    p.add_argument(
        "--snapshot-id",
        default="",
        help="Snapshot id folder name (default: UTC timestamp)",
    )
    args = p.parse_args(argv)
    return cmd_specs_extract_text(args)


if __name__ == "__main__":
    raise SystemExit(main())

