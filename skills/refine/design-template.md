# Design template

Use this layout for the file that `refine` writes. Leave out a section that has no content. Write for a reader who will build from this file and has seen neither the idea file nor the session.

```markdown
# <Product name> design

Status: refined on <date> from [`idea.md`](idea.md). Nothing is built.

## What it is

<Two or three sentences on what it does and who uses it.>

## Who it is for

<The person, what they use today, and why they would switch. Then the one part only this product does.>

## How it is used

<The first ten minutes, an ordinary day, and what the person sees when something fails. Write each as short concrete steps.>

## Decisions

Group related decisions under a subheading. Write one table row per decision.

| Decision | Why | Also considered |
| --- | --- | --- |
| <the choice, in concrete terms> | <the reason> | <options that lost, including the idea file's original decision if it was replaced> |

## Order of work

<Numbered steps. Each step is usable when it is finished. Say what each step must prove before the next one starts.>

## Left out of the first version

<What is excluded, and what leaving it out saves.>

## How other products do it

**<Product>** (<repository or site>)

- <finding>
- Source: <file, doc page or URL>. <"Read directly", "secondary source" or "from memory, not checked">

## Verified

<Claims the design depends on that were checked, each with where it was checked and the date.>

## Not verified

<Claims nobody could check. Write one line for each, with what would settle it and which step of work it blocks.>

## Open questions

<Questions that remain, and which step of work each one blocks.>

## Changes from the idea

| Change | Why | Owner's response |
| --- | --- | --- |
| <what the proposal changed, or would have changed> | <the concrete reason> | <accepted, or rejected with the owner's reason and the consequence they accepted> |
```
