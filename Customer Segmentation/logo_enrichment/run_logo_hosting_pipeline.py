#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, cwd: Path, dry_run: bool) -> None:
    printable = " ".join(cmd)
    if dry_run:
        print(f"[dry-run] {printable}")
        return
    res = subprocess.run(cmd, cwd=str(cwd))
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def _resolve_az_executable(az_path: str) -> str:
    """
    Resolve an Azure CLI executable that works on Windows + *nix.

    - If az_path is an explicit path, use it.
    - Otherwise, try PATH.
    - On Windows, fall back to common install locations (az.cmd).
    """
    candidate = (az_path or "").strip()
    if candidate and candidate not in {"az"} and Path(candidate).exists():
        return candidate

    which = shutil.which("az")
    if which:
        return which

    # Windows fallback: common Azure CLI install locations.
    fallbacks = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az",
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az",
    ]
    for fb in fallbacks:
        if Path(fb).exists():
            return fb

    # Let subprocess fail with a clear error later.
    return candidate or "az"


def _az_list_blobs(az_exe: str, account: str, container: str, *, dry_run: bool) -> set[str]:
    cmd = [
        az_exe,
        "storage",
        "blob",
        "list",
        "--account-name",
        account,
        "--container-name",
        container,
        "--auth-mode",
        "login",
        "--query",
        "[].name",
        "-o",
        "tsv",
    ]
    if dry_run:
        print(f"[dry-run] {' '.join(cmd)}")
        return set()

    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr)
        raise SystemExit(res.returncode)
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def _parse_account_container_from_base_url(base_url: str) -> tuple[str, str]:
    """
    Expected: https://<account>.blob.core.windows.net/<container>
    """
    v = (base_url or "").strip()
    if not v.startswith("http"):
        return "", ""
    v = v.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    # https://stgreen.blob.core.windows.net/logos
    try:
        host = v.split("://", 1)[1].split("/", 1)[0]
        path = v.split("://", 1)[1].split("/", 1)[1]
    except Exception:
        return "", ""
    account = host.split(".", 1)[0].strip()
    container = path.split("/", 1)[0].strip()
    return account, container


def main() -> None:
    parser = argparse.ArgumentParser(
        description="End-to-end hosted-logo pipeline: plan+download -> upload to Azure -> persist governance -> regenerate outputs."
    )
    parser.add_argument(
        "--mapping-csv",
        default="logo_enrichment/TargetLogoHosted.csv",
        help="Mapping CSV to process (default: logo_enrichment/TargetLogoHosted.csv).",
    )
    parser.add_argument(
        "--base-url",
        default="https://stgreen.blob.core.windows.net/logos",
        help="Azure container base URL (default: https://stgreen.blob.core.windows.net/logos).",
    )
    parser.add_argument(
        "--plan-csv",
        default="output/work/logos/plans/HostedLogoUploadPlan_target.csv",
        help="Where to write the upload plan (default: output/work/logos/plans/HostedLogoUploadPlan_target.csv).",
    )
    parser.add_argument(
        "--stage-dir",
        default="output/work/logos/staged_target",
        help="Local staging folder for downloads (default: output/work/logos/staged_target).",
    )
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Only download files that are missing locally (default: false).",
    )
    parser.add_argument(
        "--continue-on-download-failures",
        action="store_true",
        help="Continue to upload/persist even if some downloads fail (default: false).",
    )
    parser.add_argument(
        "--strict-download",
        action="store_true",
        help="Fail the pipeline if any downloads fail (default: false).",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip regenerating plan + downloading logos (default: false).",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip Azure upload (default: false).",
    )
    parser.add_argument(
        "--skip-persist",
        action="store_true",
        help="Skip persisting URLs into data/enrichment/MasterLogos.csv (default: false).",
    )
    parser.add_argument(
        "--skip-segmentation",
        action="store_true",
        help="Skip regenerating final outputs via segment_customers.py (default: false).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite blobs in Azure when names already exist (default: false).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would run without executing them.",
    )
    parser.add_argument(
        "--az-path",
        default="az",
        help="Azure CLI executable path/name (default: az).",
    )
    args = parser.parse_args()

    mapping_csv = (REPO_ROOT / args.mapping_csv).resolve() if not Path(args.mapping_csv).is_absolute() else Path(args.mapping_csv)
    plan_csv = (REPO_ROOT / args.plan_csv).resolve() if not Path(args.plan_csv).is_absolute() else Path(args.plan_csv)
    stage_dir = (REPO_ROOT / args.stage_dir).resolve() if not Path(args.stage_dir).is_absolute() else Path(args.stage_dir)

    if not mapping_csv.exists():
        raise SystemExit(f"Missing mapping CSV: {mapping_csv}")

    # 1) Plan + download (regenerates plan automatically).
    if not args.skip_download:
        cmd = [
            sys.executable,
            str((REPO_ROOT / "logo_enrichment" / "download_logos_from_plan.py").resolve()),
            "--mapping-csv",
            str(mapping_csv),
            "--base-url",
            args.base_url,
            "--plan-csv",
            str(plan_csv),
            "--out-dir",
            str(stage_dir),
        ]
        if args.only_missing:
            cmd.append("--only-missing")
        # Default behavior: continue so we can still upload/persist successful downloads.
        if args.continue_on_download_failures or not args.strict_download:
            cmd.append("--continue-on-failures")
        _run(cmd, cwd=REPO_ROOT, dry_run=args.dry_run)

    # 2) Upload new blobs to Azure (auth-mode login).
    existing_after_upload: set[str] = set()
    if not args.skip_upload:
        az_exe = _resolve_az_executable(args.az_path)

        account, container = _parse_account_container_from_base_url(args.base_url)
        if not account or not container:
            raise SystemExit(f"Could not parse account/container from base URL: {args.base_url}")

        stage_dir.mkdir(parents=True, exist_ok=True)
        local_files = sorted([p for p in stage_dir.iterdir() if p.is_file()])
        if not local_files:
            print(f"No local files found to upload in {stage_dir}")
        else:
            try:
                existing = _az_list_blobs(az_exe, account, container, dry_run=args.dry_run)
            except FileNotFoundError:
                raise SystemExit(
                    "Azure CLI 'az' was not found on PATH in this environment. "
                    "Run the pipeline on your machine where az is installed, "
                    "or pass --skip-upload (and upload manually), "
                    "or provide --az-path with the full path to az."
                )
            uploaded = 0
            skipped = 0
            existing_after_upload = set(existing)
            for path in local_files:
                blob_name = path.name
                if not args.overwrite and blob_name in existing:
                    skipped += 1
                    continue
                cmd = [
                    az_exe,
                    "storage",
                    "blob",
                    "upload",
                    "--account-name",
                    account,
                    "--container-name",
                    container,
                    "--auth-mode",
                    "login",
                    "--name",
                    blob_name,
                    "--file",
                    str(path),
                    "--overwrite",
                    "true" if args.overwrite else "false",
                    "--only-show-errors",
                ]
                _run(cmd, cwd=REPO_ROOT, dry_run=args.dry_run)
                uploaded += 1
                existing_after_upload.add(blob_name)
            print(f"Azure upload complete (uploaded={uploaded}, skipped_existing={skipped}, overwrite={args.overwrite})")

    # 3) Persist hosted URLs into governance.
    if not args.skip_persist:
        # Persist only blobs that are confirmed present in Azure (prevents writing hosted URLs
        # for rows whose source download failed and therefore were not uploaded).
        persist_mapping = plan_csv.with_name("HostedLogoPersistMapping.csv")
        if args.dry_run:
            print(f"[dry-run] write persist mapping: {persist_mapping}")
        else:
            if not plan_csv.exists():
                raise SystemExit(f"Missing plan CSV: {plan_csv}")
            with plan_csv.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                rows_out: list[dict[str, str]] = []
                for row in reader:
                    canonical = (row.get("Master Customer Name Canonical") or "").strip()
                    hosted = (row.get("Hosted Logo URL") or "").strip()
                    blob_name = (row.get("Blob Name") or "").strip()
                    if not canonical or not hosted or not blob_name:
                        continue
                    # Only persist URLs when we can confirm the blob exists in Azure.
                    # If upload is skipped, require the user to persist manually (or rerun with upload).
                    if args.skip_upload:
                        continue
                    if existing_after_upload and blob_name not in existing_after_upload:
                        continue
                    rows_out.append({"Master Customer Name Canonical": canonical, "Hosted Logo URL": hosted})

            if not rows_out:
                print(
                    "No hosted logos eligible for persistence (nothing confirmed uploaded). "
                    "Skipping MasterLogos.csv update."
                )
                return

            persist_mapping.parent.mkdir(parents=True, exist_ok=True)
            with persist_mapping.open("w", encoding="utf-8-sig", newline="") as out_handle:
                writer = csv.DictWriter(out_handle, fieldnames=["Master Customer Name Canonical", "Hosted Logo URL"])
                writer.writeheader()
                writer.writerows(rows_out)

        cmd = [
            sys.executable,
            str((REPO_ROOT / "logo_enrichment" / "import_hosted_logos.py").resolve()),
            "--mapping-csv",
            str(persist_mapping),
            "--apply-master-logos",
        ]
        # Hosted Logo URL is already final, so base-url isn't required here.
        _run(cmd, cwd=REPO_ROOT, dry_run=args.dry_run)

    # 4) Regenerate outputs (now includes hosted + fallback logo URLs).
    if not args.skip_segmentation:
        cmd = [sys.executable, str((REPO_ROOT / "segment_customers.py").resolve())]
        # Ensure the same env var behavior as running it from the shell.
        _run(cmd, cwd=REPO_ROOT, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
