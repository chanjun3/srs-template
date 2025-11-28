





srs-template — AI Agent OS System Requirements Catalogue

Multi-agent / Cognitive Logging / Spec-First assets for the AI Agent OS.
This repository is the canonical home for all System Requirements Specifications (SRS),
architecture policies, governance rules, and QA references.
Clone it when drafting a local SRS — but always merge changes back here.

## 1. High-Level Overview

Spec-First: Architecture and process decisions land in SRS files before implementation.

Multi-Agent OS: Requirements span planner / orchestrator / reviewer agents, governance, and assurance.

Single Source of Truth (SoT): All downstream SRS or system deliveries must reference this repo.

## 2. 6-Layer Navigation

| Layer | Purpose & Notes | Anchor Paths / Examples |
| --- | --- | --- |
| 01 — Overview / Vision | Vision, cognitive strategy, conceptual framing for AI Agent OS. | docs/overview/ → AI_Agent_NotionDB_Architecture_Requirements.md, AI_Cognitive_Framework_Report.md |
| 02 — Reference Templates (3-layer) | Templates for architecture / functional / non-functional / integration / data / QA. | docs/templates/3layer/* |
| 03 — Shared Requirements | Cross-agent functional / non-functional / integration / data requirements. Includes Cognitive Logging Architecture. | docs/requirements/* |
| 04 — Governance & Policy | Branch rules, data usage policy, access control, compliance. | docs/governance/* |
| 05 — Case Studies & Config | Agent-specific SRS packages + shared YAML configs. | docs/case-studies/<slug>/, docs/case-studies/config/*.yaml |
| 06 — Assurance & QA | CI/CD pipelines, AI literacy QA, assurance specs. | docs/assurance/* |

Searchable catalogue: docs/catalog.md
(Keep catalogue alphabetized per domain to reduce merge conflicts.)

## 3. Repository Policy
Single Source of Truth (SoT)

This repo holds the authoritative versions of all specifications.

Forking/exporting is fine — but PRs must reconcile changes back into main.

Spec Discipline & Local SRS Deltas

Any change to implementation, automation, or policy must be preceded by an SRS update.

Local SRS docs must reference this repo via relative paths.

Shared requirements or configs must be added here first, then pulled downstream.

Catalogue & Changelog Hygiene

Update docs/catalog.md and CHANGELOG.md whenever files are added or moved.

Cognitive Logging Alignment

Logging schemas, rewards, and telemetry must align with Cognitive Logging Architecture specs.

## 4. Workflow

Install dependencies

npm install

Run Markdown lint

npm run lint:md

Update catalogue + changelog

Update docs/catalog.md

Update CHANGELOG.md

Prepare PRs with context

Specify which layer / agent is affected

Provide rationale

Tag reviewers for architecture / policy / QA

## 5. Continuous Integration

.github/workflows/markdownlint.yml enforces linting on push/PR.

Additional validations:

YAML schema checks

Link consistency

Spec drift detection

These are maintained in the Assurance Layer.

## 6. Future Work / Roadmap

Cognitive Logging Validation

Spec Compliance Bot

Assurance-driven dashboards (Grafana / Prometheus)

## 7. Footer & Help

Full catalogue: docs/catalog.md

Governance inquiries: docs/governance/Data_Utilization_Policy_SRS.md

New case studies begin under Layer 05

The AI Agent OS SRS repository keeps every agent, workflow, and cognitive logging pipeline aligned under a single source of truth.
