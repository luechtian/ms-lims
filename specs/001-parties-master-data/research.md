# Phase 0 Research: Parties Master Data

**Feature**: `001-parties-master-data`
**Date**: 2026-04-16

This document records the non-trivial implementation choices made before design and their rationale. Every clarification from the spec's `## Clarifications` section already answers a user-facing question; this file answers the implementation-facing questions that follow from those answers.

No `NEEDS CLARIFICATION` markers remain from the spec. All remaining open questions are implementation choices within the constitutional stack.

---

## R1. Seed mechanism — JSON fixture + data migration

**Decision**: Ship a JSON fixture at `parties/fixtures/internal_lab.json` with explicit primary keys and load it from a hand-written data migration `parties/migrations/0002_seed_internal_lab.py`. The data migration uses `django.core.management.call_command("loaddata", "internal_lab", app_label="parties")`.

**Rationale**:
- User direction was explicit: "simple JSON fixture, no over-engineered config system; operator edits the fixture before first `migrate`."
- Data migrations run exactly once per database (tracked in `django_migrations`), so the re-run/idempotency guarantee (FR-017) is satisfied by Django's own migration machinery, not by custom upsert logic.
- `loaddata` with explicit PKs is update-or-create by nature, so even if the migration were ever re-applied via `migrate --fake-initial` gymnastics, rows would be overwritten with the fixture state, not duplicated.
- After the migration has run, user edits in the admin are not overwritten on subsequent `migrate` runs because the migration does not run again.
- Ships with a sensible minimal default (name "Internes Lab", one PI, one member) that the operator replaces before first `migrate`.

**Alternatives considered**:
- `post_migrate` signal handler — runs on every `migrate`, forcing hand-written "create only if missing" upsert logic. More code, no upside given data-migration idempotency is free.
- Custom management command (`seedparties`) — would require operator to run a second command after `migrate`, violating FR-016 ("as part of the standard database-setup step").
- `django-fixture-magic` / `django-seed` / YAML config loader — unjustified YAGNI violation for three models and a handful of rows.

**Fixture structure**: see `contracts/parties-api.md` appendix and `data-model.md` for field-level detail. Natural order inside the fixture: Institution (may be null/absent), then ResearchGroup, then all Persons, and finally a second ResearchGroup entry whose `pi` FK is populated (resolving the chicken-and-egg by splitting the two writes).

---

## R2. Case-insensitive uniqueness constraints at the DB level

**Decision**: Implement FR-010a (Institution name unique globally) and FR-010b (ResearchGroup name unique within Institution scope, globally unique when no Institution) as Django `UniqueConstraint` objects using `Lower("name")` functional expression. Define two constraints on ResearchGroup to handle the `institution IS NULL` case explicitly.

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            Lower("name"),
            name="uniq_institution_name_ci",
        ),
    ]
# on ResearchGroup:
constraints = [
    models.UniqueConstraint(
        Lower("name"), "institution",
        name="uniq_group_name_in_institution_ci",
        condition=Q(institution__isnull=False),
    ),
    models.UniqueConstraint(
        Lower("name"),
        name="uniq_group_name_no_institution_ci",
        condition=Q(institution__isnull=True),
    ),
]
```

**Rationale**:
- SQL `UNIQUE(name, institution_id)` treats `NULL != NULL`, so two groups named "Freelancer X" with `institution=NULL` would slip through a single composite constraint. Splitting into two partial constraints fixes this cleanly.
- `Lower("name")` is supported by SQLite ≥3.9 as a functional index and by Postgres natively. Works today; stays portable to the documented Postgres upgrade path.
- Enforcement at the DB layer prevents race conditions (unlikely in a single-user app, but free correctness).
- Model `clean()` re-checks for friendly error messages in the admin before the DB constraint fires.

**Alternatives considered**:
- App-level only (in `clean()`): leaves a race window, and a direct DB operation (fixture load, shell) could bypass it.
- Storing names already normalised (lowercase) in a separate `name_ci` column: unnecessary complexity; functional indexes are the standard modern answer.

---

## R3. Reversible active/inactive — plain `BooleanField`, NOT django-fsm-2

**Decision**: Model `active` as `models.BooleanField(default=True, db_index=True)` on both ResearchGroup and Person. No state machine.

**Rationale**:
- Per Q2 of the spec clarifications, deactivation is a reversible toggle — not a terminal state. django-fsm-2 is designed for multi-state lifecycles with transition guards and audit trails (Sample, Batch, Run per constitution); using it for a two-value reversible flag is overkill.
- Constitution §"Design Patterns" explicitly mandates FSM only for Sample, Batch and Run entities. Parties entities are explicitly not named there.
- `db_index=True` keeps the "filter to active only" dropdown queries fast.

**Alternatives considered**:
- django-fsm-2 with ACTIVE ↔ INACTIVE states: two-state machine adds no value (no guards, no side-effects on transition, no audit trail needed in v1).
- Soft-delete library (`django-safedelete`, `django-model-utils.SoftDeletableModel`): parties already has no delete operation for Persons (FR-010); reusing a soft-delete lib would conflate "hidden from selection" (our case) with "logically deleted" (its case).

---

## R4. Custom manager / queryset (`parties/managers.py`)

**Decision**: Each party model gets `objects = PartyQuerySet.as_manager()` where `PartyQuerySet` provides `.active()` and `.inactive()` chainable methods. Default manager returns ALL rows (active and inactive) so the Django admin shows everything; callers that want only active rows call `.active()` explicitly.

```python
class PartyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def inactive(self):
        return self.filter(active=False)
```

**Rationale**:
- Constitution §"Design Patterns": "Explicit Repository Pattern — Django Manager/QuerySet is the repository."
- Admin MUST see inactive entries too (FR-013 — "remain visible through explicit filters"); a default manager that hid them would break the admin list.
- `.active()` is the one place `api.py` and admin dropdown-filters both reach for — single source of truth for "what counts as active".

**Alternatives considered**:
- Two managers (`objects` = all, `active` = active-only): introduces a second manager name to remember and doesn't compose in chained queries as cleanly.
- Manager method on the model itself: less reusable across the three models; QuerySet method is DRY.

---

## R5. PI-must-be-member enforcement

**Decision**: Enforce FR-008 in `ResearchGroup.clean()`:

```python
def clean(self):
    super().clean()
    if self.pi_id is not None and self.pi.research_group_id != self.pk:
        raise ValidationError({"pi": "PI must be a member of this ResearchGroup."})
```

Django admin calls `full_clean()` before save, so the admin surfaces this as a field-level form error.

**Rationale**:
- Fat model (constitution §"Design Patterns"): the invariant belongs on the model, not in the admin form.
- Works uniformly regardless of entry point (admin, api, shell, fixture loading through a code path that calls `full_clean`).
- Field-level error maps cleanly to Django admin's field highlight.

**Alternatives considered**:
- `CheckConstraint` at DB level: cannot express "the Person referenced by PI must have `research_group=this group's pk`" in a standard CHECK (requires a subquery). Would need a trigger — overkill.
- Admin-only form validation: loses coverage for fixture loads and api-level calls.

**Edge case**: When creating a ResearchGroup in the admin for the first time, the group has no PK yet (`self.pk is None`). The `self.pi.research_group_id != self.pk` check then compares against None and raises. This is actually desired: a brand-new group has no members, so assigning a PI on create is always wrong. Must create group first, add Person, then set PI — which exactly matches User Story 1's documented flow.

---

## R6. Delete guard on ResearchGroup with active Persons

**Decision**: Override `ResearchGroup.delete()` to raise `django.db.models.ProtectedError` when the group has any active Persons. Also override `ResearchGroupQuerySet.delete()` to enforce the same rule on bulk deletes.

```python
def delete(self, *args, **kwargs):
    if self.persons.filter(active=True).exists():
        raise ProtectedError(
            "Cannot delete a ResearchGroup that still has active Persons. "
            "Deactivate all Persons first.",
            set(self.persons.filter(active=True)),
        )
    return super().delete(*args, **kwargs)
```

**Rationale**:
- Uses Django's standard `ProtectedError`, which the admin already displays nicely ("Cannot delete …").
- Lives on the model — no way to bypass via queryset delete or api call.
- `self.persons` is the reverse relation from `Person.research_group = FK(ResearchGroup, related_name="persons")`.

**Alternatives considered**:
- `on_delete=PROTECT` on `Person.research_group`: would protect on ANY Person (active or inactive). We want to allow deletion of a group whose Persons are all inactive (spec edge case, out of scope for cascading external refs).
- Signal on pre_delete: further from the data; harder to test; splits the logic from where the data lives.

---

## R7. Preventing Person deletion (FR-010)

**Decision**: In `PersonAdmin`, set `has_delete_permission(self, request, obj=None) -> False` for non-superusers; for superusers also return `False` during normal operation. Deactivation is the only path. Remove the bulk "delete selected" action.

**Rationale**:
- FR-010 is admin-level, not a DB constraint (the model itself can still be deleted via shell for administrative cleanup if ever needed).
- `has_delete_permission = False` cleanly hides both the row-level "Delete" button and the bulk delete action in the admin.
- Aligns with the spec: "direct deletion from the admin is disabled; deactivation is the substitute action."

**Alternatives considered**:
- Raising in `Person.delete()` too: too aggressive — would break test teardown and legitimate shell cleanup. The admin restriction is the contract; model-layer deletion stays available.

---

## R8. Immutable `Person.research_group` (FR-005a)

**Decision**: Two-layer enforcement.

1. **Admin**: `PersonAdmin.get_readonly_fields(request, obj)` returns `["research_group"]` when `obj is not None` (i.e. change form), and `[]` on the add form.
2. **Model**: `Person.clean()` compares against the DB value and raises ValidationError if `research_group_id` has changed on an existing row.

```python
def clean(self):
    super().clean()
    if self.pk:
        original_group_id = Person.objects.filter(pk=self.pk).values_list(
            "research_group_id", flat=True,
        ).first()
        if original_group_id and original_group_id != self.research_group_id:
            raise ValidationError(
                {"research_group": "Person.research_group is immutable. Deactivate and re-create in the target group."},
            )
```

**Rationale**:
- Readonly-field in admin removes the failure mode entirely at the UX level.
- Model-level check is belt-and-suspenders: catches fixture loads, api-level writes, and any other surface that bypasses the admin.
- One extra SELECT on save of an existing Person is negligible (<1 ms on SQLite).

**Alternatives considered**:
- DB-level trigger: SQLite triggers are doable but non-portable and invisible to future readers of the models.
- `django-immutablefield` 3rd-party lib: YAGNI violation; 20 lines of own code are clearer.

---

## R9. Advisory email-duplicate warning (FR-010c) — pragmatic Django admin path

**Decision**: Override `PersonAdmin.save_model()`. After `super().save_model(...)`:

```python
def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)
    duplicates = (
        Person.objects.active()
        .filter(research_group=obj.research_group, email__iexact=obj.email)
        .exclude(pk=obj.pk)
    )
    if duplicates.exists():
        self.message_user(
            request,
            f"Heads up: another active Person in {obj.research_group} already uses this email "
            f"({', '.join(p.full_name for p in duplicates)}). Saved anyway — edit if unintended.",
            level=messages.WARNING,
        )
```

**Rationale**:
- Per user direction: "im Django Admin gibt es kein natives 'warn but allow save'. Pragmatische Lösung wählen (z.B. messages.warning nach save), nicht overengineer-en."
- The Django `messages` framework is already wired up in the admin; no extra dependencies.
- Post-save warning is clearly visible (top of the change-list page after redirect) and accepts the save, matching FR-010c's "advisory, not hard rejection" intent.

**Alternatives considered**:
- Pre-save form validation that shows a warning but allows submit on second click (confirmation flow): Django admin has no first-class pattern for this; would require hand-rolled session state or JS.
- Custom admin change view override: materially more code, same outcome.
- Model `clean()` raising a non-error "warning" exception: Django doesn't have such a concept; `ValidationError` always blocks.

---

## R10. Dev-only dependency: factory-boy

**Decision**: Add `factory-boy>=3.3` to `[dependency-groups].dev` in `pyproject.toml`. Create `tests/parties/factories.py` with `InstitutionFactory`, `ResearchGroupFactory`, `PersonFactory`.

**Rationale**:
- Per constitution / user direction: "pytest + factory-boy" is the test stack.
- factory-boy is mature, stable, no runtime impact (dev-only), and plays well with pytest-django's `db` fixture.
- Three models × several test paths (models, managers, admin, api, seed) is exactly the volume where ad-hoc `Institution.objects.create(...)` starts to hurt.

**Alternatives considered**:
- Hand-written fixtures in conftest: fine for 5 tests, painful for 30.
- `model-bakery`: similar; factory-boy is the more widely known choice in Django shops and matches the user's explicit request.

---

## R11. Admin dropdown filtering to active-only (FR-012, FR-013)

**Decision**: Override `formfield_for_foreignkey` on each admin class to filter the FK queryset to `.active()` when the FK points at Person or ResearchGroup:

```python
def formfield_for_foreignkey(self, db_field, request, **kwargs):
    if db_field.name in {"pi", "research_group"}:
        kwargs["queryset"] = db_field.related_model.objects.active()
    return super().formfield_for_foreignkey(db_field, request, **kwargs)
```

**Rationale**:
- Single, uniform hook. Applied on `ResearchGroupAdmin` (filters `pi`) and `PersonAdmin` (filters `research_group` on the add form; the change form already makes it readonly per R8).
- The default queryset stays unfiltered for listing / searching, so inactive rows remain visible where they should be.

**Alternatives considered**:
- Custom form with a manually specified queryset: more boilerplate for the same result.

---

## R12. PI-inactive warning (FR-015) rendered in admin

**Decision**: Add a computed method `ResearchGroupAdmin.pi_warning(obj)` that returns an HTML-escaped warning string when `obj.pi and not obj.pi.active`. Add it to `readonly_fields` so the change form renders it as a visible row.

**Rationale**:
- Minimal code. No custom template override. The warning is visible exactly where the decision needs to be made (the group's change page).
- The model-level invariant (PI-must-be-member) is still enforced; this is purely a UX surfacing of the post-deactivation inconsistency.

**Alternatives considered**:
- Custom admin template extension: more surface area, same outcome.
- Auto-clearing PI on deactivation: explicitly ruled out by FR-015.

---

## R13. Public interface (`parties/api.py`) shape

**Decision**: Minimal, typed functions, no classes. Signatures pinned in `contracts/parties-api.md`. Interface exposes read and lookup only — no create/update/delete — because FR-022 explicitly names only "lookup … resolve PI … list active members". v1 writers go through the admin, not through api.py.

**Rationale**:
- YAGNI: future modules can add write wrappers when they actually need them.
- Keeps the contract surface tiny and auditable.
- Constitution §IV.2: `api.py` is the public interface; keeping it read-only mirrors how repositories behave in most projects — write paths live with the owning module.

**Alternatives considered**:
- Expose full CRUD wrappers: premature; unused write paths rot.
- Export model classes directly from api.py: would allow consumers to bypass the QuerySet-method contract and couple to model internals.

---

## R14. No `services.py` in this feature

**Decision**: Do not create `parties/services.py`. Revisit when the first cross-app operation lands (e.g., `projects` creating a Project that needs to resolve a PI).

**Rationale**: Constitution §"Design Patterns": "Service Layer for cross-app operations. Code that touches two or more apps lives in `{app}/services.py`". Parties currently touches no other app — no service layer earns its keep yet.

---

## Summary: open items → all resolved

| Open item | Resolution | Ref |
|---|---|---|
| Seed format | JSON fixture + data migration | R1 |
| CI uniqueness for name fields | Functional `UniqueConstraint` with `Lower(...)` | R2 |
| State machine vs. boolean | `BooleanField` (explicit non-use of FSM) | R3 |
| Manager pattern | `PartyQuerySet.as_manager()`, `.active()` | R4 |
| PI-must-be-member | `ResearchGroup.clean()` | R5 |
| Delete guard | `ResearchGroup.delete()` + queryset delete | R6 |
| Person deletion prevented | `has_delete_permission=False` in admin | R7 |
| Immutable FK | Admin readonly + `Person.clean()` | R8 |
| Email warning | `save_model` + `messages.warning` | R9 |
| Test tooling | factory-boy (dev-only) | R10 |
| Dropdown filtering | `formfield_for_foreignkey` | R11 |
| PI-inactive warning | Admin readonly display method | R12 |
| api.py shape | Read-only lookups | R13 |
| services.py | Not needed yet | R14 |

**No remaining `NEEDS CLARIFICATION`. Ready for Phase 1.**
