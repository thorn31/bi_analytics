# Power BI Theme Design Document  
**Project:** Perfection – Clean Neutral Theme  
**Canvas Size:** 1920 × 1080  
**Status:** In Progress (Foundational System Complete)

---

## 1. Theme Philosophy

The goal of this theme is to create a **calm, analytical, and highly readable reporting environment** that emphasizes:

- **Data over decoration**
- **Consistency through defaults**, not manual formatting
- **Visual hierarchy via typography and contrast**, not borders or heavy chrome
- **Muted, professional color usage** aligned with brand identity

The theme is designed to scale across:
- Executive KPI dashboards
- Operational and financial detail pages
- Dense tables and matrices
- Multi-page analytical reports

The guiding principle is that **most visuals should look “finished” immediately upon creation**, without further formatting.

---

## 2. Layout & Canvas Strategy

### Canvas
- **Resolution:** 1920 × 1080
- **Design grid:** Consistent spacing and alignment (handled at report layout level, not theme)

### Background Strategy
- **Page background:** `#F4F6F8` (light neutral grey)
- **Visual surfaces:** Pure white (`#FFFFFF`)
- **No borders**
- **No shadows**

This creates visual separation purely through **contrast**, keeping the page light and uncluttered while still allowing visuals to read as discrete “cards”.

---

## 3. Color System

### Primary Brand Colors
| Role | Hex |
|----|----|
| Primary Slate | `#425563` |
| Dark Neutral | `#414042` |
| Muted Grey | `#A2ACAB` |
| Accent Gold | `#DDA46F` |

These are used sparingly and intentionally to avoid visual noise.

---

### Data Colors (Charts & Series)

The data color palette is intentionally **near-monochrome** with controlled variance to support:
- Stacked bars
- Overlapping series
- Small multiples

```
#425563  (Primary slate)
#24323D  (Darker slate)
#5E7686  (Mid slate)
#8A9EAB  (Light slate)
#A2ACAB  (Neutral grey)
#5FB3A2  (Positive / growth)
#9C6A63  (Negative / decline)
```

**Design rationale:**
- Adjacent colors are visually distinguishable even when stacked
- Saturation is controlled to prevent visual fatigue
- Semantic colors stand out without being “alert loud”

---

### Semantic Colors

| Meaning | Hex | Rationale |
|----|----|----|
| Good | `#5FB3A2` | Cool, muted green that signals success without brightness |
| Neutral | `#8F7A56` | Warm-neutral midpoint |
| Bad | `#9C6A63` | Muted red that signals risk without alarm |

---

## 4. Typography System

### Font Family
**Segoe UI** (Windows-native, Power BI-native, highly legible)

### Weight-Based Hierarchy (Intentional)
| Usage | Font | Size |
|----|----|----|
| Page / Section Titles | Segoe UI Light | 22 |
| Visual Titles | Segoe UI Light | 12 |
| Headers / Emphasis | Segoe UI Semibold | 14 |
| Labels & Axes | Segoe UI Regular | 10 |
| KPI Callouts (default) | Segoe UI Semibold | 28 |

**Design rationale:**
- Hierarchy is communicated by **weight, not color**
- Light titles keep pages feeling open and modern
- Semibold is reserved strictly for emphasis

---

## 5. Tables & Matrices

### Approach
Tables and matrices are treated as **analytical tools**, not UI components.

Key rules:
- **No gridlines**
- **No borders**
- **White headers**
- **Hierarchy via typography only**

### Implementation
- Custom **style presets**:
  - **Clean Table**
  - **Clean Matrix**
- Presets are:
  - Defined in the theme JSON
  - Selectable in the Power BI UI
  - Defaulted for new visuals

### Header Styling
- Background: White
- Font: Segoe UI Semibold
- Purpose: Distinguish structure without visual weight

### Body Styling
- White background with very subtle zebra banding
- Regular Segoe UI for readability at density

---

## 6. What the Theme Deliberately Avoids

- Borders as separators
- Heavy header fills
- Bright red/green semantics
- Shadows and elevation effects
- Per-visual manual formatting

Anything that introduces noise or inconsistency is intentionally excluded.

---

## 7. Current State Summary

### Completed
- Color system (brand + data + semantics)
- Typography hierarchy
- Page and visual background strategy
- Table and Matrix style presets
- Validated theme import and preset behavior

---

## 8. Work Still To Be Done

### High Priority
1. **Card Visual Design**
   - Finalize spacing and typography rules
   - Reference labels (Δ vs PY)
   - Measure-driven semantic coloring

2. **Chart Defaults**
   - Axis label sizing
   - Gridline removal or softening
   - Legend placement discipline
   - Line thickness standards

### Medium Priority
3. **Header Bar System**
   - White vs slate header decision
   - Logo + title alignment rules
   - Reusable layout guidance

### Optional / Future
4. **Documentation Examples**
   - Example KPI row
   - Example table-heavy analytical page
   - Example executive summary page

---

## 9. Design North Star

> If a visual looks wrong, the fix should usually be:  
> **change the data or layout — not the formatting.**

This theme is designed to make that possible.
