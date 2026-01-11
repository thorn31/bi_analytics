# CRR Visuals & Analysis Strategy

## 1. The "Retention Overview" Dashboard (High Level)
Create a dedicated section or page for "Customer Retention."

*   **The KPI Cards (Top Row):**
    *   **Net Revenue Retention % (SC):** The star metric. How much value are we retaining/growing from contracts? (Target > 100%).
    *   **Logo Retention % (SC):** The "stickiness" metric. Are we keeping the *contracts* themselves? (Target ~90-95%).
    *   **Logo Retention % (Total):** The "relationship" metric. Are customers still buying *anything* from us (including projects/T&M) even if they dropped their contract?
        *   *Insight:* If Logo Retention (Total) > Logo Retention (SC), it means you have customers who cancelled contracts but still buy T&M/Projects. They aren't "lost," just "downgraded."

## 2. The "Churn Analysis" Visuals (Drill Down)
*   **Bar Chart: Churn Reasons (Implied):**
    *   Plot `Logo Churn Count (SC)` by `Division` or `Contract Type`.
    *   *Insight:* Identify which divisions are bleeding the most customer logos.
*   **Scatter Plot: Revenue vs. Retention:**
    *   **X-Axis:** `SC Revenue (R12M As Of)` (Customer Size).
    *   **Y-Axis:** `Net Revenue Retention %`.
    *   **Bubble Size:** `Retention Base PY`.
    *   *Insight:* Are you losing small customers (high logo churn, low revenue impact) or big customers (low logo churn, huge revenue impact)?

## 3. The "Cohort Trend" Line Chart
Show how retention is evolving over time.
*   **Axis:** `Month End`.
*   **Lines:** `Net Revenue Retention % (SC)` and `Logo Retention % (SC)`.
*   *Insight:* Is our retention improving or deteriorating? If NRR is going up but Logo Retention is going down, you are successfully upselling a shrinking customer base (risky long term).

## 4. The "At Risk" Table (Actionable List)
A grid visual filtered to show "Warning Signs" for Account Managers.
*   **Columns:** `Customer Name`, `Months Since Last Billing`, `Net Revenue Retention %`.
*   **Filter:** `Months Since Last Billing > 6` OR `Net Revenue Retention % < 80%`.
*   *Purpose:* A "Call List" for AMs to save relationships before they become churn statistics.

## 5. The "Stream Cross-Sell" Matrix
Use the **Total** vs **SC** measures to see cross-pollination.
*   **Visual:** Matrix.
*   **Rows:** `Division` (or Region).
*   **Values:**
    *   `Logo Retention % (SC)`
    *   `Logo Retention % (Total)`
    *   **Measure Delta:** `[Logo Retention % (Total)] - [Logo Retention % (SC)]`.
    *   *Insight:* A large positive delta means that Division is great at keeping customers in the ecosystem (selling them Projects/T&M) even if the formal Contract renews less often.

---

## 6. Incorporating Gross Revenue Retention (GRR)

**The Concept:**
*   **NRR (Net Revenue Retention):** The "Growth" metric. Can exceed 100%. Good for showing expansion capability.
*   **GRR (Gross Revenue Retention):** The "Health" metric. Caps upsell at the original contract value. Max is 100%. Shows how "leaky" your bucket is.

**How to Visualize it:**

### A. The "Leaky Bucket" Gauge
*   **Visual:** Gauge or Bullet Chart.
*   **Value:** `Gross Revenue Retention % (SC)`.
*   **Target:** 90% (Industry standard for healthy recurring revenue).
*   **Insight:** If GRR is 80%, you automatically lose 20% of your revenue base every year. You *must* hunt new business just to stay flat. This highlights operational/service quality issues that sales can't fix.

### B. The "Upsell Dependency" Gap
*   **Visual:** Area Chart or Line Chart.
*   **Lines:**
    1.  `Net Revenue Retention % (SC)`
    2.  `Gross Revenue Retention % (SC)`
*   **Insight (The Gap):** The space between the two lines represents **Upsell/Price Increases**.
    *   **Wide Gap:** You are great at farming existing accounts, but maybe losing too many base contracts (masked by price hikes).
    *   **Narrow Gap:** You are retaining everyone (high GRR) but failing to expand the accounts (low upsell).

### C. Quadrant Analysis (Scatter Plot)
*   **X-Axis:** `Gross Revenue Retention %` (Retention Health).
*   **Y-Axis:** `Upsell Revenue (R12M As Of)` (Expansion Ability).
*   **Dots:** `Divisions` or `Sales Reps`.
*   **Quadrants:**
    *   **Top Right:** Stars (Keep customers & Grow them).
    *   **Bottom Right:** Farmers (Keep customers, no growth).
    *   **Top Left:** Hunters/Burners (High churn, but high replacement/upsell).
    *   **Bottom Left:** Problem Area.
