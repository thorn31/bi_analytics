from __future__ import annotations

import datetime as dt
import time
from pathlib import Path
from urllib.request import Request, urlopen

from msl.pipeline.common import ensure_dir, read_csv, resolve_run_date, sha256_bytes, slugify_url, write_csv


def cmd_fetch(args) -> int:
    page_index_path = Path(args.page_index)
    run_date = resolve_run_date(args.run_date, str(page_index_path))

    out_raw_dir = ensure_dir(Path(args.out_raw_dir) / run_date)
    out_log_dir = ensure_dir(Path(args.out_log_dir) / run_date)

    rows = read_csv(page_index_path)
    log_rows: list[dict] = []

    for i, row in enumerate(rows):
        url = row["url"]
        slug = slugify_url(url)
        out_path = out_raw_dir / f"{slug}.html"
        meta_path = out_raw_dir / f"{slug}.meta.json"

        if bool(getattr(args, "skip_existing", False)) and not bool(getattr(args, "force", False)):
            if out_path.exists() and meta_path.exists():
                log_rows.append(
                    {
                        "retrieved_on": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                        "url": url,
                        "status": "SKIPPED",
                        "saved_path": str(out_path),
                        "sha256": "",
                        "error": "",
                        "brand": row.get("brand", ""),
                        "page_type_guess": row.get("page_type_guess", ""),
                    }
                )
                continue

        status = None
        error = ""
        content_hash = ""
        saved = False

        try:
            req = Request(url, headers={"User-Agent": "msl-rule-builder/0.1"})
            with urlopen(req, timeout=float(args.timeout_seconds)) as resp:  # nosec - controlled URLs
                status = getattr(resp, "status", None)
                data = resp.read()
            content_hash = sha256_bytes(data)
            out_path.write_bytes(data)
            meta_path.write_text(
                __import__("json").dumps(
                    {
                        "url": url,
                        "brand": row.get("brand", ""),
                        "page_type_guess": row.get("page_type_guess", ""),
                        "retrieved_on": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                        "sha256": content_hash,
                        "html_path": str(out_path),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            saved = True
        except Exception as e:
            error = str(e)
        finally:
            log_rows.append(
                {
                    "retrieved_on": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                    "url": url,
                    "status": status if status is not None else "",
                    "saved_path": str(out_path) if saved else "",
                    "sha256": content_hash,
                    "error": error,
                    "brand": row.get("brand", ""),
                    "page_type_guess": row.get("page_type_guess", ""),
                }
            )

        if i < len(rows) - 1:
            time.sleep(max(0.0, float(args.delay_seconds)))

    out_log_path = out_log_dir / "fetch_log.csv"
    write_csv(
        out_log_path,
        fieldnames=["retrieved_on", "url", "status", "saved_path", "sha256", "error", "brand", "page_type_guess"],
        rows=log_rows,
    )
    # Convenience manifest for downstream stages
    (out_raw_dir / "manifest.csv").write_text(
        "url,slug,html_path,meta_path,brand,page_type_guess,retrieved_on,sha256\n"
        + "\n".join(
            [
                ",".join(
                    [
                        r["url"],
                        slugify_url(r["url"]),
                        str(out_raw_dir / f"{slugify_url(r['url'])}.html"),
                        str(out_raw_dir / f"{slugify_url(r['url'])}.meta.json"),
                        r.get("brand", ""),
                        r.get("page_type_guess", ""),
                        r.get("retrieved_on", ""),
                        r.get("sha256", ""),
                    ]
                )
                for r in log_rows
                if r.get("saved_path")
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(str(out_log_path))
    return 0
