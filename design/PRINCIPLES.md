# Design principles

Portable design judgement — Stan's taste and experience, stated so it survives
a change of project. **Nothing in this file may name this repo**: no file paths,
no class names, no district panel, no San Francisco. If a line only makes sense
here, it belongs in [CONVENTIONS.md](CONVENTIONS.md) or
[IMPLEMENTATION.md](IMPLEMENTATION.md) instead.

Each entry carries a confidence: *tentative* (one correction, one session),
*firm* (held across sessions, or shipped and survived review). A tentative entry
is a working assumption, not a rule — say so when you lean on it. Promotion
happens in the deferred learning step at the end of a `/design` session, never
mid-loop.

None of this is dogma. A principle that keeps losing to the specific case is
evidence about the principle. Record that in [Tensions](#tensions) rather than
quietly obeying or quietly ignoring it.

---

## Rank the facts out loud before you touch the type

*Firm — the question that turned the whole district-panel exercise; shipped.*

Before any typographic decision: **what is most interesting here?** Answer it in
order, in words, out loud. Then let the layout fall out of the ranking — the
most interesting fact gets the headline, the next gets the line under it, and
the paperwork goes last.

Do this first because layouts that were never ranked tend to invert the ranking.
The characteristic failure is a module where the one thing a reader came for is
set in label type while four undifferentiated rows carry the administrative
detail. Nobody decided that; it is what happens when the type is chosen before
the facts are ordered.

Ask for the ranking even when you think you know it. It is cheap, it is the
input to every later decision, and it is the decision a human is best placed to
make.

## Identity versus standing is the test for what belongs in a list

*Firm — applied twice, took two rows out of a five-row panel; shipped.*

Sort every candidate fact into one of three kinds:

- **Identity** — what the subject *is*. It belongs with the name: eyebrow,
  title, kicker. It is not a list row.
- **Standing** — something the subject is on or off, in or out of, has or
  hasn't. That is a list.
- **Qualification** — something that conditions the name rather than standing
  apart from it (*when* it mattered, *which* edition, *what* period). It sits
  with the name as a dateline, not as a row.

Applying the test is subtractive: rows leave the list, and redundancies that
wording could only paper over dissolve outright, because the fact was in the
wrong place rather than badly phrased.

## A glyph that repeats is worth more than a glyph that varies

*Firm — replaced a five-icon set with a three-step scale; shipped.*

When rows carry a scale — listed / eligible / neither, done / in progress / not
started, yes / partly / no — put **the step on the scale in the icon and the
subject in the words**. Give every row its own icon and the icons distinguish
rows their own labels already distinguish; worse, a decorative set will
eventually put an affirmative mark ("✓") beside a negative fact.

Let negatives all take the same mark. Repeated down a list, a mark stops reading
as a glyph and starts reading as texture, and the whole negative half of the
list reads as one fact rather than as four things to evaluate separately.

## Each extra channel costs more than it carries

*Firm — the through-line of every pass of the district exercise; shipped.*

This is the most reusable line in this file. A distinction can be carried by
position, order, colour, weight, size, an icon, a rule, a gap, or wording.
Pick the one or two that carry it, and then **stop**. Each additional channel
does not reinforce the distinction; it spends attention that some other
distinction on the board needed.

Every reduction in the district exercise was an instance of this: the accent
went because ink-against-muted already separated affirmative from negative; the
weight change on the eyebrow went because the eyebrow's own words already said
it; the gap between the halves of a list went because colour and repetition
already separated them; two of five type styles went because order and lane
already carried rank.

The practical form is a count. Name the distinction, count the channels
carrying it, and remove down to two. If removing a channel loses nothing, it was
never carrying anything.

## Spend no accent unless this is the place to spend it

*Firm — the specimen Stan picked was the one with no accent on it.*

An accent colour is a pointer to one thing on the board. Marking the
second-most-interesting fact directly beneath the most interesting one is the
common misfire: the accent pulls the eye off the thing the module exists to
deliver, and does it at close range where the competition is worst.

Ask what the accent is for before placing it. If the distinction is already
carried (see above), the accent is a third channel, and a loud one.

## Count the type styles

*Firm — five styles in the third pass, three in the shipped one.*

Count them: every size × weight × family combination on the board is one style.
A module that needs five is usually carrying rank by size because nothing else
was asked to carry it.

**Carry rank by order, colour, position and lane.** Reserve size for the single
thing the module exists to deliver — the headline — and let everything else
share one style for facts.

## Plain language first, citation demoted to a reference

*Firm — shipped.*

A statute number, a code section, a dataset name or a schedule letter means
nothing to a reader and everything to the two people who need to look it up.
Put the plain description in the words and keep the citation inline as a
reference, in the same style, not as information in its own right.

The test: read the line aloud to someone who has never seen the source. If the
sentence still tells them what is true, the citation is correctly demoted.

## Build dark first

*Firm — standing preference, applies to every board.*

Stan works in dark mode. A light-only board is a board he has to squint at, so
the board actually being judged should be the dark one. Compose with the dark
tokens from the outset and derive the light variant from it if one is wanted,
rather than the other way round.

The rebind is mechanical in either direction; the difference is which one you
looked at while deciding.

---

## Checks to run before committing to a rule that reads data

*Firm — all four came back with something in the exercise that earned them.*

A design decision that renders a data field is a rule about every value of that
field, not just about the one on screen. Before the rule ships, run these
against the whole domain. What each check turns up in this codebase belongs in
[CONVENTIONS.md](CONVENTIONS.md); the habit of running them is general.

1. **Does the rule hold for every value?** If the design lifts, splits, trims or
   parses a phrase out of a value, scan every value and count how many the rule
   holds for. A rule that holds for 110 of 113 is a rule with three exceptions
   to draw, not a rule that fails — but you have to know that before drawing.
2. **What does the longest value do?** Find the actual ceiling and lay it out.
   Do not trust a guess about which part of a long value is redundant; long
   values are usually long in their proper part, so trimming a suffix saves
   nothing.
3. **What are the junk values?** Real datasets store `N/A`, `Unknown`, `None`,
   `0`, empty strings and sentinel dates. A design that renders the field
   verbatim will print them. Look before drawing, not after.
4. **Which records are a different shape?** There is almost always a tail of
   records written under an older schema, or by hand, or by a different
   producer. Find them and decide what they render as; they are the pages a
   migration will not touch.

---

## Tensions

Two learnings that appear to contradict are not a bug to be resolved by
overwriting one of them. Record both, and try to name the **context that
separates the cases** — that context is usually the real learning.

*None recorded yet.*
