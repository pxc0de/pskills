# gh-morning idea

Status: outcome of a brainstorm on 2026-11-10. It says what to build and why, and leaves how to the design. Nothing is built. The `refine` skill turns this file into `design.md`.

## The idea

gh-morning is a command a developer runs once in the morning. It prints the few GitHub notifications that need them and leaves out the rest.

## Who it is for

A developer who works across many repositories and gets about 200 GitHub notifications a day. Today they scan the notifications page or their email, and they miss the ones that are waiting on them.

## Why it should exist

GitHub's own filters can narrow the inbox, but they need constant upkeep as repositories come and go. Octobox gives a better inbox, and it is still an inbox to check and clear. Neither answers the question "what is waiting on me this morning?" in one screen.

GitHub pushes each notification to gh-morning by webhook as it arrives, so the tool never polls and the morning digest is ready the moment it is asked for.

## The map

- **Centre:** one screen in the terminal that shows what is waiting on me
- **Does**
  - shows review requests that are waiting on me
  - shows direct @mentions of me
  - shows CI failures on my own pull requests
  - lets me write the rules for what counts, in a form I can read
  - remembers what I have already seen, so tomorrow's digest is new
- **Not**
  - an inbox to manage or clear
  - email
  - a web app or a hosted service
- **Good means:** I read it in under a minute and trust that nothing waiting on me is missing

## In the owner's words

"i get like 200 a day and miss the ones that matter."

"i want rules i can read. it has to be predictable."

"one output, in the terminal, in the morning. not another inbox."

## What exists

**GitHub notification filters** (github.com/notifications)

- Saved filters by reason, repository and state. They have to be maintained by hand.
- Source: the owner's own use. From memory, not checked.

**Octobox** (github.com/octobox/octobox)

- A separate inbox for GitHub notifications with search, filters and archiving.
- Source: from memory, not checked.

## Turned down

- **Ranking or summarising with an LLM.** The owner wants rules they can read, because the result has to be predictable.

## For the design

- Where do the rules live, and what do they look like?
- How does the tool sign in to GitHub?
- What does the digest look like on screen?
- How does it remember what was already seen, and how does the owner mark something as dealt with?

## Not verified

- GitHub Enterprise Server offers the same notifications API as github.com. Reading the Enterprise Server REST docs would settle it.
