# Case studies

Each subdirectory contains a self-contained SRS package for a specific agent or
system. Convention:

```text
docs/case-studies/<slug>/
  README.md        # canonical SRS for the case
  assets/          # (optional) diagrams or supporting files
  configs/         # (optional) overrides specific to the case
```

Shared runtime YAML is centralized under `docs/case-studies/config/`. Reference
those files from your README instead of duplicating payloads.

Current cases span collectors, log analysis, IaC alignment, macro research, and
reinforcement learning flows. Use kebab-case for new slugs and update
[`../catalog.md`](../catalog.md) accordingly.

## Reference

- docs/spec_os/srs.md
