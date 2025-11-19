# Local SRS Template

Use this template when drafting a team-specific SRS that extends or constrains the Global SRS.
Duplicate the skeleton, fill in each section, and link back to the canonical artefacts.

## 1. Role
Describe the persona or agent responsible for this SRS (e.g., "PlannerAgent maintainer").

## 2. Input
- Enumerate input sources (APIs, datasets, prompts).
- Include format, frequency, and validation status.

## 3. Output
- Expected artefacts (reports, actions, metrics).
- Acceptance criteria or KPIs tied to the outputs.

## 4. Constraints
- Latency, throughput, compliance, regional restrictions, etc.
- Dependencies on infrastructure or upstream agents.

## 5. Forbidden
- Explicit anti-patterns or behaviours not permitted (e.g., "No direct database schema changes").
- Security/privacy restrictions.

## 6. Reference (Global SRS)
- Link back to the corresponding sections in `docs/templates/3layer/*`.
- List any shared requirement documents leveraged (e.g., `docs/requirements/non-functional/cloud_native_deployment_strategy.md`).
