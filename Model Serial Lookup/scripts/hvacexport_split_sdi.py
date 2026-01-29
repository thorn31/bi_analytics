#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def _write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def _group_key(row: dict[str, str], group_by: str) -> str:
    if group_by == "model":
        return (row.get("ModelNumber") or "").strip()
    if group_by == "unit":
        return (row.get("Unit ID") or "").strip()
    if group_by == "building_unit":
        return f"{(row.get('Building') or '').strip()}::{(row.get('Unit ID') or '').strip()}"
    raise ValueError(f"Unknown group_by={group_by}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hvacexport_split_sdi", description="Split SDI normalized CSV into train/holdout (grouped to avoid leakage).")
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-train", required=True)
    ap.add_argument("--out-holdout", required=True)
    ap.add_argument("--out-summary", default="")
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--group-by", choices=["model", "unit", "building_unit"], default="model")
    args = ap.parse_args(argv)

    in_path = Path(args.input)
    rows = _read_rows(in_path)
    if not rows:
        raise SystemExit("No rows read")

    fieldnames = list(rows[0].keys())
    gb = str(args.group_by)

    groups: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        k = _group_key(r, gb)
        if not k:
            # If group key is missing, isolate row to prevent leakage.
            k = f"__MISSING__::{i}"
        groups[k].append(i)

    keys = list(groups.keys())
    rng = random.Random(int(args.seed))
    rng.shuffle(keys)

    target_train = int(round(len(rows) * float(args.train_frac)))
    train_idx: set[int] = set()
    for k in keys:
        if len(train_idx) >= target_train:
            break
        for i in groups[k]:
            train_idx.add(i)

    train_rows = [rows[i] for i in range(len(rows)) if i in train_idx]
    holdout_rows = [rows[i] for i in range(len(rows)) if i not in train_idx]

    _write_rows(Path(args.out_train), train_rows, fieldnames)
    _write_rows(Path(args.out_holdout), holdout_rows, fieldnames)

    summary = {
        "input_rows_n": len(rows),
        "train_rows_n": len(train_rows),
        "holdout_rows_n": len(holdout_rows),
        "train_frac": float(args.train_frac),
        "seed": int(args.seed),
        "group_by": gb,
        "unique_groups_n": len(groups),
        "train_groups_n": len({k for k in keys if any(i in train_idx for i in groups[k])}),
    }
    if str(args.out_summary).strip():
        Path(args.out_summary).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

