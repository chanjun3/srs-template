# srs-template

System Requirements Specification (SRS) assets for the multi-agent / AI program.
This repository is the single source of truth (SoT) for architecture, policy, and QA material—
clone it when drafting a local SRS but merge changes back here.

## 6-layer navigation
1. **Layer 01 – Overview / Vision**  
   `docs/overview/` (e.g. [AI Agent NotionDB Architecture Requirements](docs/overview/AI_Agent_NotionDB_Architecture_Requirements.md)).
2. **Layer 02 – Reference Templates**  
   `docs/templates/3layer/` covering [architecture](docs/templates/3layer/architecture_overview.md),
   [functional](docs/templates/3layer/functional_requirements.md),
   [non-functional](docs/templates/3layer/non_functional_requirements.md),
   [integration](docs/templates/3layer/integration_requirements.md),
   [data](docs/templates/3layer/data_schema.md),
   [quality](docs/templates/3layer/quality_assurance.md).
3. **Layer 03 – Shared Requirements**  
   `docs/requirements/` split into `functional/`, `non-functional/`, `integration/`, `data/`
   (see [CognitiveLoggingArchitecture](docs/requirements/data/CognitiveLoggingArchitecture.md)).
4. **Layer 04 – Governance & Policy**  
   `docs/governance/` for [Branch Management](docs/governance/Branch_Management_Requirements.md)
   and [Data Utilization](docs/governance/Data_Utilization_Policy_SRS.md).
5. **Layer 05 – Case Studies & Config**  
   `docs/case-studies/<slug>/` for agent-specific SRS plus shared YAML under
   `docs/case-studies/config/` (`cognitive_loop.yaml`, `log_analyzer_config.yaml`,
   `reward_config.yaml`, `training_workflow.yaml`).
6. **Layer 06 – Assurance & QA**  
   `docs/assurance/` with the [CI/CD Pipeline SRS](docs/assurance/CI_CD_Pipeline_SRS.md) and
   the relocated [AI Literacy Development System SRS](docs/assurance/AI_Literacy_Development_System_SRS.md).

For a searchable list of every artefact see [`docs/catalog.md`](docs/catalog.md).

## Policy
- **Single Source of Truth**: This repo hosts the authoritative versions of all specs.
  Forking or exporting is fine, but PRs must reconcile differences back into `main`.
- **Local SRS copies**: When a team maintains a localised SRS for delivery,
  reference sections here via relative links and document deltas explicitly.
  New shared requirements or configs belong in this repo first, then can be pulled downstream.

## Workflow
1. Install dependencies (Markdown lint and formatter).

   ```bash
   npm install
   ```
2. Run lint before submitting changes.

   ```bash
   npm run lint:md
   ```
3. Update `docs/catalog.md` and `CHANGELOG.md` whenever you add/move artefacts.

### CI
`.github/workflows/markdownlint.yml` enforces the same lint inside GitHub Actions on pushes and PRs.
