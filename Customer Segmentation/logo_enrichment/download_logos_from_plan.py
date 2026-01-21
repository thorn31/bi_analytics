#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import customer_processing as cp  # noqa: E402


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _download(url: str, dest: Path, *, timeout_seconds: int = 30) -> tuple[bool, str]:
    if not url:
        return False, "missing_url"
    headers = {"User-Agent": "CustomerSegmentationLogoDownloader/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            status = getattr(resp, "status", None)
            if status not in (None, 200):
                return False, f"http_{status}"
            data = resp.read()
            if not data:
                return False, "empty_response"
    except urllib.error.HTTPError as e:
        return False, f"http_{e.code}"
    except (urllib.error.URLError, socket.timeout) as e:
        return False, f"error_{e}"

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download logo files from Source URL in a HostedLogoUploadPlan CSV into a staging folder."
    )
    parser.add_argument(
        "--mapping-csv",
        default="",
        help=(
            "Optional: mapping CSV (e.g. Customer Key + Logo_URL/Hosted Logo URL). "
            "When provided, the upload plan will be regenerated before downloading."
        ),
    )
    parser.add_argument(
        "--base-url",
        default="",
        help=(
            "Optional: base hosted URL used when regenerating the plan from --mapping-csv "
            "(e.g. https://<acct>.blob.core.windows.net/<container>)."
        ),
    )
    parser.add_argument(
        "--plan-csv",
        default="output/work/logos/plans/HostedLogoUploadPlan.csv",
        help="Path to HostedLogoUploadPlan CSV (default: output/work/logos/plans/HostedLogoUploadPlan.csv).",
    )
    parser.add_argument(
        "--out-dir",
        default="output/work/logos/staged",
        help="Output directory for downloaded files (default: output/work/logos/staged).",
    )
    parser.add_argument(
        "--stage-dir",
        default="",
        help=(
            "Optional: directory to stage local files when regenerating the plan from --mapping-csv. "
            "Defaults to --out-dir when omitted."
        ),
    )
    parser.add_argument("--max-rows", type=int, default=-1, help="Max rows to process (-1 = all).")
    parser.add_argument("--timeout-seconds", type=int, default=30, help="HTTP timeout per download.")
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Only download when the destination file does not already exist (default: false).",
    )
    parser.add_argument(
        "--write-report-always",
        action="store_true",
        help="Always write a LogoDownloadReport CSV, even when there are 0 failures (default: false).",
    )
    parser.add_argument(
        "--continue-on-failures",
        action="store_true",
        help="Do not fail the command when some downloads fail (default: false).",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan_csv).expanduser().resolve()
    if args.mapping_csv.strip():
        mapping_path = Path(args.mapping_csv).expanduser().resolve()
        if not mapping_path.exists():
            raise SystemExit(f"Missing mapping CSV: {mapping_path}")

        stage_dir = Path(args.stage_dir).expanduser().resolve() if args.stage_dir.strip() else Path(args.out_dir).expanduser().resolve()
        script_path = (REPO_ROOT / "logo_enrichment" / "import_hosted_logos.py").resolve()
        cmd = [
            sys.executable,
            str(script_path),
            "--mapping-csv",
            str(mapping_path),
            "--plan-csv",
            str(plan_path),
            "--stage-dir",
            str(stage_dir),
        ]
        if args.base_url.strip():
            cmd.extend(["--base-url", args.base_url.strip()])

        # Regenerate plan so new rows in mapping are picked up automatically.
        res = subprocess.run(cmd, cwd=str(REPO_ROOT))
        if res.returncode != 0:
            raise SystemExit(res.returncode)

    if not plan_path.exists():
        raise SystemExit(f"Missing plan CSV: {plan_path}")

    rows = _read_csv(plan_path)
    if not rows:
        raise SystemExit(f"No rows found: {plan_path}")

    required = {"Source URL", "Blob Name"}
    if not required.issubset(set(rows[0].keys())):
        raise SystemExit(f"Plan CSV missing required columns {sorted(required)}: {plan_path}")

    out_dir = Path(args.out_dir).expanduser().resolve()

    processed = 0
    downloaded = 0
    skipped = 0
    failures: list[dict[str, str]] = []

    limit = args.max_rows
    for row in rows:
        if limit == 0:
            break
        if limit > 0:
            limit -= 1

        url = (row.get("Source URL") or "").strip()
        blob_name = (row.get("Blob Name") or "").strip()
        if not url or not blob_name:
            skipped += 1
            continue

        dest = out_dir / blob_name
        if args.only_missing and dest.exists():
            skipped += 1
            continue

        ok, err = _download(url, dest, timeout_seconds=args.timeout_seconds)
        processed += 1
        if ok:
            downloaded += 1
        else:
            failures.append(
                {
                    "Source URL": url,
                    "Blob Name": blob_name,
                    "Error": err,
                }
            )

    report_path = None
    if failures or args.write_report_always:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = plan_path.parent / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"LogoDownloadReport_{ts}.csv"
        cp.write_csv_dicts(report_path, failures, fieldnames=["Source URL", "Blob Name", "Error"])

    print(f"Plan: {plan_path}")
    print(f"Output dir: {out_dir}")
    print(f"Processed: {processed}")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {len(failures)}")
    if report_path:
        print(f"Wrote report: {report_path}")
    if failures:
        if not args.continue_on_failures:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
