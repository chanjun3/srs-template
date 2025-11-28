# Self-Healing CI (FixerAgent + ReviewerAgent)

## Overview
- **FixerAgent (L4)** triages failed GitHub Actions runs (`SRS CI`). Triggered via `workflow_run` and logs decisions to `logs/fixer_agent/`.
- **ReviewerAgent (L5)** evaluates pull requests against the repository SRS, applying auto-review/merge rules and logging to `logs/reviewer_agent/`.

## Configuration
- Settings live in `self_healing_ci.toml`. Flags can be overridden by repo variables `AUTO_FIX_ENABLED` / `AUTO_MERGE_ENABLED`.
- Key options:
  - `core.auto_fix_enabled` – enable/disable FixerAgent workflow.
  - `core.auto_merge_enabled` – allow ReviewerAgent to merge.
  - `limits.max_auto_patch_lines` – diff size threshold for automation.
  - `limits.blocked_paths` – glob list of paths never auto-modified.
- Environment overrides:
  - `MAX_AUTO_PATCH_LINES` (CI/job level) replaces the TOML limit.

## Operation
1. **FixerAgent Workflow (`.github/workflows/fixer-agent.yml`):**
   - Runs when `SRS CI` finishes with failure.
   - Downloads workflow logs via `gh run download`.
   - Executes `tools/fixer_agent/main.py` (currently dry-run) which:
     - Loads SRS (`docs/spec_os/srs.md`).
     - Classifies failure & records patch/test plan.
     - Emits JSON log referencing SRS digest, blocked paths, recommended actions.
2. **ReviewerAgent Workflow (`.github/workflows/reviewer-agent.yml`):**
   - Runs on PR open/reopen/update.
   - Runs `tools/reviewer_agent/main.py` to:
     - Load TOML config + SRS hash.
     - Compute diff stats vs base branch.
     - Detect blocked paths / large diffs & decide approve/comment/block.
     - Optionally auto-merge (future work; currently prints placeholder).

## Logs & Observability
- Logs stored under `logs/fixer_agent/*.json` and `logs/reviewer_agent/*.json` with timestamped filenames including SRS hash, decisions, warnings.
- Ensure `logs/` is writable in CI environments; `.gitkeep` tracks directories in repo.

## TODO / Future Work
1. Extend FixerAgent from dry-run to real patch synthesis, branch push, and PR creation.
2. Integrate GitHub API calls for ReviewerAgent auto-approval / merge comments.
3. Enhance classification heuristics and blocked-path enforcement (glob/regex).
4. Add automated tests (unit/integration) for FixerAgent & ReviewerAgent modules.
