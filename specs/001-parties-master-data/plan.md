# Implementation Plan: Parties Master Data

**Branch**: `001-parties-master-data` | **Date**: 2026-04-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-parties-master-data/spec.md`

## Summary

Build the `parties` Django app that manages Institutions, ResearchGroups and Persons as master data for every sample supplier in the LIMS — external customers / collaboration partners and the internal lab itself. Three models, Django admin as the only v1 UI, an idempotent JSON-fixture seed for the internal lab wired into a data migration, and a thin `parties/api.py` as the public interface for future modules. Business rules (PI-must-be-member, delete-guard on groups with active Persons, immutable `Person.research_group`, scoped uniqueness on Institution and ResearchGroup names, advisory in-group email-duplicate warning) live in model `clean()` / `delete()` methods (fat models). No state machine is needed — parties entities have only a reversible active/inactive boolean.

## Technical Context

**Language/Version**: Python 3.13.4 (per constitution)
**Primary Dependencies**: Django 6.0.4 (existing), pytest-django 4.12+ (existing), factory-boy (NEW — dev-only)
**Storage**: SQLite (WAL mode, existing in `config/settings.py`)
**Testing**: pytest + pytest-django + factory-boy; tests live in `tests/parties/`
**Target Platform**: Portable Windows folder (primary); Linux/macOS dev also supported
**Project Type**: Django monolith. One new app: `parties`.
**Performance Goals**: Person search <1 s up to 10 000 Persons (SC-004). Django + SQLite + `icontains` is well inside this envelope; no special indexing needed beyond the default FK indexes and a single functional index for case-insensitive name uniqueness.
**Constraints**: Local single-process deployment (constitution §III). No network dependencies, no external services, no daemons. Every rule must be enforceable by a form submit in the Django admin.
**Scale/Scope**: ≤10 000 Persons, a few hundred ResearchGroups, tens of Institutions. All three models in one app; ~300–500 LOC for models+admin+api+migrations, ~400–600 LOC for tests+factories.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Rule | Check | Verdict |
|---|---|---|
| I. Manual-First | Django admin is 100 % manual; no automation added. | **Pass** |
| II. Faster-than-Excel | Creating a group + person takes <1 min via admin (well under the 3-min SC-002 budget). | **Pass** |
| III. Low Barrier to Entry | SQLite + `python manage.py migrate` seeds the internal lab automatically via data migration. No extra command. | **Pass** |
| IV.1 One concept = one app | `parties` app holds exactly Institution / ResearchGroup / Person. | **Pass** |
| IV.2 Apps communicate only via `api.py` / `services.py` | `parties/api.py` is the sole public entry point. No `services.py` needed (no cross-app operations in this spec). | **Pass** |
| IV.3 No circular deps | parties has zero imports from other apps. | **Pass** |
| IV.4 lipidquant Django-free | Not touched. | **N/A** |
| IV.5 New features start as own app | `parties` is its own app. | **Pass** |
| IV.6 ≤8 models / ≤2000 LOC | 3 models, ~1 kLOC estimated. | **Pass** |
| V. YAGNI | No DRF, no django-q2, no HTMX, no custom UI, no config framework. Seed is a plain JSON fixture. | **Pass** |
| Design — State Machine | Not required: parties has no Sample/Batch/Run lifecycle. Active/inactive is a reversible boolean, not a state machine. Called out explicitly so reviewers don't flag a missing FSM. | **Pass (N/A)** |
| Design — Fat Models | All invariants (PI-must-be-member, delete-guard, immutable FK, uniqueness scope) live on models. Admin and api are thin. | **Pass** |
| Design — No explicit Repository | Uses Django Manager/QuerySet via `parties/managers.py`. | **Pass** |
| Quality — Tests for every feature | `tests/parties/` covers models, managers, admin, api, seed. FR-026 mandates this. | **Pass** |
| Quality — ruff green | Target-version `py313` already in `pyproject.toml`. Code formatted with ruff. | **Pass** |
| Quality — Audit trail | django-fsm-log is optional and tied to state machines. Not applicable here. A plain `active` boolean does not need an event log in v1. | **Pass (N/A)** |
| Scope — No clinical, no multi-user, no direct instrument, no compliance | Not touched. | **Pass** |

**Constitution Check result**: All gates pass. No violations; Complexity Tracking section stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-parties-master-data/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── parties-api.md   # Public module interface (Python functions exposed by parties/api.py)
├── checklists/
│   └── requirements.md  # From /speckit.specify + /speckit.clarify
└── tasks.md             # To be produced by /speckit.tasks (NOT created here)
```

### Source Code (repository root)

```text
ms-lims/
├── config/                             # existing — Django project settings
│   ├── settings.py                     # add "parties" to INSTALLED_APPS
│   └── urls.py                         # no change (admin only)
├── parties/                            # NEW app
│   ├── __init__.py
│   ├── apps.py                         # default_auto_field, verbose_name
│   ├── models.py                       # Institution, ResearchGroup, Person (fat models)
│   ├── managers.py                     # PartyQuerySet with .active() / .inactive()
│   ├── admin.py                        # InstitutionAdmin, ResearchGroupAdmin, PersonAdmin
│   ├── api.py                          # Public interface (see contracts/parties-api.md)
│   ├── fixtures/
│   │   └── internal_lab.json           # Edited by operator before first `migrate`
│   └── migrations/
│       ├── 0001_initial.py             # auto-generated by makemigrations
│       └── 0002_seed_internal_lab.py   # hand-written data migration, idempotent
├── tests/
│   └── parties/                        # mirror app structure
│       ├── __init__.py
│       ├── conftest.py                 # shared fixtures (factories wiring)
│       ├── factories.py                # factory-boy: InstitutionFactory, ResearchGroupFactory, PersonFactory
│       ├── test_models.py              # model invariants, clean(), delete()
│       ├── test_managers.py            # .active() / .inactive() QuerySet behaviour
│       ├── test_admin.py               # admin guardrails (delete-permission, readonly FK, warning message)
│       ├── test_api.py                 # public-interface contract tests
│       └── test_seed.py                # fixture validity + data migration idempotency
├── pyproject.toml                      # add factory-boy to dev deps
└── manage.py
```

**Structure Decision**: Standard Django project + single-app layout per constitution §IV.1 and tech-stack §4.2. No backend/frontend split (server-rendered admin only). Tests are centralised under `tests/` per the existing repo layout, mirroring the app tree.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Section intentionally empty.
