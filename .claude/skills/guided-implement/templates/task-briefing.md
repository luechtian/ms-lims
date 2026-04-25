# Template: Task Briefing

Use this structure when briefing the user on a task in `workflows/teach-task.md` Step 3. Pick the tier that fits the task; do not apply Teaching-Tier to a task that only reuses already-covered concepts.

## Tier decision (always first)

- **Teaching-Tier** — task introduces ≥1 new concept, opens a new file, or crosses into a new kind of change. Use the full 7-section scaffold.
- **Apply-Tier** — task reuses already-covered concepts (second model after the first, bare admin registration, settings tweak). Use the lean scaffold.

When uncertain, ask the user: "Teaching-Tier oder Apply-Tier für diesen Task?"

---

## Teaching-Tier scaffold

`## T0XX — <short title>`
`**Umfang:** ~N Min · **Neue Konzepte:** N · **Review-Datei:** <path>`

### Thema

`<1–2 lines: what the task produces>`

### Hintergrund

`<why it exists — cite FR / research / plan / data-model line>`

### Nötiges Wissen

- **<concept A>** — NEU
- **<concept B>** — Wiederholung aus T0XX
- **<concept C>** — schon covered (kein Reminder nötig)

### Konzepte

For each NEW concept only:

**N. <concept name>**

- *Mental Model:* `<2–3 lines, plain language, no new jargon>`
- *Projekt-Anker:* `<file path + convention reference, citing plan.md / CLAUDE.md / constitution / research>`
- *Fallstrick:* `<1 line — the mistake juniors make here>`

(Known concepts only get their 1-line reminder in Nötiges Wissen, not a block here.)

### Beispiel

Runnable snippet OR `# excerpt`-marked structural sketch. Never ship a half-formed code block that looks runnable — mark it or complete it.

### Aufgabe

`<file path + exact fields/signatures/rules; literally what the user types>`

### Ich prüfe

- `<check 1 — project-convention match>`
- `<check 2 — idiomatic correctness>`
- `<check 3 — Done-condition (python manage.py check, test passes, …)>`

### Erkunden *(optional — nur wenn Task neue Models, Relationen oder QuerySet-Methoden einführt)*

```
uv run python manage.py shell
```

```python
# 2–4 Zeilen: Objekte anlegen, abfragen, Relation traversieren
# Erwartete Ausgabe als Kommentar zeigen:
# => <QuerySet [<Institution: Test GmbH>]>
```

---

## Apply-Tier scaffold

`## T0XX — <short title>`
`**Umfang:** ~N Min · **Anwendung von:** <earlier task / concept references>`

### Aufgabe

`<3–5 lines: file + what to type + any non-obvious rule>`

### Review-Fokus

`<1 line>`

---

## When to add Erkunden

Include the optional `### Erkunden` block **only** when the task introduces ≥1 of:
- A new Model (first time you can do `Model.objects.create(...)`)
- A new relation (ForeignKey, M2M — first traversal with `__` lookups)
- A custom QuerySet method or Manager

Skip for: test-only tasks, migration-only tasks, settings/config changes, second-instance registrations.

---

## Rules both tiers share

- **Konzepte + Beispiel before Aufgabe.** Mental model first, then tippen.
- **Runnable snippets or `# excerpt`-marked.** Never ship a half-formed code block as if it were complete.
- **Project rules trump generic Django advice.** Every concept anchor points at plan.md / CLAUDE.md / constitution / research — not a textbook.
- **Umfang is a time-estimate contract.** If the briefing exceeds the estimate by >50%, the user gets to say "knapper" and you comply.
- **Concepts shrink on revisit.** Second encounter = 1-line reminder + project anchor, never a full re-teach.

End both tiers with a one-line handoff:
`Ping mich, wenn der Code steht.`
