from __future__ import annotations

import csv
import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ManualOverride:
    master: str
    segment: str


LOCKED_INDUSTRIAL_GROUPS = {
    "Manufacturing",
    "Commercial Real Estate",
    "Construction",
    "Energy Services",
    "Utilities",
    "Financial Services",
    "Healthcare / Senior Living",
    "University / College",
    "Public Schools (K–12)",
    "Private Schools (K–12)",
    "Municipal / Local Government",
    "Commercial Services",
    "Non-Profit / Religious",
    "Individual / Misc",
    "Unknown / Needs Review",
}

LOCKED_SUPPORT_CATEGORIES = {
    "Retail",
    "Hospitality",
    "Telecommunications",
    "Mechanical Contractor",
}

LOCKED_METHODS = {
    "Rule-Based",
    "Entity Inference",
    "AI-Assisted Search",
    "Heuristic",
    "Manual Override",
    "Unclassified",
}


@dataclass(frozen=True)
class Classification:
    industrial_group: str
    industry_detail: str = ""
    naics: str = ""
    method: str = "Unclassified"
    confidence: str = "Low"
    rationale: str = ""
    support_category: str = ""


def confidence_for_method(method: str) -> tuple[str, str]:
    # Coarse, explainable confidence ladder aligned to SegmentationStrategy tiers.
    method = (method or "").strip()
    if method == "Manual Override":
        return "High", "Human-reviewed override"
    if method == "Rule-Based":
        return "High", "Deterministic keyword/pattern match"
    if method == "Entity Inference":
        return "Medium", "Known/recognized entity mapping"
    if method == "AI-Assisted Search":
        return "Medium", "External lookup required"
    if method == "Heuristic":
        return "Low", "Weak-signal best guess"
    return "Low", "Insufficient information"


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def default_paths() -> dict[str, Path]:
    root = repo_root()
    return {
        "input_customers": root / "input" / "CustomerLastBillingDate.csv",
        "manual_overrides": root / "input" / "ManualOverrides.csv",
        "master_websites": root / "input" / "MasterWebsites.csv",
        "master_segmentation_overrides": root / "input" / "MasterSegmentationOverrides.csv",
        "dedupe_output": root / "output" / "CustomerMasterMap.csv",
        "segmentation_output": root / "output" / "CustomerSegmentation.csv",
        "master_segmentation_output": root / "output" / "MasterCustomerSegmentation.csv",
        "dedupe_log": root / "output" / "CustomerDeduplicationLog.csv",
    }


def load_overrides(path: Path) -> Dict[str, ManualOverride]:
    overrides: Dict[str, ManualOverride] = {}
    if not path.exists():
        return overrides

    with path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            customer_key = (row.get("Customer Key") or "").strip()
            if not customer_key or customer_key.startswith("#"):
                continue
            overrides[customer_key] = ManualOverride(
                master=(row.get("Manual Master Name") or "").strip(),
                segment=(row.get("Manual Segment") or "").strip(),
            )
    return overrides


def load_master_websites(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}

    websites: Dict[str, str] = {}
    with path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            website = (row.get("Company Website") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            if website:
                websites[canonical] = website
    return websites


def load_master_segmentation_overrides(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}

    overrides: Dict[str, dict] = {}
    with path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            canonical = (row.get("Master Customer Name Canonical") or "").strip()
            if not canonical or canonical.startswith("#"):
                continue
            overrides[canonical] = {
                "Industrial Group": (row.get("Industrial Group") or "").strip(),
                "Industry Detail": (row.get("Industry Detail") or "").strip(),
                "NAICS": (row.get("NAICS") or "").strip(),
                "Method": (row.get("Method") or "").strip(),
                "Support Category": (row.get("Support Category") or "").strip(),
                "Company Website": (row.get("Company Website") or "").strip(),
                "Notes": (row.get("Notes") or "").strip(),
            }
    return overrides


def map_legacy_segment_to_industrial_group(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return ""

    locked_lower = {item.lower(): item for item in LOCKED_INDUSTRIAL_GROUPS}
    if v.lower() in locked_lower:
        return locked_lower[v.lower()]

    legacy_map = {
        "industrial": "Manufacturing",
        "manufacturing": "Manufacturing",
        "office": "Commercial Services",
        "medical": "Healthcare / Senior Living",
        "healthcare": "Healthcare / Senior Living",
        "municipal": "Municipal / Local Government",
        "muncipal": "Municipal / Local Government",
        "municpal": "Municipal / Local Government",
        "religious": "Non-Profit / Religious",
        "public schools": "Public Schools (K–12)",
        "private schools": "Private Schools (K–12)",
        "college/university": "University / College",
        "college": "University / College",
        # Retail/Hospitality are treated as support categorizations (secondary),
        # not the primary Industrial Group.
        "hospitality": "Commercial Services",
        "retail": "Commercial Services",
        "data center": "Commercial Services",
        "datacenter": "Commercial Services",
        "other": "Unknown / Needs Review",
    }
    return legacy_map.get(v.lower(), "")


def classify_customer(name: str, *, master_canonical: str = "") -> Classification:
    # Implements docs/SegmentationStrategy.md at a practical v1 level.
    name_lower = (name or "").lower()
    master_upper = (master_canonical or "").upper()

    # Step 2 — Tier 1 deterministic keyword matching (priority order)
    if re.search(r"\b(university|college|higher ed|higher education|polytechnic|community college|institute of technology)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("University / College", naics="611", method=method, confidence=confidence, rationale="Matched education keyword; " + rationale)

    rel_pat = r"\b(church|temple|mosque|synagogue|ministry|baptist|catholic|methodist|lutheran|presbyterian|episcopal|god|saint|st\.|bible|christian|bishop|our lady|notre dame|sacred heart|holy|jesuit|archdiocese|diocese|parish|chapel|synod)\b"
    if re.search(rel_pat, name_lower) or re.search(r"\b(nonprofit|non-profit|foundation|charity)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Non-Profit / Religious", naics="81", method=method, confidence=confidence, rationale="Matched religious/non-profit keyword; " + rationale)

    if re.search(r"\b(isd|usd|school district|public schools?|board of education|city schools?|county schools?)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Public Schools (K–12)", naics="611", method=method, confidence=confidence, rationale="Matched public school district keyword; " + rationale)

    if re.search(r"\b(academy|prep|collegiate|seminary|montessori)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Private Schools (K–12)", naics="611", method=method, confidence=confidence, rationale="Matched private school keyword; " + rationale)
    if "school" in name_lower and re.search(rel_pat, name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Private Schools (K–12)", naics="611", method=method, confidence=confidence, rationale="Matched school + religious context; " + rationale)
    if "school" in name_lower and re.search(r"\b(education|learning|early childhood|daycare|childcare)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Private Schools (K–12)", naics="611", method=method, confidence=confidence, rationale="Matched school + education context; " + rationale)

    if re.search(r"\b(city of|town of|village of|state of|commonwealth of)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Municipal / Local Government", naics="92", method=method, confidence=confidence, rationale="Matched city/town/state keyword; " + rationale)
    excluded_muni = re.search(r"\b(systems?|protection|security|builders?|bank|finance|food|ymca|solutions?|service|inc|llc|corp)\b", name_lower)
    if not excluded_muni and re.search(r"\b(county|fiscal court|jail|police|fire|library|municipal|govt|authority|township)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Municipal / Local Government", naics="92", method=method, confidence=confidence, rationale="Matched county/agency keyword; " + rationale)

    if re.search(r"\b(hospital|clinic|medical center|health|medical|physician|dental|dentist|surgery|veterinary|vet|healthcare|pharmacy|rehab|recovery|senior living|assisted living|nursing)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Healthcare / Senior Living", naics="62", method=method, confidence=confidence, rationale="Matched healthcare keyword; " + rationale)

    if re.search(r"\b(utility|utilities|water|sewer|wastewater|electric|power|natural gas|gas district)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Utilities", naics="22", method=method, confidence=confidence, rationale="Matched utility keyword; " + rationale)

    if re.search(r"\b(bank|credit union|mortgage|lending|loan|financial|insurance)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Financial Services", naics="52", method=method, confidence=confidence, rationale="Matched financial keyword; " + rationale)

    if re.search(r"\b(construction|contractor|builders?|roofing|plumbing|electric(al)? contractor|general contractor|design[- ]build)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Construction", naics="23", method=method, confidence=confidence, rationale="Matched construction keyword; " + rationale)

    if re.search(r"\b(mfg|manufacturing|plant|factory|steel|chemical|packaging|production)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Manufacturing", naics="31-33", method=method, confidence=confidence, rationale="Matched manufacturing keyword; " + rationale)

    if re.search(r"\b(real estate|realty|properties|property management|apartments?|leasing|development|commercial property)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Commercial Real Estate", naics="531", method=method, confidence=confidence, rationale="Matched real estate keyword; " + rationale)

    if re.search(r"\b(hotel|inn|resort|motel|lodge|restaurant|grill|cafe|coffee)\b", name_lower):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification(
            "Commercial Services",
            industry_detail="Hospitality",
            naics="72",
            method=method,
            confidence=confidence,
            rationale="Matched hospitality keyword; " + rationale,
            support_category="Hospitality",
        )

    # Identify individuals early (conservative; avoid misclassifying 2-word company names).
    if re.fullmatch(r"[A-Z][a-z]+, [A-Z][a-z]+(?: [A-Z]\.)?", (name or "").strip()):
        method = "Rule-Based"
        confidence, rationale = confidence_for_method(method)
        return Classification("Individual / Misc", method=method, confidence=confidence, rationale="Matched personal-name pattern; " + rationale)

    # Step 3 — Tier 2 entity inference (known entities/chains)
    entity_map = {
        "AMERESCO": ("Energy Services", "Energy Services", "", "Entity Inference"),
        "ARAMARK": ("Commercial Services", "Facilities / Food Service", "", "Entity Inference"),
        "AMERICAN RED CROSS": ("Non-Profit / Religious", "Non-Profit", "", "Entity Inference"),
        "WALMART": ("Commercial Services", "Big Box Retail", "44-45", "Entity Inference", "Retail"),
        "KROGER": ("Commercial Services", "Grocery Retail", "44-45", "Entity Inference", "Retail"),
        "TARGET": ("Commercial Services", "Retail", "44-45", "Entity Inference", "Retail"),
        "CVS": ("Commercial Services", "Pharmacy Retail", "44-45", "Entity Inference", "Retail"),
        "WALGREENS": ("Commercial Services", "Pharmacy Retail", "44-45", "Entity Inference", "Retail"),
        "FEDEX": ("Commercial Services", "Shipping / Logistics", "", "Entity Inference"),
        "UPS": ("Commercial Services", "Shipping / Logistics", "", "Entity Inference"),
        "US POSTAL SERVICE": ("Commercial Services", "Postal / Shipping", "", "Entity Inference"),
        "CINTAS": ("Commercial Services", "Uniforms / Facilities Services", "", "Entity Inference"),
        "CBRE": ("Commercial Real Estate", "Property Management / Brokerage", "5313", "Entity Inference"),
        "JLL": ("Commercial Real Estate", "Property Management / Brokerage", "5313", "Entity Inference"),
        "COLLIERS": ("Commercial Real Estate", "Property Management / Brokerage", "5313", "Entity Inference"),
        "CUSHMAN AND WAKEFIELD": ("Commercial Real Estate", "Property Management / Brokerage", "5313", "Entity Inference"),
        "WELLTOWER": ("Commercial Real Estate", "Healthcare Real Estate REIT", "531", "Entity Inference"),
        "ORANGETHEORY FITNESS": ("Commercial Services", "Fitness", "", "Entity Inference", "Retail"),
        "AMAZON": ("Commercial Services", "Technology / E-Commerce", "", "Entity Inference"),
    }
    if master_upper:
        for key, values in entity_map.items():
            group = values[0]
            detail = values[1]
            naics = values[2]
            method = values[3]
            support_category = values[4] if len(values) > 4 else ""
            if master_upper.startswith(key):
                confidence, rationale = confidence_for_method(method)
                return Classification(
                    group,
                    industry_detail=detail,
                    naics=naics,
                    method=method,
                    confidence=confidence,
                    rationale=f"Matched known entity '{key}'; {rationale}",
                    support_category=support_category,
                )

    # Step 5 — Heuristic assignment (weak signals)
    if re.search(r"\b(holdings?|holding|management|partners|associates)\b", name_lower):
        method = "Heuristic"
        confidence, rationale = confidence_for_method(method)
        return Classification(
            "Commercial Services",
            industry_detail="Business Services",
            method=method,
            confidence=confidence,
            rationale="Matched weak business-services signal; " + rationale,
        )

    if re.search(r"\b(properties|property)\b", name_lower):
        method = "Heuristic"
        confidence, rationale = confidence_for_method(method)
        return Classification(
            "Commercial Real Estate",
            industry_detail="Property Ownership",
            naics="531",
            method=method,
            confidence=confidence,
            rationale="Matched weak property-ownership signal; " + rationale,
        )

    if re.search(r"\b(fitness|gym)\b", name_lower):
        method = "Heuristic"
        confidence, rationale = confidence_for_method(method)
        return Classification(
            "Commercial Services",
            industry_detail="Fitness",
            method=method,
            confidence=confidence,
            rationale="Matched weak fitness signal; " + rationale,
            support_category="Retail",
        )

    # Step 6 — Fallback
    method = "Unclassified"
    confidence, rationale = confidence_for_method(method)
    return Classification("Unknown / Needs Review", method=method, confidence=confidence, rationale=rationale)


def get_master_name(name: str) -> str:
    name = name.upper()
    name = name.replace("&", " AND ")
    name = name.replace("+", " AND ")
    name = name.replace("%", " % ")
    if name.startswith("THE "):
        name = name[4:]
    suffix_pat = r"\b(LLC|INC|CO|CORP|L\.L\.C\.|INC\.|COMPANY|LIMITED|LTD|INCORPORATED|CORPORATION)\b"
    name = re.sub(suffix_pat, "", name)
    name = re.sub(r"[^\w\s%]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def to_display_name(canonical_name: str) -> str:
    value = canonical_name.strip()
    if not value:
        return value

    # Title-case while preserving true acronyms and state abbreviations.
    stopwords = {"and", "of", "the", "for", "in", "on", "at", "a", "an", "to"}
    roman_numerals = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}
    acronyms = {
        "LLC",
        "INC",
        "CO",
        "CORP",
        "LTD",
        "LP",
        "LLP",
        "PLLC",
        "PLC",
        "PC",
        "CPA",
        "USA",
        "US",
        "UPS",
        "USPS",
        "JLL",
        "CBRE",
        "NAICS",
        "K-12",
    }
    state_abbrevs = {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "DC",
    }

    def should_preserve_upper(token: str, *, is_first_word: bool) -> bool:
        if not token.isupper():
            return False
        if token in acronyms:
            return True
        if token in state_abbrevs:
            return not (is_first_word and token.lower() in stopwords)
        return False

    def format_part(part: str, *, is_first_word: bool) -> str:
        if not part:
            return part

        if any(ch.isdigit() for ch in part) or "%" in part or part in roman_numerals:
            return part

        lowered = part.lower()
        if not is_first_word and lowered in stopwords and part not in state_abbrevs:
            return lowered

        # Preserve 2-letter abbreviations (e.g., states) and known acronyms.
        if should_preserve_upper(part, is_first_word=is_first_word):
            return part

        # Handle hyphenated sub-parts like CHICK-FIL-A.
        pieces = part.split("-")
        pieces = [
            p
            if should_preserve_upper(p, is_first_word=is_first_word)
            else p.capitalize()
            for p in pieces
        ]
        return "-".join(pieces)

    words = value.split()
    formatted: List[str] = []
    for idx, word in enumerate(words):
        formatted.append(format_part(word, is_first_word=(idx == 0)))

    # Fix a few common casing patterns after title-casing.
    result = " ".join(formatted)
    result = result.replace(" Llc", " LLC").replace(" Inc", " Inc").replace(" Co", " Co")
    return result


def split_co_name(name: str) -> tuple[str, Optional[str]]:
    match = re.search(r"\s+(C/O|CO)\s+", name, re.IGNORECASE)
    if match:
        return name[: match.start()].strip(), name[match.end() :].strip()
    return name, None


def get_chain_master(name: str) -> Optional[str]:
    name_upper = name.upper()
    chains = {
        "ORANGETHEORY": "ORANGETHEORY FITNESS",
        "ORANGE THEORY": "ORANGETHEORY FITNESS",
        "FLAGSHIP": "FLAGSHIP HEALTHCARE PROPERTIES",
        "PERFECTION SERVICE": "PERFECTION SERVICES",
        "PROVIDENCE COMMERCIAL": "PROVIDENCE COMMERCIAL REAL ESTATE",
        "WALMART": "WALMART",
        "CINTAS": "CINTAS",
        "STARBUCKS": "STARBUCKS",
        "AMAZON": "AMAZON",
        "CVS": "CVS",
        "WALGREENS": "WALGREENS",
        "DOLLAR GENERAL": "DOLLAR GENERAL",
        "TARGET": "TARGET",
        "KROGER": "KROGER",
        "LOWES": "LOWES",
        "HOME DEPOT": "HOME DEPOT",
        "MCDONALDS": "MCDONALDS",
        "BURGER KING": "BURGER KING",
        "WENDYS": "WENDYS",
        "TACO BELL": "TACO BELL",
        "SUBWAY": "SUBWAY",
        "DOMINOS": "DOMINOS",
        "PIZZA HUT": "PIZZA HUT",
        "CHICK-FIL-A": "CHICK-FIL-A",
        "CHIPOTLE": "CHIPOTLE",
        "PANERA": "PANERA BREAD",
        "FEDEX": "FEDEX",
        "UPS": "UPS",
        "USPS": "US POSTAL SERVICE",
        "FIFTH THIRD": "FIFTH THIRD BANK",
        "PNC": "PNC BANK",
        "CHASE": "CHASE BANK",
        "HUNTINGTON": "HUNTINGTON BANK",
        "WELLTOWER": "WELLTOWER",
        "CUSHMAN": "CUSHMAN AND WAKEFIELD",
        "CBRE": "CBRE",
        "COLLIERS": "COLLIERS",
        "JLL": "JLL",
    }
    for key, master in chains.items():
        if name_upper.startswith(key):
            return master
    return None


def apply_fuzzy_master_dedupe(
    rows: List[dict],
    *,
    overrides: Dict[str, ManualOverride],
    similarity_threshold: float = 0.95,
) -> None:
    def comparison_key(name: str) -> str:
        noise_words = r"\b(INC|LLC|COMPANY|CORP|LTD|LIMITED|INCORPORATED|THE)\b"
        return re.sub(noise_words, "", name).strip()

    unique_names = list({row["Master Customer Name"] for row in rows if row.get("Master Customer Name")})
    unique_names.sort(key=len)

    canonical_map: Dict[str, str] = {}
    assigned: set[str] = set()

    for name in unique_names:
        if name in assigned:
            continue

        canonical_map[name] = name
        assigned.add(name)

        name_key = comparison_key(name)

        for candidate in unique_names:
            if candidate in assigned:
                continue
            candidate_key = comparison_key(candidate)

            if name_key == candidate_key:
                canonical_map[candidate] = name
                assigned.add(candidate)
                continue

            similarity = difflib.SequenceMatcher(None, name_key, candidate_key).ratio()
            if similarity > similarity_threshold:
                canonical_map[candidate] = name
                assigned.add(candidate)

    for row in rows:
        if row["Customer Key"] in overrides:
            continue
        master = row["Master Customer Name"]
        if master in canonical_map:
            row["Master Customer Name"] = canonical_map[master]


def build_master_map_rows(
    input_rows: Iterable[dict],
    *,
    overrides: Dict[str, ManualOverride],
) -> List[dict]:
    processed: List[dict] = []

    for row in input_rows:
        customer_key = row["Customer Key"]
        original_name = row["Customer Name"]

        if customer_key in overrides and overrides[customer_key].master:
            master_name = overrides[customer_key].master
            segment_source_name = master_name
        else:
            left, right = split_co_name(original_name)
            clean_left = get_master_name(left)
            chain_left = get_chain_master(clean_left)

            master_name = clean_left
            if chain_left:
                master_name = chain_left
            elif right:
                clean_right = get_master_name(right)
                chain_right = get_chain_master(clean_right)
                if chain_right:
                    master_name = chain_right

            # Match legacy behavior: segment based on original name unless a chain rule was applied.
            if chain_left:
                segment_source_name = master_name
            elif right:
                clean_right = get_master_name(right)
                chain_right = get_chain_master(clean_right)
                segment_source_name = master_name if chain_right else original_name
            else:
                segment_source_name = original_name

        processed.append(
            {
                "Customer Key": customer_key,
                "Customer Number": row.get("Customer Number", ""),
                "Original Name": original_name,
                "Master Customer Name": master_name,
                "Segment Source Name": segment_source_name,
                "Source": row.get("Source", ""),
                "Last Billing Date (Any Stream)": row.get("Last Billing Date (Any Stream)", ""),
            }
        )

    apply_fuzzy_master_dedupe(processed, overrides=overrides)
    for row in processed:
        canonical_master = row["Master Customer Name"]
        row["Master Customer Name Canonical"] = canonical_master
        row["Master Customer Name"] = to_display_name(canonical_master)

        segment_source = row.get("Segment Source Name") or ""
        if segment_source == canonical_master:
            row["Segment Source Name"] = row["Master Customer Name"]
    return processed


def build_dedupe_log_rows(
    master_rows: List[dict],
    *,
    overrides: Dict[str, ManualOverride],
    master_name_counts: Optional[Dict[str, int]] = None,
) -> List[dict]:
    log_rows: List[dict] = []

    for row in sorted(master_rows, key=lambda r: r["Master Customer Name"]):
        customer_key = row["Customer Key"]
        original = row["Original Name"]
        final_display = row["Master Customer Name"]
        final_canonical = row.get("Master Customer Name Canonical", final_display)
        merge_group_size = (master_name_counts or {}).get(final_canonical, 1)
        is_merge = merge_group_size > 1

        if customer_key in overrides and (overrides[customer_key].master or overrides[customer_key].segment):
            log_rows.append(
                {
                    "Master Customer Name": final_display,
                    "Master Customer Name Canonical": final_canonical,
                    "Original Name": original,
                    "Initial Clean Name": "(Override)",
                    "Type": "Manual Override",
                    "IsMerge": "TRUE" if is_merge else "FALSE",
                    "MergeGroupSize": str(merge_group_size),
                }
            )
            continue

        left, _ = split_co_name(original)
        s2_clean = get_master_name(left)
        chain_res = get_chain_master(s2_clean)
        s3_chain = chain_res if chain_res else s2_clean

        change_type: List[str] = []
        if left.upper() != original.upper().strip() and ("C/O" in original.upper() or "CO " in original.upper()):
            _, right = split_co_name(original)
            if right:
                clean_right = get_master_name(right)
                if get_chain_master(clean_right) == final_canonical:
                    change_type.append("C/O Swap (Right Side Chain)")
                else:
                    change_type.append("C/O Strip")
            else:
                change_type.append("C/O Strip")

        if chain_res and chain_res == final_canonical and "C/O Swap" not in ",".join(change_type):
            change_type.append("Chain Rule")

        if final_canonical != s3_chain and not change_type:
            change_type.append("Fuzzy Merge")

        if change_type or is_merge:
            log_rows.append(
                {
                    "Master Customer Name": final_display,
                    "Master Customer Name Canonical": final_canonical,
                    "Original Name": original,
                    "Initial Clean Name": s3_chain,
                    "Type": ", ".join(change_type) if change_type else "Merge",
                    "IsMerge": "TRUE" if is_merge else "FALSE",
                    "MergeGroupSize": str(merge_group_size),
                }
            )

    return log_rows


def build_segmentation_rows(
    master_rows: Iterable[dict],
    *,
    overrides: Dict[str, ManualOverride],
) -> List[dict]:
    # Segmentation should be computed at the *master* level (dimension grain),
    # then joined back to customer keys for integration into CUSTOMERS_D.
    master_rows_list = list(master_rows)
    master_classifications = build_master_segmentation_map(master_rows_list)

    output: List[dict] = []
    for row in master_rows_list:
        customer_key = row["Customer Key"]
        master_name = row["Master Customer Name"]
        master_canonical = row.get("Master Customer Name Canonical", "")

        classification = master_classifications.get(master_canonical) or Classification(
            industrial_group="Unknown / Needs Review",
            method="Unclassified",
            confidence="Low",
            rationale="Missing master classification",
        )

        # Key-level manual segment override (legacy behavior). This can cause
        # inconsistency within a master; long-term, prefer master-level overrides.
        segment_override = overrides.get(customer_key).segment if customer_key in overrides else ""
        if segment_override.strip():
            industrial_group = map_legacy_segment_to_industrial_group(segment_override.strip())
            method = "Manual Override"
            confidence, rationale = confidence_for_method(method)
            if industrial_group:
                classification = Classification(
                    industrial_group=industrial_group,
                    method=method,
                    confidence=confidence,
                    rationale=rationale,
                )
            else:
                classification = Classification(
                    industrial_group="Unknown / Needs Review",
                    industry_detail=f"Override: {segment_override.strip()}",
                    method=method,
                    confidence=confidence,
                    rationale=rationale,
                )

        output.append(
            {
                "Customer Key": customer_key,
                "Original Name": row["Original Name"],
                "Master Customer Name": master_name,
                "Industrial Group": classification.industrial_group,
                "Industry Detail": classification.industry_detail,
                "NAICS": classification.naics,
                "Method": classification.method,
                "Confidence": classification.confidence,
                "Rationale": classification.rationale,
                "Support Category": classification.support_category,
                "Source": row.get("Source", ""),
            }
        )
    return output


def build_master_segmentation_map(master_rows: List[dict]) -> Dict[str, Classification]:
    # Aggregate evidence across all customer keys that map to the same master.
    # Choose the "best" classification by confidence/method, to reduce false
    # negatives while keeping explainability.
    by_master: Dict[str, List[dict]] = {}
    for row in master_rows:
        canonical = row.get("Master Customer Name Canonical") or row.get("Master Customer Name") or ""
        by_master.setdefault(canonical, []).append(row)

    confidence_rank = {"High": 3, "Medium": 2, "Low": 1}
    method_rank = {
        "Rule-Based": 5,
        "Entity Inference": 4,
        "AI-Assisted Search": 3,
        "Heuristic": 2,
        "Unclassified": 1,
        "Manual Override": 6,  # not expected here, but keep highest
    }

    result: Dict[str, Classification] = {}
    for canonical, rows in by_master.items():
        # Evidence candidates: segment sources + display master name.
        evidence_names: List[str] = []
        for r in rows:
            evidence_names.append((r.get("Segment Source Name") or "").strip())
        evidence_names.append((rows[0].get("Master Customer Name") or "").strip())
        evidence_names = [n for n in evidence_names if n]

        best: Optional[tuple[int, int, Classification]] = None
        best_evidence: str = ""
        for evidence in evidence_names:
            classification = classify_customer(evidence, master_canonical=canonical)
            cr = confidence_rank.get(classification.confidence, 1)
            mr = method_rank.get(classification.method, 1)
            key = (cr, mr, classification)
            if best is None or (cr, mr) > (best[0], best[1]):
                best = key
                best_evidence = evidence

        if best is None:
            classification = Classification(
                industrial_group="Unknown / Needs Review",
                method="Unclassified",
                confidence="Low",
                rationale="Insufficient information",
            )
        else:
            classification = best[2]
            if best_evidence and classification.rationale:
                classification = Classification(
                    industrial_group=classification.industrial_group,
                    industry_detail=classification.industry_detail,
                    naics=classification.naics,
                    method=classification.method,
                    confidence=classification.confidence,
                    rationale=f"{classification.rationale} (evidence: '{best_evidence}')",
                    support_category=classification.support_category,
                )

        result[canonical] = classification

    return result


def build_master_segmentation_rows(master_rows: List[dict]) -> List[dict]:
    by_master: Dict[str, dict] = {}
    for row in master_rows:
        canonical = row.get("Master Customer Name Canonical") or row.get("Master Customer Name") or ""
        if canonical not in by_master:
            by_master[canonical] = {
                "Master Customer Name": row.get("Master Customer Name", ""),
                "Master Customer Name Canonical": canonical,
                "MergeGroupSize": row.get("MergeGroupSize", ""),
                "IsMerge": row.get("IsMerge", ""),
            }

    classifications = build_master_segmentation_map(master_rows)

    output: List[dict] = []
    for canonical, base in sorted(by_master.items(), key=lambda kv: kv[1]["Master Customer Name"]):
        classification = classifications.get(canonical) or Classification(
            industrial_group="Unknown / Needs Review",
            method="Unclassified",
            confidence="Low",
            rationale="Missing master classification",
        )
        output.append(
            {
                "Master Customer Name": base["Master Customer Name"],
                "Master Customer Name Canonical": base["Master Customer Name Canonical"],
                "Industrial Group": classification.industrial_group,
                "Industry Detail": classification.industry_detail,
                "NAICS": classification.naics,
                "Method": classification.method,
                "Confidence": classification.confidence,
                "Rationale": classification.rationale,
                "Support Category": classification.support_category,
                "IsMerge": base["IsMerge"],
                "MergeGroupSize": base["MergeGroupSize"],
            }
        )

    return output


def read_csv_dicts(path: Path) -> List[dict]:
    with path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_dicts(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open(mode="w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except PermissionError as exc:
        raise SystemExit(
            f"Permission error writing {path}. Close any app using the file (Excel/Power BI), then re-run."
        ) from exc
