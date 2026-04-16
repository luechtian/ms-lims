# Feature Specification: Parties Master Data

**Feature Branch**: `001-parties-master-data`
**Created**: 2026-04-16
**Status**: Draft
**Input**: User description: "Model the parties app — master-data management for Institutions, ResearchGroups and Persons. The parties app provides the stable axis for every sample supplier in the LIMS (external customers / collaborators as well as the internal lab)."

## Clarifications

### Session 2026-04-16

- Q: What uniqueness constraint should apply to Institution names and ResearchGroup names? → A: Institution name unique globally; ResearchGroup name unique within its Institution, and globally unique when no Institution is set.
- Q: Can an inactive Person or ResearchGroup be reactivated? → A: Yes — the active flag is a simple toggle (deactivation is not terminal). Returning personnel flip the flag back; history and references are preserved by the unchanged record identity.
- Q: After creation, can a Person's ResearchGroup be changed in place? → A: No — the `research_group` reference is immutable. Moving a Person to a different group is always modelled by deactivating the old Person record and creating a new Person in the target group. All other Person fields (name, email, active flag) remain editable.
- Q: What is the authoritative relationship between `Person.role` and `ResearchGroup.pi`? → A: `ResearchGroup.pi` is the single source of truth. `Person.role` is removed from the data model entirely; PI status is derived per group (the Person referenced by `group.pi` is the PI of that group; everyone else in the group is a Member). This eliminates the dual-source-of-truth invariant and collapses to one canonical record of PI-hood.
- Q: When does the internal-lab seed mechanism actually run? → A: Automatically, as part of the standard database-setup step that ships with the app (the same step an operator runs once to create the schema). No second command required. Idempotency (FR-017) makes re-running the setup step safe.
- Q: Is `Person.research_group` required, or may a Person exist without a group? → A: Required — every Person MUST belong to a ResearchGroup. Lone contributors (freelance researchers, ad-hoc contacts) are modelled by creating a small one-person ResearchGroup (Institution optional, the single Person is also the group's PI). This keeps the sample-supply chain uniform and removes the "ungrouped Person" code path from every downstream query.
- Q: What is the scope of the advisory email-duplicate warning? → A: Warn only on duplicate email **within the same ResearchGroup**. Cross-group duplicates are silently accepted (shared institutional mailboxes like `lab@heidelberg.de`, and the deactivate-old-create-new pattern for group transfers, make cross-group duplicates legitimate). No hard rejection in any case.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Onboard an external research group as sample supplier (Priority: P1)

An operator receives a first inquiry from a new external research group. Before any sample batch can be accepted, the supplier chain (optional institution → research group → first person → principal investigator) must be recorded so that subsequent sample intakes can reference a stable, identifiable supplier.

**Why this priority**: This is the core reason the parties app exists. Without being able to register an external supplier, no external project or sample intake can be created. Ship this slice and the LIMS can already accept external work, even without any of the other stories.

**Independent Test**: An operator opens the administrative interface, creates (or reuses) an Institution, creates a ResearchGroup under it, adds the first Person to that group, then promotes that Person to be the group's Principal Investigator. The finished chain is visible in the group detail view and can be referenced from other modules.

**Acceptance Scenarios**:

1. **Given** no existing entries, **When** the operator creates an Institution "University of Heidelberg" with a free-text address and an optional website, **Then** the Institution appears in the list of institutions and can be referenced by one or more ResearchGroups.
2. **Given** an Institution exists, **When** the operator creates a ResearchGroup "AG Müller" pointing at that Institution but without a Principal Investigator yet, **Then** the ResearchGroup is saved as active with no PI yet, and this is not treated as an error.
3. **Given** a ResearchGroup exists without members, **When** the operator adds a new Person with first name, last name, email and the ResearchGroup assignment, **Then** the Person appears under that group as a Member (no role field is required at creation).
4. **Given** a ResearchGroup has at least one Person, **When** the operator assigns that Person as the group's Principal Investigator, **Then** the assignment is accepted and the group is now fully linked.
5. **Given** a ResearchGroup has no members, **When** the operator tries to assign a Principal Investigator who belongs to a different group, **Then** the action is rejected with a clear message that the PI must be a member of the group.
6. **Given** an operator wants to register a freelance customer, **When** they create a ResearchGroup without an Institution, **Then** the ResearchGroup is created successfully (Institution is optional context, not a hard dependency).

---

### User Story 2 - Have the internal lab available on first start (Priority: P2)

On a fresh LIMS installation, internal measurements must be possible immediately. This requires a pre-existing ResearchGroup that represents the lab itself, populated with the lab's own team members.

**Why this priority**: This is a precondition for every internal measurement and removes a setup step that every operator would otherwise have to do manually. It is P2 because if it is missing, the operator can still create the internal lab manually using the functionality shipped with User Story 1 — the experience is worse but not blocked.

**Independent Test**: On a fresh database, an operator opens the parties administrative interface and immediately sees a ResearchGroup named for the internal lab with its team members already present and marked active, without having entered anything manually.

**Acceptance Scenarios**:

1. **Given** a newly initialised database, **When** the operator opens the ResearchGroups list, **Then** exactly one ResearchGroup representing the internal lab is already present.
2. **Given** the internal lab ResearchGroup is present, **When** the operator opens its detail view, **Then** the configured internal team members are listed as active Persons.
3. **Given** the seed data has already been applied once, **When** the seeding mechanism runs again (e.g. during deployment), **Then** no duplicate entries are created and existing data is not overwritten.

---

### User Story 3 - Preserve history when people leave or the group's PI changes (Priority: P2)

Personnel inside a research group changes — members come and go, and eventually the Principal Investigator changes too. When someone leaves, their record must remain in the database because existing sample intakes and projects reference them. However, they must not clutter dropdowns for new assignments.

**Why this priority**: Historical integrity is essential for scientific traceability, but the feature only becomes load-bearing once the system has been in use for some months. It is not a day-one blocker.

**Independent Test**: An operator marks an existing Person as inactive. The Person is still retrievable via detail view and list filter "inactive", but no longer appears in the default dropdowns used to select people for new records. A replacement Person is added to the same group.

**Acceptance Scenarios**:

1. **Given** an active Person in a group, **When** the operator sets the Person to inactive, **Then** the Person record remains in the database with all associated history.
2. **Given** a Person is inactive, **When** any other part of the system lists selectable Persons for a new assignment, **Then** the inactive Person is excluded by default.
3. **Given** an inactive Person still exists, **When** the operator explicitly searches for inactive Persons or opens the Person's detail view, **Then** the record is fully visible and readable.
4. **Given** a ResearchGroup still has at least one active Person, **When** the operator attempts to delete the ResearchGroup, **Then** deletion is prevented with a clear message.
5. **Given** the outgoing Person was the group's Principal Investigator, **When** they are set to inactive, **Then** the operator is alerted that the group's PI slot now points at an inactive Person and should be reassigned.

---

### User Story 4 - Find people and see who currently works where (Priority: P3)

An operator needs to find a Person by partial name or email, find a ResearchGroup by name, and quickly see who is currently active inside a given group.

**Why this priority**: This is a quality-of-life story. Without it the data is still correct and usable, but navigation is slower. It becomes important once the number of parties grows past a handful.

**Independent Test**: With a populated database, the operator types a partial name or email into the search field and sees matching active Persons. Opening a ResearchGroup shows only its currently active members by default.

**Acceptance Scenarios**:

1. **Given** multiple Persons exist, **When** the operator searches by part of a last name, **Then** matching active Persons are listed; inactive Persons are included only when an explicit filter is set.
2. **Given** multiple Persons share a last name, **When** the operator searches by email fragment, **Then** the correct Person is found.
3. **Given** a ResearchGroup with a mix of active and inactive Persons, **When** the operator opens the group, **Then** the default view lists only the active members.

---

### User Story 5 - Safely expose parties to other apps (Priority: P2)

Other modules of the LIMS (projects, samples, sample intakes, later reporting) need to reference Institutions, ResearchGroups and Persons without reaching into this app's internals. A stable, documented public interface is required so the rest of the system can evolve without breaking.

**Why this priority**: Without this, module boundaries collapse on first cross-module work. It is P2 because no other module exists yet in code — but the interface must exist before projects/samples work begins.

**Independent Test**: A reviewer reads the parties module and finds a single, documented public interface file that exposes exactly the read and lookup operations other modules need; a repository-wide check shows no other module importing from the parties internal models.

**Acceptance Scenarios**:

1. **Given** the parties module is shipped, **When** another module needs a Person, ResearchGroup, or Institution reference, **Then** it can obtain it via the documented public module interface only.
2. **Given** a developer tries to import directly from the parties internal model file from another module, **When** code review or a lint check runs, **Then** the violation is flagged.

---

### Edge Cases

- **Group without Institution**: Freelance / independent customers must be storable as a ResearchGroup with no Institution. This is an expected case, not an error.
- **Group without a PI yet**: When a new external group is being onboarded, the group may legally exist before its first Person and therefore before its PI is known. The system must allow a group in this intermediate state and must not break if a PI slot is empty.
- **PI assignment must be a member of the group**: Assigning a Person from a different group as PI is invalid.
- **Deactivating the current PI**: The group's PI slot then points at an inactive Person. The system surfaces this condition but does not auto-clear the slot (historical reference must survive).
- **Deactivating a ResearchGroup**: A ResearchGroup can be set to inactive. All its Persons remain as they are; the group is hidden from dropdowns for new associations but stays available via history lookups.
- **Deleting a ResearchGroup**: Prevented if the group has any active Persons. Deleting a group whose Persons are all inactive is allowed only if no external references (projects, sample intakes) depend on it — out of scope for this spec but must not be silently bypassed.
- **Deleting a Person**: Prevented outright once the Person is (or could be) referenced by other modules. Within this spec, direct deletion from the admin is disabled; deactivation is the substitute action.
- **Re-seeding on an existing database**: The internal-lab seed mechanism is idempotent. It does not duplicate existing entries and does not overwrite user edits.
- **Duplicate emails across Persons**: Within the same ResearchGroup, two Persons with identical emails are flagged (advisory warning, not hard rejection) because this is almost always a data-entry mistake. Across different ResearchGroups, duplicate emails are accepted silently — shared institutional mailboxes and the deactivate-old-create-new pattern for group transfers make cross-group duplicates legitimate.
- **PI is a property of the group, not the Person**: There is no role field on Person. A Person is displayed as "PI of {group}" exactly when `group.pi` references them; everyone else in the group is displayed as "Member". Career level (postdoc, PhD, technician, master student, etc.) is intentionally not stored. Per-project responsibility ("who handled this sample set?") is modelled elsewhere, not on Person.

## Requirements *(mandatory)*

### Functional Requirements

**Entities and fields**

- **FR-001**: The system MUST allow creating, reading, updating and deactivating Institutions with a name, a free-text address and an optional web URL.
- **FR-002**: The system MUST allow creating, reading, updating and deactivating ResearchGroups with a name and an optional Institution reference.
- **FR-003**: The system MUST allow creating, reading, updating and deactivating Persons with first name, last name, email and exactly one ResearchGroup reference. After creation, every Person field MUST be editable EXCEPT the `research_group` reference, which is immutable (see FR-005a).
- **FR-004**: The system MUST NOT store a role attribute on Person. PI status is a property of a ResearchGroup (via `ResearchGroup.pi`), not of a Person. In any display context, the Person referenced by `group.pi` is shown as "PI of {group}"; every other active Person in the group is shown as "Member". Finer-grained career distinctions (postdoc / PhD / technician / master student / etc.) are deliberately not modelled — what matters operationally is whether a Person is the group's PI or a regular member. Downstream per-project responsibility (e.g. "who is responsible for this sample set?") is a separate concern of later modules.

**Relationships and integrity**

- **FR-005**: Each Person MUST belong to exactly one ResearchGroup. The `research_group` reference MUST NOT be nullable. Lone contributors (freelance researchers, ad-hoc contacts who cannot be attached to an existing organisational group) are modelled by creating a one-person ResearchGroup for them (Institution optional; the single Person is assigned as that group's PI).
- **FR-005a**: The `research_group` reference on a Person MUST be immutable after creation. The administrative interface MUST NOT offer an edit control for this field on an existing Person. A Person who changes group MUST be handled by deactivating the existing record and creating a new Person in the target group; the two records are independent by design.
- **FR-006**: Each ResearchGroup MUST be allowed to exist without an Institution (Institution is optional context).
- **FR-007**: Each ResearchGroup MUST be allowed to have an optional Principal Investigator, expressed as a reference to a Person.
- **FR-008**: When a Principal Investigator is assigned to a ResearchGroup, the referenced Person MUST already be a member of that same ResearchGroup. Otherwise the assignment MUST be rejected with a message that names this rule.
- **FR-009**: A ResearchGroup that currently has one or more active Persons MUST NOT be deletable. Deletion MUST be rejected with a message naming the reason.
- **FR-010**: Persons MUST NOT be deletable through the administrative interface. Deactivation is the substitute action. (Rationale: Persons will be referenced by downstream modules — projects, sample intakes — and must survive as historical references.)
- **FR-010a**: Institution names MUST be unique across the whole database (case-insensitive comparison). Attempting to create a second Institution with the same name MUST be rejected with a clear message.
- **FR-010b**: ResearchGroup names MUST be unique within the scope of their Institution (case-insensitive comparison). ResearchGroups with no Institution MUST have a name that is unique across all other ResearchGroups with no Institution. A name collision MUST be rejected with a clear message that names the scope.
- **FR-010c**: Person emails MUST NOT be hard-rejected as duplicates. When the operator enters a Person whose email matches another Person **in the same ResearchGroup**, the system MUST display an advisory warning (likely data-entry mistake) but MUST still allow the save. Duplicate emails across different ResearchGroups MUST be accepted silently, with no warning.

**Activity state**

- **FR-011**: Both Persons and ResearchGroups MUST have an explicit active / inactive state; the default on creation is active. The state is a reversible toggle — deactivation is NOT a terminal operation, and an inactive Person or ResearchGroup MAY be set back to active at any time, preserving the same record identity and all references.
- **FR-012**: Inactive Persons MUST be hidden from every default selection control offered for new associations (dropdowns, autocomplete lists). They MUST remain visible through explicit filters and direct detail lookup.
- **FR-013**: Inactive ResearchGroups MUST be hidden from every default selection control offered for new associations. They MUST remain visible through explicit filters and direct detail lookup.
- **FR-014**: Deactivating a Person MUST preserve all existing references and relationships to that Person.
- **FR-015**: When the Principal Investigator of a ResearchGroup is deactivated, the system MUST surface the resulting inconsistency (e.g. warning in the group detail view) but MUST NOT auto-clear the PI reference.

**Seed data for internal lab**

- **FR-016**: The system MUST seed a pre-populated ResearchGroup representing the internal lab (with the lab's configured team members as active Persons and the configured PI assigned) as an automatic part of the standard database-setup step that an operator already runs once to create the schema. No separate command or extra operator action is required. On a fresh database this produces the seeded internal lab on the operator's first interaction with the app.
- **FR-017**: The seeding operation MUST be idempotent: re-running it against a database that already contains the seeded internal lab MUST NOT create duplicates and MUST NOT overwrite subsequent user edits.
- **FR-018**: The identity and membership of the internal lab (group name, list of Persons with their name / email, and which Person is the group's PI) MUST be configurable per deployment (i.e. not hard-coded in model code), so that each lab can tailor its own seed.

**Discovery and search**

- **FR-019**: Users MUST be able to search Persons by any substring of last name, first name or email, case-insensitive.
- **FR-020**: Users MUST be able to search ResearchGroups by any substring of the group name, case-insensitive.
- **FR-021**: For a given ResearchGroup, users MUST be able to retrieve its currently active members as a distinct view (the answer to "who is currently in AG Müller?").

**Public module interface and module boundary**

- **FR-022**: The parties module MUST expose a single, documented public interface entry point for use by other modules. This entry point MUST cover at minimum: lookup of an Institution, ResearchGroup or Person by identifier; resolving the Principal Investigator of a ResearchGroup; listing active members of a ResearchGroup.
- **FR-023**: Other modules MUST NOT reach into the parties module's internal model layer directly; access MUST go through the public interface. (This mirrors the Modularity Hard Rules of the project constitution.)

**Administrative UI**

- **FR-024**: A usable administrative interface MUST exist for v1 that allows operators to exercise every functional requirement above without writing code. No custom UI beyond the administrative interface is required for this spec.
- **FR-025**: From the Person list, operators MUST be able to tell active Persons apart from inactive Persons at a glance (e.g. via a visible indicator or filter state).

**Quality and verification**

- **FR-026**: Every functional requirement above MUST be covered by at least one automated test, including the guard rules (PI-must-be-member, cannot-delete-group-with-active-Persons, inactive-Persons-excluded-from-dropdowns, seed-idempotency, boundary between the parties public interface and its internals).

### Key Entities *(include if feature involves data)*

- **Institution**: Optional contextual parent for a ResearchGroup. Represents a university, company, clinic etc. Attributes: name (mandatory), address (free text), website (optional). Participates in no hard business rule — it is organisational context.
- **ResearchGroup**: The stable axis of the parties model. Represents a laboratory, working group, or customer firm. Attributes: name (mandatory), optional Institution, optional Principal Investigator reference (must be a member), active / inactive state. Persists across personnel turnover; the internal lab is modelled as one of these.
- **Person**: An individual belonging to exactly one ResearchGroup. Attributes: first name, last name, email, ResearchGroup (immutable after creation), active / inactive state. No role attribute — PI-hood is expressed on the ResearchGroup via `ResearchGroup.pi`, not on the Person. Career level (postdoc, PhD, technician, master student, etc.) is not tracked. Persons turn over more frequently than the group.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a fresh installation the internal lab and its seeded team members are present and usable without any manual action by the operator. Verified by: opening the administrative interface right after install and seeing the internal lab with its configured members.
- **SC-002**: An operator can record a completely new external supplier chain (Institution → ResearchGroup → first Person → PI assignment) in under 3 minutes, starting from an empty state and using only the administrative interface.
- **SC-003**: Deactivating a Person who is referenced anywhere in the system never destroys the reference; the Person can always be re-found via an explicit inactive filter in the same screen where they would normally appear.
- **SC-004**: A search by any substring of a Person's last name, first name or email returns that Person within one second for databases up to 10,000 Persons, and only surfaces active Persons by default.
- **SC-005**: Attempting to delete a ResearchGroup that has active Persons is rejected 100% of the time and produces a message that names the reason without requiring the operator to read logs or documentation.
- **SC-006**: Assigning a Person who does not belong to a given ResearchGroup as that group's PI is rejected 100% of the time and produces a message that names the rule.
- **SC-007**: A code review of any second module (e.g. the future projects module) confirms that it references Institutions, ResearchGroups and Persons exclusively through the public interface and not via internal model imports.
- **SC-008**: The first-start seed mechanism is idempotent: running it twice against the same database produces the same visible state as running it once, with no duplicates and no lost user edits.

## Assumptions

- **Fixed technology stack**: This spec is written for the project's constitutional stack (Python 3.13, Django 6.0, SQLite, pytest, administrative interface provided by the framework). The term "administrative interface" throughout this spec refers to that framework-provided UI, which is the designated v1 UI for parties.
- **Internal-lab seed content is operator-configurable**: The identity of the internal lab (its name), its initial team members (first name, last name, email), and which of those members is the group's PI are provided via a per-deployment configuration (e.g. a fixture, settings value, or environment-driven data file). The deployed default in source control can be a minimal placeholder; each operator adjusts it before first start.
- **Address is free-text**: No structured address parsing, validation, postal-code rules or geocoding. A single multi-line text field suffices for v1.
- **Persons are master data, not user accounts**: Authentication, login, permissions, and user-account features are explicitly out of scope for parties. The administrative interface's own authentication is sufficient for v1.
- **Email uniqueness is advisory and scoped per group**: The system warns on duplicate emails within the same ResearchGroup (likely data-entry mistake), accepts duplicates across different ResearchGroups silently (shared institutional mailboxes, historical records for people who changed groups), and never hard-rejects on email.
- **Person-to-group relationship is immutable**: A Person belongs to exactly one ResearchGroup for their whole lifetime in the system. Moving a Person between groups is modelled by deactivating the old Person record and creating a new Person record in the target group — not by editing the group reference. This preserves historical integrity of existing references.
- **Out of scope for this spec** (tracked for later specs, named here so planning knows not to size for them):
  - Any link to Projects or SampleIntakes (Projects module does not yet exist).
  - Any custom UI outside the administrative interface.
  - Bulk import of Persons from external sources (CSV, LDAP, etc.).
  - Email sending, invitation flows, notification features.
  - Structured address fields or address validation.
  - Authentication, login, or user-account features for Persons.
