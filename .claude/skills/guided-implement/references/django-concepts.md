# Django Concepts Index

A compact map of Django concepts likely to show up in this project's tasks. Not a tutorial — it's the set of things you might need to deep-dive. Each entry has a one-sentence mental model plus where this project uses it. For deeper material, link to the Django docs or the relevant `specs/` file; don't paste docs inline.

## Models layer

### Model

The Python class backing a table. Fields are class attributes; metadata (ordering, constraints, indexes) lives in a nested `Meta` class. In this project: `parties/models.py` holds `Institution`, `ResearchGroup`, `Person`.

### Manager and QuerySet

The manager is the table-level object (`Model.objects`) through which you make queries; the QuerySet is the chainable lazy query the manager returns. Custom queryset methods (like `.active()`) become reusable chainable filters. In this project: `PartyQuerySet` in `parties/managers.py`, attached via `objects = PartyQuerySet.as_manager()`. Managers live in a dedicated file, not models.py — see plan.md.

### `Meta.constraints` vs field `unique=True`

`constraints` takes named `UniqueConstraint` / `CheckConstraint` objects that live in the database and are Django-aware. Prefer these: names make migrations legible, and you can express things field-level `unique` can't (case-insensitive via `Lower(...)`, partial constraints via `condition=Q(...)`, composite uniqueness). Field-level `unique=True` is the quick-and-dirty fallback.

### `Meta.ordering`

Default ordering applied to every queryset that doesn't override it. Handy but has a cost: every list query eats that ORDER BY. Check perf for large tables before reaching for it.

### `on_delete`

Required argument on every FK. Encodes the business rule for what happens when the parent row is deleted:

| Option | Meaning | Typical use |
|--------|---------|-------------|
| `CASCADE` | Children are deleted too. | Ownership-style relations. Rare. |
| `PROTECT` | Deleting the parent is forbidden while children exist (`ProtectedError`). | When losing children would be data loss. |
| `SET_NULL` | Child survives, FK becomes `NULL` (requires `null=True`). | Optional relationships (e.g. PI). |
| `SET_DEFAULT` | Child FK resets to the field's default. | Rare; needs a sane default. |
| `DO_NOTHING` | Django does nothing; DB may raise IntegrityError. | Advanced, when you're handling it at the DB layer. |

### `related_name` and `related_query_name`

Controls the reverse accessor. `ResearchGroup.persons.all()` comes from `Person.research_group = ForeignKey(..., related_name="persons")`. Use `"+"` to disable the reverse relation when you don't want it (e.g. ResearchGroup.pi uses `"+"` because Person.research_group already models the membership).

### `clean()` vs `save()` vs form validation

Three layers:

- **Field validators** (`validators=[...]`) — per-field checks run during form cleaning.
- **`Model.clean()`** — object-level invariants (multi-field rules). Runs when `full_clean()` is called or when a `ModelForm` cleans. The ModelAdmin calls `full_clean()` through its form by default.
- **`Model.save()`** — persistence. Don't put validation here; by the time you've reached `save()` the system has decided the object is valid.

The PI-must-be-member check for ResearchGroup lives in `clean()`, not `save()`. See tasks.md T017 and research R5.

### Migrations

`makemigrations` generates a migration file from model diffs; `migrate` applies pending migrations to the database. Commit migration files — they are source code, not build artefacts. Don't hand-edit generated migrations unless you know why. Data migrations (for backfills or seeding) are regular migrations with `RunPython` operations — see the "internal lab seed" story in spec.md for a project example.

## Admin

### `ModelAdmin`

The per-model admin configuration class, registered against a model in `apps/admin.py`. Common attributes: `list_display`, `list_filter`, `search_fields`, `readonly_fields`. Forms are auto-generated from the model but can be overridden with `form = MyForm`.

### Admin and `full_clean()`

The default admin form is a `ModelForm` and runs `full_clean()` as part of form validation — which means `Model.clean()` errors become field-level form errors automatically. If the user wires the constraint in `clean()` correctly, the admin surfaces it without extra work.

## Testing (pytest + pytest-django)

### `pytest-django`'s `db` fixture

Unlocks database access for a test. In this project it's enabled project-wide — you don't need to pass it explicitly to every test.

### factory-boy

Data builders for test objects. `DjangoModelFactory` binds to a model; `SubFactory` builds related objects. In this project: `tests/parties/factories.py` — `InstitutionFactory`, `ResearchGroupFactory`, `PersonFactory`. Use factories in tests instead of hand-constructing model instances.

### `assertRaises` / `pytest.raises`

For testing expected failures — `ValidationError` from `full_clean()`, `ProtectedError` from a blocked delete, `IntegrityError` from a constraint violation.

## Where to go deeper

- Official docs: <https://docs.djangoproject.com/en/6.0/> — always prefer the version-matched docs (6.0 for this project).
- This project's research log: `specs/<feature>/research.md` for decision rationale.
- Data model: `specs/<feature>/data-model.md` for field-level contracts.
