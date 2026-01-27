"""
Ruleset Manager: Centralized logic for CURRENT.txt pointer management and ruleset cleanup.

This module provides:
- read_current_ruleset(): Read CURRENT.txt and return the ruleset directory path
- update_current_pointer(): Update CURRENT.txt to point to a given ruleset directory
- list_ruleset_dirs(): List valid ruleset directories sorted by mtime (newest first)
- cleanup_old_rulesets(): Remove old rulesets beyond retention count, protecting CURRENT.txt target
- resolve_ruleset_dir(): Resolve ruleset: explicit arg > CURRENT.txt > None
"""
from __future__ import annotations

import shutil
from pathlib import Path

RULES_NORMALIZED_DIR = Path("data/rules_normalized")
CURRENT_POINTER_FILE = "CURRENT.txt"
LEGACY_POINTER_FILE = "CURRENT_PHASE1.txt"
DEFAULT_RETENTION_COUNT = 5


def read_current_ruleset(base_dir: Path | None = None) -> Path | None:
    """
    Read CURRENT.txt and return the ruleset directory path.

    Returns None if CURRENT.txt doesn't exist or points to a non-existent directory.
    """
    base = base_dir or RULES_NORMALIZED_DIR
    pointer_file = base / CURRENT_POINTER_FILE

    if not pointer_file.exists():
        return None

    content = pointer_file.read_text(encoding="utf-8").strip()
    if not content:
        return None

    # Handle both relative (to base_dir) and absolute paths
    ruleset_path = Path(content)
    if not ruleset_path.is_absolute():
        # Content may include the base dir prefix or just the folder name
        if content.startswith(str(base)):
            ruleset_path = Path(content)
        else:
            ruleset_path = base / ruleset_path.name

    if ruleset_path.exists() and ruleset_path.is_dir():
        return ruleset_path

    return None


def update_current_pointer(ruleset_dir: Path, base_dir: Path | None = None) -> None:
    """
    Update CURRENT.txt to point to the given ruleset directory.

    The pointer file stores the path relative to the working directory,
    matching the format: data/rules_normalized/<ruleset_name>
    """
    base = base_dir or RULES_NORMALIZED_DIR
    pointer_file = base / CURRENT_POINTER_FILE

    # Store path relative to working directory for consistency
    pointer_content = str(ruleset_dir)
    pointer_file.write_text(pointer_content + "\n", encoding="utf-8")


def list_ruleset_dirs(base_dir: Path | None = None) -> list[Path]:
    """
    List valid ruleset directories sorted by mtime (newest first).

    A valid ruleset directory contains SerialDecodeRule.csv and/or AttributeDecodeRule.csv.
    """
    base = base_dir or RULES_NORMALIZED_DIR

    if not base.exists():
        return []

    candidates: list[Path] = []
    for p in base.iterdir():
        if not p.is_dir():
            continue
        # Valid ruleset has at least one of the rule CSV files
        if (p / "SerialDecodeRule.csv").exists() or (p / "AttributeDecodeRule.csv").exists():
            candidates.append(p)

    # Sort by modification time, newest first
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)


def cleanup_old_rulesets(
    retention_count: int = DEFAULT_RETENTION_COUNT,
    dry_run: bool = False,
    base_dir: Path | None = None,
) -> list[Path]:
    """
    Remove old rulesets beyond retention count.

    Always protects the directory pointed to by CURRENT.txt.
    Returns list of directories that were (or would be in dry_run) removed.

    Also removes legacy CURRENT_PHASE1.txt if it exists.
    """
    base = base_dir or RULES_NORMALIZED_DIR

    # Remove legacy pointer file
    legacy_pointer = base / LEGACY_POINTER_FILE
    if legacy_pointer.exists():
        if dry_run:
            print(f"Would remove legacy pointer: {legacy_pointer}")
        else:
            legacy_pointer.unlink()
            print(f"Removed legacy pointer: {legacy_pointer}")

    # Get current ruleset to protect it
    current_ruleset = read_current_ruleset(base)

    # Get all rulesets sorted by mtime (newest first)
    all_rulesets = list_ruleset_dirs(base)

    if len(all_rulesets) <= retention_count:
        return []

    # Rulesets to keep: the newest `retention_count` + the current one (if not already in top N)
    to_keep = set(all_rulesets[:retention_count])
    if current_ruleset:
        to_keep.add(current_ruleset)

    # Rulesets to remove
    to_remove = [r for r in all_rulesets if r not in to_keep]

    def _on_rmtree_error(func, path, exc_info):
        """
        Error handler for shutil.rmtree.
        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.
        If the error is because the file is being used by another process, it just fails.
        """
        import stat
        import os
        
        # Check if access error
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        else:
            # Re-raise the original exception if we can't handle it
            raise

    for ruleset in to_remove:
        if dry_run:
            print(f"Would remove: {ruleset}")
        else:
            try:
                shutil.rmtree(ruleset, onerror=_on_rmtree_error)
                print(f"Removed: {ruleset}")
            except (PermissionError, OSError) as e:
                print(f"WARNING: Failed to remove: {ruleset} ({e}) - likely file in use")

    return to_remove


def resolve_ruleset_dir(
    explicit_dir: str | Path | None,
    base_dir: Path | None = None,
) -> Path | None:
    """
    Resolve ruleset directory with priority: explicit arg > CURRENT.txt > None.

    Args:
        explicit_dir: Explicitly provided ruleset directory (from CLI arg)
        base_dir: Base directory for CURRENT.txt lookup

    Returns:
        Resolved Path to ruleset directory, or None if not resolvable
    """
    # Priority 1: Explicit argument
    if explicit_dir:
        path = Path(explicit_dir)
        if path.exists() and path.is_dir():
            return path
        # If explicit but doesn't exist, return None (caller should error)
        return None

    # Priority 2: CURRENT.txt
    current = read_current_ruleset(base_dir)
    if current:
        return current

    # Priority 3: None (caller decides what to do)
    return None


def cmd_cleanup_rulesets(args) -> int:
    """CLI handler for cleanup-rulesets command."""
    retention = getattr(args, "retention", DEFAULT_RETENTION_COUNT)
    dry_run = getattr(args, "dry_run", False)

    base_dir = Path(args.rules_base_dir) if getattr(args, "rules_base_dir", None) else RULES_NORMALIZED_DIR

    removed = cleanup_old_rulesets(
        retention_count=retention,
        dry_run=dry_run,
        base_dir=base_dir,
    )

    if dry_run:
        print(f"\nDry run: {len(removed)} ruleset(s) would be removed.")
    else:
        print(f"\nCleanup complete: {len(removed)} ruleset(s) removed.")

    # Show what remains
    remaining = list_ruleset_dirs(base_dir)
    print(f"Remaining rulesets: {len(remaining)}")
    for r in remaining[:10]:
        print(f"  - {r.name}")
    if len(remaining) > 10:
        print(f"  ... and {len(remaining) - 10} more")

    return 0
