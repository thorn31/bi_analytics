from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from msl.pipeline.common import ensure_dir, resolve_run_date


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _normalize_image_url(url: str) -> str:
    u = (url or "").strip()
    if u.startswith("//"):
        return "https:" + u
    return u


def _safe_name_from_url(url: str) -> str:
    p = urlparse(url)
    base = Path(p.path).name or "image"
    # Strip query-ish suffixes if any
    base = base.split("?")[0].split("#")[0]
    return base


def cmd_fetch_images(args) -> int:
    extracted_file = Path(args.extracted_file)
    run_date = resolve_run_date(args.run_date, str(extracted_file))

    out_dir = ensure_dir(Path(args.out_dir) / run_date)
    out_log_dir = ensure_dir(Path(args.out_log_dir) / run_date)

    image_urls: set[str] = set()
    with extracted_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            for url in rec.get("image_urls") or []:
                if isinstance(url, str) and url.strip():
                    image_urls.add(_normalize_image_url(url))

    urls = sorted(image_urls)
    log_rows: list[dict] = []

    for i, url in enumerate(urls):
        url = _normalize_image_url(url)
        status = ""
        error = ""
        sha = ""
        saved_path = ""
        try:
            req = Request(url, headers={"User-Agent": "msl-rule-builder/0.1"})
            with urlopen(req, timeout=float(args.timeout_seconds)) as resp:  # nosec - controlled URLs
                status = str(getattr(resp, "status", ""))
                data = resp.read()
            sha = _sha256(data)
            name = _safe_name_from_url(url)
            saved_path = str(out_dir / f"{sha[:12]}__{name}")
            Path(saved_path).write_bytes(data)
        except Exception as e:
            error = str(e)

        log_rows.append(
            {
                "retrieved_on": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                "url": url,
                "status": status,
                "sha256": sha,
                "saved_path": saved_path,
                "error": error,
            }
        )

        if i < len(urls) - 1:
            time.sleep(max(0.0, float(args.delay_seconds)))

    log_path = out_log_dir / "fetch_images_log.csv"
    with log_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["retrieved_on", "url", "status", "sha256", "saved_path", "error"])
        w.writeheader()
        w.writerows(log_rows)

    print(str(log_path))
    return 0
