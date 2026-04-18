---

description: "Task list for Parties Master Data feature implementation"
---

# Tasks: Parties Master Data

**Input**: Design documents from `/specs/001-parties-master-data/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/parties-api.md, quickstart.md

**Tests**: INCLUDED — FR-026 mandates automated test coverage for every functional requirement. Tests within each story are written first and expected to fail before the corresponding implementation task completes.

**Organization**: Grouped by user story (US1–US5 from spec.md). Each phase is an independently verifiable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US5)
- All paths are repo-root-relative

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bring the `parties` app into existence and wire dev tooling.

- [x] T001 Scaffold the `parties` Django app: create `parties/__init__.py`, `parties/apps.py` (`PartiesConfig` with `default_auto_field = "django.db.models.BigAutoField"` and `verbose_name = "Parties"`), empty `parties/models.py`, `parties/admin.py`, `parties/api.py`, `parties/managers.py`, and `parties/migrations/__init__.py`. Create the directory `parties/fixtures/` (empty for now).
- [x] T002 Register the new app in `config/settings.py`: append `"parties.apps.PartiesConfig"` to `INSTALLED_APPS`.
- [x] T003 [P] Add `factory-boy>=3.3` to `[dependency-groups].dev` in `pyproject.toml`; run `uv sync --extra dev` and verify `factory` imports in a shell.
- [x] T004 [P] Create the test tree skeleton: `tests/parties/__init__.py` and an empty-but-importable `tests/parties/conftest.py` (can stay empty — pytest-django's `db` fixture is already enabled project-wide).

**Checkpoint**: `python manage.py check` passes; the app is registered but has no models yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The three model skeletons, manager, initial migration, and bare admin registration. Every user story depends on this phase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Implement `PartyQuerySet` in `parties/managers.py` with `.active()` (filter `active=True`) and `.inactive()` (filter `active=False`) chainable methods (research R4).
- [x] T006 [P] Implement bare `Institution` model in `parties/models.py` with fields (`name`, `address`, `website`, `active`), `objects = PartyQuerySet.as_manager()`, `Meta.ordering = ["name"]`, `Meta.constraints = [UniqueConstraint(Lower("name"), name="uniq_institution_name_ci")]`, and `__str__` (data-model §Institution; research R2).
- [x] T007 [P] Implement bare `ResearchGroup` model in `parties/models.py` with fields (`name`, `institution` FK null, `pi` FK to Person null with `on_delete=SET_NULL` and `related_name="+"`, `active`, `created_at`, `updated_at`), `objects = PartyQuerySet.as_manager()`, `Meta.ordering = ["name"]`, two partial unique constraints on `Lower("name")` per R2, `__str__`, and a thin `active_members()` method returning `self.persons.active()`. **Do NOT** add `clean()` or `delete()` overrides yet — those belong to US1 and US3.
- [x] T008 [P] Implement bare `Person` model in `parties/models.py` with fields (`first_name`, `last_name`, `email`, `research_group` FK `null=False` `on_delete=PROTECT` `related_name="persons"`, `active`, `created_at`, `updated_at`), `objects = PartyQuerySet.as_manager()`, `Meta.indexes = [Index(["last_name","first_name"]), Index(["email"])]`, `Meta.ordering = ["last_name","first_name"]`, `__str__`, and `full_name` property. **Do NOT** add `clean()` yet — that belongs to US3.
- [x] T009 Generate the initial schema migration: `python manage.py makemigrations parties` produces `parties/migrations/0001_initial.py`. Commit the file. Run `python manage.py migrate` and confirm the three tables exist.
- [x] T010 Create bare admin registrations in `parties/admin.py`: `InstitutionAdmin`, `ResearchGroupAdmin`, `PersonAdmin` with `list_display` showing the obvious identifying columns (no custom behavior yet — US1/US3/US4 extend these files).
- [x] T011 [P] Create `tests/parties/factories.py` with `InstitutionFactory`, `ResearchGroupFactory` (defaulting `pi=None` to sidestep chicken-and-egg), and `PersonFactory`. Use factory-boy's `DjangoModelFactory` and `SubFactory`.
- [x] T012 [P] Add a foundation smoke test in `tests/parties/test_models.py::test_foundation_can_create_all_three` that uses the factories to create one Institution, one ResearchGroup, one Person and asserts they persist.

**Checkpoint**: `uv run pytest tests/parties/ -v` passes one green test; admin shows three empty list pages.

---

## Phase 3: User Story 1 — Onboard an external research group (Priority: P1) 🎯 MVP

**Goal**: Operator creates Institution → ResearchGroup → Person → assigns PI via admin; PI-must-be-member invariant is enforced.

**Independent Test**: Acceptance Scenarios 1–6 of US1 in spec.md. Manual: SC-002 (<3 min end-to-end onboarding via admin). Automated: PI-must-be-member tests pass.

### Tests for User Story 1 (write first, expect failures before T016/T017)

- [ ] T013 [P] [US1] In `tests/parties/test_models.py`, add `test_pi_can_be_none_on_new_group` — creating a ResearchGroup without a PI succeeds and `group.pi is None`.
- [ ] T014 [P] [US1] In `tests/parties/test_models.py`, add `test_pi_must_be_member_happy_path` — assigning a Person of the same group as PI passes `full_clean()` and saves.
- [ ] T015 [P] [US1] In `tests/parties/test_models.py`, add `test_pi_must_be_member_rejects_other_group` — assigning a Person from a different ResearchGroup as PI raises `ValidationError` with key `pi`.
- [ ] T016 [P] [US1] In `tests/parties/test_admin.py`, add `test_admin_onboarding_flow_roundtrip` — superuser client POSTs to admin add URLs in order (Institution → ResearchGroup → Person → set PI) and verifies a 302 redirect on each step plus the final group has the expected PI.

### Implementation for User Story 1

- [ ] T017 [US1] Add `clean()` to `ResearchGroup` in `parties/models.py` enforcing the PI-must-be-member invariant (research R5): raise `ValidationError({"pi": "PI must be a member of this ResearchGroup."})` when `self.pi_id is not None and self.pi.research_group_id != self.pk`.
- [ ] T018 [US1] In `parties/admin.py`, polish `InstitutionAdmin.list_display = ("name", "website", "active")`, `ResearchGroupAdmin.list_display = ("name", "institution", "pi", "active")`, `PersonAdmin.list_display = ("last_name", "first_name", "email", "research_group", "active")`. Ensure `ResearchGroupAdmin` surfaces the PI-must-be-member `ValidationError` as a field-level form error (Django's default `ModelForm` already does this — verify in T016).

**Checkpoint**: `pytest tests/parties/ -k "US1 or pi_must"` green. Manual onboarding flow works end-to-end in admin.

---

## Phase 4: User Story 2 — Internal lab seeded on first start (Priority: P2)

**Goal**: `python manage.py migrate` on a fresh database produces a "Internes Lab" ResearchGroup with configured Persons and PI.

**Independent Test**: Acceptance Scenarios 1–3 of US2. Manual: drop `db.sqlite3`, run `migrate`, open admin. Automated: fixture validity + migration idempotency tests.

### Tests for User Story 2

- [ ] T019 [P] [US2] In `tests/parties/test_seed.py`, add `test_internal_lab_fixture_is_valid_json` — open `parties/fixtures/internal_lab.json`, parse it, assert top-level is a non-empty list.
- [ ] T020 [P] [US2] In `tests/parties/test_seed.py`, add `test_loaddata_creates_internal_lab` — on an empty DB, call `call_command("loaddata", "internal_lab", app_label="parties")` and assert exactly one ResearchGroup named "Internes Lab" with at least one Person and `pi_id is not None`.
- [ ] T021 [P] [US2] In `tests/parties/test_seed.py`, add `test_loaddata_is_idempotent` — run `loaddata` twice in sequence; assert the Person and ResearchGroup counts are unchanged after the second run (verifies FR-017 + SC-008).
- [ ] T022 [P] [US2] In `tests/parties/test_seed.py`, add `test_migrate_seeds_internal_lab` (uses pytest-django's `django_db(transaction=True)` or a fresh-DB fixture) — after `migrate` completes, the internal-lab group is present.

### Implementation for User Story 2

- [ ] T023 [US2] Create `parties/fixtures/internal_lab.json` per data-model.md §Fixture shape. Two-phase layout: ResearchGroup pk=1 with `pi=null`, then Person pk=1 with `research_group=1`, then ResearchGroup pk=1 again with `pi=1`. Use `REPLACE_ME` placeholders for personal names / emails so operators know to edit before first migrate.
- [ ] T024 [US2] Create `parties/migrations/0002_seed_internal_lab.py` — a hand-written data migration with a single `RunPython` operation that imports `django.core.management.call_command` and calls `call_command("loaddata", "internal_lab", app_label="parties")`. Reverse op: `migrations.RunPython.noop`. Depends on `0001_initial`.

**Checkpoint**: Drop `db.sqlite3`; run `python manage.py migrate`; confirm internal lab appears in admin. All US2 tests pass.

---

## Phase 5: User Story 3 — Preserve history when people leave (Priority: P2)

**Goal**: Deactivation keeps data; dropdowns hide inactive; Persons can't be deleted; groups with active members can't be deleted; `Person.research_group` can't be reassigned; deactivating a PI surfaces a warning.

**Independent Test**: Acceptance Scenarios 1–5 of US3. Automated across models/managers/admin.

### Tests for User Story 3

- [ ] T025 [P] [US3] In `tests/parties/test_managers.py`, add `test_party_queryset_active_filters_inactive` and `test_party_queryset_inactive_is_complement` across Institution, ResearchGroup, Person.
- [ ] T026 [P] [US3] In `tests/parties/test_models.py`, add `test_delete_group_with_active_persons_raises_protected_error` — uses `pytest.raises(ProtectedError)`.
- [ ] T027 [P] [US3] In `tests/parties/test_models.py`, add `test_delete_group_with_only_inactive_persons_succeeds`.
- [ ] T027b [P] [US3] In `tests/parties/test_models.py`, add `test_deactivation_preserves_person_and_references` — create an Institution, ResearchGroup, and Person via factories; assign the Person as the group's PI; toggle `person.active=False` and `group.save()`. Assert: (a) the Person row still exists (`Person.objects.filter(pk=person.pk).exists()`), (b) the ResearchGroup's `pi_id` still references that Person (no auto-clear), (c) the Person appears in `Person.objects.inactive()` and is absent from `Person.objects.active()`, (d) the group's reverse relation `self.persons` still yields the Person when the queryset is unfiltered. Closes FR-014 + SC-003.
- [ ] T028 [P] [US3] In `tests/parties/test_models.py`, add `test_queryset_delete_also_honours_guard` — `ResearchGroup.objects.filter(...).delete()` raises when any group in the slice has active Persons.
- [ ] T029 [P] [US3] In `tests/parties/test_models.py`, add `test_person_research_group_is_immutable_on_save` — change `research_group_id` on an existing Person and call `full_clean()` → `ValidationError` on `research_group`.
- [ ] T030 [P] [US3] In `tests/parties/test_admin.py`, add `test_person_has_no_delete_permission` — assert `PersonAdmin.has_delete_permission(request, obj)` returns False both for a row and None.
- [ ] T031 [P] [US3] In `tests/parties/test_admin.py`, add `test_person_research_group_is_readonly_on_change_form` — render `PersonAdmin.get_readonly_fields(request, person)` and assert `"research_group"` is included; also assert empty on the add form.
- [ ] T032 [P] [US3] In `tests/parties/test_admin.py`, add `test_admin_fk_dropdowns_filter_to_active_only` — render the ResearchGroup add form and assert inactive Persons are not in the `pi` queryset; render Person add form and assert inactive Groups are not in the `research_group` queryset.
- [ ] T033 [P] [US3] In `tests/parties/test_admin.py`, add `test_pi_warning_shown_when_pi_inactive` — GET the ResearchGroup change view for a group whose PI is inactive; assert the warning string appears in the response body.

### Implementation for User Story 3

- [ ] T034 [US3] Add `delete()` override to `ResearchGroup` in `parties/models.py` (research R6): if `self.persons.filter(active=True).exists()`, raise `ProtectedError(...)`.
- [ ] T035 [US3] Add `delete()` override to `PartyQuerySet` in `parties/managers.py` for ResearchGroup use (research R6): iterate, raise on first violator.
- [ ] T036 [US3] Add `clean()` to `Person` in `parties/models.py` enforcing immutable `research_group` (research R8): single SELECT to fetch the DB value, raise `ValidationError({"research_group": ...})` on mismatch when `self.pk` is set.
- [ ] T037 [US3] In `PersonAdmin` (`parties/admin.py`), implement `has_delete_permission(self, request, obj=None) -> False`, and remove `delete_selected` from `actions` (research R7).
- [ ] T038 [US3] In `PersonAdmin`, implement `get_readonly_fields(self, request, obj=None)` returning `("research_group",)` when `obj is not None`, else `()` (research R8).
- [ ] T039 [US3] In `parties/admin.py`, implement `formfield_for_foreignkey` on `ResearchGroupAdmin` (filter `pi` queryset to `Person.objects.active()`) and on `PersonAdmin` (filter `research_group` queryset to `ResearchGroup.objects.active()` on the add form) (research R11).
- [ ] T040 [US3] In `ResearchGroupAdmin`, implement `pi_warning(self, obj)` method returning a short HTML-safe warning string when `obj.pi_id and not obj.pi.active`; add `"pi_warning"` to `readonly_fields` (research R12).
- [ ] T041 [US3] In all three admins, add `list_filter = ("active",)` and include the `active` column as a boolean-iconed field in `list_display` to satisfy FR-025 (operators can tell active from inactive at a glance).
- [ ] T042 [US3] In `PersonAdmin`, override `save_model(self, request, obj, form, change)` to emit `messages.WARNING` when another active Person in the same ResearchGroup shares the email (research R9; FR-010c). Include the duplicating Person's name in the message.
- [ ] T043 [P] [US3] In `tests/parties/test_admin.py`, add `test_duplicate_email_within_group_triggers_warning` (same-group duplicate → warning message present after save) and `test_duplicate_email_across_groups_is_silent` (cross-group duplicate → no warning).

**Checkpoint**: All US3 tests green. Manual spot-check: deactivate a PI, open group — warning appears.

---

## Phase 6: User Story 4 — Search and active members view (Priority: P3)

**Goal**: Admin search finds Persons by name/email substring and Groups by name; group change view shows active members.

**Independent Test**: Acceptance Scenarios 1–3 of US4. Automated via admin test client; SC-004 performance assertion with 10k Persons.

### Tests for User Story 4

- [ ] T044 [P] [US4] In `tests/parties/test_admin.py`, add `test_person_search_by_last_name_fragment`, `test_person_search_by_first_name_fragment`, and `test_person_search_by_email_fragment` — GET the Person changelist with `?q=` and assert matches. Verify case-insensitivity.
- [ ] T045 [P] [US4] In `tests/parties/test_admin.py`, add `test_research_group_search_by_name`.
- [ ] T046 [P] [US4] In `tests/parties/test_admin.py`, add `test_research_group_change_view_shows_only_active_members_by_default`.
- [ ] T047 [P] [US4] In `tests/parties/test_admin.py`, add `test_person_search_under_one_second_at_10k` (SC-004): batch-create 10 000 Persons via `PersonFactory.create_batch(...)` in a session-scoped fixture; assert a search returns within 1.0 s using `time.perf_counter`. Skip with `@pytest.mark.slow` so ordinary runs stay fast; include in CI full-suite runs.

### Implementation for User Story 4

- [ ] T048 [US4] In `PersonAdmin` (`parties/admin.py`), set `search_fields = ("first_name", "last_name", "email")`.
- [ ] T049 [US4] In `ResearchGroupAdmin`, set `search_fields = ("name",)`.
- [ ] T050 [US4] In `ResearchGroupAdmin`, add a `PersonInline` (TabularInline) listing active members: override `get_queryset` to apply `.active()`. Fields shown: first_name, last_name, email. Read-only — adding Persons still goes via the Person admin per FR-005a / US3.

**Checkpoint**: Search works in the admin; group page shows active members; 10k-perf test stays under 1 s locally.

---

## Phase 7: User Story 5 — Public api.py interface (Priority: P2)

**Goal**: Other modules read parties data via `parties/api.py` only; all 7 contract functions implemented and tested.

**Independent Test**: Acceptance Scenarios 1–2 of US5. Automated contract tests.

### Tests for User Story 5

- [ ] T051 [P] [US5] In `tests/parties/test_api.py`, add `test_get_institution_returns_instance_or_none` — returns the Institution for a valid id, returns `None` for a missing id, returns inactive Institutions too.
- [ ] T052 [P] [US5] In `tests/parties/test_api.py`, add `test_get_research_group_returns_instance_or_none` (same pattern, incl. inactive).
- [ ] T053 [P] [US5] In `tests/parties/test_api.py`, add `test_get_person_returns_instance_or_none` (same pattern, incl. inactive — historical-reference guarantee).
- [ ] T054 [P] [US5] In `tests/parties/test_api.py`, add `test_get_pi_returns_assigned_pi_or_none` (including the inactive-PI case, per contract).
- [ ] T055 [P] [US5] In `tests/parties/test_api.py`, add `test_list_active_members_excludes_inactive` — create a group with 2 active and 1 inactive Person; assert exactly 2 returned, ordered by `(last_name, first_name)`.
- [ ] T056 [P] [US5] In `tests/parties/test_api.py`, add `test_list_active_research_groups_excludes_inactive` and `test_list_active_institutions_excludes_inactive`.
- [ ] T057 [P] [US5] In `tests/parties/test_api.py`, add `test_api_is_the_only_public_surface` — scan `parties/api.py` via `ast` and assert every public symbol (no leading `_`) is one of the 7 documented contract functions (defensive test against accidental widening of the public surface).

### Implementation for User Story 5

- [ ] T058 [US5] Implement all 7 functions in `parties/api.py` per `contracts/parties-api.md`: `get_institution`, `get_research_group`, `get_person`, `get_pi`, `list_active_members`, `list_active_research_groups`, `list_active_institutions`. Each with type hints and a docstring citing the relevant FR.
- [ ] T059 [US5] Ensure the `parties/api.py` module has `__all__` listing exactly the 7 public names (enforces T057 at import time).

**Checkpoint**: `pytest tests/parties/test_api.py -v` green. Consumers in future apps can `from parties import api` and call any of the 7 functions.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, lint, perf sanity, manual SC validation.

- [ ] T060 [P] Run `uv run ruff check parties/ tests/parties/` and fix any warnings.
- [ ] T061 [P] Run `uv run ruff format parties/ tests/parties/`.
- [ ] T062 Run the whole parties test suite: `uv run pytest tests/parties/ -v` — all green, no warnings.
- [ ] T063 Manual run of `specs/001-parties-master-data/quickstart.md §2a` (SC-002): onboard a new external group end-to-end via admin; stopwatch the run; confirm <3 min.
- [ ] T064 Manual run of quickstart §1b (SC-001): delete `db.sqlite3`, run `python manage.py migrate`, open admin, confirm the internal lab + configured Persons are present without any manual action.
- [ ] T065 [P] Update `CLAUDE.md` "Actual Project Structure" block if the `parties/` tree ended up differing from the plan. Add any notable gotchas encountered during implementation.
- [ ] T066 Add a one-line note in `contracts/parties-api.md` "Change log" if any signature changed during implementation; otherwise leave at v1.
- [ ] T067 Sanity-check SC-007: grep the repo for `from parties.models` — the only hits should be within `parties/` itself, `tests/parties/`, and migration files. Anything else indicates a boundary violation in a later feature and must be refactored to go through `api.py`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: no prerequisites.
- **Phase 2 Foundational**: depends on Phase 1.
- **Phase 3 (US1)**: depends on Phase 2.
- **Phase 4 (US2)**: depends on Phase 2. Can run in parallel with Phase 3, 5, 6, 7.
- **Phase 5 (US3)**: depends on Phase 2. Can run in parallel with Phase 3, 4, 6, 7.
- **Phase 6 (US4)**: depends on Phase 2. Search is independent of the invariants; can run in parallel with Phase 3, 4, 5, 7.
- **Phase 7 (US5)**: depends on Phase 2. api.py surface is a read-only veneer and does not need US1/US3 business rules to be in place, so it can run in parallel — but consumers should wait for US1 and US3 before relying on semantic correctness.
- **Phase 8 Polish**: depends on all user-story phases that are in scope for the release.

### Within a user story

- Tests are written first (within the same phase). They MUST fail before their matching implementation task lands.
- Model changes (in `parties/models.py`) precede admin refinements that depend on them.
- Admin tasks touching the SAME file (`parties/admin.py`) are NOT parallelizable — keep them sequential (T018, T037, T038, T039, T040, T041, T042, T048, T049, T050 all edit the same file).
- Tests across DIFFERENT files ARE parallelizable — `test_models.py`, `test_managers.py`, `test_admin.py`, `test_api.py`, `test_seed.py`.

### Parallel opportunities

- **Phase 1**: T003 and T004 [P] while T001/T002 finish.
- **Phase 2**: After T005 (managers) lands, T006/T007/T008 [P] (three separate models) can be drafted together, though they all live in `parties/models.py` — one dev must serialize the edits into that single file; the [P] marker here means "independent content", not "truly concurrent file writes".
- **Phase 3–7**: Once Phase 2 is green, all four remaining stories can proceed in parallel across three developers. One works the `models.py` lane, one the `admin.py` lane, one the `api.py`+tests lane.
- **Within a story**: test tasks [P] across different test files can be written concurrently before the implementation lands.

### Parallel example: User Story 3 test sprint

```bash
# Five test authors can draft these five files in parallel; none touch models/admin yet:
Task: "T025 test_party_queryset_* in tests/parties/test_managers.py"
Task: "T026/T027/T028 delete-guard tests in tests/parties/test_models.py"
Task: "T029 immutable-FK test in tests/parties/test_models.py (same file as T026-28 — sequential within the file)"
Task: "T030/T031/T032/T033 admin guardrail tests in tests/parties/test_admin.py"
Task: "T043 email-warning tests in tests/parties/test_admin.py (same file — sequential)"
```

---

## Implementation Strategy

### MVP = User Story 1

1. Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1).
2. Stop. Validate: operator can onboard an external group in under 3 min; PI-must-be-member works.
3. Merge + ship.

### Incremental deliveries after MVP

- **Internal-lab convenience**: add Phase 4 (US2). Operators stop needing to hand-bootstrap internal data.
- **History hardening**: add Phase 5 (US3). Now the data is safe against accidental destruction / rewrites.
- **Public surface**: add Phase 7 (US5). Unblocks the next spec (projects app) to consume parties.
- **Search**: add Phase 6 (US4). Last because benefits scale with data volume.
- **Polish**: Phase 8 after the final shipped story.

### Parallel-team strategy

After Phase 2 lands, three developers can take US1+US5 (MVP + consumer surface), US3 (history hardening), and US2+US4+polish (seed + search) respectively. Code conflicts are confined to `parties/models.py` and `parties/admin.py` and are serialized via short PRs.

---

## Notes

- `[P]` = touches a different file / has no dep on an incomplete sibling task.
- Tests first within each story; do not mark an implementation task complete while its matching test is still red.
- Commit after each task or tight logical group; fast PRs keep admin.py conflicts tiny.
- Every task has an absolute file path so that an agent executor can work without additional context.
- Avoid: introducing DRF / HTMX / task queues (YAGNI per constitution §V); relaxing the module boundary (constitution §IV.2); turning the advisory email warning into a hard rejection (spec FR-010c).
