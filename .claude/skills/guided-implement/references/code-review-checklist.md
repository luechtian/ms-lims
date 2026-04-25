# Code Review Checklist

The lens for reviewing the user's task code. Apply in this order — stop reviewing and flag immediately if any earlier check fails.

## 0. Does it run?

Before anything else: does `python manage.py check` pass? Did the test task's test move from red to green (or at least stop erroring for the wrong reason)? If the code doesn't import or migrate, that's the entire review. Everything else is moot.

## 1. Does it satisfy the task?

Re-read the task text. Every bullet must be visible in the code:
- All named fields present?
- All named `Meta` entries (`ordering`, `constraints`, `indexes`) present?
- All named methods (`__str__`, `full_name`, `active_members`) present?
- Any "**Do NOT** add X yet" clauses respected?

Missing-what-the-task-asked-for is a blocking finding.

## 2. Does it respect the project rules?

Walk the user's code against `references/project-context.md`. The high-leverage checks:

- **Module boundaries.** Any import of `parties.models` from outside `parties/`? Blocking.
- **Managers in `managers.py`**, not inline in the model. Blocking if a new manager class is defined in `models.py`.
- **`Meta.constraints` for uniqueness**, not field-level `unique=True` (unless the spec explicitly says the field-level form). Non-blocking if it happens to work, but worth a teaching moment.
- **`on_delete` chosen deliberately.** Is it the right business rule for this relationship? If `CASCADE` appears on a relationship whose spec says "PROTECT" or "SET_NULL", blocking.
- **Comments carry a _why_**, not a _what_. A `# set name` comment above `self.name = name` is noise; a `# see research R5 for why PI lives on the group, not Person` is signal. Non-blocking but always callable.
- **Tests exist.** If this is an implementation task whose preceding test task is also `[ ]`, the user skipped tests. Flag and offer to back up.

## 3. Is it idiomatic Django 6 / Python 3.13?

- Type hints present on non-trivial function signatures? Not required on every line (Django's own style is light on hints in model bodies), but public API functions — like anything in `parties/api.py` — should have them.
- Modern syntax: `X | None` over `Optional[X]`, `list[int]` over `List[int]`, f-strings over `%`.
- No `except:` without a class name. No swallowed exceptions.
- No copy-paste between models that a base class or manager method could collapse. Don't jump to abstraction on the first instance — three repetitions is the honest threshold.
- Names pull their weight. `qs = Person.objects.filter(...)` is fine; `x = Person.objects.filter(...)` isn't.

## 4. Does it match the data model and contracts?

Cross-check against `specs/<feature>/data-model.md` and `contracts/*.md`:

- Field types match (`CharField(max_length=...)` vs `TextField`, `EmailField` vs plain `CharField`).
- Nullability matches (`null=True, blank=True` vs required).
- `related_name` matches what the contract promises other apps can use.
- Constraint names match the spec (the exact string `uniq_institution_name_ci` etc.) — these names surface in migration history and shouldn't drift.

## 5. Are the tests meaningful?

A test that always passes is worse than no test. Check:

- The test's assertion is actually about the behaviour under test, not incidental (e.g. "object exists" is not a test of uniqueness — the constraint violation is).
- Negative cases exist where they matter: does a test assert that a forbidden state raises the expected exception, not just that the happy path works?
- Factory usage is appropriate — the test reads like "arrange one Institution, one group, one person; act; assert", not a block of manual field assignment.

## How to deliver findings

Use `templates/review-report.md` and keep under ~40 lines total. Structure:

1. **Works** — one line. If it doesn't run, say so here and stop.
2. **Project-convention hits** — 1–3 concrete compliments. Cite the rule and the line.
3. **Idiomatic improvements** — up to 3, ranked by leverage. For each:
   - The finding in one line.
   - Before (what's there, 1–3 lines).
   - After (the suggested change, 1–3 lines).
   - Why this is the project's preference (cite a file).
   - **Blocking** or **Optional** — the user needs to know whether ticking the task is gated on this.
4. **Tests** — present & meaningful? If tests are a separate upcoming task, name the task ID.

Never apply the changes yourself. Teach, then hand back.
