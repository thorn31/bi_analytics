---
name: batch_enrichment
description: A rigorous workflow to autonomously research, verify, and enrich master customer records (websites, NAICS, Industry Detail) in batches. It distinguishes between verified matches and ambiguous ones, applies the verified data, and logs the ambiguous items with detailed research narratives for manual review.
---

# Batch Enrichment Workflow

This skill guides the agent through a systematic process of enriching master customer data.

## 1. Preparation
- **Goal**: Generate a prioritized queue of "Unknown" or incomplete records.
- **Action**: Run the queue builder script.
  ```bash
  python enrichment/build_master_enrichment_queue.py --limit 50
  ```
- **Context**: The output is saved to `output/work/enrichment/MasterEnrichmentQueue.csv`.

## 2. Research & Classification
- **Goal**: Find definitive data for as many items as possible.
- **Action**: For each item in the queue (or the top N items):
    1.  **Analyze**: Look at `Example Customer Names` and `Example Locations` to establish context.
    2.  **Search**: Use `google_web_search` to find the official corporate website.
    3.  **Verify**:
        *   Does the domain match the location?
        *   Does the business activity match the `Industrial Group`?
    4.  **Classify**:
        *   **Verified**: High confidence. You found the exact domain (e.g., `kroger.com`) or a clear parent company.
        *   **Ambiguous/Holding**: No website, generic name (e.g., "B&B Properties"), or conflicting results.
    5.  **Assign Codes**:
        *   **NAICS**: Prioritize specificity (6-digit) *only if supported by evidence*. Use 2, 3, or 4-digit codes if the company performs a variety of services or if the exact activity is unclear (e.g., `23` for General Construction vs `238220` for HVAC).
        *   **Industry Detail**: A concise, human-readable description (e.g., "Automotive Stamping", "Public School District").

## 3. Execution (The "Dual Path")
- **Goal**: Update the data source of truth safely.
- **Action**:
    1.  **Populate Queue**: Update the `output/work/enrichment/MasterEnrichmentQueue.csv` file with your research findings.
        *   **For Verified Items**:
            *   Populate `Company Website (Approved)`, `NAICS (Approved)`, and `Industry Detail (Approved)`.
            *   Set `Enrichment Status` = 'Verified'.
            *   Set `Enrichment Source` = 'Analyst'.
            *   **Rule**: A `Verified` row must include at least one approved value (website and/or NAICS and/or industry detail), otherwise it will not be applied.
        *   **For Ambiguous/Skipped Items**:
            *   **Crucial**: Do NOT leave blank.
            *   Set `Enrichment Status` = 'Deferred'.
            *   Set `Enrichment Rationale` = Short reason for skip (e.g., "Ambiguous generic name", "Individual account").
            *   **Research Narrative**: Set `Notes` = A detailed explanation of your research findings (e.g., "Found three different 'Design Build Solutions' in Cincinnati; one is residential roofing, another is commercial. Without a street address, I cannot definitively link the correct website.").
            *   **Persistence**: Deferred items are applied into `data/enrichment/MasterEnrichment.csv` even when no approved values are present (this prevents “ghost” deferrals that only exist in markdown logs).
    2.  **Human-In-The-Loop Review (Required)**: Before applying, present a short summary to the user (or analyst) for confirmation.
        *   **Verified**: List the master canonicals + approved website/NAICS/detail you plan to apply.
        *   **Deferred**: List the master canonicals + rationale (and note that a narrative exists in `Notes`).
        *   Ask explicitly: “Proceed to apply these updates to `data/enrichment/MasterEnrichment.csv`?”
    2.  **Apply Updates**: Run the existing application script to commit the changes to `MasterEnrichment.csv`.
        ```bash
        python enrichment/apply_master_enrichment_queue.py
        ```
    3.  **Regenerate Outputs**: Run the segmentation engine to propagate changes to the final deliverables.
        ```bash
        python segment_customers.py
        ```

## 4. Reporting & Handoff
- **Goal**: Provide a clean audit trail.
- **Action**: Generate a Markdown summary for the user.
    *   **File Path**: `output/enrichment_logs/Batch_YYYYMMDD_HHMM.md`
    *   **Content**:
        *   **✅ Enriched**: List of customers successfully updated.
        *   **⚠️ Deferred**: List of customers marked as deferred, including the **Rationale** and the detailed **Research Narrative** from the Notes field.
- **Next Step**: Ask the user: "Batch complete. Ready for the next one?"
