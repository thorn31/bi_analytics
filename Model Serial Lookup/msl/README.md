# msl/

`msl` is the CLI + library code for:
- ruleset building: ingest cached source content → normalize → validate/export rulesets
- decode engine: decode equipment exports with those rulesets
- mining/evaluation: baseline/mine/audit/promote rules from labeled asset exports

Entry points:
- CLI: `python3 -m msl --help` (see `msl/cli.py`)
- Operator wrapper: `python3 scripts/actions.py --help`
- Decoder logic: `msl/decoder/`
- Pipeline commands: `msl/pipeline/`

Rulesets:
- Current recommended ruleset path is stored in `data/rules_normalized/CURRENT.txt`.
