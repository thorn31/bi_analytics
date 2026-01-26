from __future__ import annotations

import csv
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path


_ALNUM_MODEL_RE = re.compile(r"\b[A-Z0-9][A-Z0-9-]{6,}\b")
_PLACEHOLDER_RE = re.compile(r"\b(?:ELECTRICAL|VOLTAGE)\s+([A-Z])\b", re.IGNORECASE)


@dataclass(frozen=True)
class VoltageMapping:
    code: str
    volts: str
    phase: str | None
    hz: str | None

    def normalized_value(self) -> str:
        v = self.volts.replace(" ", "")
        ph = (self.phase or "").strip()
        hz = (self.hz or "").strip()
        parts = [v]
        if ph:
            parts.append(ph)
        if hz:
            parts.append(hz)
        return "-".join(parts)


def _parse_fractional_number(value: str) -> float | None:
    """
    OCR often outputs 3½ as "3%" or "3 %". Also "1½" -> "1%".
    Keep this conservative: only interpret '%' as .5 when it is adjacent to a digit.
    """
    t = value.strip()
    if not t:
        return None
    t = t.replace("½", ".5").replace("¼", ".25").replace("¾", ".75")
    # Treat "3%" / "3 %" as 3.5
    t = re.sub(r"(\d)\s*%\b", r"\1.5", t)
    t = t.replace(" ", "")
    try:
        return float(t)
    except Exception:
        return None


def _parse_capacity_code_to_tons(text: str) -> dict[str, float]:
    """
    Extract mappings like:
      036 - 3 tons
      18 = 1.5 tons
      024 = 2 Ton
    """
    t = text.upper()
    out: dict[str, float] = {}

    for m in re.finditer(r"\b(\d{2,3})\s*(?:=|-|—)\s*([0-9]+(?:\.[0-9]+)?|\d\s*%|\d+½)\s*TON", t):
        code = m.group(1)
        val = _parse_fractional_number(m.group(2))
        if val is None:
            continue
        # Normalize to 0.5 increments (avoid OCR jitter)
        out[code] = round(val * 2.0) / 2.0

    return out


def _parse_code_to_value_lines(text: str, *, label: str, values: dict[str, str | list[str]]) -> dict[str, str]:
    """
    Generic parser for lines like:
      S Single-Stage
      T Two-Stage
      X = R410A
    `values` maps canonical output values -> accepted OCR keywords/synonyms.
    """
    t = text.upper()
    out: dict[str, str] = {}
    for canonical, keywords in values.items():
        keywords_list = keywords if isinstance(keywords, list) else [keywords]
        for kw in keywords_list:
            # Allow separators like '=', '-', ':', or whitespace
            rx = re.compile(rf"\b([A-Z0-9])\s*(?:=|-|:)?\s*{re.escape(str(kw).upper())}\b")
            for m in rx.finditer(t):
                out[m.group(1)] = canonical
    return out


def _parse_efficiency_code_ranges(text: str) -> dict[str, str]:
    """
    Extract code -> range mappings like:
      13.4-13.7=3
      16.0-16.9=6
    Returns { "3": "13.4-13.7", ... }
    """
    t = text.upper().replace(" ", "")
    out: dict[str, str] = {}
    for m in re.finditer(r"(\d{1,2}\.\d)\-(\d{1,2}\.\d)=([A-Z0-9])", t):
        lo, hi, code = m.group(1), m.group(2), m.group(3)
        out[code] = f"{lo}-{hi}"
    return out


def _normalize_text(value: str) -> str:
    return " ".join((value or "").replace("\xa0", " ").replace("\u202f", " ").split()).strip()


def _normalize_model_token(value: str) -> str:
    t = _normalize_text(value).upper()
    # Preserve dashes (many nomenclature formats rely on them)
    t = re.sub(r"[^A-Z0-9-]+", "", t)
    return t


def _extract_model_candidates(text: str) -> list[str]:
    def is_modelish(tok: str) -> bool:
        if len(tok) < 8:
            return False
        if "/" in tok:
            return False
        if not any(ch.isalpha() for ch in tok) or not any(ch.isdigit() for ch in tok):
            return False
        bad = ["HZ", "PH", "SEER", "EER", "R410A", "410A", "BTU", "MBH", "TON"]
        up = tok.upper()
        if any(b in up for b in bad):
            return False
        # Common OCR artifacts / labels rather than actual model numbers.
        if any(b in up for b in ["HEATPUMP", "IDENTIFICATION", "NOMENCLATURE", "MODELNUMBER", "MODELIDENTIFICATION"]):
            return False
        if "REGION" in up:
            return False
        if up.endswith("NOTE") or up.endswith("NOTES") or up.endswith("LEGEND"):
            return False
        # Too many separators is usually not a real model token.
        if tok.count("-") >= 7:
            return False
        # Most model numbers have a manufacturer/family prefix early on (not just trailing OCR words).
        if not any(ch.isalpha() for ch in tok[:4]):
            return False
        # Avoid tokens that are overwhelmingly numeric (often table ranges / callouts).
        digits = sum(ch.isdigit() for ch in tok)
        if digits / max(len(tok), 1) > 0.85:
            return False
        return True

    t = text.upper()
    out: set[str] = set()

    # 1) Token scan
    for m in _ALNUM_MODEL_RE.finditer(t):
        tok = _normalize_model_token(m.group(0))
        if is_modelish(tok):
            out.add(tok)

    # 2) Line-based collapse (handles "T 1 2 M- 036 -230-6 - 4" style)
    for line in t.splitlines():
        if not line.strip():
            continue
        collapsed = re.sub(r"\s+", "", line)
        collapsed = re.sub(r"[^A-Z0-9-]+", "", collapsed)
        if is_modelish(collapsed):
            out.add(collapsed)

    return sorted(out, key=lambda x: (-len(x), x))


def _parse_voltage_mappings(text: str) -> list[VoltageMapping]:
    t = text.upper()
    mappings: dict[str, VoltageMapping] = {}

    # Pattern: "K = 208/230-60-1"
    for m in re.finditer(r"\b([A-Z0-9])\s*=\s*(\d{2,3}(?:[/-]\d{2,3})?)\s*-\s*(\d{2})\s*-\s*(\d)\b", t):
        code, volts, hz, phase = m.group(1), m.group(2), m.group(3), m.group(4)
        mappings[code] = VoltageMapping(code=code, volts=volts.replace("-", "/"), phase=phase, hz=hz)

    # Pattern: "3 - 208/230 V Three-Phase 60 Hz" (or Two/Single)
    for m in re.finditer(
        r"\b([A-Z0-9])\s*-\s*(\d{2,3}(?:[/-]\d{2,3})?)\s*V?\s*(?:,|\s)+"
        r"(SINGLE|ONE|TWO|THREE)\s*-\s*PHASE\s*(\d{2})\s*HZ\b",
        t,
    ):
        code = m.group(1)
        volts = m.group(2).replace("-", "/")
        ph_word = m.group(3)
        hz = m.group(4)
        ph = {"SINGLE": "1", "ONE": "1", "TWO": "2", "THREE": "3"}.get(ph_word, "")
        if ph:
            mappings[code] = VoltageMapping(code=code, volts=volts, phase=ph, hz=hz)

    # Pattern: "230 = 208/230v-60hz-1ph"
    for m in re.finditer(
        r"\b(\d{2,3})\s*=\s*(\d{2,3}(?:[/-]\d{2,3})?)\s*V?\s*-\s*(\d{2})\s*HZ\s*-\s*(\d)\s*P",
        t,
    ):
        code = m.group(1)
        volts = m.group(2).replace("-", "/")
        hz = m.group(3)
        ph = m.group(4)
        mappings[code] = VoltageMapping(code=code, volts=volts, phase=ph, hz=hz)

    # Pattern: "1 208/230 V, 1 Phase, 60 Hz"
    for m in re.finditer(
        r"\b([A-Z0-9])\s+(\d{2,3}(?:[/-]\d{2,3})?)\s*V\b.{0,40}?\b(\d)\s*PHASE\b.{0,40}?\b(\d{2})\s*HZ\b",
        t,
        flags=re.IGNORECASE,
    ):
        code = m.group(1).upper()
        volts = m.group(2).replace("-", "/")
        ph = m.group(3)
        hz = m.group(4)
        mappings[code] = VoltageMapping(code=code, volts=volts, phase=ph, hz=hz)

    return list(mappings.values())


def _build_regex_template_from_example(example: str, code: str) -> tuple[str, str] | None:
    """
    Build (model_regex, extraction_pattern_regex) for a code found in an example model string.
    Returns a pattern that captures the code group (group 1) and a conservative model_regex anchored to the start.
    """
    ex = _normalize_model_token(example)
    if not ex:
        return None

    # Locate the code occurrence. If it occurs multiple times, avoid guessing.
    idx = ex.find(code)
    if idx < 0:
        return None
    # Require uniqueness (otherwise we don't know which occurrence is the intended "slot").
    if ex.find(code, idx + 1) >= 0:
        return None

    # Build a full pattern from the example: literal alphas kept, digit-runs generalized.
    # Replace the matched code segment with a capture group.
    before = ex[:idx]
    after = ex[idx + len(code) :]

    def encode_fragment(s: str) -> str:
        out = ""
        i = 0
        while i < len(s):
            ch = s[i]
            if ch.isdigit():
                j = i
                while j < len(s) and s[j].isdigit():
                    j += 1
                out += rf"\\d{{{j-i}}}"
                i = j
            else:
                out += re.escape(ch)
                i += 1
        return out

    if code.isdigit():
        cap = rf"(\\d{{{len(code)}}})"
    elif len(code) == 1:
        cap = r"([A-Z0-9])"
    else:
        cap = rf"([A-Z0-9]{{{len(code)}}})"
    full = "^" + encode_fragment(before) + cap + encode_fragment(after) + "$"

    # Conservative family filter: require at least a 3-char anchored literal prefix.
    prefix_letters = re.sub(r"[^A-Z0-9]", "", before)[:4]
    if len(prefix_letters) < 3:
        model_regex = ""
    else:
        model_regex = "^" + re.escape(prefix_letters)

    return model_regex, full


def _build_regex_from_template_with_placeholder(template: str, placeholder: str) -> tuple[str, str] | None:
    ex = _normalize_model_token(template)
    if not ex or placeholder not in ex:
        return None
    # Only if placeholder appears once.
    if ex.count(placeholder) != 1:
        return None
    idx = ex.index(placeholder)
    before = ex[:idx]
    after = ex[idx + 1 :]

    def encode_fragment(s: str) -> str:
        out = ""
        i = 0
        while i < len(s):
            ch = s[i]
            if ch.isdigit():
                j = i
                while j < len(s) and s[j].isdigit():
                    j += 1
                out += rf"\\d{{{j-i}}}"
                i = j
            else:
                out += re.escape(ch)
                i += 1
        return out

    full = "^" + encode_fragment(before) + r"([A-Z0-9])" + encode_fragment(after) + "$"

    prefix_letters = re.sub(r"[^A-Z0-9]", "", before)[:4]
    model_regex = "^" + re.escape(prefix_letters) if len(prefix_letters) >= 3 else ""
    return model_regex, full


def cmd_mine_model_ocr_attributes(args) -> int:
    input_csv = Path(args.input_csv)
    if not input_csv.exists():
        raise SystemExit(f"Missing input CSV: {input_csv}")

    out_path = Path(args.out_overrides)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    max_rows = int(args.max_rows or 0)
    rows_seen = 0
    written = 0

    with input_csv.open("r", newline="", encoding="utf-8") as f_in, out_path.open("w", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            rows_seen += 1
            if max_rows and rows_seen > max_rows:
                break

            brand = (row.get("brand") or "").strip()
            ocr_path = (row.get("ocr_text_path") or "").strip()
            source_url = (row.get("source_url") or "").strip()
            if not brand or not ocr_path:
                continue
            p = Path(ocr_path)
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")

            models = _extract_model_candidates(text)
            volts = _parse_voltage_mappings(text)
            cap_map = _parse_capacity_code_to_tons(text)

            stage_map = _parse_code_to_value_lines(
                text,
                label="Compressor Stage",
                values={
                    "Single-Stage": ["SINGLE STAGE", "SINGLE-STAGE"],
                    "Two-Stage": ["TWO STAGE", "TWO-STAGE"],
                },
            )

            # Refrigerant code mappings (most common: R410A)
            refr_map = _parse_code_to_value_lines(
                text,
                label="Refrigerant",
                values={
                    "R410A": ["R-410A", "R410A"],
                    "R32": ["R-32", "R32"],
                },
            )

            if not models:
                continue

            def emit_mapped_attribute(
                *,
                attribute_name: str,
                units: str,
                mapping: dict[str, str] | dict[str, float],
            ) -> None:
                nonlocal written
                if not mapping:
                    return

                min_total_codes = {
                    "VoltageVoltPhaseHz": 1,
                    "NominalCapacityTons": 2,
                    "CompressorStage": 1,
                    "Refrigerant": 1,
                }.get(attribute_name, 2)

                if len(mapping) < min_total_codes:
                    return

                # Group codes into shared templates so we emit fewer rules and avoid per-code noise.
                grouped: dict[tuple[str, str], dict[str, str]] = {}
                examples_by_template: dict[tuple[str, str], list[str]] = {}

                for code, value in mapping.items():
                    code_s = str(code)
                    value_s = str(value)

                    # Prefer examples where the code appears uniquely to avoid ambiguous binding.
                    candidates = [m for m in models if code_s in m]
                    candidates = [m for m in candidates if m.count(code_s) == 1]
                    if not candidates:
                        continue

                    # Prefer examples with clear token boundaries for purely-numeric codes.
                    if code_s.isdigit():
                        boundary = re.compile(rf"(^|[-_]){re.escape(code_s)}($|[-_A-Z])")
                        bounded = [m for m in candidates if boundary.search(m)]
                        if bounded:
                            candidates = bounded

                    example = candidates[0]
                    built = _build_regex_template_from_example(example, code_s)
                    if not built:
                        continue
                    model_regex, pat = built
                    key = (model_regex, pat)
                    grouped.setdefault(key, {})[code_s] = value_s
                    examples_by_template.setdefault(key, []).append(example)

                for (model_regex, pat), mapping2 in grouped.items():
                    # Per-rule: allow single-code rules when the overall mapping is supported,
                    # because many OCR snippets include only a single explicit model example.
                    if not mapping2:
                        continue

                    ve = {"data_type": "Text", "pattern": {"regex": pat, "group": 1}, "mapping": mapping2}
                    obj = {
                        "rule_type": "decode",
                        "brand": brand,
                        "model_regex": model_regex,
                        "attribute_name": attribute_name,
                        "value_extraction": ve,
                        "units": units,
                        "examples": sorted(set(examples_by_template.get((model_regex, pat), [])))[:5],
                        "limitations": "Derived from OCR of Building-Center model nomenclature diagram; may be incomplete or noisy.",
                        "evidence_excerpt": _normalize_text(text)[:220],
                        "source_url": source_url or "building_center_ocr",
                        "retrieved_on": dt.date.today().isoformat(),
                        "image_urls": [row.get("image_url")] if row.get("image_url") else [],
                    }
                    f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                    written += 1

            # Voltage (mapped values)
            emit_mapped_attribute(
                attribute_name="VoltageVoltPhaseHz",
                units="Volt-Phase-Hz",
                mapping={m.code: m.normalized_value() for m in volts},
            )

            # Capacity from code (tons)
            emit_mapped_attribute(
                attribute_name="NominalCapacityTons",
                units="Tons",
                mapping={k: str(v) for k, v in cap_map.items()},
            )

            # Stage / refrigerant / efficiency range
            emit_mapped_attribute(
                attribute_name="CompressorStage",
                units="",
                mapping=stage_map,
            )
            emit_mapped_attribute(
                attribute_name="Refrigerant",
                units="",
                mapping=refr_map,
            )
            # Efficiency-range decoding is too ambiguous without an explicit placeholder indicating
            # where the code lives in the model. Keep OCR artifacts for manual review instead.

    print(str(out_path))
    return 0
