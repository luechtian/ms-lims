# Quickstart: Parties Master Data

**Feature**: `001-parties-master-data`
**Date**: 2026-04-16

Day-one operator and developer walkthrough for the `parties` app. Written against the constitutional stack (Python 3.13, Django 6.0, SQLite). All paths are repo-root-relative.

---

## 1. First-time setup (operator)

### 1a. Edit the internal-lab fixture before first `migrate`

Open `parties/fixtures/internal_lab.json`. Replace the `REPLACE_ME` placeholders with your internal-lab identity:

```json
{
  "model": "parties.person",
  "pk": 1,
  "fields": {
    "first_name": "Johanna",
    "last_name": "Koddebusch",
    "email": "johanna@example.org",
    "research_group": 1,
    "active": true
  }
}
```

You may add more Persons with `pk: 2, 3, …` and the same `research_group: 1`. Adjust the ResearchGroup's `name` in the first and third entries if "Internes Lab" doesn't fit.

### 1b. Migrate

```powershell
python manage.py migrate
```

Expected output includes:

```
Applying parties.0001_initial... OK
Applying parties.0002_seed_internal_lab... OK
```

Your internal lab + Persons are now in the database.

### 1c. Verify in the admin

```powershell
python manage.py createsuperuser   # if you haven't yet
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/`, log in, click "Research groups" → you should see your internal lab with the configured Persons attached and the PI set.

---

## 2. Everyday operator workflows

### 2a. Onboard a new external research group (US1, SC-002)

From the admin home:

1. **Institutions** → **Add**: enter the university/company name, optional address, optional website → Save.
2. **Research groups** → **Add**: name the group, pick the Institution you just created (or leave empty for a freelance customer), leave **PI** empty for now → Save.
3. **Persons** → **Add**: first name / last name / email, pick the Research group you just created → Save.
4. **Research groups** → click your group → set **PI** to the Person you just added → Save.

Target: under 3 minutes end-to-end (SC-002 — manual acceptance test, not pytest).

### 2b. Personnel change — someone leaves

1. **Persons** → click the leaving Person → uncheck **Active** → Save.
2. If that Person was the group's PI, the group detail view shows a warning: "PI is currently inactive — please reassign." Create or pick a new Person in the same group and set them as PI.

### 2c. Personnel change — someone returns

1. **Persons** → filter "By active" → **No** → click the returning Person → check **Active** → Save.
2. The Person is back in all dropdowns for new assignments.

### 2d. Move a Person to a different group

Per FR-005a, `research_group` is immutable. The correct workflow is:

1. Deactivate the existing Person record (2b above).
2. **Persons** → **Add** → enter the same name / email, pick the new group → Save.

Existing downstream references (sample intakes, projects) stay pointed at the historical Person in the old group. New references use the new Person.

---

## 3. Developer walkthrough

### 3a. Install dev deps

```powershell
uv sync --extra dev
```

This pulls factory-boy alongside pytest / pytest-django / ruff.

### 3b. Run the parties test suite

```powershell
uv run pytest tests/parties/ -v
```

Expected: every test green. The suite covers:

- Model invariants (PI-must-be-member, delete-guard, immutable FK)
- QuerySet `.active()` / `.inactive()` behaviour
- Admin guardrails (no-delete for Person, readonly FK on change form, warning message on in-group email duplicate, FK dropdowns filtered to active)
- `parties/api.py` lookups, PI resolver, active-member listing
- Fixture validity and data-migration idempotency

### 3c. Use the public api

From another app or a shell:

```python
from parties import api

pi = api.get_pi(group)                          # Person | None
members = api.list_active_members(group)        # QuerySet[Person]
groups  = api.list_active_research_groups()     # QuerySet[ResearchGroup]
```

Never:

```python
from parties.models import Person  # ❌ violates constitution §IV.2
```

### 3d. Create test data with factories

```python
from tests.parties.factories import (
    InstitutionFactory,
    ResearchGroupFactory,
    PersonFactory,
)

group = ResearchGroupFactory(institution=InstitutionFactory())
alice = PersonFactory(research_group=group)
group.pi = alice
group.full_clean()
group.save()
```

---

## 4. Acceptance test mapping (spec → steps above)

| SC | How verified | Location |
|---|---|---|
| SC-001 (seed present on fresh install) | §1b + §1c | manual |
| SC-002 (<3 min to onboard external group) | §2a | manual (not pytest) |
| SC-003 (deactivation preserves references) | `tests/parties/test_models.py::test_deactivation_preserves_person_and_references` | pytest |
| SC-004 (<1 s search on 10k Persons) | `tests/parties/test_admin.py::test_search_perf_10k` (with factory-boy batch) | pytest |
| SC-005 (cannot delete group with active Persons) | `tests/parties/test_models.py::test_delete_guard` | pytest |
| SC-006 (PI-must-be-member rejected 100%) | `tests/parties/test_models.py::test_pi_must_be_member_rule` | pytest |
| SC-007 (no direct imports from parties.models in other apps) | ruff custom rule or manual review at PR time | tooling + review |
| SC-008 (seed idempotency) | `tests/parties/test_seed.py::test_migration_rerun_is_noop` | pytest |

---

## 5. Troubleshooting

**"UNIQUE constraint failed: uniq_institution_name_ci"** — you are trying to create a second Institution with the same name (case-insensitive). Find the existing one instead.

**"PI must be a member of this ResearchGroup"** — you selected a PI from a different group. Either pick a Person who belongs to this group, or create a new one in this group first.

**"Cannot delete a ResearchGroup that still has active Persons"** — deactivate all Persons in the group first, then delete. Or don't delete — inactive groups stay out of dropdowns on their own.

**Fixture edits seem to have no effect after `migrate`** — data migrations run exactly once per database. If you've already run `migrate`, edit the records directly in the admin. The fixture is only consulted on the first `migrate`.
