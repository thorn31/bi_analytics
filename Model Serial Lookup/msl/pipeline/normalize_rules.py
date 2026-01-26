from __future__ import annotations

import html as html_lib
import json
import os
import re
from pathlib import Path
from html.parser import HTMLParser

from msl.pipeline.common import ensure_dir, resolve_run_date


SYSTEM_PROMPT = """You are normalizing extracted HVAC serial/model decoding documentation into strict JSON objects.

Rules:
- Only use facts present in the provided section_text and example_values.
- Do not infer missing mappings or decades. If ambiguous, mark decade_ambiguity.is_ambiguous=true.
- Output MUST be valid JSON Lines (one JSON object per input record) with exactly the required keys.

SerialDecodeRule required keys:
brand, style_name, serial_regex, date_fields, example_serials, decade_ambiguity, evidence_excerpt, source_url, retrieved_on

ModelDecodeRule required keys (when applicable):
brand, model_regex, capacity_code, examples, limitations, evidence_excerpt, source_url, retrieved_on

If the section cannot be reliably converted to a rule, output an object:
{ "skip": true, "reason": "...", "source_url": "...", "retrieved_on": "YYYY-MM-DD", "brand": "...", "section_title": "..." }
"""

_CONTACT_MFR_RE = re.compile(r"\b(contact (the )?manufacturer|must contact (the )?manufacturer)\b", re.IGNORECASE)
_PLACEHOLDER_TITLE_RE = re.compile(r"(#|unknown|\bx+\b)", re.IGNORECASE)
_BARE_STYLE_TITLE_RE = re.compile(r"^\s*style\s*\d+\s*:\s*$", re.IGNORECASE)

_ORDINAL_RE = re.compile(r"(\d+)\s*(st|nd|rd|th)", re.IGNORECASE)
_RANGE_RE = re.compile(r"(\d+)\s*(st|nd|rd|th)?\s*(?:-|to|&)\s*(\d+)\s*(st|nd|rd|th)?", re.IGNORECASE)
_DIGIT_RANGE_RE = re.compile(r"\b(?:pos(?:ition)?s?|digits?|chars?|characters?)\s*(\d+)\s*(?:-|to|through|thru|&|and)\s*(\d+)\b", re.IGNORECASE)
_DIGIT_PAIR_RE = re.compile(r"\b(?:pos(?:ition)?s?|digits?|chars?|characters?)\s*(\d+)\s*(?:&|and)\s*(\d+)\b", re.IGNORECASE)
_FIRST_N_RE = re.compile(r"\bfirst\s+(\d+)\s+(?:digits?|numbers?|chars?|characters?)\b", re.IGNORECASE)
_LEGEND_RE = re.compile(
    r"\blegend\s*:\s*"
    r".{0,400}?\byear\s+is\s+red\b"
    r".{0,400}?\bmonth\s+is\s+green\b"
    r".{0,400}?\b(?:week\s+is\s+(?:light\s+)?blue|day\s+is\s+blue)\b",
    re.IGNORECASE | re.DOTALL,
)
_IGNORE_LETTERS_RE = re.compile(r"\b(?:disregard|ignore)\b.*\bletter", re.IGNORECASE)

EVIDENCE_EXCERPT_MAX_CHARS = 600

_WORD_ORDINALS: dict[str, int] = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
}


def _normalize_word_ordinals(text: str) -> str:
    # Convert "3 rd" -> "3rd" and "first" -> "1st" for easier regex matching.
    t = re.sub(r"\b(\d+)\s+(st|nd|rd|th)\b", r"\1\2", text, flags=re.IGNORECASE)
    for w, n in _WORD_ORDINALS.items():
        t = re.sub(rf"\b{w}\b", f"{n}th" if n not in (1, 2, 3) else {1: '1st', 2: '2nd', 3: '3rd'}[n], t, flags=re.IGNORECASE)
    return t


def _collapse_ws(value: str) -> str:
    t = html_lib.unescape(value or "")
    return " ".join(t.replace("\xa0", " ").replace("\u202f", " ").split()).strip()


def _evidence_excerpt(value: str) -> str:
    # Keep instructions readable in Excel without losing critical trailing clauses.
    return _collapse_ws(value)[:EVIDENCE_EXCERPT_MAX_CHARS]


def _fuzzy_title_regex(title: str) -> re.Pattern:
    """
    Build a case-insensitive regex that matches a title even if HTML tags / &nbsp; / extra whitespace
    appear between tokens.
    """
    t = _collapse_ws(title)
    if not t:
        return re.compile(r"$^")
    tokens = t.split(" ")
    joiner = r"(?:\s|&nbsp;|&#160;|\xa0|\u202f|<[^>]+>)+"
    pat = joiner.join([re.escape(tok) for tok in tokens])
    return re.compile(pat, flags=re.IGNORECASE)


class _ColoredTextParser(HTMLParser):
    """
    Parses a small HTML snippet and captures alphanumeric characters with a coarse color label
    based on <span style="color: ..."> wrappers.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignore_depth = 0
        self._color_stack: list[str] = []
        self.chars: list[tuple[str, str]] = []  # (char, color_label)

    def handle_starttag(self, tag: str, attrs):
        tag_l = tag.lower()
        if tag_l in {"script", "style"}:
            self._ignore_depth += 1
            return
        if self._ignore_depth:
            return
        if tag_l == "span":
            style = ""
            for k, v in attrs:
                if k.lower() == "style":
                    style = v or ""
                    break
            style_l = style.lower()
            # Common representations of red/green/blue used by Building-Center.
            if "ff0000" in style_l or "red" in style_l:
                self._color_stack.append("RED")
            elif "00ff00" in style_l or "008000" in style_l or "339966" in style_l or "green" in style_l:
                self._color_stack.append("GREEN")
            elif (
                "0000ff" in style_l
                or "33cccc" in style_l
                or "3366ff" in style_l
                or "00b0f0" in style_l
                or "blue" in style_l
            ):
                self._color_stack.append("BLUE")
            else:
                self._color_stack.append("OTHER")

    def handle_endtag(self, tag: str):
        tag_l = tag.lower()
        if tag_l in {"script", "style"} and self._ignore_depth:
            self._ignore_depth -= 1
            return
        if self._ignore_depth:
            return
        if tag_l == "span" and self._color_stack:
            self._color_stack.pop()

    def handle_data(self, data: str):
        if self._ignore_depth:
            return
        if not data:
            return
        color = self._color_stack[-1] if self._color_stack else "OTHER"
        for ch in data:
            if ch.isalnum():
                self.chars.append((ch.upper(), color))


def _positions_from_color(chars: list[tuple[str, str]], wanted: str) -> dict | None:
    positions = [i + 1 for i, (_ch, c) in enumerate(chars) if c == wanted]
    if not positions:
        return None
    # Prefer contiguous range when possible; otherwise positions_list.
    if positions == list(range(min(positions), max(positions) + 1)):
        return {"positions": {"start": min(positions), "end": max(positions)}}
    return {"positions_list": positions}


def _preferred_serial_examples(examples: list[str]) -> list[str]:
    """
    Prefer examples that look like real serials (letters+digits) and are not obvious artifacts.
    Also drop examples that are strict substrings of a longer example.
    """
    cleaned: list[str] = []
    for e in examples or []:
        if not isinstance(e, str):
            continue
        t = re.sub(r"[^A-Z0-9-]", "", e.upper()).strip()
        if not t:
            continue
        if t.startswith("STYLE"):
            continue
        if not any(ch.isdigit() for ch in t):
            continue
        cleaned.append(t)
    # Prefer those containing at least one letter and one digit.
    rich = [e for e in cleaned if any(ch.isalpha() for ch in e) and any(ch.isdigit() for ch in e)]
    pool = rich or cleaned
    # Unique, longest-first.
    uniq: list[str] = []
    for e in sorted(set(pool), key=lambda x: (-len(x), x)):
        if any(e != other and e in other for other in uniq):
            continue
        uniq.append(e)
    return uniq


def _try_extract_from_color_legend(record: dict, section_title: str) -> dict | None:
    """
    If the page shows a colored example in HTML (red/green/blue spans), extract deterministic
    position ranges. Many pages include an explicit legend, but some (e.g. Bosch water heater styles)
    use colors without a legend line.
    """
    section_text = (record.get("section_text") or "")
    raw_html_path = record.get("raw_html_path") or ""
    if not raw_html_path:
        return None
    try:
        html = Path(raw_html_path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    # Find occurrences of this style. Prefer the one whose <h1> contains colored spans.
    title_rx = _fuzzy_title_regex(section_title)
    matches = [m.start() for m in title_rx.finditer(html)]
    if not matches:
        return None

    candidates = _preferred_serial_examples(record.get("example_values") or [])

    def parse_colored_block_window(pos: int) -> tuple[list[tuple[str, str]], str] | None:
        window = html[pos : pos + 20000]
        # Find candidate blocks and select one that matches the fuzzy title.
        # Some pages use <h1>, others use <p> for the style examples.
        blocks = re.findall(r"<(?:h1|p)[^>]*>.*?</(?:h1|p)>", window, flags=re.IGNORECASE | re.DOTALL)
        for blk in blocks[:18]:
            if title_rx.search(blk):
                parser = _ColoredTextParser()
                parser.feed(blk)
                parser.close()
                if not parser.chars:
                    continue
                if not any(c in {"RED", "GREEN", "BLUE"} for _ch, c in parser.chars):
                    continue
                example_all = "".join([ch for ch, _c in parser.chars])
                if len(example_all) < 6 or not any(ch.isdigit() for ch in example_all):
                    continue

                # Prefer blocks where we can align to a known example serial.
                for cand in candidates:
                    cand_norm = re.sub(r"[^A-Z0-9]", "", cand.upper())
                    if cand_norm and cand_norm in example_all:
                        return (parser.chars, cand_norm)
        return None

    chars: list[tuple[str, str]] | None = None
    aligned_example: str | None = None
    for pos in matches[:8]:
        parsed = parse_colored_block_window(pos)
        if parsed:
            chars, aligned_example = parsed
            break
    if not chars:
        return None

    # Map legend colors to fields.
    date_fields: dict = {}
    year_pos = _positions_from_color(chars, "RED")
    month_pos = _positions_from_color(chars, "GREEN")
    week_pos = _positions_from_color(chars, "BLUE")
    if year_pos:
        date_fields["year"] = year_pos
    if month_pos:
        date_fields["month"] = month_pos
    if week_pos:
        date_fields["week"] = week_pos
    if "year" not in date_fields:
        return None

    if not aligned_example:
        return None
    example_all = "".join([ch for ch, _c in chars])
    slice_start = example_all.find(aligned_example)
    if slice_start == -1:
        return None
    example = aligned_example

    # Slice chars down to just the serial token and recompute positions.
    chars = chars[slice_start : slice_start + len(example)]
    year_pos = _positions_from_color(chars, "RED")
    month_pos = _positions_from_color(chars, "GREEN")
    week_pos = _positions_from_color(chars, "BLUE")
    date_fields = {}
    if year_pos:
        date_fields["year"] = year_pos
    if month_pos:
        date_fields["month"] = month_pos
    if week_pos:
        date_fields["week"] = week_pos
    if "year" not in date_fields:
        return None

    return {"date_fields": date_fields, "example_from_html": example}


def _extract_positions(text: str) -> dict | None:
    t = _normalize_word_ordinals(" ".join(text.split()))
    max_position = 60  # guardrail: positions should be small; avoid misreading year ranges like 1960–1979

    # Patterns like "first 4 digits"
    m = _FIRST_N_RE.search(t)
    if m:
        n = int(m.group(1))
        if 0 < n <= max_position:
            return {"positions": {"start": 1, "end": n}}

    # Patterns like "positions 3-4" or "digits 1 and 2"
    m = _DIGIT_RANGE_RE.search(t)
    if m:
        start = int(m.group(1))
        end = int(m.group(2))
        if start > end:
            start, end = end, start
        if 0 < start <= max_position and 0 < end <= max_position:
            return {"positions": {"start": start, "end": end}}
    m = _DIGIT_PAIR_RE.search(t)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        if 0 < a <= max_position and 0 < b <= max_position:
            start, end = (a, b) if a <= b else (b, a)
            return {"positions": {"start": start, "end": end}}

    m = _RANGE_RE.search(t)
    if m:
        start = int(m.group(1))
        end = int(m.group(3))
        if start <= 0 or end <= 0 or start > max_position or end > max_position:
            return None
        if start > end:
            start, end = end, start
        return {"positions": {"start": start, "end": end}}
    ords = [int(m.group(1)) for m in _ORDINAL_RE.finditer(t)]
    if len(ords) >= 2 and ("combined" in t.lower() or "&" in t or "and" in t.lower()):
        # If non-contiguous, represent explicitly.
        uniq = []
        for o in ords:
            if o <= max_position and o not in uniq:
                uniq.append(o)
        if len(uniq) >= 2:
            return {"positions_list": uniq}
    if len(ords) == 1:
        if ords[0] <= max_position:
            return {"positions": {"start": ords[0], "end": ords[0]}}
    return None


def _find_position_snippet(section_text: str, field: str) -> str | None:
    field_terms = {
        "year": ["year", "yr", "yy"],
        "month": ["month", "mo", "mm"],
        "week": ["week", "wk"],
        "day": ["day"],
    }[field]

    field_re = r"(?:%s)" % "|".join([re.escape(t) for t in field_terms])

    def slice_to_field_clause(line: str) -> str:
        """
        Many sections pack multiple field instructions into a single line (year + month + codes).
        Slice the line down to the clause that starts at the target field term and ends before the
        next field term (year/month/week/day) if present.
        """
        if not line:
            return line
        ll = line.lower()
        starts = [ll.find(t) for t in field_terms if ll.find(t) >= 0]
        if not starts:
            return line
        start = min(starts)
        # Stop at the next field term mention after the start.
        other_terms = ["year", "month", "week", "day"]
        cut_points = []
        for t in other_terms:
            pos = ll.find(t, start + 1)
            if pos >= 0:
                cut_points.append(pos)
        end = min(cut_points) if cut_points else len(line)
        return line[start:end].strip()

    # Prefer explicit "<field> of manufacture..." patterns first.
    m = re.search(rf"{field_re}\s+of\s+manufacture[^\n.]*([.\n]|$)", section_text, flags=re.IGNORECASE)
    if m:
        return slice_to_field_clause(m.group(0))

    # Fallback: scan lines for "year/month/week/day" + "position/digit/character" language.
    for line in [l.strip() for l in section_text.splitlines() if l.strip()]:
        ll = line.lower()
        if not any(t in ll for t in field_terms):
            continue
        if any(k in ll for k in ["position", "digit", "character", "chars", "char", "pos", "letter"]):
            return slice_to_field_clause(line)
        if any(k in ll for k in ["can be determined", "determined by", "indicates", "represents", "is the"]):
            return slice_to_field_clause(line)
    return None


def _snippet_letter_is_value(snippet: str) -> bool:
    """
    True when the snippet indicates the date field itself is encoded as a letter code
    (requiring a chart/mapping), not when "letter" is mentioned only as an anchor/delimiter.
    """
    s = " ".join((snippet or "").lower().split())
    # Normalize spaced ordinals: "1 st" -> "1st"
    s = re.sub(r"\b(\d+)\s+(st|nd|rd|th)\b", r"\1\2", s, flags=re.IGNORECASE)
    if "letter" not in s:
        return False
    # Anchor/delimiter phrasing (digits relative to a letter) is NOT a letter-coded value.
    if any(p in s for p in ["preceding the letter", "before the letter", "after the letter", "following the middle letter", "middle letter"]):
        return False
    # Common letter-coded language.
    if any(p in s for p in ["letter digit", "letter code", "letter indicates", "letter is", "is the letter", "represented by the letter"]):
        return True
    # If it explicitly says to use a letter position for the field, treat as letter-coded.
    if re.search(r"\b(?:\d+(?:st|nd|rd|th)|first|second|third)\s+letter\b", s, flags=re.IGNORECASE):
        return True
    return False


def _find_middle_letter_index(example: str) -> int | None:
    """
    Attempt to identify a "middle letter" / factory-code letter position in a serial example.
    Many Building-Center pages describe date digits relative to this letter.

    Returns 1-based index of the letter.
    """
    if not example:
        return None
    s = example.upper()
    m = re.search(r"\d([A-Z])\d", s)
    if m:
        return m.start(1) + 1  # 1-based
    # Fallback: pick the first letter that has digits somewhere after it (common serial layouts).
    for i, ch in enumerate(s, start=1):
        if "A" <= ch <= "Z" and any(c.isdigit() for c in s[i:]):
            return i
    return None


def _convert_relative_to_absolute(pos_spec: dict, ref_index_1based: int) -> dict | None:
    """
    Convert a positions/positions_list spec interpreted as offsets from a reference index
    into absolute 1-based positions within the serial string.
    """
    if not isinstance(pos_spec, dict) or not ref_index_1based:
        return None
    if "positions" in pos_spec and isinstance(pos_spec["positions"], dict):
        start = int(pos_spec["positions"]["start"])
        end = int(pos_spec["positions"]["end"])
        return {"positions": {"start": ref_index_1based + start, "end": ref_index_1based + end}}
    if "positions_list" in pos_spec and isinstance(pos_spec["positions_list"], list):
        return {"positions_list": [ref_index_1based + int(p) for p in pos_spec["positions_list"]]}
    return None


def _serial_regex_from_examples(examples: list[str]) -> str:
    cleaned = [e for e in examples if isinstance(e, str) and e]
    if not cleaned:
        return ""
    lengths = sorted({len(e) for e in cleaned})
    if len(lengths) != 1:
        # Fallback: variable length examples (rare). Keep conservative but still alnum-only.
        alphabet = "A-Z0-9" + ("-" if any("-" in e for e in cleaned) else "")
        return rf"^[{alphabet}]{{{min(lengths)},{max(lengths)}}}$"

    length = lengths[0]
    cols: list[set[str]] = [set() for _ in range(length)]
    for e in cleaned:
        if len(e) != length:
            continue
        for i, ch in enumerate(e.upper()):
            cols[i].add(ch)

    def token_for(chars: set[str]) -> str:
        if not chars:
            return r"[A-Z0-9]"
        if chars.issubset(set("0123456789")):
            return r"\d"
        if chars.issubset(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")):
            s = "".join(sorted(chars))
            # If many letters, don't enumerate; keep broad.
            if len(chars) > 10:
                return r"[A-Z]"
            return f"[{re.escape(s)}]"
        if chars.issubset(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")):
            return r"[A-Z0-9]"
        if chars.issubset(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")):
            return r"[A-Z0-9-]"
        return r"."

    tokens = [token_for(c) for c in cols]

    # Collapse runs of identical tokens: \d\d\d -> \d{3}
    parts: list[str] = []
    run_tok = None
    run_len = 0
    for tok in tokens + [None]:
        if tok == run_tok:
            run_len += 1
            continue
        if run_tok is not None:
            if run_tok == r"\d" and run_len > 1:
                parts.append(rf"\d{{{run_len}}}")
            elif run_tok in {r"[A-Z]", r"[A-Z0-9]", r"[A-Z0-9-]"} and run_len > 1:
                parts.append(run_tok[:-1] + rf"]{{{run_len}}}")
            elif run_len > 1 and run_tok.startswith("[") and run_tok.endswith("]"):
                parts.append(run_tok + rf"{{{run_len}}}")
            else:
                parts.append(run_tok * run_len)
        run_tok = tok
        run_len = 1

    return "^" + "".join(parts) + "$"


_MONTH_NAME_TO_NUM: dict[str, int] = {
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


def _extract_letter_mapping(section_text: str) -> dict[str, int] | None:
    # Extract mappings like:
    # - A=1, B=2
    # - A - Jan, B - February
    # - A : 2009 (year mapping)
    mapping: dict[str, int] = {}
    # Month name mapping
    for m in re.finditer(r"\b([A-Z])\s*[-:=]\s*([A-Z]{3,9}|\d{1,4})\b", section_text, flags=re.IGNORECASE):
        key = m.group(1).upper()
        val_raw = m.group(2).upper()
        if val_raw.isdigit():
            mapping[key] = int(val_raw)
            continue
        if val_raw in _MONTH_NAME_TO_NUM:
            mapping[key] = _MONTH_NAME_TO_NUM[val_raw]
            continue
    # Looser: "A JAN" sequences in tables
    for m in re.finditer(r"\b([A-Z])\s+(JANUARY|JAN|FEBRUARY|FEB|MARCH|MAR|APRIL|APR|MAY|JUNE|JUN|JULY|JUL|AUGUST|AUG|SEPTEMBER|SEPT|SEP|OCTOBER|OCT|NOVEMBER|NOV|DECEMBER|DEC)\b", section_text, flags=re.IGNORECASE):
        mapping[m.group(1).upper()] = _MONTH_NAME_TO_NUM[m.group(2).upper()]

    if len(mapping) >= 3:
        return mapping
    return None


def _heuristic_normalize_one(record: dict) -> dict:
    section_text = (record.get("section_text") or "").strip()
    section_title = (record.get("section_title") or "").strip()
    example_values = _preferred_serial_examples(record.get("example_values") or [])
    style_example_raw = (record.get("style_example_raw") or "").strip()
    image_urls = record.get("image_urls") or []

    def hydrate_section_text() -> str:
        """
        Some pages include a compact "Style N: <example>" list near the top, and then the real
        decoding instructions later on the same page. When the extracted section_text is too short,
        use raw_html_path to locate a better text window.
        """
        raw_html_path = record.get("raw_html_path") or ""
        if not raw_html_path:
            return section_text
        try:
            html = Path(raw_html_path).read_text(encoding="utf-8", errors="replace")
        except Exception:
            return section_text
        if not html:
            return section_text

        # Search for the exact title string; prefer an occurrence whose surrounding text contains decode keywords.
        needle = section_title
        if not needle or len(needle) < 6:
            return section_text
        title_rx = _fuzzy_title_regex(needle)
        positions = [m.start() for m in title_rx.finditer(html)]
        if not positions:
            return section_text

        def window_text(pos: int) -> str:
            snippet = html[pos : pos + 7000]
            # Strip tags quickly for keyword detection.
            text = re.sub(r"<[^>]+>", " ", snippet)
            text = _collapse_ws(text)
            return text[:1600]

        best = ""
        for pos in positions[:6]:
            txt = window_text(pos)
            ll = txt.lower()
            if ("year" in ll and "manufact" in ll) and any(k in ll for k in ["digit", "digits", "position", "character"]):
                return txt
            if len(txt) > len(best):
                best = txt
        return best or section_text

    # If a section was synthesized from an example list and has almost no content, try to hydrate from the HTML.
    if section_title.lower().startswith("style") and len(section_text) < 80:
        hydrated = hydrate_section_text()
        if hydrated and len(hydrated) > len(section_text):
            section_text = hydrated
            record = dict(record)
            record["section_text"] = section_text

    # If the page uses the "Legend: Year=RED; Month=GREEN; Week=BLUE" convention, try extracting positions
    # directly from the colored HTML example.
    brand_l = (record.get("brand") or "").strip().lower()
    # Trane Style 1 is explicitly era-dependent (2002–2009 vs 2010+). The colored legend examples on the page
    # include both eras and are not sufficient to derive a single deterministic rule, so don't short-circuit
    # on legend extraction here.
    if not (brand_l == "trane" and section_title.lower().startswith("style 1:")):
        legend_extracted = _try_extract_from_color_legend(record, section_title)
        if legend_extracted:
            # Merge extracted positions into date_fields so we can produce a decode rule even when the
            # section text doesn't include position statements (common on some water heater pages).
            extracted_date_fields = legend_extracted["date_fields"]
            html_example = legend_extracted["example_from_html"]
            if not example_values:
                example_values = [html_example]
            elif html_example not in example_values:
                example_values = [html_example] + example_values
            # If we can build a regex and have year positions, emit decode.
            serial_regex = _serial_regex_from_examples(example_values)
            if serial_regex:
                return {
                    "rule_type": "decode",
                    "brand": record.get("brand"),
                    "style_name": section_title,
                    "serial_regex": serial_regex,
                    "date_fields": extracted_date_fields,
                    "example_serials": example_values,
                    "decade_ambiguity": {"is_ambiguous": True, "notes": "Year not 4 digits"},
                    "evidence_excerpt": _evidence_excerpt(section_text),
                    "source_url": record.get("source_url"),
                    "retrieved_on": record.get("retrieved_on"),
                    "image_urls": image_urls,
                }

    # Some pages include an "Example serial number styles/formats found" list where each <li> contains
    # a bare "Style N:" marker and an example serial, but no decoding instructions. These create a lot of noise.
    # If the title is bare and the body contains no decoding keywords, skip it.
    if _BARE_STYLE_TITLE_RE.match(section_title):
        ll = section_text.lower()
        has_decode_keywords = any(k in ll for k in ["year", "month", "week", "day", "manufact", "digit", "char", "position"])
        if not has_decode_keywords and len(section_text) <= 120:
            return {
                "skip": True,
                "reason": "example_list_only",
                "source_url": record.get("source_url"),
                "retrieved_on": record.get("retrieved_on"),
                "brand": record.get("brand"),
                "section_title": record.get("section_title"),
                "raw_html_path": record.get("raw_html_path"),
            }

    # Guidance-only record: explicit instruction to contact manufacturer / no deterministic decode.
    if section_text and _CONTACT_MFR_RE.search(section_text):
        return {
            "rule_type": "guidance",
            "brand": record.get("brand"),
            "style_name": section_title,
            "serial_regex": "",
            "date_fields": {},
            "example_serials": [],
            "decade_ambiguity": {"is_ambiguous": True, "notes": "No deterministic decode rule provided"},
            "guidance_action": "contact_manufacturer",
            "guidance_text": section_text[:800],
            "evidence_excerpt": _evidence_excerpt(section_text),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "image_urls": image_urls,
        }

    # Preserve guidance behavior.
    guidance = _manual_normalize_one(record)
    if guidance.get("rule_type") == "guidance":
        return guidance

    if not section_text or not section_title.lower().startswith("style"):
        return {
            "skip": True,
            "reason": "not_a_style_section",
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "brand": record.get("brand"),
            "section_title": record.get("section_title"),
            "raw_html_path": record.get("raw_html_path"),
        }

    extracted_mapping = _extract_letter_mapping(section_text)
    has_mapping_text = extracted_mapping is not None

    # Special-case: some pages describe conditional logic within a single Style (e.g., Trane style changed in 2010).
    # We split into multiple deterministic rules based on the explicit conditions and example prefixes.
    if (record.get("brand") or "").strip().lower() == "trane" and section_title.lower().startswith("style 1:") and example_values:
        st_lower = section_text.lower()
        if "from 2002 to 2009" in st_lower and "starting in 2010" in st_lower:
            ex_3 = [e for e in example_values if re.match(r"^\d{3}[A-Z0-9]+$", e)]
            ex_4 = [e for e in example_values if re.match(r"^\d{4}[A-Z0-9]+$", e)]
            if ex_3 and ex_4:
                base = {
                    "rule_type": "decode",
                    "brand": record.get("brand"),
                    "evidence_excerpt": _evidence_excerpt(section_text),
                    "source_url": record.get("source_url"),
                    "retrieved_on": record.get("retrieved_on"),
                    "image_urls": image_urls,
                    # Both variants use 1- or 2-digit year codes; decade ambiguity must be surfaced.
                    "decade_ambiguity": {"is_ambiguous": True, "notes": "Year code is not 4 digits"},
                }
                return [
                    {
                        **base,
                        "style_name": "Style 1 (2002-2009)",
                        "serial_regex": r"^(?=.*[A-Z])\d{3}[A-Z0-9]{3,30}$",
                        "date_fields": {
                            "year": {
                                "positions": {"start": 1, "end": 1},
                                "transform": {"type": "year_add_base", "base": 2000, "min_year": 2002, "max_year": 2009},
                            },
                            "week": {"positions": {"start": 2, "end": 3}},
                        },
                        "example_serials": ex_3,
                    },
                    {
                        **base,
                        "style_name": "Style 1 (2010+)",
                        "serial_regex": r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$",
                        "date_fields": {
                            "year": {"positions": {"start": 1, "end": 2}, "transform": {"type": "year_add_base", "base": 2000, "min_year": 2010}},
                            "week": {"positions": {"start": 3, "end": 4}},
                        },
                        "example_serials": ex_4,
                    },
                ]

    # Parse date field position statements.
    date_fields: dict = {}
    missing_mappings: list[str] = []
    field_notes: list[str] = []
    for field in ["year", "month", "week", "day"]:
        snippet = _find_position_snippet(section_text, field)
        if not snippet:
            continue
        if _snippet_letter_is_value(snippet) and not has_mapping_text:
            # Do not downgrade the entire style if we can still decode year/week, etc.
            # Record that this particular field requires a chart/manual mapping.
            chart_spec: dict = {"requires_chart": True, "snippet": snippet[:200]}
            # If the snippet also includes an explicit position/digit/character range, keep it;
            # OCR-derived mappings can then make the field deterministic without manual work.
            pos = _extract_positions(snippet)
            if pos:
                chart_spec.update(pos)
            date_fields[field] = chart_spec
            missing_mappings.append(field)
            continue
        pos = _extract_positions(snippet)
        # Handle instructions expressed relative to a "middle letter" (factory code) where the ordinals
        # represent offsets from that letter (e.g., "3rd & 4th numbers following the middle letter").
        if pos and re.search(r"\bfollowing the middle letter\b", snippet, flags=re.IGNORECASE) and example_values:
            mid = _find_middle_letter_index(example_values[0])
            if mid:
                abs_pos = _convert_relative_to_absolute(pos, mid)
                if abs_pos:
                    pos = abs_pos

        # Handle variable-width prefix year codes like "1st one or two digits preceding the letter".
        if field == "year" and re.search(r"\bone\s+or\s+two\b", snippet, flags=re.IGNORECASE):
            if re.search(r"\bpreced(?:ing|e)\s+the\s+letter\b", snippet, flags=re.IGNORECASE):
                pos = {"pattern": {"regex": r"^(\d{1,2})[A-Z]", "group": 1}}

        # If the instructions explicitly say to ignore/disregard leading letters, shift positions based on example.
        #
        # Some pages say "1st digit / 2nd digit / etc" even when the serial begins with letters (e.g. "FD687...").
        # In those cases, "digit" usually means "numeric digit" (not the first character). Apply the same shift
        # even if the text doesn't explicitly say "ignore letters".
        if pos and example_values:
            snippet_l = snippet.lower()
            digit_language = bool(re.search(r"\b(digit|digits|numerical)\b", snippet_l)) or (
                bool(re.search(r"\bnumbers?\b", snippet_l)) and "serial number" not in snippet_l
            )
            character_language = bool(re.search(r"\b(char|chars|character|characters)\b", snippet_l))
            ex0 = next((e for e in example_values if re.match(r"^[A-Z]+\\d", e)), example_values[0]).upper()
            ex_len = len(ex0)

            def slice_from_pos(example: str, spec: dict) -> str | None:
                if not example or not isinstance(spec, dict):
                    return None
                if "positions" in spec and isinstance(spec["positions"], dict):
                    a = int(spec["positions"]["start"])
                    b = int(spec["positions"]["end"])
                    if a < 1 or b < 1 or a > len(example) or b > len(example):
                        return None
                    if a > b:
                        a, b = b, a
                    return example[a - 1 : b]
                if "positions_list" in spec and isinstance(spec["positions_list"], list):
                    out = []
                    for p in spec["positions_list"]:
                        pp = int(p)
                        if pp < 1 or pp > len(example):
                            return None
                        out.append(example[pp - 1])
                    return "".join(out)
                return None

            def shift_pos(spec: dict, shift: int) -> dict:
                if "positions" in spec and isinstance(spec["positions"], dict):
                    return {"positions": {"start": int(spec["positions"]["start"]) + shift, "end": int(spec["positions"]["end"]) + shift}}
                if "positions_list" in spec and isinstance(spec["positions_list"], list):
                    return {"positions_list": [int(p) + shift for p in spec["positions_list"]]}
                return spec

            prefix_letters = 0
            for ch in ex0:
                if ch.isdigit():
                    break
                if "A" <= ch <= "Z":
                    prefix_letters += 1
                else:
                    break

            if prefix_letters and digit_language and not character_language:
                shifted = shift_pos(pos, prefix_letters)
                unshifted_value = slice_from_pos(ex0, pos)
                shifted_value = slice_from_pos(ex0, shifted)
                # Only apply the shift when it fixes an obvious non-digit extraction and stays in bounds.
                if shifted_value is not None and shifted_value.isdigit() and (unshifted_value is None or not unshifted_value.isdigit()):
                    pos = shifted

        if pos and _IGNORE_LETTERS_RE.search(snippet) and example_values:
            # Prefer an example with a leading letter prefix (e.g., FDxxxx) when shifting.
            ex0 = next((e for e in example_values if re.match(r"^[A-Z]+\\d", e)), example_values[0]).upper()
            prefix_letters = 0
            for ch in ex0:
                if ch.isdigit():
                    break
                if "A" <= ch <= "Z":
                    prefix_letters += 1
                else:
                    break
            if prefix_letters:
                shifted = shift_pos(pos, prefix_letters)
                # Only apply if it remains in-bounds for the preferred example.
                if slice_from_pos(ex0, shifted) is not None:
                    pos = shifted

        if pos:
            date_fields[field] = pos
            if extracted_mapping is not None and _snippet_letter_is_value(snippet):
                date_fields[field]["mapping"] = extracted_mapping
            # Some pages note the digits are reversed (e.g., "29" -> "92") to get the year.
            if field == "year" and re.search(r"\brevers", snippet, flags=re.IGNORECASE):
                date_fields[field]["transform"] = {"type": "reverse_string"}

    if "year" not in date_fields:
        refs = ""
        if image_urls:
            refs = " Images: " + ", ".join(image_urls[:3])
            return {
                "rule_type": "guidance",
                "brand": record.get("brand"),
                "style_name": section_title,
                "serial_regex": "",
                "date_fields": {},
                "example_serials": [],
                "decade_ambiguity": {"is_ambiguous": True, "notes": "Year positions not captured from text; chart/image likely required"},
                "guidance_action": "chart_required",
                "guidance_text": ("Year positions not captured from text; chart/manual review required." + refs).strip(),
                "evidence_excerpt": _evidence_excerpt(section_text),
                "source_url": record.get("source_url"),
                "retrieved_on": record.get("retrieved_on"),
                "image_urls": image_urls,
            }

        # No images and no year positions: keep as guidance so downstream can surface "no data" deterministically.
        txt = section_text.strip()
        if not txt:
            txt = "No decoding instructions captured for this style."
        return {
            "rule_type": "guidance",
            "brand": record.get("brand"),
            "style_name": section_title,
            "serial_regex": "",
            "date_fields": {},
            "example_serials": [],
            "decade_ambiguity": {"is_ambiguous": True, "notes": "No year position instructions found"},
            "guidance_action": "no_data",
            "guidance_text": txt[:800],
            "evidence_excerpt": _evidence_excerpt(txt),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "image_urls": image_urls,
        }

    def _try_example_from_title_or_raw(min_len: int) -> list[str]:
        """
        Some extracted sections lose example_values, but the style title (or style_example_raw)
        often contains a concrete example serial. Try to recover a plausible example to enable
        regex generation and validation.
        """
        candidates: list[str] = []
        for src in [section_title, style_example_raw]:
            if not src:
                continue
            t = src
            # Remove the leading "Style N:" and arrows.
            t = re.sub(r"^\s*→?\s*style\s*\d+\s*:\s*", "", t, flags=re.IGNORECASE)
            # Prefer the first token containing at least one digit.
            for tok in re.split(r"[\s,/;()]+", t):
                tok = tok.strip()
                if not tok:
                    continue
                up = re.sub(r"[^A-Z0-9-]", "", tok.upper())
                if not up:
                    continue
                if up.startswith("STYLE"):
                    continue
                if not any(ch.isdigit() for ch in up):
                    continue
                # Avoid obvious artifacts (e.g., "3-DIGIT", "5TH-7TH").
                if re.search(r"\bDIGIT\b", up) or re.search(r"\bPOSITION", up):
                    continue
                if min_len and len(up) < min_len:
                    continue
                candidates.append(up)
        return _preferred_serial_examples(candidates)

    if not example_values:
        required_max_pos = 0
        for spec in (date_fields or {}).values():
            if not isinstance(spec, dict) or spec.get("requires_chart") is True:
                continue
            if "positions" in spec and isinstance(spec["positions"], dict):
                required_max_pos = max(required_max_pos, int(spec["positions"].get("end", 0)))
            if "positions_list" in spec and isinstance(spec["positions_list"], list):
                try:
                    required_max_pos = max(required_max_pos, max(int(p) for p in spec["positions_list"]))
                except Exception:
                    continue
        example_values = _try_example_from_title_or_raw(required_max_pos)

    # If we have no trustworthy examples (or the title is clearly a placeholder), keep as guidance.
    if not example_values or (style_example_raw and _PLACEHOLDER_TITLE_RE.search(style_example_raw)):
        return {
            "rule_type": "guidance",
            "brand": record.get("brand"),
            "style_name": section_title,
            "serial_regex": "",
            "date_fields": date_fields,
            "example_serials": example_values,
            "decade_ambiguity": {"is_ambiguous": True, "notes": "No validated example serial for this style"},
            "guidance_action": "pattern_no_example",
            "guidance_text": section_text[:800],
            "evidence_excerpt": _evidence_excerpt(section_text),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "image_urls": image_urls,
        }

    serial_regex = _serial_regex_from_examples(example_values)
    if not serial_regex:
        return {
            "rule_type": "guidance",
            "brand": record.get("brand"),
            "style_name": section_title,
            "serial_regex": "",
            "date_fields": date_fields,
            "example_serials": example_values,
            "decade_ambiguity": {"is_ambiguous": True, "notes": "Could not build regex from examples"},
            "guidance_action": "pattern_no_example",
            "guidance_text": section_text[:800],
            "evidence_excerpt": _evidence_excerpt(section_text),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "image_urls": image_urls,
        }

    # Decade ambiguity if year isn't 4 digits.
    year_info = date_fields.get("year", {})
    year_width = None
    if "positions" in year_info:
        year_width = year_info["positions"]["end"] - year_info["positions"]["start"] + 1
    elif "positions_list" in year_info:
        year_width = len(year_info["positions_list"])
    ambiguous = (year_width is None) or (year_width < 4)

    rule: dict = {
        "rule_type": "decode",
        "brand": record.get("brand"),
        "style_name": section_title,
        "serial_regex": serial_regex,
        "date_fields": date_fields,
        "example_serials": example_values,
        "decade_ambiguity": {"is_ambiguous": bool(ambiguous), "notes": "Year not 4 digits" if ambiguous else ""},
        "evidence_excerpt": _evidence_excerpt(section_text),
        "source_url": record.get("source_url"),
        "retrieved_on": record.get("retrieved_on"),
        "image_urls": image_urls,
    }

    # If any date fields require a chart/manual mapping, keep that as guidance text but still allow decoding year/week.
    if missing_mappings:
        rule["guidance_action"] = "chart_required"
        rule["guidance_text"] = (
            f"Some date fields require chart/manual mapping: {', '.join(sorted(set(missing_mappings)))}."
        )
    return rule


def _manual_normalize_one(record: dict) -> dict:
    section_text = (record.get("section_text") or "").strip()
    section_title = (record.get("section_title") or "").strip()
    example_values = record.get("example_values") or []
    image_urls = record.get("image_urls") or []

    # Guidance-only record: no decode possible, explicitly instructs contacting manufacturer.
    if section_text and _CONTACT_MFR_RE.search(section_text) and not example_values:
        return {
            "rule_type": "guidance",
            "brand": record.get("brand"),
            "style_name": section_title,
            "serial_regex": "",
            "date_fields": {},
            "example_serials": [],
            "decade_ambiguity": {"is_ambiguous": True, "notes": "No deterministic decode rule provided"},
            "guidance_action": "contact_manufacturer",
            "guidance_text": section_text[:800],
            "evidence_excerpt": _evidence_excerpt(section_text),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "image_urls": image_urls,
        }

    return {
        "skip": True,
        "reason": "manual_normalization_required (no API key configured); run with an LLM provider to create decode rules",
        "source_url": record.get("source_url"),
        "retrieved_on": record.get("retrieved_on"),
        "brand": record.get("brand"),
        "section_title": record.get("section_title"),
        "raw_html_path": record.get("raw_html_path"),
    }


def _heuristic_attribute_from_model_decoder(record: dict) -> dict:
    section_text = (record.get("section_text") or "").strip()
    examples = record.get("example_values") or []
    brand = record.get("brand")
    image_urls = record.get("image_urls") or []
    pdf_urls = record.get("pdf_urls") or []

    # Only handle model decoder pages for now
    if record.get("page_type") != "tonnage_decoder":
        return {"skip": True, "reason": "not_model_decoder"}

    # We start with capacity-related attributes because they're the most common explicit ones.
    attr_tons = "NominalCapacityTons"
    attr_code = "NominalCapacityCode"

    # Parse mapping lines like "18 = 1.5 tons"
    mapping: dict[str, float] = {}
    for m in re.finditer(r"\b(\d{2,3})\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*tons?\b", section_text, flags=re.IGNORECASE):
        mapping[m.group(1)] = float(m.group(2))

    # Parse position statements like "7th and 8th digits" / "3rd and 4th digits"
    pos = None
    m = re.search(r"\b(\d+)(?:st|nd|rd|th)\s+and\s+(\d+)(?:st|nd|rd|th)\s+(?:digits?|numbers?)\b", section_text, flags=re.IGNORECASE)
    if m:
        start = int(m.group(1))
        end = int(m.group(2))
        if 0 < start <= 60 and 0 < end <= 60:
            if start > end:
                start, end = end, start
            pos = {"start": start, "end": end}

    # If the page indicates the code is "in the middle" / not anchored, do not emit a deterministic decode rule.
    ambiguous_location = bool(
        re.search(r"\b(in\s+the\s+middle|somewhere\s+in\s+the\s+middle|center\s+of\s+the\s+model)\b", section_text, flags=re.IGNORECASE)
    )

    # Infer an explicit transform only if it is stated in text (no guessing).
    transform = None
    if re.search(r"\bdivide(?:d)?\s+by\s+12\b", section_text, flags=re.IGNORECASE) and re.search(r"\btons?\b", section_text, flags=re.IGNORECASE):
        transform = {"expression": "tons = code / 12"}

    # If we have neither mapping nor positions/pattern, we can't extract anything deterministically.
    # If the page has a nomenclature diagram (image/pdf), preserve it as guidance so it can be OCR'd or manually transcribed later.
    if not mapping and not pos:
        refs: list[str] = []
        refs.extend([u for u in (pdf_urls or []) if isinstance(u, str) and u])
        refs.extend([u for u in (image_urls or []) if isinstance(u, str) and u])
        refs_text = ""
        if refs:
            refs_text = " References: " + ", ".join(refs[:5])
        out: list[dict] = []
        if refs:
            out.append(
                {
                    "rule_type": "guidance",
                    "brand": brand,
                    "model_regex": "",
                    "attribute_name": "ModelNomenclature",
                    "value_extraction": {},
                    "units": "",
                    "examples": examples,
                    "limitations": "Model decoder content is in an image/PDF; OCR or manual transcription required for deterministic attributes.",
                    "evidence_excerpt": _evidence_excerpt(section_text),
                    "source_url": record.get("source_url"),
                    "retrieved_on": record.get("retrieved_on"),
                    "guidance_action": "chart_required",
                    "guidance_text": ("Model nomenclature requires image/PDF review." + refs_text).strip(),
                    "image_urls": image_urls,
                }
            )
        out.append(
            {
                "rule_type": "guidance",
                "brand": brand,
                "model_regex": "",
                "attribute_name": attr_tons,
                "value_extraction": {},
                "units": "Tons",
                "examples": examples,
                "limitations": "Model decoder text did not include a deterministic extraction rule.",
                "evidence_excerpt": _evidence_excerpt(section_text),
                "source_url": record.get("source_url"),
                "retrieved_on": record.get("retrieved_on"),
                "guidance_action": "chart_required" if refs else "no_data",
                "guidance_text": (section_text[:800] + refs_text)[:900],
                "image_urls": image_urls,
            }
        )
        return out

    # Always emit a safe CapacityCode attribute when we can extract code positions/pattern.
    code_extraction: dict = {"data_type": "Text"}
    if pos:
        code_extraction["positions"] = pos
    elif mapping:
        codes = sorted(mapping.keys(), key=lambda x: (-len(x), x))
        code_extraction["pattern"] = {"regex": r"(" + "|".join([re.escape(c) for c in codes]) + r")", "group": 1}
    else:
        code_extraction = {}

    # If we can produce tons deterministically, emit tons; otherwise emit guidance for tons.
    tons_extraction: dict = {"data_type": "Number"}
    if pos:
        tons_extraction["positions"] = pos
    elif mapping:
        codes = sorted(mapping.keys(), key=lambda x: (-len(x), x))
        tons_extraction["pattern"] = {"regex": r"(" + "|".join([re.escape(c) for c in codes]) + r")", "group": 1}

    if mapping:
        tons_extraction["mapping"] = mapping
    if transform:
        tons_extraction["transform"] = transform

    # Prefer mapping/transform for an actual decode rule only when the location is deterministic:
    # - positions exist, OR
    # - examples exist (so we can later validate tighter model_regex/placement), AND the page doesn't say "middle".
    if (mapping or transform) and not ambiguous_location and (pos or examples):
        return {
            "rule_type": "decode",
            "brand": brand,
            "model_regex": "",
            "attribute_name": attr_tons,
            "value_extraction": tons_extraction,
            "units": "Tons",
            "examples": examples,
            "limitations": "",
            "evidence_excerpt": _evidence_excerpt(section_text),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "image_urls": image_urls,
        }

    # If mapping exists but the code location is ambiguous, keep as guidance so downstream can still surface the table.
    if (mapping or transform) and (ambiguous_location or not (pos or examples)):
        refs = ""
        if image_urls:
            refs = " Images: " + ", ".join(image_urls[:3])
        return {
            "rule_type": "guidance",
            "brand": brand,
            "model_regex": "",
            "attribute_name": attr_tons,
            "value_extraction": tons_extraction,
            "units": "Tons",
            "examples": examples,
            "limitations": "Tonnage mapping exists but the model-code location is not deterministic from captured text.",
            "evidence_excerpt": _evidence_excerpt(section_text),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "guidance_action": "chart_required" if image_urls else "no_data",
            "guidance_text": ("Tonnage code location is ambiguous; manual review required." + refs).strip(),
            "image_urls": image_urls,
        }

    # Otherwise, emit the code as decode and a guidance for tons.
    if code_extraction:
        return {
            "rule_type": "decode",
            "brand": brand,
            "model_regex": "",
            "attribute_name": attr_code,
            "value_extraction": code_extraction,
            "units": "",
            "examples": examples,
            "limitations": "Extracts the capacity code only; no deterministic tons transform provided on the page.",
            "evidence_excerpt": _evidence_excerpt(section_text),
            "source_url": record.get("source_url"),
            "retrieved_on": record.get("retrieved_on"),
            "image_urls": image_urls,
        }

    return {
        "rule_type": "guidance",
        "brand": brand,
        "model_regex": "",
        "attribute_name": attr_tons,
        "value_extraction": {},
        "units": "Tons",
        "examples": examples,
        "limitations": "No deterministic extraction rule found.",
        "evidence_excerpt": _evidence_excerpt(section_text),
        "source_url": record.get("source_url"),
        "retrieved_on": record.get("retrieved_on"),
        "guidance_action": "no_data",
        "guidance_text": section_text[:800],
        "image_urls": image_urls,
    }


def _openai_normalize_one(record: dict, api_key: str, model: str) -> dict:
    import requests

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Normalize this extracted section:\n" + json.dumps(record, ensure_ascii=False),
            },
        ],
        "text": {"format": {"type": "json_object"}},
    }

    resp = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    # Responses API: prefer output_text if present; fall back to structured fields.
    output_text = data.get("output_text")
    if output_text:
        return json.loads(output_text)

    # Fallback: find first text content in output items.
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and "text" in content:
                return json.loads(content["text"])

    raise RuntimeError("OpenAI response did not include JSON output")


def cmd_normalize(args) -> int:
    extracted_dir = Path(args.extracted_dir)
    run_date = resolve_run_date(args.run_date, str(extracted_dir))
    out_dir = ensure_dir(Path(args.out_dir) / run_date)

    api_key = args.openai_api_key or os.getenv("OPENAI_API_KEY")
    if args.provider == "openai" and not api_key:
        raise SystemExit("Missing OpenAI API key. Pass --openai-api-key or set OPENAI_API_KEY.")

    if args.input_file:
        extracted_files = [extracted_dir / args.input_file]
    else:
        default = extracted_dir / "extracted_sections.jsonl"
        extracted_files = [default] if default.exists() else sorted(extracted_dir.glob("*.jsonl"))
    extracted_files = [p for p in extracted_files if p.exists()]
    if not extracted_files:
        raise SystemExit(f"No extracted JSONL files found in {extracted_dir}")

    out_serial = out_dir / "serial_rules.jsonl"
    out_attr = out_dir / "attribute_rules.jsonl"
    out_skips = out_dir / "skips.jsonl"

    max_sections = int(args.max_sections or 0)
    processed = 0
    seen_keys: set[tuple] = set()
    include_brands = set([b for b in (args.include_brand or []) if b])

    with (
        out_serial.open("w", encoding="utf-8") as f_serial,
        out_attr.open("w", encoding="utf-8") as f_attr,
        out_skips.open("w", encoding="utf-8") as f_skip,
    ):
        for path in extracted_files:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if include_brands and record.get("brand") not in include_brands:
                        continue
                    if args.provider == "manual":
                        normalized = _manual_normalize_one(record)
                    elif args.provider == "heuristic":
                        if record.get("page_type") == "tonnage_decoder":
                            normalized = _heuristic_attribute_from_model_decoder(record)
                        else:
                            normalized = _heuristic_normalize_one(record)
                    else:
                        normalized = _openai_normalize_one(record, api_key=api_key, model=args.openai_model)
                    processed += 1

                    normalized_items = normalized if isinstance(normalized, list) else [normalized]
                    for item in normalized_items:
                        # Dedupe common duplicates when the same record appears in multiple extracted files.
                        if item.get("skip") is not True:
                            dedupe_key = (
                                item.get("rule_type", "decode"),
                                item.get("brand"),
                                item.get("style_name"),
                                item.get("serial_regex"),
                                item.get("guidance_action"),
                                item.get("guidance_text"),
                                item.get("attribute_name"),
                                item.get("model_regex"),
                                item.get("source_url"),
                            )
                            if dedupe_key in seen_keys:
                                continue
                            seen_keys.add(dedupe_key)

                        if item.get("skip") is True:
                            f_skip.write(json.dumps(item, ensure_ascii=False) + "\n")
                        elif "serial_regex" in item:
                            f_serial.write(json.dumps(item, ensure_ascii=False) + "\n")
                        elif "attribute_name" in item:
                            f_attr.write(json.dumps(item, ensure_ascii=False) + "\n")
                        else:
                            f_skip.write(
                                json.dumps(
                                    {
                                        "skip": True,
                                        "reason": "Unrecognized normalized object shape",
                                        "normalized": item,
                                    },
                                    ensure_ascii=False,
                                )
                                + "\n"
                            )

                    if max_sections and processed >= max_sections:
                        break
            if max_sections and processed >= max_sections:
                break

    print(str(out_dir))
    return 0
