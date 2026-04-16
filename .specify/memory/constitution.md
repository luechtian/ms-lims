<!--
Sync Impact Report
==================
Version change: (template/uninitialized) → 1.0.0
Rationale: Initial ratification — replaces placeholder template with concrete
           project constitution derived from docs/decisions/ms-lims-requirements.md
           and docs/decisions/ms-lims-tech-stack-referenz-v2.md.

Modified principles:
  - [PRINCIPLE_1_NAME]        → I. Manual-First
  - [PRINCIPLE_2_NAME]        → II. Faster-than-Excel
  - [PRINCIPLE_3_NAME]        → III. Low Barrier to Entry
  - [PRINCIPLE_4_NAME]        → IV. Modularity
  - [PRINCIPLE_5_NAME]        → V. YAGNI

Added sections:
  - Tech Stack Constraints (non-negotiable versions + tool choices)
  - Design Patterns (pragmatic, Django-aware)
  - Modularity — Hard Rules (checkable app-boundary rules)
  - Quality Standards (tests, lint, audit trail, printable docs)
  - Architecture Guardrails (three pillars, composition, functional/OOP split)
  - Scope Guardrails (explicit v1 non-goals)

Removed sections: none (placeholder slots SECTION_2/SECTION_3 replaced with
                 concrete, named sections).

Templates requiring updates:
  - .specify/templates/plan-template.md    ⚠ pending — Constitution Check gate is
    a placeholder. A follow-up pass should spell out concrete gates derived from
    this constitution (modularity rules, tech stack fixity, YAGNI, test coverage
    of state transitions, print-document completeness). No changes made in this
    ratification pass because the gate is already content-free and will be
    filled by the next /speckit.plan run that touches this template.
  - .specify/templates/spec-template.md    ✅ no changes required — spec template
    has no constitution-specific references.
  - .specify/templates/tasks-template.md   ✅ no changes required — task template
    is principle-agnostic; its test / phase structure is compatible with the
    Quality Standards and Modularity sections.
  - .specify/templates/agent-file-template.md  ✅ no changes required.
  - .specify/templates/checklist-template.md   ✅ no changes required.

Follow-up TODOs: none. All placeholder tokens resolved in this revision.
-->

# MS-LIMS Constitution

MS-LIMS is a lightweight, web-based Laboratory Information Management System for
mass-spectrometry labs. Authoritative detail on requirements lives in
`docs/decisions/ms-lims-requirements.md`; authoritative detail on the tech stack
lives in `docs/decisions/ms-lims-tech-stack-referenz-v2.md`. This constitution is
the short, binding layer above both: principles and rules that govern every
spec, plan, and implementation in this repository.

## Core Principles

### I. Manual-First

Every workflow MUST be built for manual execution first. Automation — Hamilton
worklist generation, MS vendor result parsers, task queues — is added only
after the manual process is digitally represented and understood. Rationale:
automating a poorly-understood workflow hard-codes the misunderstanding; we
learn the real shape of the work by doing it manually in the LIMS first.

### II. Faster-than-Excel

If a workflow in the LIMS takes longer than in Excel, the feature has failed.
This rule applies in particular to sample registration and extraction-batch
formation — the two flows where Excel currently wins on keystrokes. Every
feature touching these paths MUST justify its friction budget relative to
the Excel baseline.

### III. Low Barrier to Entry

Deployment MUST remain portable: copy a folder, double-click, the LIMS runs.
A colleague MUST be able to try the LIMS within two minutes, with no
database server, no admin rights, no separate install. SQLite is the primary
database for v1; Postgres is an explicit upgrade path, not a starting point.

### IV. Modularity

Modularity is non-negotiable and is enforced by checkable rules (see
`Modularity — Hard Rules` below). `lipidquant` MUST remain a standalone Python
package with no Django dependency. Features start as their own Django app even
when small — the five-minute cost of `startapp` buys isolated boundaries from
birth.

### V. YAGNI

Features such as task queues (django-q2, Celery), Django REST Framework,
Hamilton integration, and MS-vendor result parsers MUST NOT be introduced
prophylactically. They are added only when a concrete, named need exists in a
spec. Rationale: every premature abstraction becomes a maintenance tax that
taxes the principles above.

## Tech Stack Constraints

The following choices are non-negotiable without an explicit amendment to this
constitution. Changing them requires a version bump and a dated entry in the
Sync Impact Report.

- Python 3.13.4
- Django 6.0.4
- SQLite as the primary database (Postgres only on concrete need — upgrade
  path remains open)
- `uv` as the package manager
- `pytest` + `pytest-django` as the test framework
- `ruff` as linter and formatter (target-version `py313`)
- `django-fsm-2` for state machines (NOT `viewflow.fsm`)
- HTMX 2.x + Alpine.js 3.x via CDN for frontend interactivity (no npm, no
  build step)
- Server-side rendering as the default (no SPA)

## Design Patterns

Patterns are chosen pragmatically and with Django's batteries-included
posture in mind.

- State Machine (`django-fsm-2`) is the heart of the system. Every Sample,
  Batch, and Run entity MUST have a formal lifecycle with auditable
  transitions.
- Fat Models, Skinny Views. Business logic lives in models and managers, not
  in views. Views are HTTP translators.
- Service Layer for cross-app operations. Code that touches two or more apps
  lives in `{app}/services.py`, not inside a single app's views or models.
- Adapter Pattern for external systems. Hamilton and MS vendor parsers MUST
  be fronted by a `Protocol`, with file-exchange as the default implementation
  and a mock for tests.
- Pure functions for data transformation: plate-layout computation, QC
  evaluation, result parsing, `lipidquant` math. No database access inside
  these functions.

Explicitly NOT used (because Django already covers them):

- Explicit Repository Pattern — Django Manager/QuerySet is the repository.
- Unit-of-Work class — `transaction.atomic()` is the unit of work.
- Data Access Object — unnecessary abstraction on top of the ORM.

## Modularity — Hard Rules

These rules are checkable, not interpretable. Every spec and every plan MUST
be validated against them.

1. One concept = one Django app. The currently planned apps are:
   - `parties`       — Institution, ResearchGroup, Person
   - `projects`      — Project, SampleIntake
   - `samples`       — OriginalSample, Extract
   - `storage`       — Freezer, Drawer, Rack, Position
   - `extractions`   — Protocol, Batch, MasterMix
   - `analyses`      — MeasurementRun, AnalysisResult
   - `instruments`   — Instrument, Adapter
   - `lipidquant`    — standalone Python package, NOT a Django app

   Further apps (e.g. `reporting`, `users`, `audit`) MAY be added later
   provided they follow these same rules.

2. Apps communicate only via `{app}/api.py` or `{app}/services.py`. Direct
   imports from another app's `models.py` or `views.py` are forbidden.

3. No circular dependencies between apps. Where coupling is unavoidable,
   Django signals MUST be used.

4. `lipidquant` is Django-free. No `django` imports are permitted.
   Checkable: `grep -r "django" lipidquant/` MUST return nothing.

5. New features start as their own app, even when they begin small. Cost:
   five minutes for `startapp`. Benefit: isolated boundaries from day one.

6. App-size warning threshold: more than ~8 models or ~2000 lines of code in
   a single app is a split signal and MUST be addressed in the next plan
   touching that app.

## Quality Standards

- Every feature has tests. There are NO exceptions for state transitions —
  each `@transition` in a state machine MUST have at least one happy-path and
  one guard-failure test.
- `ruff` MUST be green before every commit.
- Audit trail for sample state changes is required even without regulatory
  pressure, via `django-fsm-log`. This exists for debuggability and user
  trust, not for compliance.
- Printable documents (sample lists, extraction protocols, plate maps) are
  first-class citizens. They are integral parts of the modules that produce
  them, not an afterthought export.

## Architecture Guardrails

- Three pillars: Sample Management, Extraction Management, Analysis
  Management. Every feature lives under one of the three, or makes the case
  for a fourth pillar explicitly in its spec.
- The Sample state machine is the heart. Every step of a sample from intake
  to reported result MUST be formal, auditable, and traceable.
- Composition over inheritance. Python `Protocol` types instead of deep
  inheritance hierarchies.
- Functional for data transformation (plate layout, QC evaluation, result
  parsing). OOP for state and identity (models, adapters).

## Scope Guardrails (explicit v1 non-goals)

The following are OUT of scope for v1. Any spec that violates these items
MUST either amend this constitution or be rejected.

- No clinical patient samples. Biological research samples only.
- No multi-user or network installation. Local-only, portable folder.
- No direct instrument binding (Hamilton, MS vendor parsers). File exchange
  is the default; direct binding is deferred.
- No regulatory compliance as a requirement (21 CFR Part 11, ISO 17025).
  Regulatory material lives in the tech-stack reference as background
  knowledge only.

## Governance

- This constitution is consulted at every `/speckit.specify`, `/speckit.plan`,
  and `/speckit.analyze` invocation. Where a spec or plan conflicts with the
  constitution, the constitution wins — unless the constitution is
  explicitly amended in the same change.
- Amendments require their own commit with a rationale and a bumped version
  using semantic versioning:
  - MAJOR: backward-incompatible principle removal or redefinition.
  - MINOR: new principle or materially expanded section.
  - PATCH: clarifications, wording, typo fixes.
- Authoritative source for detailed requirements:
  `docs/decisions/ms-lims-requirements.md`.
- Authoritative source for tech-stack detail:
  `docs/decisions/ms-lims-tech-stack-referenz-v2.md`.

**Version**: 1.0.0 | **Ratified**: 2026-04-16 | **Last Amended**: 2026-04-16
