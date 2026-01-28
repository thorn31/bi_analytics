# data/reports/

This folder is the canonical home for **run outputs** (baselines, audits, coverage reports, workflow runs).

Notes:
- Most contents are gitignored (large + reproducible).
- A small set of pointer files is tracked so “latest” is obvious.

Tracked pointers:
- `data/reports/CURRENT_RUN.txt`: latest wrapper run id (from `scripts/actions.py`)
- `data/reports/CURRENT_BASELINE.txt`: latest baseline run id (from truth evaluation)

To open the latest run folder:
```bash
run_id="$(cat data/reports/CURRENT_RUN.txt | tr -d '\r\n')"
ls "data/reports/${run_id}"
```

