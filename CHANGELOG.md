# Changelog
All notable changes to this repository will be documented in this file.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and uses ISO dates in JST.

## [2025-11-19]
### Added
- Introduced 6-layer navigation + SoT/local-SRS policy to `README.md`.
- Added shared config hub `docs/case-studies/config/` plus README relocation.
- Authored `docs/overview/glossary.md` and expanded `docs/overview/README.md` with branch policy.
- Added `docs/requirements/functional/_templates/Local_SRS_Template.md` for localised specs.
- Introduced `.yamllint.yaml` and `.github/workflows/srs-ci.yml` (markdownlint, yamllint, lychee).

### Changed
- Merged `Standard_CollectorAgent_Framework_Requirements.md` into
  `docs/templates/3layer/architecture_overview.md`.
- Renamed `40_05_CognitiveLoggingArchitecture.md` to `docs/requirements/data/CognitiveLoggingArchitecture.md`.
- Relocated `AI_Literacy_Development_System_SRS.md` to `docs/assurance/`.
- Updated catalogue/READMEs to new paths and cleaned Markdown links.
- Relaxed Markdown line-length guardrails via `.markdownlint.yaml`.

### Refactor
- **Refactor: SRS structure normalization**
  - **Before**
    ```
    .
    ├── cognitive_loop.yaml
    ├── 00_Overview/
    ├── 10_Functional_Requirements/
    ├── 20_NonFunctional_Requirements/
    ├── 30_Integration_Requirements/
    ├── 40_Data_Requirements/
    └── 50_Quality_Assurance/
    ```
  - **After**
    ```
    .
    ├── docs/
    │   ├── overview/
    │   ├── templates/3layer/
    │   ├── requirements/{functional,non-functional,integration,data}/
    │   ├── governance/
    │   ├── case-studies/{...}/
    │   └── assurance/
    ├── docs/case-studies/config/
    ├── README.md
    └── .github/workflows/{markdownlint.yml,srs-ci.yml}
    ```

## [2025-11-18]
### Added
- Introduced role-oriented `docs/` tree with overview, governance, case studies,
  templates, shared requirement blocks, and assurance artefacts.
- Added catalogue (`docs/catalog.md`), subdirectory READMEs, and `configs/README.md`
  so contributors can locate artefacts quickly.
- Created project-level `README.md` outlining workflows plus lint/CI guidance.
- Added `.markdownlint.yaml`, `package.json`, and GitHub Actions workflow for Markdown linting.

### Changed
- Consolidated the duplicated `3layer_*` specs into `docs/templates/3layer/`.
- Moved agent-specific SRS into `docs/case-studies/<slug>/README.md`.
- Collected YAML configs under `configs/`.
