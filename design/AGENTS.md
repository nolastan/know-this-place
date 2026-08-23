# The design module

This directory is design work *about* the site, not part of the site. Nothing
here is served, linked, or included in `sitemap.xml`.

It is a **self-improving module**, like [`research/`](../research/AGENTS.md):
the files below are written by the [`/design`](../.claude/skills/design/SKILL.md)
skill as it works, and are expected to be better after every session.
[`/ui`](../.claude/skills/ui/SKILL.md) is the fast path — it reads two of them
and writes to none.

`/design` **deliberately shadows the built-in skill of the same name** (Claude
Design's canvas editor). In this repo, designing a module means the Paper loop
and this corpus, not a one-off canvas. Renaming
`.claude/skills/design/` is the only way to get the built-in back — a project
skill wins on name, and nothing can address the shadowed one while both are
called `design`.

## Direction of truth is one-way: code → design

[`shared/site.css`](../shared/site.css) is the canonical design system. A Paper
file mirrors it and is never a source for it. **When a mock and the stylesheet
disagree, the stylesheet is right and the mock is stale.**

Porting an improvement the other way — Paper → code — is something a human asks
for. **An invocation of `/design` is the human asking**, and the whole point of
the loop, so it needs no further permission. What the rule still forbids is the
unprompted case: an agent doing other work in this repo does not get to
"improve" a module in Paper and land it in `shared/site.css` on its own
initiative. See ground rule 5 in the root [AGENTS.md](../AGENTS.md).

## The layers

Knowledge lives in separate files so a layer can be swapped or reused on its
own.

| File | What belongs in it |
|---|---|
| [PRINCIPLES.md](PRINCIPLES.md) | Portable design judgement. Nothing about this repo, this stack, or this tool. |
| [CONVENTIONS.md](CONVENTIONS.md) | How design work is done *here* — the generator, the data checks, specimen rules, porting back. |
| [PAPER.md](PAPER.md) | paper.design quirks only. Isolated so another tool could replace this file alone. |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | Translation onto this front end: tokens, type, rem→px, metrics, icons. Facts, no judgement. |
| [META.md](META.md) | What works about *learning* in this module. |
| [RULES-OF-THUMB.md](RULES-OF-THUMB.md) | Generated. The distilled corpus — the first thing `/design` reads and one of two things `/ui` reads. |
| [GAPS.md](GAPS.md) | Appended by `/ui` when it had to guess. Observations, not learnings. |

**The placement test.** If a line would still make sense in a different
codebase, it goes in PRINCIPLES. If it names a file, a class or a dataset here,
it goes in CONVENTIONS or IMPLEMENTATION. If it names a Paper MCP call, it goes
in PAPER. IMPLEMENTATION must be unreadable as standalone design advice — the
moment it starts explaining *why*, the why belongs in PRINCIPLES.

## How the knowledge is written

- **Confidence is explicit.** A single correction lands *tentative*. It is
  promoted to *firm* only after it holds across sessions.
- **Contradictions are recorded, not overwritten.** Two learnings that disagree
  usually differ by context; naming that context is the real learning. See
  [Tensions](PRINCIPLES.md#tensions).
- **Nothing here is dogma.** A principle that keeps losing to the specific case
  is evidence about the principle.
- **Git is the version history.** No changelogs, no dated revision lists inside
  these files.

The Paper file, its page-per-module structure, and the specimen boards are
described in [CONVENTIONS.md → The Paper file](CONVENTIONS.md#the-paper-file).
