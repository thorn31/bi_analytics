# Net Revenue Retention (NRR) Logic Explained

This document explains the logic behind the **Net Revenue Retention (NRR)** calculations in the Power BI report, specifically focusing on how customers are classified as "Churned" versus "Lapsed."

## 1. The "As Of" Anchor Date
Every calculation starts with a single **Anchor Date**. This is the reference point for "Today" in the report.

*   **Logic:** The report looks at your Date Slicer selection and snaps to the **latest available Service Contract data**.
*   **Example:** If you select "FY2026" but data only exists through **December 2025**, the Anchor Date becomes **Dec 31, 2025**.

## 2. The Two Comparison Windows
Once the Anchor Date is set, the system looks at two specific 12-month periods:

1.  **Current Period (CY):** The 12 months ending on the Anchor Date.
    *   *Example:* Jan 1, 2025 – Dec 31, 2025
2.  **Prior Period (PY):** The 12 months *before* the Current Period.
    *   *Example:* Jan 1, 2024 – Dec 31, 2024

## 3. How Status is Determined (The "Who Counts?" Rule)
NRR only measures how well we retained customers who were **already with us** in the Prior Period.

| Customer Scenario | Revenue in Prior Period (PY) | Revenue in Current Period (CY) | Status | Impact on NRR |
| :--- | :---: | :---: | :--- | :--- |
| **Steady** | ✅ Yes ($10k) | ✅ Yes ($10k) | **Steady** | Neutral (100%) |
| **Growth** | ✅ Yes ($10k) | ✅ Yes ($15k) | **Upsell** | Positive (>100%) |
| **Decline** | ✅ Yes ($10k) | ✅ Yes ($5k) | **Contraction** | Negative (<100%) |
| **Lost Recently** | ✅ Yes ($10k) | ❌ No ($0) | **Churned** | Negative (0%) |
| **Lost Long Ago** | ❌ No ($0) | ❌ No ($0) | **Lapsed** | **Excluded** |
| **New Customer** | ❌ No ($0) | ✅ Yes ($10k) | **New Business** | **Excluded** |

---

## 4. The "Churn vs. Lapsed" Cliff (Example)
*Why does a customer count as Churn one month, but disappear the next?*

Imagine **Anchor Date = Dec 31, 2025**.
*   **Prior Period (PY):** Jan 2024 – Dec 2024.

### Scenario A: Last Bill was Jan 1, 2024
*   **Is Jan 1, 2024 in the Prior Period?** Yes.
*   **Result:** This customer counts as **Base Revenue**.
*   **Current Status:** Since they have paid nothing since, they are marked as **Churned**.
*   **Impact:** They hurt the NRR score.

### Scenario B: Last Bill was Dec 1, 2023
*   **Is Dec 1, 2023 in the Prior Period?** No. (It is before Jan 2024).
*   **Result:** This customer had **$0 revenue** in the Prior Period (Jan–Dec 2024).
*   **Current Status:** **Lapsed / Inactive**.
*   **Impact:** They are **excluded** from the calculation entirely. We already "counted" their churn in last year's report; we don't count it again this year.
