# Documentation structure

The documentation tree is organized around the responsibilities normally seen on
SRS efforts:

- **Overview** – program-wide narratives and architecture essays.
- **Templates** – canonical, reusable chunks that SRS authors can import.
- **Requirements** – curated requirement sets organised by attribute (functional,
  non-functional, integration, data, quality).
- **Governance** – branching, data usage, and policy artefacts.
- **Case studies** – concrete agent/system SRS packages.
- **Assurance** – verification, CI/CD, and release gates.
- **Shared config** – common YAML payloads under `case-studies/config/`.

For a file-by-file inventory see [`catalog.md`](catalog.md). Each subdirectory
also contains its own `README.md` to explain how to contribute new material.
