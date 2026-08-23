---
name: design
description: Design a module of this site in Paper (paper.design) using the repo's design module (design/) — the accumulated principles, codebase conventions, tool quirks and front-end translation for know-this-place. Invoked as /design with no argument to pick up the most valuable open design work, or /design <request> for a specific module, panel or layout. Use whenever the task is mocking, redesigning, critiquing or specifying a visual module of this site, or porting a Paper design back into shared/site.css — even when the user doesn't say "design". Not for implementing UI directly in code with no exploration; that is /ui.
---

# Design module

`design/` is where this project decides **how a module looks** before it is
built. The rest of the repo presents the result. This skill is the door into
that module, and it always runs in **teacher mode** — this is a solo project,
there is no other kind of user. Every session iterates, explores, learns, and
writes back into the module.

The module's own files are the authority; start at
[design/AGENTS.md](../../../design/AGENTS.md).

**This skill deliberately shadows the built-in `design` skill** (Claude Design's
canvas editor), which shares the name. Inside this repo, `/design` means this
loop and nothing else. That is the intent: design here is the Paper loop with a
knowledge module behind it, not a one-off canvas. To reach the canvas editor
again, rename this skill's directory — a project skill wins on name, so there is
no way to address the shadowed one while both are called `design`.

## The loop

### 1. Open the session

Read [design/GAPS.md](../../../design/GAPS.md) and report anything pending in
two lines or less — those are the places `/ui` had to guess, and they are
candidate work. Then say what you are about to design and why, briefly.

### 2. Get something on screen

Read **[design/RULES-OF-THUMB.md](../../../design/RULES-OF-THUMB.md) only**, plus
[design/PAPER.md](../../../design/PAPER.md) for the mechanics, and render. Do not
read the full corpus first. The point of the distilled file is that a board
exists before the reading does.

Before mocking a module that renders data, the checks in the rules of thumb are
not optional — read the generator in
[`scripts/seed_pages.py`](../../../scripts/seed_pages.py), and glob the
`data.json` files for the real value domain and counts.

### 3. Iterate — this is the deliverable, not the overhead

**Explore; do not settle early.**

- Generate **many options**, not one refined thing. Two directions side by side
  beats one direction defended.
- Take **multiple independent passes**. The district panel took five and shed
  something on every one.
- **Print intermediate output into Paper** so the process is visible. A rejected
  board that shows why it was rejected is worth keeping on the page.
- Screenshot and critique your own board between passes — at artboard level,
  never node level.

Refine against the full corpus ([PRINCIPLES.md](../../../design/PRINCIPLES.md),
[CONVENTIONS.md](../../../design/CONVENTIONS.md),
[IMPLEMENTATION.md](../../../design/IMPLEMENTATION.md)) in the later passes, once
there is something concrete for it to bite on.

### 4. Learn — implicitly, and never in the loop's way

**Never ask what to remember. Never wait for a save command.** A correction from
Stan is a lesson; recognise it, generalise past the specific case, and queue it.

**Queue mid-session, write at the end.** Keep a running list of observations
while you work and keep designing. The heavy part — generalising, choosing the
layer, promoting confidence, reconciling contradictions, regenerating the rules
of thumb — happens in a single deferred step at the end. Prefer spawning a
subagent for it so the design session isn't paying for it.

When the deferred step runs:

- Place each observation by the test in
  [design/AGENTS.md → The layers](../../../design/AGENTS.md#the-layers).
- Write new learnings as **tentative**. Promote to firm only when it has held
  across sessions.
- On a contradiction, **record the tension** in
  [Tensions](../../../design/PRINCIPLES.md#tensions) and try to name the context
  that separates the cases. Do not overwrite the older learning.
- Note anything about *how the learning went* in
  [META.md](../../../design/META.md).
- **Regenerate [RULES-OF-THUMB.md](../../../design/RULES-OF-THUMB.md)** from the
  corpus, whole. Delete any gap-log entry the session actually filled.

### 5. Close the session

Report **what was learned**, briefly — a few lines, not a transcript. Don't
narrate writes as they happen, and don't go entirely silent about them either.

## Porting back into the codebase

An invocation of `/design` is a human asking, so porting a settled design into
`shared/site.css` is in scope when the design is settled. Follow
[CONVENTIONS.md → Porting a design back into the site](../../../design/CONVENTIONS.md#porting-a-design-back-into-the-site):
scope new classes to the module, change the generator before the pages,
migrations are scratchpad scripts, expect and report the tail, verify with
`getComputedStyle` after a hard reload, and run `python3 scripts/validate.py`.

The root [AGENTS.md](../../../AGENTS.md) binds without exception for anything
that touches a page under `san-francisco/`.

## `/design` with no request

Take the first of these with something in it: an open item in
[GAPS.md](../../../design/GAPS.md); a module whose flaws the district exercise
already diagnosed and which still carries them (the other aside panels); a board
in the Paper file that has drifted from `site.css`; a layer of the module that is
thin or badly placed.

Say which you picked and why, in a line.
