# Core Concepts (Archived)

This project uses a **hybrid architecture** to decode equipment data. It combines "Librarian" work (documentation) with "Detective" work (data mining) to create a robust, layered ruleset.

## The Three Phases

### Phase 1: The Librarian (Source of Truth)
*   **Goal:** Create rules from *verified documentation* (web pages, manuals).
*   **Method:** Scrapes sites (like Building-Center), parses text instructions (regex, positions), and builds a baseline ruleset.
*   **Authority:** High. If a manual says "Serial starts with A", we believe it.
*   **Command:** `msl normalize`

### Phase 2: The Engine (Runtime)
*   **Goal:** Execute the rules against data.
*   **Method:** Takes a CSV of assets and the current ruleset, runs the logic (Regex matching, Date decoding), and outputs results.
*   **Authority:** None. It just follows orders from Phase 1/3.
*   **Command:** `msl decode`

### Phase 3: The Detective (Gap Filling)
*   **Goal:** Discover *new* rules from *real-world data*.
*   **Method:** Looks at thousands of un-decoded assets (with known dates) and finds statistical patterns (Heuristics).
*   **Authority:** Medium. Must pass strict statistical gates (e.g., 98% accuracy) to be accepted.
*   **Command:** `msl phase3-mine` -> `msl phase3-promote`

---

## Developing a New Heuristic

When you want to "develop a new heuristic," it means different things depending on which source you are targeting: **Text** or **Data**.

### Type A: The "Text Parser" (Phase 1)
**"I want to get better rules from the HTML/PDFs I already have."**

*   **Problem:** The documentation exists, but our code is too "dumb" to read it.
    *   *Example:* The manual says *"The year is indicated by the 3rd digit"*, but our parser only understands *"3rd digit = year"*.
*   **Where to work:** `msl/pipeline/normalize_rules.py`
*   **Workflow:**
    1.  Locate the skipped/failed sections in `data/rules_staged/` or reports.
    2.  Write a new Regex or Python logic in `_heuristic_normalize_one`.
    3.  Re-run `msl normalize`.
*   **Result:** Enriches the **Base Ruleset** by extracting more valid rules from the source text.

### Type B: The "Data Miner" (Phase 3)
**"The documentation is silent/missing. I want to find patterns in the raw asset list."**

*   **Problem:** We have 10,000 serial numbers for a brand, but no manual.
    *   *Example:* You notice that for 'Brand X', the serial number always starts with the manufacturing year (e.g., '99...' for 1999).
*   **Where to work:** `msl/pipeline/phase3_mine.py`
*   **Workflow:**
    1.  Load the "Training Data" (Assets with *Known* Years/Capacities).
    2.  Write a function to test your hypothesis (e.g., "Check if the first 2 digits match the known year").
    3.  Run `msl phase3-mine`.
    4.  If the accuracy is high (>98%), promote it via `msl phase3-promote`.
*   **Result:** Creates **New Rules** from scratch to fill coverage gaps.

---

## How They Merge (Additive)

The system is designed to layer these contributions:

1.  **Phase 1 Rules** form the hard foundation.
2.  **Phase 3 Rules** are layered on top to fill gaps.
3.  **Phase 2 Engine** runs the combined "Master Ruleset".

If you add a Phase 1 heuristic today, it might "override" a guessed Phase 3 rule because the documented rule is considered more authoritative.
