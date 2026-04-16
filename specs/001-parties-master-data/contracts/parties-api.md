# Contract: `parties/api.py` — Public Module Interface

**Feature**: `001-parties-master-data`
**Status**: Draft v1

This file defines the **only** interface other Django apps may use to read parties data. Direct imports from `parties.models` or `parties.admin` in other apps are forbidden by constitution §IV.2 and enforced by review + a linter check (see Task list, post-plan).

**Scope**: Read-only lookups and list helpers. No write functions — v1 writers go through the Django admin. This boundary is deliberate (research R13) and may be extended by a future spec when a concrete cross-app write need lands.

---

## Type aliases

```python
from parties.models import Institution, Person, ResearchGroup

# These are the only three model classes consumers may receive as return values.
# Consumers MUST treat them as read-only (do not call .save() on a returned
# object from another module — route writes through this app's admin or a
# future write extension to api.py).
```

---

## Functions

### Lookups by identifier

```python
def get_institution(institution_id: int) -> Institution | None:
    """Return the Institution with the given id, or None if not found.

    Returns the institution regardless of active state; callers that need
    only active institutions should check `.active` themselves or use
    `list_active_institutions()`.

    Satisfies: FR-022 (lookup of Institution by identifier).
    """


def get_research_group(group_id: int) -> ResearchGroup | None:
    """Return the ResearchGroup with the given id, or None if not found.

    Returns the group regardless of active state.

    Satisfies: FR-022 (lookup of ResearchGroup by identifier).
    """


def get_person(person_id: int) -> Person | None:
    """Return the Person with the given id, or None if not found.

    Returns the person regardless of active state — downstream modules
    legitimately need to resolve historical references to inactive Persons
    (e.g. "who submitted this sample intake in 2024?").

    Satisfies: FR-022 (lookup of Person by identifier).
    """
```

### Principal Investigator resolution

```python
def get_pi(group: ResearchGroup) -> Person | None:
    """Return the Person currently assigned as PI of the given ResearchGroup,
    or None if the group has no PI set.

    Returns the PI even if the PI is inactive — per FR-015, the reference
    is preserved on deactivation; callers decide whether to surface a warning.

    Satisfies: FR-022 (resolving the PI of a ResearchGroup).
    """
```

### Listing active members and groups

```python
def list_active_members(group: ResearchGroup) -> QuerySet[Person]:
    """Return a QuerySet of active Persons in the given ResearchGroup,
    ordered by last_name, first_name.

    Excludes inactive Persons even if they were members. Returns an empty
    QuerySet if the group has no active members.

    Satisfies: FR-021 ("who is currently in AG Müller?"), FR-022
    (listing active members of a ResearchGroup).
    """


def list_active_research_groups() -> QuerySet[ResearchGroup]:
    """Return a QuerySet of all active ResearchGroups, ordered by name.

    Satisfies: common dropdown/listing need from later modules (projects,
    sample intakes). Active-only by default so callers don't each
    re-filter.
    """


def list_active_institutions() -> QuerySet[Institution]:
    """Return a QuerySet of all active Institutions, ordered by name.

    Satisfies: dropdown/listing need from the admin of later modules.
    """
```

---

## Rules for consumers

1. **Never import from `parties.models` or `parties.admin` in another app.** Use only this module.
2. **Treat returned objects as read-only.** Do not call `.save()`, `.delete()`, or mutate fields. If you need a write, extend this contract in a follow-up spec.
3. **Respect `None` returns.** `get_*` functions return `None` for missing identifiers; handle it.
4. **Do not re-filter `list_active_*` results for active state.** They are already active-filtered by contract.

## Rules for the parties app

1. **These signatures are stable.** Changing them requires a new spec or a contract version bump.
2. **Implementation may change freely** behind these signatures. The function bodies live in `parties/api.py`; model internals are invisible to consumers.
3. **All listed functions MUST have a corresponding test in `tests/parties/test_api.py`** (FR-026).

---

## Not in this contract (v1)

- Write/create/update/delete helpers. If a later module needs to create a Person from code (e.g. bulk CSV import), a new spec extends this contract.
- Search helpers (`find_persons_by_email`, etc.). The admin search covers the v1 user-facing need; code-level search is YAGNI until a caller exists.
- Bulk lookups (`get_persons([1, 2, 3])`). Add when a caller needs them.

## Change log

| Version | Date | Change |
|---|---|---|
| v1 (draft) | 2026-04-16 | Initial contract: three lookups, PI resolver, three active-list helpers. |
