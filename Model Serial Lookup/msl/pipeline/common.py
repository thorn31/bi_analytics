from __future__ import annotations

import csv
import datetime as dt
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


def resolve_run_date(explicit: str | None, *hints: str) -> str:
    if explicit:
        return explicit
    for hint in hints:
        match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", hint)
        if match:
            return match.group(0)
    return dt.date.today().isoformat()


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def slugify_url(url: str, max_len: int = 120) -> str:
    parsed = urlparse(url)
    base = (parsed.netloc + parsed.path).strip("/")
    base = re.sub(r"[^a-zA-Z0-9]+", "_", base).strip("_").lower()
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    slug = f"{base[:max_len]}__{digest}" if base else digest
    return slug


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_building_center_url(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    return host.endswith("building-center.org")


@dataclass(frozen=True)
class PageIndexRow:
    brand: str
    url: str
    page_type_guess: str
    discovered_on: str

