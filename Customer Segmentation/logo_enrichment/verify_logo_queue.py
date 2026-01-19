#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import socket
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import customer_processing as cp  # noqa: E402


@dataclass(frozen=True)
class FetchResult:
    domain: str
    url: str
    status_code: Optional[int]
    content_type: str
    content_length: str
    outcome: str
    error: str


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def build_logo_url(domain: str, token: str, *, size: int = 128) -> str:
    # Use fallback=404 so “no logo” is detectable.
    return (
        f"https://img.logo.dev/{domain}"
        f"?token={token}&size={size}&format=png&retina=true&fallback=404"
    )


def build_apistemic_url(domain: str) -> str:
    # Apistemic supports fallback=404 to avoid monograms.
    return f"https://logos-api.apistemic.com/domain:{domain}?fallback=404"


def candidate_domains(domain: str) -> Iterable[str]:
    """
    Try the provided domain first, then progressively fall back by removing
    the left-most label until 2 labels remain.

    Example: jcps.kyschools.us -> jcps.kyschools.us, kyschools.us
    """
    d = cp.normalize_company_website(domain)
    if not d:
        return []

    parts = d.split(".")
    seen = set()
    out: List[str] = []

    def add(x: str) -> None:
        if x and x not in seen:
            seen.add(x)
            out.append(x)

    add(d)
    while len(parts) > 2:
        parts = parts[1:]
        add(".".join(parts))
        # Stop once we’re down to 2 labels.
        if len(parts) <= 2:
            break
    return out


def head_or_get(url: str, *, timeout_seconds: int = 15) -> Tuple[Optional[int], str, str, str]:
    """
    Returns (status_code, content_type, content_length, error_message)
    """
    headers = {"User-Agent": "CustomerSegmentationLogoVerifier/1.0"}

    def attempt(method: str) -> Tuple[Optional[int], str, str, str]:
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                status = getattr(resp, "status", None)
                ct = (resp.headers.get("Content-Type") or "").strip()
                cl = (resp.headers.get("Content-Length") or "").strip()
                return status, ct, cl, ""
        except urllib.error.HTTPError as e:
            ct = (getattr(e, "headers", None) or {}).get("Content-Type", "") if hasattr(e, "headers") else ""
            cl = (getattr(e, "headers", None) or {}).get("Content-Length", "") if hasattr(e, "headers") else ""
            return e.code, (ct or "").strip(), (cl or "").strip(), ""
        except (urllib.error.URLError, socket.timeout) as e:
            return None, "", "", str(e)

    status, ct, cl, err = attempt("HEAD")
    if status is None and err:
        # Network/DNS error; GET won't help.
        return status, ct, cl, err

    # Some CDNs don’t support HEAD; fallback to GET.
    if status in (405, 501) or (status is None and not err):
        return attempt("GET")
    return status, ct, cl, err


def verify_domain(domain: str, *, provider: str, token: str) -> FetchResult:
    for candidate in candidate_domains(domain):
        if provider == "apistemic":
            url = build_apistemic_url(candidate)
        else:
            url = build_logo_url(candidate, token)

        status, ct, cl, err = head_or_get(url)

        if err:
            return FetchResult(candidate, url, status, ct, cl, "error", err)

        if status == 200 and ct.lower().startswith("image/"):
            return FetchResult(candidate, url, status, ct, cl, "ok", "")

        if status == 404:
            # Try the next fallback domain candidate.
            continue

        if status in (401, 403):
            return FetchResult(candidate, url, status, ct, cl, "auth_error", "")

        return FetchResult(candidate, url, status, ct, cl, "unexpected", "")

    # All candidates returned 404.
    final_domain = cp.normalize_company_website(domain)
    if final_domain:
        url = build_apistemic_url(final_domain) if provider == "apistemic" else build_logo_url(final_domain, token)
    else:
        url = ""
    return FetchResult(final_domain, url, 404, "image/png", "", "not_found", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Logo.dev availability for domains in LogoQueue.csv.")
    parser.add_argument(
        "--queue",
        type=str,
        default="",
        help="Optional path to LogoQueue.csv (defaults to output/work/logos/LogoQueue.csv).",
    )
    parser.add_argument(
        "--domains",
        type=str,
        default="",
        help="Comma-separated domains to verify (bypasses the queue).",
    )
    parser.add_argument("--max-rows", type=int, default=50, help="Max rows to verify in this run.")
    parser.add_argument(
        "--provider",
        type=str,
        default="logo_dev",
        choices=["logo_dev", "apistemic"],
        help="Logo provider to verify against.",
    )
    args = parser.parse_args()

    token = ""
    if args.provider == "logo_dev":
        token = (os.environ.get("LOGO_DEV_PUBLISHABLE_KEY") or "").strip()
        if not token:
            raise SystemExit("Missing env var LOGO_DEV_PUBLISHABLE_KEY (do not pass tokens as CLI args).")

    paths = cp.default_paths()
    to_check: List[dict] = []
    if args.domains.strip():
        for raw in args.domains.split(","):
            d = cp.normalize_company_website(raw)
            if not d:
                continue
            to_check.append(
                {
                    "Master Customer Name Canonical": "",
                    "Company Website": d,
                    "Logo Domain (Approved)": d,
                    "Hosted Logo URL": "",
                    "Attempt Count": "0",
                    "Notes": "",
                }
            )
    else:
        queue_path = Path(args.queue).expanduser() if args.queue else (paths["work_dir"] / "logos" / "LogoQueue.csv")
        if not queue_path.exists():
            raise SystemExit(f"Missing queue file: {queue_path}")

        # Read queue rows.
        source_rows: List[dict] = []
        with queue_path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                source_rows.append(row)

        # Verify only rows without hosted URL first, then cap by max-rows.
        def priority(r: dict) -> tuple:
            hosted = (r.get("Hosted Logo URL") or "").strip()
            attempt_count = int(((r.get("Attempt Count") or "0").strip() or "0"))
            return (1 if hosted else 0, attempt_count)

        to_check = sorted(source_rows, key=priority)[: max(0, args.max_rows)]

    report_rows: List[dict] = []
    verified_at = now_utc_iso()
    for row in to_check:
        canonical = (row.get("Master Customer Name Canonical") or "").strip()
        website = (row.get("Company Website") or "").strip()
        approved = (row.get("Logo Domain (Approved)") or "").strip()
        base_domain = approved or website

        res = verify_domain(base_domain, provider=args.provider, token=token)

        report_rows.append(
            {
                "Verified At": verified_at,
                "Master Customer Name Canonical": canonical,
                "Company Website": website,
                "Logo Domain Used": res.domain,
                "Outcome": res.outcome,
                "HTTP Status": "" if res.status_code is None else str(res.status_code),
                "Content-Type": res.content_type,
                "Content-Length": res.content_length,
                "Error": res.error,
                "Notes": (row.get("Notes") or "").strip(),
            }
        )

    out_dir = paths["work_dir"] / "logos"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"LogoVerifyReport_{ts}.csv"
    fieldnames = [
        "Verified At",
        "Master Customer Name Canonical",
        "Company Website",
        "Logo Domain Used",
        "Outcome",
        "HTTP Status",
        "Content-Type",
        "Content-Length",
        "Error",
        "Notes",
    ]
    cp.write_csv_dicts(out_path, report_rows, fieldnames)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
