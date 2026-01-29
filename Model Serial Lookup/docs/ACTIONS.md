# ACTIONS — Contracts + Commands

Canonical entry point:
```bash
python3 scripts/actions.py --help
```

This wrapper orchestrates existing `msl` commands and standardizes outputs.

## Output formats (standard)
- Tables: `*.csv`
- Record streams: `*.jsonl`
- Small summaries/metadata: `*.json`
- Human reports: `*.md`
- Logs: `*.log`

## Common flags
- `--run-id`: explicit run folder name under `data/reports/`
- `--tag`: used to generate a default run id
- `--ruleset-dir`: ruleset dir or ruleset id (defaults to CURRENT)

## Action: `ruleset.validate`
Purpose: resolve current ruleset, validate schema, emit counts + issues.

Command:
```bash
python3 scripts/actions.py ruleset.validate --tag check
```

Outputs:
- `data/reports/<run-id>/ruleset.validate/ruleset_counts.json`
- `data/reports/<run-id>/ruleset.validate/ruleset_issues.jsonl`
- `data/reports/<run-id>/ruleset.validate/stdout.log`

Success:
- CURRENT resolves to an existing ruleset folder with `SerialDecodeRule.csv`

## Action: `decode.run --input <csv>`
Purpose: run deterministic decode against an asset dataset.

Command:
```bash
python3 scripts/actions.py decode.run --input <assets.csv> --tag decode
```

Outputs:
- `data/reports/<run-id>/decode.run/decoded.csv`
- `data/reports/<run-id>/decode.run/attributes_long.csv`
- `data/reports/<run-id>/decode.run/decode_summary.json`

## Action: `eval.coverage --input <csv>`
Purpose: coverage summary.
- If labeled (has `KnownManufactureYear`), this routes to `eval.truth`.
- If unlabeled, this runs `msl gap-report`.

Command:
```bash
python3 scripts/actions.py eval.coverage --input <assets.csv> --tag coverage
```

Outputs (unlabeled):
- `data/reports/<run-id>/eval.coverage/gap_report.csv`
- `data/reports/<run-id>/eval.coverage/gap_report.summary.json`
- `data/reports/<run-id>/eval.coverage/coverage_report.md`

## Action: `eval.truth --input <labeled.csv>`
Purpose: baseline accuracy/coverage vs ground truth (year now; expandable later).

Command:
```bash
python3 scripts/actions.py eval.truth --input <labeled.csv> --tag truth
```

Outputs (from baseline engine):
- `data/reports/<run-id>/eval.truth/baseline_decoder_scorecard.csv`
- `data/reports/<run-id>/eval.truth/next_targets.md`
- `data/reports/<run-id>/eval.truth/training_data_profile.md`

## Action: `mine.rules --input <labeled.csv>`
Purpose: mine deterministic candidate rules from labeled data.

Command:
```bash
python3 scripts/actions.py mine.rules --input <labeled.csv> --tag mine
```

Outputs:
- Candidates: `data/rules_discovered/<run-id>/candidates/`
- Mining reports (engine-native): `data/reports/<run-id>/` (root-level mining summaries)
- Wrapper metadata: `data/reports/<run-id>/mine.rules/`

## Action: `eval.candidates --input <labeled.csv> --candidates-dir <dir>`
Purpose: audit candidates (holdout + collision checks).

Command:
```bash
python3 scripts/actions.py eval.candidates --input <labeled.csv> --candidates-dir <candidates-dir> --tag audit
```

Outputs:
- `data/reports/<run-id>/eval.candidates/holdout_validation_results.csv`
- `data/reports/<run-id>/eval.candidates/false_positive_audit.csv`

## Manual additions inclusion
The wrapper treats `data/rules_discovered/manual_additions/` as an **always-on overlay** for:
- `workflow.improve` (creates `candidates_effective/` in the run root)
- `ruleset.promote` (merges manual additions into a `candidates_effective/` dir before promotion)

Disable this with `--no-manual-additions`.

## Action: `ruleset.promote --new-ruleset-id <id> --candidates-dir <dir>`
Purpose: promote candidates into a new immutable ruleset folder under `data/rules_normalized/`.

Hard gates:
- Candidate decode rows must satisfy minimum schema requirements (e.g., serial candidates require `example_serials`).

Audit gating:
- If `--audit-dir` is provided (optional), promotion is gated by audit metrics and thresholds.
- If `--audit-dir` is omitted, promotion promotes all candidates (still deduped + safety checks).
- Wrapper flag `--promote-all` forces skipping audit gating.

Command:
```bash
python3 scripts/actions.py ruleset.promote \
  --new-ruleset-id 2026-01-28-sdi-master-v4 \
  --candidates-dir data/rules_discovered/<run-id>/candidates \
  --tag promote
```

Outputs:
- New ruleset folder: `data/rules_normalized/<new-ruleset-id>/`
- Logs: `data/reports/<run-id>/ruleset.promote/`

## Action: `workflow.improve --input <labeled.csv> [--promote]`
Purpose: run a single deterministic “improve” chain and write one consolidated report.

Chain:
1. `ruleset.validate`
2. `decode.run`
3. `eval.truth`
4. `mine.rules`
5. `eval.candidates`
6. optional `ruleset.promote`
7. optional re-run truth and write deltas

Command:
```bash
python3 scripts/actions.py workflow.improve --input <labeled.csv> --tag improve
```

Consolidated output:
- `data/reports/<run-id>/WORKFLOW_REPORT.md`
- Convenience copies in the run root:
  - `data/reports/<run-id>/NEXT_TARGETS.md` (from truth evaluation)
  - `data/reports/<run-id>/NEXT_TARGETS_AFTER.md` (after promotion, if promoted)
  - `data/reports/<run-id>/RULESET_DIFF.md` (after promotion, if promoted)
