# ms-lims Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-16

## Active Technologies

- Python 3.13.4 (per constitution) + Django 6.0.4 (existing), pytest-django 4.12+ (existing), factory-boy (NEW — dev-only) (001-parties-master-data)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.13.4 (per constitution): Follow standard conventions

## Recent Changes

- 001-parties-master-data: Added Python 3.13.4 (per constitution) + Django 6.0.4 (existing), pytest-django 4.12+ (existing), factory-boy (NEW — dev-only)

<!-- MANUAL ADDITIONS START -->

## Actual Project Structure (Django monolith)

```text
ms-lims/
├── config/             # Django project (settings, urls, wsgi/asgi)
├── parties/            # apps: Institution, ResearchGroup, Person (001)
├── tests/              # centralised test suite, mirrors app tree
├── docs/decisions/     # requirements + tech-stack reference
└── specs/              # spec-kit specs per feature
```

The template-generated `src/` + `tests/` block above is inaccurate — Django apps live at the repo root, not under `src/`.

## Actual Commands

```powershell
uv run pytest tests/                 # run all tests
uv run pytest tests/parties/ -v      # feature-scoped
uv run ruff check .                  # lint
uv run ruff format .                 # format
python manage.py migrate             # schema + seed internal lab
python manage.py runserver           # admin on :8000
```

## Module boundary rule (constitution §IV.2)

Other apps reach parties ONLY via `parties/api.py`. Never import from `parties.models` in another app. See `specs/001-parties-master-data/contracts/parties-api.md` for the canonical public interface.
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->
