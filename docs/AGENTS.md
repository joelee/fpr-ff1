# Documentation Agent Guide

Documentation is part of the product. Update docs in the same change that makes them true.

## Maintained Documents

- `README.md`: project overview, quick start, common commands, and links to deeper docs.
- `docs/architecture.md`: system context, major modules, boundaries, key design decisions, and diagrams.
- `docs/configuration.md`: all non-secret config keys, defaults, lookup order, and secret handling rules.
- `docs/directory-structure.md`: repository layout and what belongs in each directory.
- `docs/developer-guide.md`: setup, development workflow, testing, linting, type checking, debugging, and release notes.
- `docs/backlog.md`: high-level feature backlog and links to feature directories.
- `docs/ideas/AGENTS.md`: contract for any agent writing idea reports under `docs/ideas/`.
- `docs/reviews/AGENTS.md`: contract for any agent writing code-review reports under `docs/reviews/`.
- `docs/plans/AGENTS.md`: contract for any agent writing delivery plans under `docs/plans/`.

## Rules

- Keep docs concise and specific to this project.
- Prefer examples over abstract guidance when the example removes ambiguity.
- Do not document secrets or real credentials.
- If behavior, commands, config, or directory structure changes, update the matching document.
- If a feature adds or changes public behavior, update `README.md` or explain why it does not need a README change.
- If a feature changes architecture, update `docs/architecture.md`.
- If a feature changes config, update `docs/configuration.md`.
- If a feature changes repository layout, update `docs/directory-structure.md`.
- If a feature changes developer workflows, update `docs/developer-guide.md`.
- If a feature is added, dropped, blocked, or completed, update `docs/backlog.md`.
