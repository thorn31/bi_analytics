# msl/

`msl` is the CLI + library code for:
- **Phase 1**: ingest cached Building-Center content → normalize → validate/export rulesets
- **Phase 2**: decode equipment exports with those rulesets
- **Phase 3**: baseline/mine/promote rules from labeled asset exports

Entry points:
- CLI: `python3 -m msl --help` (see `msl/cli.py`)
- Decoder logic: `msl/decoder/`
- Pipeline commands: `msl/pipeline/`

Rulesets:
- Current recommended ruleset path is stored in `data/rules_normalized/CURRENT.txt`.
