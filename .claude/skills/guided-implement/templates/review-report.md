# Template: Review Report

Use this structure when reviewing the user's code in `workflows/teach-task.md` Step 5. Fill each section, cut any that's empty. Target: ≤ 40 lines total.

---

**Review — `T0XX`**

**Works:** `<one line — "python manage.py check passes and test_X is green" OR "doesn't import: <error>, stopping here until fixed">`

`<If "Works" failed, stop the review. Discuss the error with the user and loop. Do not continue to the sections below until the code runs.>`

**Project-convention hits:**
- `<file:line — concrete compliment. e.g. "parties/models.py:42 — nailed related_name='persons'; contract in contracts/parties-api.md expects exactly that inverse.">`
- `<... up to 3 if earned. If nothing rises above the bar, skip this section — don't manufacture praise.>`

**Idiomatic improvements:**

1. `<one-line finding>` — **Blocking** / **Optional**
   ```python
   # before
   <1–3 lines from the user's code>
   ```
   ```python
   # after
   <1–3 lines with the change>
   ```
   Why: `<cite the project file or Python/Django convention — one line>`

2. `<... up to 3 items, ranked by leverage>`

**Tests:**
- `<status — "test task T0XX-1 written and red→green through this implementation" | "test task T0XX-1 still [ ] — the implementation is ahead of its test; back up and write the test first">`
- `<if there are test quality issues — e.g. "test asserts object.pk, not the uniqueness violation we actually want to prove">`

---

**Next: comprehension check.** (Ask one targeted _why_ question per `workflows/teach-task.md` Step 6. Don't include the question in the review itself — ask it as a fresh message so the user can answer without scrolling past the diff.)
