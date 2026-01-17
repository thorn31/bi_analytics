from __future__ import annotations

from customer_processing import (
    build_master_segmentation_rows,
    build_segmentation_rows,
    confidence_for_method,
    default_paths,
    load_master_websites,
    load_master_segmentation_overrides,
    load_overrides,
    read_csv_dicts,
    write_csv_dicts,
)


def main() -> None:
    paths = default_paths()

    master_map_path = paths["dedupe_output"]
    overrides_path = paths["manual_overrides"]
    websites_path = paths["master_websites"]
    master_seg_overrides_path = paths["master_segmentation_overrides"]
    output_segmentation = paths["segmentation_output"]
    output_master_segmentation = paths["master_segmentation_output"]

    if not master_map_path.exists():
        raise SystemExit(
            f"Error: Master map not found at {master_map_path}. Run dedupe first: `python3 dedupe_customers.py`"
        )

    overrides = load_overrides(overrides_path)
    websites = load_master_websites(websites_path)
    master_seg_overrides = load_master_segmentation_overrides(master_seg_overrides_path)
    master_rows = read_csv_dicts(master_map_path)

    master_segmentation_rows = build_master_segmentation_rows(master_rows)
    for row in master_segmentation_rows:
        canonical = (row.get("Master Customer Name Canonical") or "").strip()
        if canonical in master_seg_overrides:
            o = master_seg_overrides[canonical]
            if o.get("Industrial Group"):
                row["Industrial Group"] = o["Industrial Group"]
            if o.get("Industry Detail"):
                row["Industry Detail"] = o["Industry Detail"]
            if o.get("NAICS"):
                row["NAICS"] = o["NAICS"]
            if o.get("Method"):
                row["Method"] = o["Method"]
            if o.get("Support Category"):
                row["Support Category"] = o["Support Category"]
            if o.get("Company Website"):
                row["Company Website"] = o["Company Website"]
            override_method = o.get("Method") or ""
            if override_method:
                row["Method"] = override_method

            # Confidence/rationale should reflect governance posture.
            if (row.get("Method") or "").strip() == "AI-Assisted Search":
                row["Confidence"] = "Low"
                row["Rationale"] = "Queued for AI-assisted search"
            elif (row.get("Method") or "").strip() in {"Rule-Based", "Entity Inference", "Heuristic"}:
                conf, rationale = confidence_for_method((row.get("Method") or "").strip())
                row["Confidence"] = conf
                row["Rationale"] = f"Master override ({rationale.lower()})"
            else:
                row["Confidence"] = "High"
                row["Rationale"] = "Master override"
        if not row.get("Company Website"):
            row["Company Website"] = websites.get(canonical, "")
    segmentation_rows = build_segmentation_rows(master_rows, overrides=overrides)

    write_csv_dicts(
        output_master_segmentation,
        master_segmentation_rows,
        fieldnames=[
            "Master Customer Name",
            "Master Customer Name Canonical",
            "Industrial Group",
            "Industry Detail",
            "NAICS",
            "Method",
            "Confidence",
            "Rationale",
            "Support Category",
            "Company Website",
            "IsMerge",
            "MergeGroupSize",
        ],
    )
    write_csv_dicts(
        output_segmentation,
        segmentation_rows,
        fieldnames=[
            "Customer Key",
            "Original Name",
            "Master Customer Name",
            "Industrial Group",
            "Industry Detail",
            "NAICS",
            "Method",
            "Confidence",
            "Rationale",
            "Support Category",
            "Source",
        ],
    )

    print(f"Loaded {len(overrides)} manual overrides from {overrides_path}.")
    print(f"Loaded {len(websites)} master websites from {websites_path}.")
    print(f"Loaded {len(master_seg_overrides)} master segmentation overrides from {master_seg_overrides_path}.")
    print(f"Processed {len(segmentation_rows)} rows.")
    print(f"Saved master segmentation to {output_master_segmentation}")
    print(f"Saved segmentation output to {output_segmentation}")


if __name__ == "__main__":
    main()
