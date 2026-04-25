# Workflow: Concept Lookup (on-demand deep dive)

<required_reading>
**Read these reference files NOW:**
1. `references/pedagogy.md` — explanation depth and the "project-specific callout" rule.
2. Whichever of `references/django-concepts.md` / `references/python-concepts.md` is relevant to the concept.
</required_reading>

<process>
## Step 1: Pin down what the user is actually asking

A bare "teach me managers" is ambiguous. Before explaining, clarify with one question if needed:
- Scope — "Do you want the Django Manager pattern in general, or specifically how this project uses it in `parties/managers.py`?"
- Depth — "One-paragraph mental model, or the full 'why does this exist / when do I reach for it / common pitfalls' walkthrough?"

If the user says "just explain it", pick: one-paragraph mental model + one project-specific example + one pitfall. That's almost always right.

## Step 2: Deliver the explanation

Structure:

1. **Mental model (1 paragraph)** — what the concept _is_ in plain language. No jargon the user hasn't already met this session.
2. **Idiomatic example (≤10 lines of code)** — prefer an example pulled from this codebase if one exists (you can Read `parties/` or any app to find a real usage). Second-best: a canonical Django/Python example.
3. **Project-specific callout** — where this concept lives in ms-lims, or which CLAUDE.md / constitution rule governs its use here. Concrete file paths beat abstract advice.
4. **When NOT to reach for it** — common beginner trap. One line.
5. **Pointer** — if the user wants more, name the authoritative source (Django docs page, PEP number, or this project's reference file). Do not paste the docs.

Total length: aim for ≤25 lines. If the concept genuinely needs more, offer "want me to go deeper on <sub-topic>?" — don't dump.

## Step 3: Record that the concept was taught

If a session scratchpad exists (look for `specs/<feature>/.learning-state.md`), append the concept to the "Concepts covered" list with today's date. This feeds adaptive depth in future `teach-task.md` runs — you won't re-teach the same thing.

If no session is active (the user invoked `/guided-implement` in concept-only mode), skip this step. No scratchpad means no cross-session memory by design.

## Step 4: Offer the next step

Three options:
- **Another concept** → loop this workflow.
- **Resume the task** → if a session was active, return to whichever workflow was in flight.
- **Done** → acknowledge and stop.
</process>

<success_criteria>
This workflow is complete when:
- [ ] The concept question has been scoped (general vs project-specific, depth).
- [ ] Explanation delivered in the five-section structure, ≤25 lines when possible.
- [ ] Example is idiomatic and, where possible, sourced from this codebase.
- [ ] A project-specific callout is included.
- [ ] Scratchpad updated (if session active).
- [ ] Next step offered.
</success_criteria>
