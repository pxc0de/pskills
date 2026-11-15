# Brief template

Use this layout for the file that `brainstorm` writes. Leave out a section that has no content. Write for a reader who was not in the session.

```markdown
# <Idea name> brief (draft, unreviewed)

Status: outcome of a brainstorm on <date>. Nobody has built or reviewed any of it. Every decision is open to challenge.

## What it is

<Two or three sentences on what it does and who uses it.>

## What the owner wants

<Their goals, close to their own words. Include the constraints they stated, such as "few solid features".>

## Why it should exist

<Which existing products are close, and what this one does that they do not.>

## Decisions

Group related decisions under a subheading. Write one table row per decision.

| Decision | Why | Also considered | Who does it this way |
| --- | --- | --- | --- |
| <the choice> | <the reason given> | <options turned down> | <product, or "none found"> |

When the owner chose against the interviewer's recommendation, add **(recommended instead: <the recommendation>)** to the Decision cell.

## Order of work

<If the session covered it, the steps in order. Each step should be usable when it is finished.>

## Left out on purpose

<What the first version excludes.>

## How other products do it

For each product, write what it does about the questions above and where you read it.

**<Product>** (<repository or site>)

- <finding>
- Source: <file, doc page or URL>. <"Read directly", "secondary source" or "from memory, not checked">

## Not verified

<Claims the design depends on that nobody has tested or looked up. Write one line for each, with what would settle it.>

## Not discussed

<Questions the session did not reach. A reviewer should start here.>
```
