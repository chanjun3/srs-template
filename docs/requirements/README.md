# Shared requirements

Domain-specific requirement sets that can be imported into multiple SRS
packages. Subdirectories currently cover:

- `functional/` – reusable capability definitions (add a README when populated).
- `non-functional/` – SLAs, resilience, and deployment strategies.
- `integration/` – interaction models plus host-environment contracts.
- `data/` – schemas, streaming/retention policies.

To reference a requirement block from a case study, link relative to repo root
(e.g. `../../requirements/integration/Serverless_Execution_Architecture.md`).
