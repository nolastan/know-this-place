# Gap log

Cases `/ui` had to guess at because
[RULES-OF-THUMB.md](RULES-OF-THUMB.md) and
[IMPLEMENTATION.md](IMPLEMENTATION.md) didn't cover them.

**These are observations about missing guidance, not learnings.** No confidence
level. Never promoted into principles. Never consulted as a source of design
advice, by `/ui` or by anything else. The only thing that reads this log is
`/design`, at the start of a session, to see where the corpus is thin.

Format — one line each, newest first:

```
- `YYYY-MM-DD` **What was being built** — what wasn't covered; what was guessed.
```

Keep it scannable: if a new entry repeats an existing one, merge them and note
that it recurred rather than adding a second line. An entry whose gap has since
been filled by a real rule gets deleted, by `/design`, in the same session that
fills it.

---

- `2026-09-08` **Permit timeline items, tightened (issue #285)** — nothing covers
  what a documented indicator becomes when the decision removes its colour
  channel: the `.cost` tier is specified as "a rising warm hue", the issue took
  the hue away, and "never introduce new colours" leaves lit-glyph count on ink
  as the only move. Guessed the meta row's own `--muted` for the lit glyphs so
  the row reads in one tone.
- `2026-09-08` **Permit timeline items, tightened (issue #285)** — BLOCKS.md
  names two kinds of deliberately excluded filing for the line under the rail
  ($1 street-space, DBI duplicates) and no rule for a third; guessed that a
  status the render drops wholesale is the same kind of admission, counted in
  the same line, and that a stored `permit_summary.note` takes the second
  clause rather than a second sentence.
- `2026-09-11` **Current occupant panel (issue #283)** — nothing covers an
  outbound commercial call to action (a referral link) on an address page, or
  how loud it may be; guessed a full-width outlined button in `--accent` with a
  muted disclosure line beneath, as the one place on the page to spend the
  accent. Nor is there a rule for weekly opening hours in a speclist; guessed
  one row per run of days ("Tue–Thu", "Sat, Sun", "Daily"), 12-hour times,
  days the listing omits as a "Closed" row, and a `--muted` "Last updated" line
  under the last merchant.
