# Customer Classification & Segmentation Specification (v1)

## Purpose

This document defines the **authoritative process** for classifying customers into:
- Industrial Group (vertical segment)
- Industry Detail
- NAICS (reference classification)
- Method (how the classification was determined)

The goal is to support:
- Revenue-by-vertical analysis
- Customer concentration and retention analysis
- Consistent, explainable executive reporting

This process prioritizes **stability, auditability, and analytical usefulness** over perfect legal entity resolution.

---

## Core Principles

1. Classification is **analytical**, not legal.
2. Billing intermediaries (e.g., `c/o`) do **not** define the customer.
3. Deterministic rules take precedence over inference.
4. AI-assisted search is used **only when necessary**.
5. Every classification must be explainable.

---

## Field Definitions

### 1. Industrial Group
**Definition**  
High-level vertical segment used for executive reporting and revenue analysis.

**Rules**
- Exactly one value per Customer Entity
- Must come from a locked list
- Changes only via rule updates or manual override

**Locked Values**
- Manufacturing  
- Commercial Real Estate  
- Construction  
- Energy Services  
- Utilities  
- Financial Services  
- Healthcare / Senior Living  
- University / College  
- Public Schools (K–12)  
- Private Schools (K–12)  
- Municipal / Local Government  
- Commercial Services  
- Non-Profit / Religious  
- Individual / Misc  
- Unknown / Needs Review  

---

### 1b. Support Category (Secondary)
**Definition**  
Optional secondary classification used to tag customers that are **retail-facing** or part of the **hospitality** domain, without making those the primary vertical.

**Rules**
- Optional (can be blank)
- Zero or one value per Customer Entity (v1)
- Used for cross-cutting analysis (e.g., “Retail customers within Commercial Services”)

**Locked Values**
- Retail
- Hospitality

---

### 2. Industry Detail
**Definition**  
Human-readable refinement providing additional context within an Industrial Group.

**Rules**
- Optional
- Not required to be unique
- Can evolve without breaking reports
- Should align with NAICS descriptions when possible

**Examples**
- Industrial Label Manufacturing  
- Mortgage Lending / Servicing  
- Design-Build Contractor  
- Assisted Living Facilities  
- Industrial Property Ownership  

---

### 3. NAICS (Primary)
**Definition**  
Standards-based reference classification used for validation, benchmarking, and future enrichment.

**Rules**
- Single value
- Stored as text
- Prefer 2–4 digit depth
- Never the sole driver of Industrial Group assignment

**Allowed States**
- Populated (confident)
- Null (unknown or not applicable)

---

### 4. Method
**Definition**  
Describes *how* the classification was determined.

**Allowed Values (Locked)**

| Method | Description |
|------|------------|
| Rule-Based | Deterministic keyword or pattern match |
| Entity Inference | Known organization or widely recognized entity |
| AI-Assisted Search | External or semantic lookup required |
| Heuristic | Best-guess based on weak signals |
| Manual Override | Human-reviewed and approved |
| Unclassified | Insufficient information |

---

## Classification Pipeline (Order of Operations)

### Step 1 — Pre-Processing
- Normalize customer name
- Extract Primary Name
- Remove corporate suffixes
- Parse and ignore `c/o` entities
- Identify Individuals early

**Output:** Clean Customer Entity candidate

---

### Step 2 — Deterministic Keyword Matching (Tier 1)
This is the **first and preferred** classification mechanism.

**Examples**
- `University`, `College` → University / College  
- `School District`, `ISD`, `USD` → Public Schools (K–12)  
- `City of`, `County of`, `Town of` → Municipal  
- `Hospital`, `Medical Center` → Healthcare / Senior Living  
- `Utilities`, `Water`, `Sewer`, `Electric` → Utilities  

**Rules**
- Applied in priority order
- If matched, classification stops
- Method = Rule-Based
- NAICS assigned at 2–3 digit level when appropriate

**Note (Retail/Hospitality)**
- Retail and Hospitality keywords should generally populate `Support Category` and/or `Industry Detail` rather than becoming the primary `Industrial Group`.

---

### Step 3 — Entity Inference (Tier 2)
Used when deterministic rules fail.

**Signals**
- Widely known brands
- Public institutional entities
- Recognizable manufacturers or service providers
- Prior organizational knowledge

**Examples**
- Ameresco → Energy Services  
- Aramark → Commercial Services  
- American Red Cross → Non-Profit / Religious  

**Output**
- Industrial Group
- Industry Detail
- NAICS (if clear)
- Method = Entity Inference

---

### Step 4 — AI-Assisted Search (Tier 3)
Used **only when name-based inference is insufficient**.

**When AI Search Is Used**
- Ambiguous personal-name firms
- Generic holding companies
- Multi-service firms with unclear focus
- Examples:
  - “Al. Neyer LLC”
  - “Ameriplex 2 LLC”
  - “Ark LLC”

**What AI Search Provides**
- Business description
- Primary activity
- Market focus (owner, operator, manufacturer, etc.)

**Constraints**
- AI search supports classification; it does not override deterministic rules
- Results must be intuitive and defensible
- Used sparingly

**Method**
- Method = AI-Assisted Search

---

### Step 5 — Heuristic Assignment (Tier 4)
Used only when:
- No deterministic rule applies
- Entity inference and AI search are inconclusive
- Some signal still exists

**Signals**
- Keywords like `Mortgage`, `Fitness`, `Manufacturing`
- Legal structure patterns
- Historical analyst knowledge

**Rules**
- Conservative
- NAICS optional
- Flagged for later review if material

**Method**
- Method = Heuristic

---

### Step 6 — Fallback
If insufficient information exists:
- Industrial Group = Unknown / Needs Review
- Industry Detail = Null
- NAICS = Null
- Method = Unclassified

---

## NAICS Assignment Rules

| Scenario | NAICS Behavior |
|-------|----------------|
| Institutional (Schools, Universities) | Assign 2–3 digit |
| Known manufacturer | Assign 4–6 digit |
| Commercial Real Estate owner | 5311 / 5313 |
| Shell LLC | Null |
| Individual | Null |

NAICS is **supporting metadata**, not the driver.

---

## Manual Overrides

- Supersede all automated logic
- Must include:
  - Reason
  - Date
  - Owner
- Method = Manual Override
- Confidence implicitly High

---

## Example Classifications

### American Mortgage Service Company
- Industrial Group: Financial Services  
- Industry Detail: Mortgage Lending / Servicing  
- NAICS: 522292  
- Method: Heuristic  

### Ameriplex 2 LLC
- Industrial Group: Commercial Real Estate  
- Industry Detail: Industrial Property Ownership  
- NAICS: 531120  
- Method: AI-Assisted Search  

---

## Design Intent

This framework ensures:
- Consistent vertical reporting
- Trustworthy customer analytics
- Minimal rework as data evolves
- Clear explanation when classifications are questioned

This is an **analytics-first** classification system, not a master data system.

---

## Future Enhancements (Out of Scope for v1)
- Multiple verticals per customer
- Automated domain-based validation
- Confidence-weighted revenue reporting
- Parent / subsidiary rollups
