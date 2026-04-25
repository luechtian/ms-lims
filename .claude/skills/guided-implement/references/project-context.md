# Project Context Reference

How to anchor teaching in the ms-lims repo specifically, not generic Django. These are the files that carry binding decisions; cite them by name.

## The authority stack (highest wins)

1. **Constitution** — `.specify/memory/constitution.md`. Rules are binding across every feature. Treat violations as blocking review findings, not stylistic nits.
2. **CLAUDE.md** (repo root) — project-wide conventions and commands. Already loaded into your context on every invocation.
3. **Feature plan** — `specs/<feature>/plan.md`. Architectural decisions scoped to the feature (e.g. where models, managers, admin customisations live).
4. **Feature spec** — `specs/<feature>/spec.md`. Functional requirements (FR-001 etc.) and acceptance scenarios.
5. **Research log** — `specs/<feature>/research.md`. Rationale for each non-obvious decision (R1, R2, ...). When `tasks.md` cites "(research R4)", this is where to look.
6. **Data model** — `specs/<feature>/data-model.md`. Field-level contract for each model.
7. **API contract** — `specs/<feature>/contracts/*.md`. The public interface other apps are allowed to depend on.
8. **Quickstart / tasks** — `specs/<feature>/quickstart.md`, `tasks.md`. How to run and the ordered punch list.

When teaching, reach down the stack only as far as you need. A manager-location question is answered by plan.md; don't cite the constitution unless it actually applies.

## Canonical rules likely to come up in reviews

These are worth memorising — they recur and they are exactly the kind of "project convention beats generic" moment that teaches.

### Module boundaries (constitution §IV.2)

> Other apps reach `parties` ONLY via `parties/api.py`. Never import from `parties.models` in another app.

If the user's code (or test) imports `from parties.models import ...` from outside the parties app, that's a blocking review finding. Point at the api.py file and the constitution clause. The equivalent rule applies to other apps once they exist.

### Managers live in `managers.py`, not `models.py`

Per plan.md §Models for 001-parties-master-data. The `PartyQuerySet` lives in `parties/managers.py` and the model attaches it via `objects = PartyQuerySet.as_manager()`. Don't accept a model file with its own manager class inline.

### `Meta.constraints` for uniqueness, not `unique=True`

Prefer `UniqueConstraint` objects in `Meta.constraints` so the constraint name and conditions are explicit and case-insensitive variants are expressible (`UniqueConstraint(Lower("name"), name="uniq_..._ci")`). Field-level `unique=True` is a last resort.

### `on_delete` is a business decision

- `PROTECT` — deletion of the parent forbidden while children exist. Used for Person→ResearchGroup: deleting a group with people in it is a data-loss operation the app must not allow silently.
- `SET_NULL` — the child survives, the FK becomes NULL. Used for ResearchGroup.pi: if the PI's Person record is removed, the group survives PI-less.
- `CASCADE` — children vanish with the parent. Use rarely and intentionally; never the default.

When the user picks the wrong one, the teaching moment is "what operation are you trying to forbid or allow?"

### Comments are rare (CLAUDE.md)

> Default to writing no comments. Only add one when the WHY is non-obvious.

A junior's instinct will be to explain the code in comments. Push back gently on comments that describe _what_ the code does — the identifier should do that. Accept comments that carry a non-obvious _why_.

### Tests first (this project's tasks.md convention)

Each user story lists its tests _before_ the implementation task and expects the test to fail before the implementation makes it pass. Reviewing an implementation task's code with no test in place is an incomplete review — flag it and point at the test task ID.

## Commands the user actually runs

From CLAUDE.md (Windows / bash shell):

```bash
uv run pytest tests/                 # all tests
uv run pytest tests/parties/ -v      # feature-scoped
uv run ruff check .                  # lint
uv run ruff format .                 # format
python manage.py migrate             # schema + seed
python manage.py runserver           # admin on :8000
python manage.py check               # sanity check without migrations
```

When you suggest a command, use these exact forms. The user's environment is Windows with a bash shell — Unix syntax, forward slashes.

## Python + Django versions

- Python 3.13.4 (per constitution). Type hints and modern syntax (`match`, `x | None`, generic `list[int]`) are fair game.
- Django 6.0.4. When you reach for a feature, pick what's current in 6.0, not what was current in 4.x. If you're unsure, say so and check the docs rather than guessing.
