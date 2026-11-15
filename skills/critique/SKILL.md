---
name: critique
description: Review a design brief as an independent reviewer who was not part of the discussion that produced it. Check the claims it depends on, find the decisions most likely to be wrong, and propose a smaller and firmer version. Works on a brief written by the brainstorm skill or on any design document. Run only when the user invokes it.
disable-model-invocation: true
---

# Critique

The user has a brief that records an idea and the decisions made about it. Review it as someone whose job is to find what is wrong before anyone builds it. Then help the owner correct the brief.

Run this skill only when the user asks for it by name.

## Before you start

Use a session that did not produce the brief. If you took part in the discussion behind it, you have already accepted each answer, and your review will miss what you agreed to. Tell the user to open a new session and stop.

Ask for the brief's path if the user did not give one. The `brainstorm` skill writes briefs to `docs/brainstorm/`.

Read the brief and nothing about how it was made. Do not ask for the conversation that produced it. You may read the project's files and outside sources to check facts.

## 1. Say what you understood

Write two or three sentences that describe the idea, using only the brief. Then list anything you could not work out from it. A brief that a new reader cannot follow has a defect, so record each gap as a finding.

## 2. Check the claims

A design fails when a fact it depends on is false. Find those facts and test them.

- Check every item under "Not verified".
- Check every finding about another product that the brief labels as secondary or from memory.
- Find claims the brief states as fact without a label, and check the ones a decision depends on.

Check each claim at its source. Read the code, the official docs or the tool's own output. Record each result as confirmed, false or could not check, with where you looked.

## 3. Look for what is wrong

Review in this order, because the earlier items go wrong more often.

1. **Decisions made against the recommendation.** The brief marks them. Work out whether the owner's reason is sound or whether the recommendation was right.
2. **Questions the session did not reach.** Decide which of them block the first step of work.
3. **Decisions that conflict.** Two choices that cannot both be true, or a later choice that undoes the reason for an earlier one.
4. **Decisions with no reason given.** Ask what the reason would be, and whether it survives.
5. **Decisions that are expensive to change later.** Give these more time than the rest.
6. **The first step of work.** Say whether someone could start it today, and what is missing if not.
7. **Size.** Name what the first version could drop and still be worth using.

Each finding needs a concrete failure. Say who is affected, what happens to them, and when. "This may not scale" is not a finding. "The gateway has no accounts, so one misbehaving host can use the whole notification quota" is a finding.

Do not invent objections to fill the report. When a decision is sound, say so in one line and continue. State each real problem directly, without softening it.

## 4. Write the report

Write the report to a file beside the brief, named `<brief-name>.critique.md`. Do not edit the brief yet. Tell the user the path.

```markdown
# Critique of <brief name>

Reviewed on <date> from the brief alone.

## The idea as the brief describes it

<Two or three sentences, then anything the brief left unclear.>

## Claims checked

| Claim | Result | Where checked |
| --- | --- | --- |
| <claim> | confirmed, false or could not check | <file, page or command> |

## Findings

Order them by severity. Number them so the owner can refer to them.

### 1. <The problem in one line>

- Severity: blocks the work, should change, or minor
- Decision affected: <which one>
- What goes wrong: <who is affected, what happens, when>
- Evidence: <what you read or ran>
- Do this instead: <the change you propose>

## Decisions that hold

<One line for each decision you examined and found sound.>

## What to cut

<What the first version can drop, and what dropping it saves.>

## Questions for the owner

<Decisions the brief needs that only the owner can make.>
```

## 5. Correct the brief with the owner

Give the user a short summary with the most severe findings first. Then take the findings one at a time and ask whether the owner accepts each one. Ask in plain language, and give your recommended answer.

Change the brief only for findings the owner accepts. For each change, keep the previous decision under "Also considered" and note that the critique caused the change. Move claims you confirmed out of "Not verified". Correct or remove claims you found false.

When the owner rejects a finding, record their reason in the report and leave the brief unchanged.

Do not start building. The outputs are the report and the corrected brief.
