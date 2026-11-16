# Design template

Use this layout for the file that `refine` writes. Leave out a section that has no content. Write for a reader who will build from this file and has seen neither the idea file nor the session.

```markdown
# <Product name> design

Status: refined on <date> from [`idea.md`](idea.md). Nothing is built.

## What it is

<Two or three sentences on what it does and who uses it.>

## Who it is for

<The person, what they use today, and why they would switch.>

## What it must do well

<The one thing at the centre of the product, and what the owner said makes it good. Every decision below was checked against this.>

## How it is used

<The first ten minutes, an ordinary day, and what the person sees when something fails. Write each as short concrete steps.>

## Decisions

Group related decisions under a subheading. Put the decisions that are expensive to change first. Write one table row per decision.

| Decision | Why | Also considered |
| --- | --- | --- |
| <the choice, in concrete terms> | <the reason> | <options that lost, and which product uses each> |

When the owner chose against the interviewer's recommendation, add **(recommended instead: <the recommendation>)** to the Decision cell. When the owner did not know and took the recommendation for now, add **(provisional: <what would settle it>)**.

## Order of work

<Numbered steps. Each step is usable when it is finished, and the part only this product does comes early. Say what each step must prove before the next one starts.>

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

<Questions that remain, and which step of work each one blocks. Say when a question needs a prototype, and what the prototype must show.>

## Changes from the idea

| Change | Why | Owner's response |
| --- | --- | --- |
| <where the design departs from the idea file, or would have> | <the concrete reason> | <accepted, or rejected with the owner's reason and the consequence they accepted> |
```
