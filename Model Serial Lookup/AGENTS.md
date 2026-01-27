# AGENTS.md — Model Serial Lookup

Use the documentation in `docs/` as the source of truth for intent and workflow.

Start here:
- `docs/CONCEPTS.md`: high-level architecture (Librarian vs Detective).
- `docs/STATUS.md` for current baseline ruleset + how to run/reproduce the pipeline.
- `docs/TODO.md` for the current checklist (Phase 1/2/3); keep it updated as you make progress.
- `docs/README.md` for a short index of the docs set.

Current pointers (avoid hardcoding run IDs in docs/scripts):
- `data/rules_normalized/CURRENT.txt` for the current recommended ruleset.
- `data/rules_normalized/CURRENT_PHASE1.txt` for the current Phase 1 baseline ruleset.
- `data/reports/CURRENT_BASELINE.txt` for the current baseline report folder.

Plans:
- `docs/PLAN.md` for Phase 1 (Building-Center ingestion → versioned rules).
- `docs/PLAN_PHASE2.md` for Phase 2 (deterministic decoder engine).
- `docs/PLAN_PHASE3.md` for Phase 3 (rule discovery from labeled asset reports).

Guidelines:
- Prefer deterministic extraction/validation; don’t invent rules not supported by source text.
- Always write new outputs to a new versioned folder under `data/` (don’t overwrite existing rulesets).
- When milestones change, update `docs/STATUS.md` and `docs/TODO.md`.
