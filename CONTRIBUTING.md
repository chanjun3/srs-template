# Contributing

This repository is the global Single Source of Truth. Follow the steps below to
propose SRS changes or add localised specifications.

## Branching model

- Cut feature branches using the format `feat/srs-refactor-YYYY-MM-DD`.
  - Example for this iteration: `feat/srs-refactor-2025-11-18`.
- A frozen snapshot of `origin/main` is preserved on `backup/pre-refactor-2025-11-18`.
  Do not force-push or delete backup branches.

## Workflow

1. Branch from `main` using the naming convention above.
2. Apply your documentation or config changes.
3. Run the linters locally:

   ```bash
   npm run lint:md
   yamllint .
   ```

4. Open a pull request targeting `main`.
5. Request review from at least one maintainer; only merge after CI (markdownlint,
   yamllint, lychee) is green.
6. Merge via the PR UI—never push directly to `main`.

## Local SRS additions

1. Copy `docs/requirements/functional/_templates/Local_SRS_Template.md`
   into your target folder (e.g., `docs/case-studies/<slug>/local.md`).
2. Fill out all sections (Role / Input / Output / Constraints / Forbidden / Reference).
3. Cross-link to the relevant Global SRS sections in `docs/templates/3layer/`.
4. Reference any shared configs from `docs/case-studies/config/`.
5. Update `docs/catalog.md`, `CHANGELOG.md`, and include reviewers in the PR description.
