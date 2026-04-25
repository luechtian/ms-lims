# Workflow: Teach a Single Task (core per-task loop)

<required_reading>
**Read these reference files NOW:**
1. `references/pedagogy.md` — adaptive depth, Socratic style, comprehension checks.
2. `references/code-review-checklist.md` — what to look for when reviewing the user's code.
3. `references/session-state.md` — how to update the scratchpad.

**Read these on demand (only the ones this task touches):**
- `references/django-concepts.md` — Django idioms index.
- `references/python-concepts.md` — Python idioms index.
- `references/project-context.md` — how to cite project rules.
</required_reading>

<process>
## Step 1: Read the task in full

Open `specs/<feature>/tasks.md` and re-read the task text for the current T0XX. Note:
- Phase and user story (context).
- File paths mentioned (where the user will type).
- Any explicit references like "(research R4)" or "(data-model §Institution)" — **follow those breadcrumbs** before briefing. They carry the reasoning the spec author wanted the implementer to understand.

Also open the files the task names (read-only) to see current state.

## Step 2: Identify the concepts in play

List the Django + Python concepts the user will need to produce this code. Examples:
- Manager vs QuerySet (`as_manager()`, chainable queryset methods).
- `UniqueConstraint(Lower(...))` for case-insensitive uniqueness.
- `on_delete=PROTECT` vs `SET_NULL` vs `CASCADE` semantics.
- `Model.clean()` vs `Model.save()` validation layering.
- factory-boy `DjangoModelFactory` and `SubFactory`.
- pytest fixtures and the `db` fixture from pytest-django.

Cross-check each concept against the `.learning-state.md` "concepts covered" list.
- **Not covered yet** → deep dive in Step 3.
- **Already covered** → one-line reminder only.

## Step 3: Deliver the briefing

First decide the tier (see `templates/task-briefing.md`):

- **Teaching-Tier** — task introduces ≥1 new concept, opens a new file, or crosses into a new kind of change.
- **Apply-Tier** — task only reuses already-covered concepts.

When uncertain, ask the user. Both tiers require the `**Umfang:** ~N Min · …` header at the top so the user can early-exit before typing.

**Teaching-Tier sections** (fixed order): Thema · Hintergrund · Nötiges Wissen · Konzepte · Beispiel · Aufgabe · Ich prüfe. Mental model before Aufgabe, always. Deep-dive NEW concepts only (Mental Model · Projekt-Anker · Fallstrick). Known concepts get a one-line reminder in Nötiges Wissen.

**Apply-Tier sections**: Aufgabe (3–5 lines) · Review-Fokus (1 line). No concept deep dives — if you catch yourself writing one, you're in the wrong tier.

Cite project rules (CLAUDE.md / constitution / plan / research) inline, not as a separate block.

End with a single line: `Ping mich, wenn der Code steht.`

**Exploration block:** If the task introduces a new Model, relation, or custom QuerySet method, append the optional `### Erkunden` section from `templates/task-briefing.md`. Use `uv run python manage.py shell` (IPython). Include 2–4 shell lines with expected output as comments. Skip for test-only, migration-only, or config tasks.

## Step 4: Wait for the handoff signal

Do not chase. The user writes in silence. They will come back with one of:
- "Done, review please." → Step 5.
- "Stuck on X." → answer the specific question, then return here; don't volunteer the solution unless they ask for it directly.
- "Just write it." → confirm once ("This steps out of learning mode for this task — still want me to?"), then if confirmed, write the code yourself, teach line-by-line as you go, and note in the scratchpad that this task was Claude-written.

## Step 5: Review

Read the files the user changed. Use `templates/review-report.md` as the structure and `references/code-review-checklist.md` as the lens. The review has four sections:

1. **Works** — one line confirming the happy path runs (or, if it doesn't, state that first and stop reviewing until it does).
2. **Project-convention hits** — lines where the user nailed a project rule. Be specific; a concrete compliment teaches.
3. **Idiomatic improvements** — up to three suggestions, ordered by leverage. Cite the convention or PEP being missed; show the before/after snippet; never touch the file. For each, state whether it's blocking (must fix to tick the task) or optional (worth learning but not required now).
4. **Tests** — did the associated test task get written and does it run? If tests are the next numbered task, flag that instead.

Keep the whole review under ~40 lines. A wall of feedback overwhelms juniors.

## Step 6: Comprehension check

Ask exactly **one** targeted question about the _why_, not the _what_. Good examples:
- "Why did we use `on_delete=PROTECT` for Person.research_group instead of CASCADE?"
- "Why does this constraint live in `Meta.constraints` instead of `unique=True` on the field?"
- "Why is `clean()` the right place for the PI-must-be-member check, not `save()`?"

Listen. If the answer is shaky, offer a 2–3 line corrective and note the concept as "needs revisit" in the scratchpad. If the user hand-waves ("let's move on"), accept it but note "skipped check — T0XX" in the scratchpad. Patterns matter.

## Step 7: Tick and update state

Propose ticking the task's checkbox in `tasks.md`. On the user's OK, delegate **both** file writes to a background agent so they don't bloat the main chat context:

```
Agent(
  description: "Tick T0XX and update learning-state",
  run_in_background: true,
  prompt: "Edit specs/<feature>/tasks.md: change the checkbox on the line for T0XX from `- [ ]` to `- [x]`. Do not touch any other lines.

  Then update specs/<feature>/.learning-state.md:
  - Add T0XX to the 'Completed this session' list.
  - Append these newly covered concepts: <list>.
  - Append these review notes: <notes, or 'none'>.

  Read both files first, then apply the minimal edits."
)
```

Confirm to the user that the state update is running in the background and continue immediately to Step 8.

## Step 8: Offer the next step

Three options:
- **Continue** to the next `[ ]` task → loop back to Step 1 of this workflow for the new T0XX.
- **Pause** — summarise what's been covered this session in 3 lines, remind the user how to resume (`/guided-implement <slug>`), stop.
- **Phase recap** — if the next task crosses a phase boundary in tasks.md, proactively suggest `workflows/phase-recap.md`.
</process>

<success_criteria>
This workflow is complete when:
- [ ] Task text and its breadcrumbs (research/plan/data-model refs) have been read.
- [ ] Briefing delivered using the template, with adaptive depth.
- [ ] User has written the code themselves and signalled completion.
- [ ] Review delivered in the four-section format.
- [ ] One comprehension question has been asked and answered (or explicitly waived).
- [ ] Task checkbox ticked in `tasks.md` with user consent.
- [ ] Scratchpad updated with task ID, new concepts, and any review notes.
- [ ] Next step proposed (continue / pause / recap).
</success_criteria>
