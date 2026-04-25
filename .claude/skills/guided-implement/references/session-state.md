# Session State Reference

The `.learning-state.md` scratchpad lives at `specs/<feature>/.learning-state.md` and is the session's memory across workflows and restarts. This file describes its format and the rules for keeping it honest.

## Why it exists

Two concrete jobs:

1. **Adaptive depth** — so `teach-task.md` knows which concepts have already been deep-dived and can switch to one-line reminders.
2. **Cross-session resume** — so when the user comes back next week and runs `/guided-implement 001-parties-master-data`, you can skim this file and pick up intelligently.

It does **not** duplicate `tasks.md` — checkbox state lives in `tasks.md` and only there. The scratchpad complements it.

## Format

Markdown with three required sections. See `templates/learning-state.md` for the literal template.

```markdown
---
feature: 001-parties-master-data
started: 2026-04-16
---

## Completed this session

- T001 — 2026-04-16 — user-written
- T005 — 2026-04-16 — user-written
- T006 — 2026-04-17 — Claude-written (user requested "just write it")

## Concepts covered

- `PartyQuerySet` / `as_manager()` — T005 — 2026-04-16
- `UniqueConstraint(Lower(...))` for case-insensitive uniqueness — T006 — 2026-04-16
- `on_delete=PROTECT` vs SET_NULL vs CASCADE — T008 — needs revisit

## Review notes

- User wants to remember: Django's `Meta.ordering` sorts every default queryset — check perf before adding.
- Skipped comprehension check — T007 (push through foundational phase).
```

## Rules for edits

1. **You may edit this file.** It is not implementation code. Write/Edit freely.
2. **Append, don't rewrite.** Historical entries are signal. Don't "clean up" old notes unless the user explicitly asks.
3. **Dates are absolute.** Convert "today" / "yesterday" in user speech to `YYYY-MM-DD` at write time.
4. **Mark the authorship.** When you record a completed task, note whether it was user-written or Claude-written. This is how the phase recap surfaces "we short-circuited here, maybe revisit".
5. **Don't invent concepts.** Record a concept as "covered" only if you actually _taught_ it — not if the task happened to use it. See `pedagogy.md`.
6. **Needs-revisit is sacred.** If a concept ends up flagged for revisit, do NOT remove the flag until the user has demonstrated understanding in a subsequent comprehension check. Then move it to "covered" with a note like "revisited T0XX".

## Reading the file

When starting a session, read this file after reading `tasks.md`. Use it in this order:

1. Check `Concepts covered` — this determines adaptive depth for every upcoming briefing.
2. Check `needs revisit` entries — these bias your next comprehension checks.
3. Skim `Review notes` — these are things the user wanted you to remember across sessions.
4. Ignore `Completed this session` for done-ness; trust `tasks.md` checkboxes instead. The scratchpad list is for retrospectives, not correctness.

## What NOT to put here

- Implementation code. Ever.
- Long-form concept explanations (those belong in `references/`, not per-feature scratchpads).
- Personal data beyond what `spec.md` already contains.
- Anything secret (env vars, tokens) — the scratchpad is checked into git by default unless the user has `.gitignore`d `.learning-state.md`. Confirm git-ignoring with the user on first session if they prefer the scratchpad stay local.
