#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_ACCOUNT_NAME = "stgreen"
DEFAULT_CONTAINER_NAME = "datasets"
DEFAULT_PREFIX = "customer_segmentation"


def _default_az_path() -> str | None:
    az = shutil.which("az")
    if az:
        return az

    # Common Windows install locations (PowerShell / cmd execution alias issues are common).
    candidates = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c

    return None


def _run(cmd: list[str], dry_run: bool) -> None:
    if dry_run:
        print("DRY RUN:", " ".join(cmd))
        return
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload CustomerSegmentation outputs to Azure Blob Storage (datasets/customer_segmentation)."
    )
    parser.add_argument("--account-name", default=DEFAULT_ACCOUNT_NAME, help="Storage account name.")
    parser.add_argument("--container-name", default=DEFAULT_CONTAINER_NAME, help="Container name.")
    parser.add_argument(
        "--prefix",
        default=DEFAULT_PREFIX,
        help="Blob virtual folder prefix (e.g., customer_segmentation).",
    )
    parser.add_argument(
        "--az-path",
        default=None,
        help="Optional full path to az or az.cmd (useful if az is not on PATH).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without uploading.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    outputs = [
        repo_root / "output" / "final" / "CustomerSegmentation.csv",
        repo_root / "output" / "final" / "MasterCustomerSegmentation.csv",
    ]

    missing = [str(p) for p in outputs if not p.exists()]
    if missing:
        raise SystemExit(
            "Missing required output file(s):\n- "
            + "\n- ".join(missing)
            + "\n\nRun:\n  python3 dedupe_customers.py\n  python3 segment_customers.py"
        )

    az_path = args.az_path or _default_az_path()
    if not az_path:
        raise SystemExit(
            "Azure CLI 'az' was not found on PATH.\n"
            "Install Azure CLI or pass --az-path, e.g.\n"
            r'  py -3 publish_datasets_to_blob.py --az-path "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"'
        )

    for local_path in outputs:
        blob_name = f"{args.prefix}/{local_path.name}"
        cmd = [
            az_path,
            "storage",
            "blob",
            "upload",
            "--account-name",
            args.account_name,
            "--auth-mode",
            "login",
            "--container-name",
            args.container_name,
            "--name",
            blob_name,
            "--file",
            str(local_path),
            "--overwrite",
        ]
        _run(cmd, args.dry_run)
        print(f"Uploaded: {local_path} -> {args.account_name}/{args.container_name}/{blob_name}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode) from e
