# Contributing

Thanks for your interest in contributing to mlcrawler! This guide covers the basics for getting started.

## Development setup

This project uses `uv` for dependency management and `hatch`/`hatchling` for building.

```bash
# install uv and sync dependencies
uv sync

# run tests
uv run pytest
```

## Code style

We use `ruff` for linting and formatting and `mypy` for optional static typing checks. Pre-commit hooks are installed and run automatically by the project.

Follow these guidelines:

- Run `uvx ruff check .` before creating a PR
- Run `uvx mypy src/` to check types
- Keep changes focused and add tests for new behavior

## Documentation

- Docs live in the `docs/` directory and are built with MkDocs + Material theme.
- To preview locally:

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

## Pull Requests

- Create a branch for your work
- Add tests for bug fixes and new features
- Keep PRs small and focused
- Add entries to CHANGELOG when appropriate

Thanks for helping improve mlcrawler!
