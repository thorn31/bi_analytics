# PowerBI Git Workflow

This folder contains PBIP-based Power BI projects. Use the workflow below to keep changes clean, reviewable, and versioned.

## Day-to-day workflow

1. Create a branch per change (e.g., feature/crr-new-measure, fix/gp-floor-slider).
2. Open the *.pbip from the project's current/ folder in Power BI Desktop.
3. Make edits, then save and close Power BI Desktop.
4. Review changes with git status and git diff.
5. Commit with a clear message.
6. Push the branch and merge to main (via PR or local merge).

## Project structure rules

- Keep only one "current" PBIP project per report in current/.
- Use archive/ for older versions; use git tags for releases instead of v0x folders.
- Store docs in docs/, snippets in code-snippets/, and data samples in data/.
- Do not rename *.Report or *.SemanticModel folders; Power BI expects those names.

## Git hygiene

- Keep *.pbix out of git (ignored in .gitignore).
- Avoid committing volatile cache files under .pbi/.

## Release flow

- When a version is ready, merge to main and tag the release (e.g., crr-v05).
- Optionally export a .pbix for distribution, but do not commit it.
