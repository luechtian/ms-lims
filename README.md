# ms-lims

[![CI](https://github.com/luechtian/ms-lims/actions/workflows/ci.yml/badge.svg)](https://github.com/luechtian/ms-lims/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Django 6](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A lightweight, web-based Laboratory Information Management System (LIMS) for mass-spectrometry labs. Covers sample management, extraction management, and analysis management.

---

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/) (package manager)

## Setup

```bash
git clone https://github.com/luechtian/ms-lims.git
cd ms-lims

uv sync --group dev
uv run python manage.py migrate
uv run python manage.py runserver
```

Admin interface: http://localhost:8000/admin

## Development

```bash
# Run tests
uv run pytest tests/

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## Project structure

```
ms-lims/
├── config/       # Django project configuration (settings, urls)
├── parties/      # Institutions, research groups, persons
├── tests/        # Centralised test suite
└── specs/        # Feature specifications
```

## License

[MIT](LICENSE)
