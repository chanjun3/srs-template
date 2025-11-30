# System Requirements Specification (Global SRS)

1. Overview
2. System Architecture
3. Behavioral Rules
4. Syntax Rules

   4.1 Markdown Rules

      - 見出しは 1 レベルずつ昇格 (MD001)
      - 見出し前後は空行1つ (MD022)
      - 番号リストは常に "1." (MD029)
      - 箇条書き前後に空行 (MD032)
      - コードフェンス前後に空行 (MD031)
      - 160文字以内 (MD013)
      - 裸URL禁止 (MD034)
      - タブ禁止 (MD010)
      - 空行は最大1つ (MD012)
      - EOFは1改行 (MD047)

   4.2 YAML Rules

      - インデントは2スペース
      - タブ禁止
      - 重複キー禁止

   4.3 JSON Rules

      - trailing comma禁止
      - strict JSONのみ

   4.4 Python Rules

      - black準拠
      - flake8違反禁止

5. Functional Requirements (Links Only)

   - PlannerAgent: docs/requirements/functional/planner/Local_SRS.md
   - CoderAgent: docs/requirements/functional/coder/Local_SRS.md
   - CriticAgent: docs/requirements/functional/critic/Local_SRS.md
   - ReviewerAgent: docs/requirements/functional/reviewer/Local_SRS.md
   - OrchestratorAgent: docs/requirements/functional/orchestrator/Local_SRS.md
   - ResearchAgent: docs/requirements/functional/research/Local_SRS.md

6. Non-functional Requirements (Links Only)

7. Data Requirements (Links Only)

8. Integration Requirements (Links Only)

9. Assurance / CI/CD Requirements (Links Only)

10. Glossary

## (1) Syntax Invariants

- CI YAML indentation SHALL be exactly 2 spaces per nesting level, and any deviation invalidates the workflow.
- Tabs, full-width spaces, and mixed indentation sequences SHALL be rejected within every YAML rule block.
- `run: |` multi-line command blocks SHALL preserve consistent indentation for all included lines relative to the `run` key and SHALL NOT introduce stray spacing.
- HEREDOC style sections SHALL close with an indentation that exactly matches their opener; mismatched indentation invalidates the block.
- Steps under `jobs.lint.steps` SHALL remain correctly nested; any mis-nesting that moves steps outside this hierarchy invalidates the YAML.

## (2) Failure-Handling Semantics

- Lint steps that specify `continue-on-error: true` SHALL continue execution while still recording failure status for downstream guards.
- A fail guard such as `if: failure()` SHALL be present to ensure the workflow reacts deterministically to prior lint failures.
- Steps using `if: always()` for log generation and artifact upload SHALL execute regardless of previous outcomes to guarantee evidence capture.
- Always-run steps SHALL only be employed when upstream steps cannot abort the job; otherwise the workflow risks silent termination.

## (3) CIFixerAgent Interface Contract

- The produced artifact SHALL be named `srs-ci-logs` and no other identifier is permitted.
- The artifact contents SHALL include `${{ github.workspace }}/ci-summary.log` exactly at that path.
- Presence of the artifact is a REQUIRED precondition for CIFixerAgent triage; absence SHALL block FixerAgent execution.
- Any modification to artifact name, path, or structure SHALL be treated as a breaking change that requires explicit SRS approval.

## (4) Observability & Critical Fault Definitions

- Workflow silent invalidation SHALL be defined as a lint workflow executing without emitting logs or artifacts despite configuration requiring them.
- Silent invalidation SHALL be classified as a Critical SRS Violation and SHALL trigger escalation.
- A CI workflow that does not appear in GitHub Actions SHALL be deemed invalid and SHALL NOT be processed by FixerAgent.
- Missing required artifacts SHALL be classified as infrastructure faults and SHALL NOT be attributed to FixerAgent failures.

## (5) Integration Requirements: Self-Healing Pipeline

- The upstream workflow titled `Debug AI Agent Automation` SHALL remain immutable in name; downstream triggers SHALL reference the exact string and any renaming requires explicit SRS approval.
- The upstream workflow SHALL upload an artifact named `pytest-logs` whose contents include the file `pytest_output.txt`; omission of either identifier constitutes a contract breach.
- Upstream workflows SHALL invoke `pytest` via `set -euo pipefail` and MUST terminate using `exit "${PIPESTATUS[0]}"` (or equivalent) so that non-zero statuses propagate to `workflow_run.conclusion`.
- The downstream workflow `FixerAgent Self-Healing Pipeline` SHALL trigger exclusively via `workflow_run` events originating from `Debug AI Agent Automation` executions whose `conclusion` equals `failure`.
- Artifact IO contracts SHALL guarantee that FixerAgent consumes `artifacts/pytest_output.txt` extracted from the `pytest-logs` artifact without renaming the directories or files.
- The upstream/downstream relationship (Debug AI Agent Automation → FixerAgent Self-Healing Pipeline) SHALL remain one-to-one; additional
  downstream workflows MUST register independently to avoid ambiguity.
