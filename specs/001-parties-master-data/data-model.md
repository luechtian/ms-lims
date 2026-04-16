# Phase 1 Data Model: Parties Master Data

**Feature**: `001-parties-master-data`
**Date**: 2026-04-16

This document translates the spec's Key Entities + Functional Requirements into concrete Django model definitions. Every field maps to a spec requirement; every invariant names the FR it enforces.

---

## Entity summary

| Entity | Purpose | Count (v1 scale) |
|---|---|---|
| Institution | Optional organisational parent | tens |
| ResearchGroup | Stable sample-supplier axis; internal lab modelled as one | hundreds |
| Person | Member of exactly one ResearchGroup | ≤10 000 |

No state machine on any entity — see research R3.

---

## Institution

| Field | Type | Notes | Spec ref |
|---|---|---|---|
| `id` | `BigAutoField` (default PK) | — | — |
| `name` | `CharField(max_length=255)` | Case-insensitive unique globally via functional `UniqueConstraint(Lower("name"))` | FR-001, FR-010a |
| `address` | `TextField(blank=True, default="")` | Free text; no structured parsing | FR-001, Assumptions |
| `website` | `URLField(blank=True, default="")` | Optional | FR-001 |
| `active` | `BooleanField(default=True, db_index=True)` | Soft-retire an Institution; inactive Institutions hidden from FK dropdowns | FR-011 analogue (spec lists active state for Persons/ResearchGroups; extending to Institution for UI consistency) |

**Constraints**

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            Lower("name"),
            name="uniq_institution_name_ci",
        ),
    ]
    ordering = ["name"]
```

**Manager**: `objects = PartyQuerySet.as_manager()` (see `parties/managers.py`)

**Methods**

- `__str__` → `self.name`
- `clean()` — no additional invariants beyond DB constraints.

> **Note on `active` for Institution**: the spec does not explicitly mandate an `active` flag on Institution — only on Person and ResearchGroup (FR-011). We extend the pattern to Institution for admin-dropdown consistency (an Institution used only by now-defunct groups should be hide-able). If this turns out to bloat the tests, we will remove it in a future spec — for v1 it's one field and one manager method, free of cost.

---

## ResearchGroup

| Field | Type | Notes | Spec ref |
|---|---|---|---|
| `id` | `BigAutoField` | — | — |
| `name` | `CharField(max_length=255)` | Scoped uniqueness — unique within Institution, and globally unique when `institution IS NULL` | FR-002, FR-010b |
| `institution` | `ForeignKey(Institution, null=True, blank=True, on_delete=PROTECT, related_name="research_groups")` | Optional; `PROTECT` so Institution deletion can't orphan groups | FR-002, FR-006 |
| `pi` | `ForeignKey(Person, null=True, blank=True, on_delete=SET_NULL, related_name="+")` | Optional; must be a member (see invariant I1). `SET_NULL` chosen deliberately — if a Person record is ever hard-deleted via shell, the group survives with an empty PI slot (matches FR-015 semantics). | FR-007, FR-008 |
| `active` | `BooleanField(default=True, db_index=True)` | Reversible per Q2 of spec clarifications | FR-011 |
| `created_at` | `DateTimeField(auto_now_add=True)` | Audit visibility in admin | — |
| `updated_at` | `DateTimeField(auto_now=True)` | Audit visibility in admin | — |

**Constraints**

```python
class Meta:
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
    ordering = ["name"]
```

**Invariants**

- **I1 (PI-must-be-member, FR-008)**: If `pi_id is not None`, then `self.pi.research_group_id == self.pk`. Enforced in `clean()`; raises `ValidationError({"pi": ...})`.
- **I2 (Delete-guard, FR-009)**: `self.delete()` raises `ProtectedError` if `self.persons.filter(active=True).exists()`. Mirrored on `ResearchGroupQuerySet.delete()` for bulk deletes.

**Methods**

- `__str__` → `self.name`
- `clean()` — enforces I1.
- `delete()` — enforces I2.
- `active_members()` → `self.persons.active()` (thin wrapper; used by admin + api).

---

## Person

| Field | Type | Notes | Spec ref |
|---|---|---|---|
| `id` | `BigAutoField` | — | — |
| `first_name` | `CharField(max_length=100)` | — | FR-003 |
| `last_name` | `CharField(max_length=100)` | — | FR-003 |
| `email` | `EmailField(max_length=254)` | Not unique at DB level; advisory warning via admin only (see FR-010c + R9) | FR-003, FR-010c |
| `research_group` | `ForeignKey(ResearchGroup, null=False, on_delete=PROTECT, related_name="persons")` | **Immutable after creation** (FR-005a). Enforced in `clean()` + admin `readonly_fields`. | FR-003, FR-005, FR-005a |
| `active` | `BooleanField(default=True, db_index=True)` | Reversible toggle; hidden from selection dropdowns when False | FR-011, FR-012, FR-014 |
| `created_at` | `DateTimeField(auto_now_add=True)` | — | — |
| `updated_at` | `DateTimeField(auto_now=True)` | — | — |

> **Deliberately absent**: `role`. Per spec clarification Q4, PI-hood is a property of `ResearchGroup.pi`, not of Person. There is no role column.

**Constraints**

```python
class Meta:
    indexes = [
        models.Index(fields=["last_name", "first_name"]),
        models.Index(fields=["email"]),
    ]
    ordering = ["last_name", "first_name"]
```

**Invariants**

- **I3 (Immutable FK, FR-005a)**: on update of an existing row, `research_group_id` must equal the value currently in the database. Enforced in `clean()` with a single SELECT on the original row.
- **I4 (Advisory in-group email duplicate, FR-010c)**: NOT enforced as a model validation error — see R9; handled by `PersonAdmin.save_model` as a `messages.WARNING`.

**Methods**

- `__str__` → `f"{self.first_name} {self.last_name}"`
- `full_name` (property) → same as `__str__`, used in admin list and api outputs.
- `clean()` — enforces I3.

---

## Relationships

```
Institution (0..1) ──< ResearchGroup (1..N) ──< Person (1..N)
                                   │
                                   └── pi ──→ Person  (optional, same-group invariant)
```

- `Institution` → `ResearchGroup` (1:N, optional): `institution.research_groups`
- `ResearchGroup` → `Person` (1:N): `research_group.persons`
- `ResearchGroup` → `Person` via `pi` (0..1 each way, same-group invariant): `research_group.pi`

No many-to-many relations. No self-referential chains beyond the PI → Person → group loop (resolved by nullable PI + ordered inserts).

---

## Manager / QuerySet

One shared `PartyQuerySet` in `parties/managers.py`, used on all three models:

```python
class PartyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def inactive(self):
        return self.filter(active=False)
```

Exposed as:

```python
class Institution(models.Model):
    ...
    objects = PartyQuerySet.as_manager()

# identical on ResearchGroup and Person
```

**Consumers**:

- Admin `formfield_for_foreignkey` → `.active()` to filter FK dropdowns (FR-012, FR-013).
- `parties/api.py` → `.active()` for all public list/lookup helpers (FR-021).
- Tests → both `.active()` and `.inactive()` to verify filtering behaviour.

---

## Fixture shape (`parties/fixtures/internal_lab.json`)

```json
[
  {
    "model": "parties.researchgroup",
    "pk": 1,
    "fields": {
      "name": "Internes Lab",
      "institution": null,
      "pi": null,
      "active": true
    }
  },
  {
    "model": "parties.person",
    "pk": 1,
    "fields": {
      "first_name": "REPLACE_ME",
      "last_name": "REPLACE_ME",
      "email": "pi@example.org",
      "research_group": 1,
      "active": true
    }
  },
  {
    "model": "parties.researchgroup",
    "pk": 1,
    "fields": {
      "name": "Internes Lab",
      "institution": null,
      "pi": 1,
      "active": true
    }
  }
]
```

Two-phase structure resolves the chicken-and-egg on load: ResearchGroup saved first with `pi=null`, then Person saved with FK to group, then ResearchGroup upserted with `pi=1`. `loaddata` processes the list in order and re-saves the second group entry, producing the final state in a single fixture load.

**Operator action before first migrate**: edit the two `REPLACE_ME` fields (and email) to match the real internal lab PI; optionally add more Person entries with `pk=2, 3, …` and `research_group=1`.

---

## Migration plan (two migrations)

1. `parties/migrations/0001_initial.py` — auto-generated from model code via `python manage.py makemigrations parties`. Contains all three tables, constraints, and indexes.
2. `parties/migrations/0002_seed_internal_lab.py` — hand-written data migration with a single `RunPython` op that calls `call_command("loaddata", "internal_lab", app_label="parties")`. Reverse op is `RunPython.noop` (we don't undo seed data on migrate rollback).

Both migrations run together on a fresh `python manage.py migrate`, producing a database with the schema + seeded internal lab in one step (satisfies FR-016).

---

## Traceability matrix (FR → field/method)

| FR | Enforced by |
|---|---|
| FR-001 | Institution model fields |
| FR-002 | ResearchGroup model fields |
| FR-003 | Person model fields |
| FR-004 | Absence of Person.role field + ResearchGroup.pi field |
| FR-005 | `Person.research_group` with `null=False` |
| FR-005a | `Person.clean()` I3 + admin readonly |
| FR-006 | `ResearchGroup.institution` with `null=True` |
| FR-007 | `ResearchGroup.pi` with `null=True` |
| FR-008 | `ResearchGroup.clean()` I1 |
| FR-009 | `ResearchGroup.delete()` I2 |
| FR-010 | `PersonAdmin.has_delete_permission` |
| FR-010a | `Institution.Meta.constraints` |
| FR-010b | `ResearchGroup.Meta.constraints` (two partial unique) |
| FR-010c | `PersonAdmin.save_model` warning |
| FR-011 | `active` BooleanField on all three |
| FR-012 | Admin `formfield_for_foreignkey` |
| FR-013 | Admin `formfield_for_foreignkey` |
| FR-014 | Active flag toggle does not cascade; asserted by `tests/parties/test_models.py::test_deactivation_preserves_person_and_references` |
| FR-015 | `ResearchGroupAdmin.pi_warning` readonly display |
| FR-016–18 | Data migration 0002 + `fixtures/internal_lab.json` |
| FR-019 | `PersonAdmin.search_fields` |
| FR-020 | `ResearchGroupAdmin.search_fields` |
| FR-021 | `ResearchGroup.active_members()` + `api.list_active_members` |
| FR-022, FR-023 | `parties/api.py` (see contracts) |
| FR-024, FR-025 | Admin classes with list_display |
| FR-026 | `tests/parties/*` |
