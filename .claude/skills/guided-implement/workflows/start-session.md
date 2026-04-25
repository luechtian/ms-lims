# Workflow: Start or Resume a Guided Implementation Session

<required_reading>
**Read these reference files NOW:**
1. `references/project-context.md` — how to anchor teaching in this project's docs.
2. `references/session-state.md` — the `.learning-state.md` scratchpad format.
3. `references/pedagogy.md` — adaptive depth + comprehension-check rules.
</required_reading>

<process>
## Step 1: Confirm which feature

If the invocation included a slug (e.g. `001-parties-master-data`), echo it back and confirm. Otherwise list every directory under `specs/` matching `NNN-*` and ask which one.

```
Glob: specs/*/tasks.md
```

Reject features that have no `tasks.md` — the spec isn't ready for implementation yet. Tell the user to run the speckit tasks step first.

## Step 2: Load the canonical project anchors

Read these four, in order, so you can cite them later:

1. `CLAUDE.md` (repo root) — already loaded into your context. Re-skim for rules that touch this feature.
2. `.specify/memory/constitution.md` — binding project-wide rules.
3. `specs/<feature>/plan.md` — architectural decisions for this feature.
4. `specs/<feature>/spec.md` — functional requirements (FR-*) and acceptance scenarios.

Skim, don't dump. You're building a mental index of "if the user hits X, it's decided in Y".

## Step 3: Load or initialise the learning scratchpad

Check whether `specs/<feature>/.learning-state.md` exists.

**If missing:** Delegate creation to a background agent so the write doesn't pollute context:

```
Agent(
  description: "Init learning-state for <feature>",
  run_in_background: true,
  prompt: "Copy templates/learning-state.md from the guided-implement skill (.claude/skills/guided-implement/templates/learning-state.md) into specs/<feature>/.learning-state.md. Fill in the feature slug and today's date. Leave every other section empty."
)
```

Then continue to Step 4 immediately — you don't need the file to be written before orienting the user.

**If present:** Read it. It tells you:
- Which tasks are already done in this session (ignore; tasks.md is the source of truth for done-ness).
- Which concepts have been covered — **this drives adaptive depth.** Do not re-teach concepts listed here unless the user asks.
- Prior review notes and user-flagged "remember this" items.

## Step 4: Reconcile tasks.md with scratchpad

Read `specs/<feature>/tasks.md` and find the first task whose checkbox is `[ ]`. That's the next task.

If a task is checked `[x]` but not recorded in the scratchpad's "completed" list, briefly ask the user: "I see T00X is already ticked — did we cover it together, or did you do it solo and want a retrospective review?"
- If solo: offer to route to `workflows/teach-task.md` in review-only mode (start at the Review step).
- If they just want to skip ahead: add it to the completed list, no fuss.

## Step 5: Orient the user

Output a short orientation. Keep it under 15 lines. Structure:

```
You're on feature: <slug> — <feature name from spec.md>.
Current phase: <Phase N: name from tasks.md>.
Next task: T0XX — <one-sentence description>.
Concepts the scratchpad says we've already covered: <list, or "none yet">.
Recent review notes to keep in mind: <list, or "none">.

Ready to start T0XX? (yes / skip / look at a different task / just ask me something first)
```

## Step 6: Hand off

On "yes" → load `workflows/teach-task.md` and follow it for T0XX.
On "skip" → mark the current task with a note in the scratchpad ("skipped by user on <date>") and advance to the next `[ ]` task.
On "different task" → ask which one, validate it exists, jump there.
On "just ask me something first" → load `workflows/concept-lookup.md`.
</process>

<success_criteria>
This workflow is complete when:
- [ ] A feature slug is confirmed and its `tasks.md` / `.learning-state.md` are both located.
- [ ] Project anchors (CLAUDE.md, constitution, plan, spec) have been skimmed.
- [ ] The next `[ ]` task is identified.
- [ ] The user has been oriented in ≤15 lines.
- [ ] Control has been handed off to the appropriate next workflow.
</success_criteria>
