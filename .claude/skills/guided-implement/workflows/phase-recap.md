# Workflow: Phase Recap

<required_reading>
**Read these reference files NOW:**
1. `references/pedagogy.md` — consolidation and spaced-repetition rules.
2. `references/session-state.md` — how the scratchpad records what was covered.
</required_reading>

<process>
## Step 1: Identify the phase that just closed

Open `specs/<feature>/tasks.md`. Find the phase heading (e.g. `## Phase 2: Foundational`) whose tasks are all `[x]`. That's the one to recap. If more than one phase has closed since the last recap, offer to recap each in turn.

## Step 2: Rebuild the phase's arc from the scratchpad + tasks.md

From `specs/<feature>/.learning-state.md` and `tasks.md`, assemble:
- Which concepts were introduced during this phase.
- Which project rules came up (cite CLAUDE.md / constitution lines).
- Any "needs revisit" notes from comprehension checks in this phase.
- The checkpoint line at the end of the phase (`**Checkpoint**: ...`) — that's the success statement the phase promised.

## Step 3: Deliver the recap

Structure (keep it under ~30 lines):

1. **What we built** — 2–3 bullets naming the artefacts now existing (app scaffolded, three models migrated, factories in place, etc.).
2. **Concepts you met** — list with a one-line "why it matters in this codebase" for each.
3. **Project rules that landed** — citations, not re-explanations. The user should now know where these rules live, not just what they say.
4. **Loose ends** — anything flagged as "needs revisit" during the phase. Do not let these roll over silently.

## Step 4: Consolidation check

Ask 2–3 short questions that span the phase, not single-task trivia. Good examples for the Foundational phase of parties:
- "Where does a manager live in this project, and why not in models.py?"
- "What's the difference between `Meta.constraints` and putting `unique=True` on the field, and which does this project default to?"
- "Person's `research_group` uses `on_delete=PROTECT`. What operation does that forbid, and what error would you see?"

Keep it a conversation. If answers are solid, tick the phase mentally and move on. If any are shaky, offer a short corrective and append "revisit in phase N+1 briefings" to the scratchpad.

## Step 5: Stage the next phase

Read the opening of the next phase in tasks.md. Summarise in ~3 lines what's coming and what new concepts the user should brace for. This is a preview, not a briefing — full briefing happens in `workflows/teach-task.md` when the user starts the next task.

Offer: "Ready for the first task of Phase N+1, or pause here?"
</process>

<success_criteria>
This workflow is complete when:
- [ ] The closed phase has been identified from tasks.md.
- [ ] Recap delivered in the four-section structure.
- [ ] 2–3 consolidation questions asked and discussed.
- [ ] Any shaky answers noted as "revisit" in the scratchpad.
- [ ] Next phase previewed in ≤3 lines.
- [ ] User directed either to the next task or a pause.
</success_criteria>
