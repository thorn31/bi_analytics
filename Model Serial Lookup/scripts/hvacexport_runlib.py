from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path


def utc_compact_ts() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")


def ensure_clean_derived(snapshot_dir: Path, *, archive_existing: bool = True) -> Path:
    """
    Ensure snapshot_dir/derived is "clean" for new-style run outputs.

    Policy:
    - New outputs go under derived/runs/<run-id>/.
    - Any legacy top-level files under derived/ are moved into derived/_archive/<ts>/ (not deleted).
    """
    derived = snapshot_dir / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    (derived / "runs").mkdir(parents=True, exist_ok=True)

    keep_files = {"LATEST_RUN.txt", "LATEST_CANDIDATES.txt", "LATEST_CATALOG.txt"}
    legacy_files = [p for p in derived.iterdir() if p.is_file() and p.name not in keep_files]
    if legacy_files and archive_existing:
        archive_dir = derived / "_archive" / utc_compact_ts()
        archive_dir.mkdir(parents=True, exist_ok=True)
        for p in legacy_files:
            dst = archive_dir / p.name
            try:
                shutil.move(str(p), str(dst))
            except PermissionError:
                # Some environments (e.g., Windows mounts) may block renames/unlinks; best-effort archive.
                try:
                    shutil.copy2(str(p), str(dst))
                except Exception:
                    continue
                try:
                    p.unlink()
                except Exception:
                    # Leave original in place if we can't delete it.
                    pass
    return derived


def create_run_dir(snapshot_dir: Path, *, run_id: str) -> Path:
    derived = ensure_clean_derived(snapshot_dir, archive_existing=True)
    run_dir = derived / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (derived / "LATEST_RUN.txt").write_text(f"{run_id}\n", encoding="utf-8")
    return run_dir
