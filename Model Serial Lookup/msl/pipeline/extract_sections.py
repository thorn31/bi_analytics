from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from html.parser import HTMLParser

from msl.pipeline.common import ensure_dir, resolve_run_date


SERIAL_LIKE_RE = re.compile(r"\b[A-Z0-9][A-Z0-9\-\s]{5,}\b", re.IGNORECASE)
SERIAL_TOKEN_RE = re.compile(r"\b[A-Z0-9-]{6,}\b", re.IGNORECASE)
SPACED_ALNUM_RE = re.compile(r"\b(?:[A-Z0-9]{1,4}\s+){2,}[A-Z0-9]{2,}\b", re.IGNORECASE)

PLACEHOLDER_EXAMPLE_RE = re.compile(r"(#|unknown|\bx+\b)", re.IGNORECASE)

IMG_SRC_RE = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)
PDF_HREF_RE = re.compile(r"""<a[^>]+href=["']([^"']+\.pdf(?:\?[^"']*)?)["']""", re.IGNORECASE)

FOOTER_STOP_PHRASES = [
    "brand history",
    "page last updated",
    "contact info",
    "trademarks (disclaimer)",
    "powered by",
    "toggle the widgetbar",
    "type and press",
    "privacy policy",
    "terms of use",
]

NOTES_KEY_PHRASES = [
    "only known method",
    "contact the manufacturer",
    "contact manufacturer",
    "must contact the manufacturer",
    "must contact manufacturer",
    "determine manufacture date",
    "determine the date of manufacture",
    "not represented",
    "further assistance",
]

STYLE_MARKER_RE = re.compile(r"^\s*style\s*\d+\s*:\s*", re.IGNORECASE)
STYLE_MARKER_ANY_RE = re.compile(r"style\s*\d+\s*:\s*", re.IGNORECASE)

def _normalize_ws(value: str) -> str:
    # Normalize common non-breaking spaces and collapse whitespace.
    return " ".join(value.replace("\xa0", " ").replace("\u202f", " ").split()).strip()


class _StyleSectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignore_depth = 0  # script/style

        self._in_title = False
        self.title_text_parts: list[str] = []

        self._in_heading: str | None = None
        self._heading_text_parts: list[str] = []

        self._collecting = False
        self._seen_first_style = False
        self._current_title: str | None = None
        self._current_parts: list[str] = []
        self._current_images: list[str] = []

        self.preamble_parts: list[str] = []
        self.sections: list[dict] = []

    @property
    def title_text(self) -> str:
        return " ".join(" ".join(self.title_text_parts).split()).strip()

    @property
    def preamble_text(self) -> str:
        raw = "".join(self.preamble_parts)
        return "\n".join([p.strip() for p in raw.splitlines() if p.strip()]).strip()

    def handle_starttag(self, tag: str, attrs):
        tag_l = tag.lower()
        if tag_l in {"script", "style"}:
            self._ignore_depth += 1
            return
        if self._ignore_depth:
            return

        if tag_l == "title":
            self._in_title = True
            return

        if tag_l in {"h1", "h2", "h3", "h4", "h5"}:
            self._in_heading = tag_l
            self._heading_text_parts = []
            return

        if self._collecting and tag_l == "img":
            src = None
            for k, v in attrs:
                if k.lower() == "src":
                    src = v
                    break
            if src:
                self._current_images.append(src)

    def handle_endtag(self, tag: str):
        tag_l = tag.lower()
        if tag_l in {"script", "style"}:
            self._ignore_depth = max(0, self._ignore_depth - 1)
            return
        if self._ignore_depth:
            return

        if tag_l == "title":
            self._in_title = False
            return

        if self._in_heading == tag_l:
            heading_text = _normalize_ws(" ".join(self._heading_text_parts))
            self._in_heading = None
            self._heading_text_parts = []

            # Only treat headings that actually start a style block as "Style ..." sections.
            # This avoids false positives like "Example serial number styles/formats found: Style 1: ... Style 2: ..."
            if STYLE_MARKER_RE.match(heading_text):
                self._seen_first_style = True
                if self._collecting and self._current_title:
                    self._flush_section()
                self._collecting = True
                self._current_title = heading_text
                self._current_parts = []
                self._current_images = []
            elif STYLE_MARKER_ANY_RE.search(heading_text):
                # Some pages embed multiple "Style N:" examples inside a heading/list container.
                # Split them into per-style synthetic sections so we don't miss the brand entirely.
                starts = [m.start() for m in STYLE_MARKER_ANY_RE.finditer(heading_text)]
                for i, start in enumerate(starts):
                    end = starts[i + 1] if i + 1 < len(starts) else len(heading_text)
                    segment = heading_text[start:end].strip()
                    if not segment:
                        continue
                    examples: set[str] = set()
                    for m2 in SERIAL_TOKEN_RE.finditer(segment):
                        tok = m2.group(0).strip().upper()
                        if len(tok) >= 6 and any(ch.isdigit() for ch in tok):
                            examples.add(tok)
                    for m2 in SPACED_ALNUM_RE.finditer(segment):
                        tok = re.sub(r"\s+", "", m2.group(0)).strip().upper()
                        tok = re.sub(r"[^A-Z0-9-]", "", tok)
                        if len(tok) >= 6 and any(ch.isdigit() for ch in tok):
                            examples.add(tok)
                    self.sections.append(
                        {
                            "section_title": segment,
                            "section_text": segment,
                            "example_values": sorted(examples)[:50],
                            "style_example_raw": None,
                            "has_images": False,
                            "image_urls": [],
                        }
                    )
            return

        if self._collecting and tag_l in {"p", "br", "li", "tr", "div"}:
            self._current_parts.append("\n")

    def handle_data(self, data: str):
        if self._ignore_depth:
            return
        if self._in_title:
            self.title_text_parts.append(data)
            return
        if self._in_heading:
            self._heading_text_parts.append(data)
            return
        # Detect style markers in non-heading contexts too (many pages use <li>/<strong> for style labels).
        data_compact = _normalize_ws(data) if data else ""
        if data_compact and STYLE_MARKER_RE.match(data_compact):
            heading_text = data_compact
            self._seen_first_style = True
            if self._collecting and self._current_title:
                self._flush_section()
            self._collecting = True
            self._current_title = heading_text
            self._current_parts = []
            self._current_images = []
            return
        if self._collecting and data and data.strip():
            lowered = data.lower()
            if any(p in lowered for p in FOOTER_STOP_PHRASES):
                self._flush_section()
                self._collecting = False
                self._current_title = None
                self._current_parts = []
                self._current_images = []
                return
            # Keep whitespace between chunks to avoid concatenating words.
            self._current_parts.append(data.strip() + " ")
        elif (not self._seen_first_style) and data and data.strip():
            # Capture pre-style caveats (often includes "contact manufacturer" notes).
            self.preamble_parts.append(data.strip() + " ")

    def close(self):
        super().close()
        if self._collecting and self._current_title:
            self._flush_section()

    def _flush_section(self) -> None:
        raw = "".join(self._current_parts)
        section_text = "\n".join([p.strip() for p in raw.splitlines() if p.strip()])
        if not section_text:
            return
        examples: set[str] = set()
        # Prefer the explicit style example in the heading (often spaced), normalized.
        title_example: str | None = None
        title_example_raw: str | None = None
        if self._current_title and ":" in self._current_title:
            after_colon = self._current_title.split(":", 1)[1].strip()
            title_example_raw = after_colon
            # If the style example is a placeholder/pattern (####, "unknown", etc.), don't treat it as an example serial.
            if PLACEHOLDER_EXAMPLE_RE.search(after_colon):
                title_example_raw = after_colon
                title_example = None
                examples = set()
            else:
                # Remove parenthetical explanatory text before splitting to avoid splitting on "or" inside parentheses.
                cleaned = re.sub(r"\([^)]*\)", " ", after_colon)

                # Split on explicit alternation markers first (~or~, -or-, |), then on " or " with spaces.
                first_parts = re.split(r"\s*(?:~or~|-or-|\|)\s*", cleaned, flags=re.IGNORECASE)
                parts: list[str] = []
                for p in first_parts:
                    parts.extend([x for x in re.split(r"\s+or\s+", p, flags=re.IGNORECASE) if x.strip()])

                def best_serial_fragment(part: str) -> str:
                    # Keep token-like pieces (digits and short letters) but stop at trailing descriptors like "Bryant & Carrier".
                    tokens = [t for t in re.split(r"\s+", part.strip()) if t]
                    kept: list[str] = []
                    seen_digit = False
                    for tok in tokens:
                        tok_clean = re.sub(r"[^A-Z0-9-]", "", tok.upper())
                        if not tok_clean:
                            continue
                        has_digit = any(ch.isdigit() for ch in tok_clean)
                        is_wordy_alpha = tok_clean.isalpha() and len(tok_clean) > 2
                        if seen_digit and is_wordy_alpha:
                            break
                        kept.append(tok_clean)
                        if has_digit:
                            seen_digit = True
                    return "".join(kept)

                normalized_parts: list[str] = []
                for part in parts:
                    norm = best_serial_fragment(part)
                    if len(norm) >= 6 and any(ch.isdigit() for ch in norm):
                        normalized_parts.append(norm)
                if normalized_parts:
                    # Use the first as the canonical title example, but keep all valid examples.
                    title_example = normalized_parts[0]
                    examples.update(normalized_parts)

        # If we have a title example, use it exclusively (avoids capturing instructional text like "2nd character").
        if title_example:
            example_values = sorted(examples)[:50]
            self.sections.append(
                {
                    "section_title": self._current_title,
                    "section_text": section_text,
                    "example_values": example_values,
                    "style_example_raw": title_example_raw,
                    "has_images": bool(self._current_images),
                    "image_urls": sorted(set(self._current_images)),
                }
            )
            return

        for m in SERIAL_TOKEN_RE.finditer(section_text):
            token = m.group(0).strip().upper()
            if len(token) >= 6 and any(ch.isdigit() for ch in token):
                examples.add(token)

        # Handle serials written as spaced groups, e.g. "AUB U 08 05 00386"
        for m in SPACED_ALNUM_RE.finditer(section_text):
            token = re.sub(r"\s+", "", m.group(0)).strip().upper()
            token = re.sub(r"[^A-Z0-9-]", "", token)
            if len(token) >= 6 and any(ch.isdigit() for ch in token):
                examples.add(token)

        example_values = sorted(examples)[:50]
        self.sections.append(
            {
                "section_title": self._current_title,
                "section_text": section_text,
                "example_values": example_values,
                "style_example_raw": title_example_raw,
                "has_images": bool(self._current_images),
                "image_urls": sorted(set(self._current_images)),
            }
        )


def guess_brand_from_html(title_text: str) -> str:
    return title_text.split(" - ")[0].strip() if title_text else "Unknown"

def guess_brand_from_url(url: str) -> str:
    """
    Best-effort brand extraction from Building-Center URL slugs.
    Examples:
      /trane-hvac-age/ -> TRANE
      /american-standard-water-heater-age/ -> AMERICAN STANDARD
      /carrier-tonnage-decoder/ -> CARRIER
    """
    if not url:
        return "Unknown"
    try:
        from urllib.parse import urlparse

        path = (urlparse(url).path or "/").strip("/").lower()
    except Exception:
        return "Unknown"
    if not path:
        return "Unknown"

    slug = path.split("/")[-1]
    for suffix in ["-hvac-age", "-water-heater-age", "-tonnage-decoder"]:
        if slug.endswith(suffix):
            slug = slug[: -len(suffix)]
            break
    slug = slug.strip("-")
    if not slug:
        return "Unknown"
    return slug.replace("-", " ").strip().upper()


def extract_style_sections(html: str) -> tuple[str, list[dict]]:
    parser = _StyleSectionParser()
    parser.feed(html)
    parser.close()
    return parser.title_text, parser.sections


def extract_page_notes_from_preamble(preamble_text: str) -> str | None:
    if not preamble_text:
        return None
    lower = preamble_text.lower()
    if not any(k in lower for k in NOTES_KEY_PHRASES):
        return None

    # Keep only sentences/lines containing key phrases to avoid dumping the whole page chrome.
    chunks = [c.strip() for c in re.split(r"[.\n]+", preamble_text) if c.strip()]
    keep: list[str] = []
    for chunk in chunks:
        ll = chunk.lower()
        if any(k in ll for k in NOTES_KEY_PHRASES):
            keep.append(chunk)
    if not keep:
        return preamble_text[:800]
    return "\n".join(keep)[:800]


def parse_page(html: str) -> tuple[str, list[dict], str]:
    parser = _StyleSectionParser()
    parser.feed(html)
    parser.close()
    return parser.title_text, parser.sections, parser.preamble_text


class _AllTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignore_depth = 0
        self.lines: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() in {"script", "style"}:
            self._ignore_depth += 1

    def handle_endtag(self, tag: str):
        if tag.lower() in {"script", "style"} and self._ignore_depth:
            self._ignore_depth -= 1

    def handle_data(self, data: str):
        if self._ignore_depth:
            return
        d = data.strip()
        if d:
            self.lines.append(d)


def extract_model_decoder_text(html: str) -> tuple[str, list[str]]:
    """
    Returns (section_text, example_values) for model-decoder pages (including tonnage/capacity and other model-derived attributes).
    We keep only relevant lines to avoid nav/footer noise.
    """
    parser = _AllTextParser()
    parser.feed(html)
    parser.close()
    lines = parser.lines

    keep: list[str] = []
    window = 0
    for line in lines:
        ll = line.lower()
        trigger = any(
            k in ll
            for k in [
                "tonnage",
                "tons",
                "btu",
                "capacity",
                "model number",
                "digits",
                "digit",
                "positions",
                "position",
                "=",
                "example",
                "designates",
                "divided by",
                "divide by",
                "voltage",
                "volt",
                "phase",
                "hz",
                "amp",
                "amps",
                "horsepower",
                " hp",
                "cfm",
                "gpm",
                "refrigerant",
                "motor",
                "seer",
                "eer",
                "kw",
            ]
        )
        if trigger:
            window = 3
            keep.append(line)
            continue
        if window > 0:
            keep.append(line)
            window -= 1

    # Example model tokens: uppercase alnum strings with digits, length >= 6.
    example_values: set[str] = set()
    for line in keep:
        for tok in re.findall(r"\b[A-Z0-9]{6,}\b", line.upper()):
            if any(ch.isdigit() for ch in tok):
                example_values.add(tok)

    # Also capture spaced model patterns as contiguous.
    for line in keep:
        m = SPACED_ALNUM_RE.search(line)
        if m:
            tok = re.sub(r"\s+", "", m.group(0)).upper()
            tok = re.sub(r"[^A-Z0-9-]", "", tok)
            if len(tok) >= 6 and any(ch.isdigit() for ch in tok):
                example_values.add(tok)

    section_text = "\n".join([l for l in keep if l.strip()])[:4000]
    return section_text, sorted(example_values)[:50]


def cmd_extract(args) -> int:
    raw_dir = Path(args.raw_dir)
    run_date = resolve_run_date(args.run_date, str(raw_dir))
    out_dir = ensure_dir(Path(args.out_dir) / run_date)

    html_files = sorted(raw_dir.glob("*.html"))
    if not html_files:
        raise SystemExit(f"No HTML files found in {raw_dir}")

    max_files = int(args.max_files or 0)
    if max_files and max_files > 0:
        html_files = html_files[:max_files]

    out_path = out_dir / str(args.out_file)
    with out_path.open("w", encoding="utf-8") as f:
        for html_path in html_files:
            html = html_path.read_text(encoding="utf-8", errors="replace")
            title_text, sections, preamble_text = parse_page(html)
            notes = extract_page_notes_from_preamble(preamble_text)

            meta_path = html_path.with_suffix(".meta.json")
            meta = {}
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    meta = {}

            # Prefer deriving the brand from the URL slug to avoid grouping/alias mistakes in discovery.
            brand_guess = guess_brand_from_url(meta.get("url") or "") or meta.get("brand") or guess_brand_from_html(title_text)
            page_type = meta.get("page_type_guess") or ("hvac_age" if sections else "other")

            if notes:
                record = {
                    "brand": brand_guess,
                    "page_type": page_type,
                    "source_url": meta.get("url"),
                    "retrieved_on": (meta.get("retrieved_on") or run_date),
                    "section_title": "Notes",
                    "example_values": [],
                    "style_example_raw": None,
                    "section_text": notes,
                    "section_html": None,
                    "has_images": False,
                    "image_urls": [],
                    "raw_html_path": str(html_path),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            if page_type == "tonnage_decoder":
                section_text, examples = extract_model_decoder_text(html)
                if section_text:
                    image_urls = sorted(set(IMG_SRC_RE.findall(html)))
                    pdf_urls = sorted(set(PDF_HREF_RE.findall(html)))
                    record = {
                        "brand": brand_guess,
                        "page_type": page_type,
                        "source_url": meta.get("url"),
                        "retrieved_on": (meta.get("retrieved_on") or run_date),
                        "section_title": "Model Decoder",
                        "example_values": examples,
                        "style_example_raw": None,
                        "section_text": section_text,
                        "section_html": None,
                        "has_images": bool(image_urls),
                        "image_urls": image_urls,
                        "pdf_urls": pdf_urls,
                        "raw_html_path": str(html_path),
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

            for sec in sections:
                record = {
                    "brand": brand_guess,
                    "page_type": page_type,
                    "source_url": meta.get("url"),
                    "retrieved_on": (meta.get("retrieved_on") or run_date),
                    "section_title": sec["section_title"],
                    "example_values": sec["example_values"],
                    "style_example_raw": sec.get("style_example_raw"),
                    "section_text": sec["section_text"],
                    "section_html": None,
                    "has_images": sec["has_images"],
                    "image_urls": sec["image_urls"],
                    "raw_html_path": str(html_path),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(str(out_path))
    return 0
