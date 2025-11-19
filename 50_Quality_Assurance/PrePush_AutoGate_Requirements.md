# Pre-Push / Pre-Check Auto-Gate Requirements

## 1. Purpose
- Pre-push auto-gate enforces spec-first quality gates before any branch leaves a developer workstation, protecting SRS, policy-tracker-ai, and sibling repos from inconsistent or unsafe commits.
- The hook and its centrally managed PowerShell script keep AI agent workflows deterministic and auditable, ensuring Codex-aligned automation can rely on clean baselines.

## 2. Scope
- Applies to repositories: SRS (primary), policy-tracker-ai, and any downstream workspace inheriting Codex QA governance.
- Covers `.git/hooks/pre-push` hook invocation, delegated PowerShell orchestration, and required lint/test utilities but excludes infrastructure beyond local workstation execution.

## 3. Definitions
- **Spec-first**: Workflow where requirements and policies precede implementation and CI/CD.
- **Auto-gate**: Mandatory automated check that blocks `git push` until all criteria succeed.
- **Central script**: Version-controlled PowerShell entry point stored once (e.g., `tools/hooks/pre_push.ps1`) and referenced by repositories via relative path.
- **Fail-fast**: Execution halts at the first unmet requirement, returning non-zero status to Git.

## 4. System Overview
- `.git/hooks/pre-push` is a lightweight shim that calls the shared PowerShell script via relative/absolute reference.
- The script enumerates branch state, workspace cleanliness, secrets, schema, lint, and smoke tests; failures block pushes.
- Results are streamed to the terminal with actionable error messages designed for AI/agent consumption.

## 5. Functional Requirements (FR)
| ID | Requirement |
| --- | --- |
| FR-1 | Validate current branch naming matches approved policies (e.g., `feat/*`, `fix/*`, `release/*`). |
| FR-2 | Detect uncommitted changes (`git status --porcelain`), warning on untracked files and failing when staged content diverges from HEAD. |
| FR-3 | Scan for secret artifacts (`*.env`, `*.key`, `*.pem`, `.supabase/config`) in tracked/untracked paths; block pushes upon detection. |
| FR-4 | Run YAML, Markdown, and JSON schema/syntax checks using repo-standard linters (e.g., `yamllint`, `markdownlint-cli`, `jq --exit-status .`). |
| FR-5 | Invoke Supabase migration lint (e.g., `supabase db lint`) ensuring migrations remain reversible and ordered. |
| FR-6 | Execute Python and JavaScript linters plus smoke tests (`pytest -q --maxfail=1`, `npm run lint && npm run test -- --runInBand --bail`). |
| FR-7 | Emit explicit warnings listing untracked files; require user acknowledgement (flag/override) when files are intentionally ignored. |
| FR-8 | Aggregate exit codes and terminate immediately on first failure (fail-fast) with guidance to rerun `tools\\hooks\\pre_push.ps1 --fix`. |

## 6. Non-Functional Requirements (NFR)
- NFR-1 Reliability: Hook must succeed/fail deterministically across Windows, WSL, and CI shells.
- NFR-2 Performance: Total runtime ≤ 60 seconds on reference hardware; parallelize lint/test blocks when safe.
- NFR-3 Maintainability: Single PowerShell source managed centrally to avoid drift; documentation inline with SRS glossary.
- NFR-4 Security: No secrets logged; scans must respect `.gitignore` but still inspect sensitive patterns.
- NFR-5 Observability: Structured console output (timestamps + status tags) for ingestion by AI agents.

## 7. Operational Requirements (OR)
- OR-1 Deployment: Hook installation automated via `tools\hooks\install.ps1`, symlinking `.git/hooks/pre-push` to central script.
- OR-2 Configuration: Repository root stores minimal config (`hooks.config.json`) listing enabled checks; default enables all.
- OR-3 Recovery: Provide `--skip` flag gated by environment variable (`ALLOW_PREPUSH_BYPASS=1`) with audit logging.
- OR-4 Compatibility: Script must run under PowerShell 7+, fall back to pwsh core on macOS/Linux; no Bash-only logic.
- OR-5 Logging: Errors recorded to `%USERPROFILE%\.codex\logs\pre_push.log` for troubleshooting while keeping repo clean.

## 8. Directory & Placement Rules
- `.git/hooks/pre-push` contains only a shim invoking `..\tools\hooks\pre_push.ps1`.
- Central PowerShell scripts reside in `tools\hooks\` for SRS, `tools\hooks\` for policy-tracker-ai, and mirrored relative paths for other repos.
- No script duplication; repositories reference the canonical script via relative path or lightweight wrapper.

## 9. Rationale & Architectural Justification
- Centralized reference prevents drift that commonly occurs when hooks are copied per repo; updates propagate instantly to all dependents, preserving spec integrity.
- Spec-first AI workflows demand consistent enforcement so Codex agents can reason about deterministic pipelines; referencing ensures identical logic across workspaces.
- Fail-fast behavior shortens feedback loops, aligning with DevOps resilience goals and multi-agent coordination.

## 10. Future Extensions
- Integrate Codex auto-remediation mode where failed checks emit structured payloads consumable by repair agents.
- Add AI policy-tracker integration to ensure pushes reference approved policy tickets.
- Support configurable check bundles (e.g., `--profile minimal`, `--profile release`) without editing the hook itself.

## 11. Change Log
| Version | Date | Author | Notes |
| --- | --- | --- | --- |
| 0.1 | 2025-11-18 | Codex Agent | Initial creation of Pre-Push / Pre-Check Auto-Gate Requirements (Priority P1).

