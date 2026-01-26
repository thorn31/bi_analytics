from __future__ import annotations

import datetime as dt
import re
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from msl.pipeline.common import ensure_dir, is_building_center_url, resolve_run_date, slugify_url, write_csv


BRAND_KEYWORDS: dict[str, list[str]] = {
    "Carrier/ICP": ["carrier", "icp", "comfortmaker", "heil", "tempstar", "day & night", "day and night"],
    "Trane": ["trane"],
    "York/JCI": ["york", "johnson controls", "jci", "luxaire", "coleman"],
    "Lennox": ["lennox", "ducane", "armstrong air"],
    "Rheem/Ruud": ["rheem", "ruud"],
    "Goodman/Amana/Daikin": ["goodman", "amana", "daikin"],
    "AAON": ["aaon"],
    "Mitsubishi": ["mitsubishi"],
    "LG": ["lg"],
}


def guess_brand(text: str) -> str:
    t = text.lower()
    for brand, keywords in BRAND_KEYWORDS.items():
        if any(k in t for k in keywords):
            return brand
    return ""


def guess_page_type(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["water-heater-age", "water heater age"]):
        return "water_heater_age"
    if any(k in t for k in ["tonnage-decoder", "tonnage decoder"]):
        return "tonnage_decoder"
    if any(k in t for k in ["hvac-age", "hvac age"]):
        return "hvac_age"
    if any(k in t for k in ["tonnage", "btu", "btuh", "capacity", "decoder"]):
        return "tonnage_decoder"
    if any(k in t for k in ["hvac age", "serial", "age of", "manufacture date"]):
        return "hvac_age"
    return "other"


_ANCHOR_RE = re.compile(r"""<a\s+[^>]*href=["']([^"']+)["'][^>]*>(.*?)</a>""", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def extract_links(html: str, base_url: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for match in _ANCHOR_RE.finditer(html):
        href = unescape(match.group(1)).strip()
        if not href:
            continue
        absolute = canonicalize_building_center_url(urljoin(base_url, href))
        if not is_building_center_url(absolute):
            continue
        raw_text = unescape(match.group(2))
        text = " ".join(_TAG_RE.sub(" ", raw_text).split())
        links.append((text, absolute))
    return links


def _get(url: str, timeout: float = 30.0) -> str:
    req = Request(url, headers={"User-Agent": "msl-rule-builder/0.1"})
    with urlopen(req, timeout=timeout) as resp:  # nosec - controlled URLs
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def canonicalize_building_center_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.endswith("building-center.org"):
        host = "www.building-center.org"
    path = parsed.path or "/"
    return urlunparse(("https", host, path, "", "", ""))


_TRAILING_MARKS_RE = re.compile(r"[®™©]+$")
_PARENS_RE = re.compile(r"\s*\([^)]*\)")
_MULTISPACE_RE = re.compile(r"\s+")


def clean_link_brand_name(link_text: str) -> str:
    # Remove trademark symbols and parenthetical notes, keep readable brand.
    t = link_text.strip()
    t = t.replace("\u00ad", "")  # soft hyphen
    t = _TRAILING_MARKS_RE.sub("", t).strip()
    t = _PARENS_RE.sub("", t).strip()
    t = t.replace("®", "").replace("™", "").replace("©", "")
    t = _MULTISPACE_RE.sub(" ", t).strip(" -–—\t")
    return t or "Unknown"


def should_include(url: str, page_type_guess: str) -> bool:
    path = urlparse(url).path.lower()
    # Keep discovery strictly to page types we can process deterministically.
    return bool(re.search(r"/[^/]*-(hvac-age|tonnage-decoder|water-heater-age)/?$", path))


def page_type_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    if "tonnage-decoder" in path:
        return "tonnage_decoder"
    if "hvac-age" in path:
        return "hvac_age"
    if "water-heater-age" in path:
        return "water_heater_age"
    return "other"


def cmd_discover(args) -> int:
    run_date = resolve_run_date(args.run_date)
    out_dir = ensure_dir(Path(args.out_dir) / run_date)

    rows: dict[str, dict] = {}
    for seed_url in args.seed_url:
        html = _get(seed_url, timeout=30.0)
        discovered_on = dt.date.today().isoformat()

        for text, url in extract_links(html, seed_url):
            url = canonicalize_building_center_url(url)
            key = slugify_url(url)
            combined = f"{text} {url}"
            page_type_guess = page_type_from_url(url) or guess_page_type(combined)

            if not should_include(url, page_type_guess):
                continue

            brand_group = guess_brand(combined)
            brand = brand_group or clean_link_brand_name(text)

            rows[key] = {
                "brand": brand,
                "url": url,
                "page_type_guess": page_type_guess,
                "discovered_on": discovered_on,
                "link_text": text,
                "seed_url": seed_url,
            }

    out_path = out_dir / "page_index.csv"
    write_csv(
        out_path,
        fieldnames=["brand", "url", "page_type_guess", "discovered_on", "link_text", "seed_url"],
        rows=rows.values(),
    )
    print(str(out_path))
    return 0
