from __future__ import annotations

from collections import Counter

from customer_processing import (
    build_dedupe_log_rows,
    build_master_map_rows,
    default_paths,
    load_overrides,
    read_csv_dicts,
    write_csv_dicts,
)


def main() -> None:
    paths = default_paths()

    input_path = paths["input_customers"]
    overrides_path = paths["manual_overrides"]
    output_master_map = paths["dedupe_output"]
    output_log = paths["dedupe_log"]

    if not input_path.exists():
        raise SystemExit(f"Error: Input file not found at {input_path}")

    overrides = load_overrides(overrides_path)
    input_rows = read_csv_dicts(input_path)

    master_rows = build_master_map_rows(input_rows, overrides=overrides)
    master_counts = Counter(row["Master Customer Name Canonical"] for row in master_rows)
    for row in master_rows:
        group_size = master_counts[row["Master Customer Name Canonical"]]
        row["IsMerge"] = "TRUE" if group_size > 1 else "FALSE"
        row["MergeGroupSize"] = str(group_size)

    log_rows = build_dedupe_log_rows(
        master_rows, overrides=overrides, master_name_counts=dict(master_counts)
    )

    write_csv_dicts(
        output_master_map,
        master_rows,
        fieldnames=[
            "Customer Key",
            "Customer Number",
            "Original Name",
            "Master Customer Name",
            "Master Customer Name Canonical",
            "Segment Source Name",
            "IsMerge",
            "MergeGroupSize",
            "Source",
            "Last Billing Date (Any Stream)",
        ],
    )
    write_csv_dicts(
        output_log,
        log_rows,
        fieldnames=[
            "Master Customer Name",
            "Master Customer Name Canonical",
            "Original Name",
            "Initial Clean Name",
            "Type",
            "IsMerge",
            "MergeGroupSize",
        ],
    )

    input_keys = {row["Customer Key"] for row in input_rows}
    override_keys = set(overrides.keys())
    missing_override_keys = sorted(override_keys - input_keys)

    print(f"Loaded {len(overrides)} manual overrides from {overrides_path}.")
    if missing_override_keys:
        print(f"Warning: {len(missing_override_keys)} override keys not found in input.")
    print(f"Processed {len(master_rows)} input rows.")
    print(f"Saved master map to {output_master_map}")
    print(f"Saved deduplication log to {output_log}")


if __name__ == "__main__":
    main()
