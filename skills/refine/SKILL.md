---
name: refine
description: Turn an idea file into a final design. Read the idea as an independent reviewer and as the product's user, check the claims it depends on, fix what is wrong, fill what is vague, cut what does not earn its place, and settle each change with the owner. Writes design.md. Works on an idea file written by the brainstorm skill or on any draft design. Run only when the user invokes it.
disable-model-invocation: true
---

# Refine

The user has an idea file that records an idea and the decisions made about it. Turn it into a design someone could build from. Find what is wrong, make the vague parts concrete, and make the product better for the person who will use it. Then write the design with the owner's agreement.

Finding faults is half the job. For every problem you find, propose the better version.

Run this skill only when the user asks for it by name.

## Before you start

Use a session that did not produce the idea file. If you took part in the discussion behind it, you have already accepted each answer, and you will miss what you agreed to. Tell the user to open a new session and stop.

Ask for the idea file's path if the user did not give one. The `brainstorm` skill writes it to `docs/idea.md`.

Read the idea file and nothing about how it was made. Do not ask for the conversation that produced it. You may read the project's files and outside sources to check facts.

## 1. Say what you understood

Write two or three sentences that describe the idea, using only the idea file. Then list anything you could not work out from it. Each gap is something the design must answer.

## 2. Check the claims

A design fails when a fact it depends on is false. Find those facts and test them.

- Check every item under "Not verified".
- Check every finding about another product that the idea file labels as secondary or from memory.
- Find claims the idea file states as fact without a label, and check the ones a decision depends on.

Check each claim at its source. Read the code, the official docs or the tool's own output. Run the tool when running it is cheap. Record each result as confirmed, false or could not check, with where you looked.

## 3. Use the product in your head

Read the idea again as the person who will use the product. Walk through these moments and write down what that person sees and does at each one.

- **The first ten minutes.** Installing it, setting it up, and the first time it does something useful.
- **An ordinary day.** The thing they do most often, from start to finish.
- **The moment it goes wrong.** The network is down, a step fails, or they made a mistake. Say what they see and what they can do next.

Then answer four questions.

1. **Who is it for, and what do they use today?** Name the product or habit it replaces. If the idea cannot say why this person would switch, the design has no reason to exist yet.
2. **Which part can only this product do?** Find it, and check how early the order of work lets the owner try it. A distinctive part that arrives last is tested last.
3. **Where did the walk-through stop?** Every point where you had to guess what happens is a gap. Every word such as "simple", "tasteful" or "fast" that names a wish without a behaviour is a gap.
4. **Which features did the walk-through never touch?** They are candidates to cut.

## 4. Look for what is wrong

Review in this order, because the earlier items go wrong more often.

1. **Decisions made against the recommendation.** The idea file marks them. Work out whether the owner's reason is sound or whether the recommendation was right.
2. **Questions the session did not reach.** Decide which of them block the first step of work.
3. **Decisions that conflict.** Two choices that cannot both be true, or a later choice that undoes the reason for an earlier one.
4. **Decisions with no reason given.** Ask what the reason would be, and whether it survives.
5. **Decisions that are expensive to change later.** Give these more time than the rest.
6. **The first step of work.** Say whether someone could start it today, and what is missing if not.
7. **Size.** Name what the first version could drop and still be worth using.

## 5. Turn each finding into a proposal

Write one proposal for each thing you found in steps 2 to 4. A proposal is one of five kinds.

- **Fix.** A decision that is wrong or rests on a false claim. Give the replacement.
- **Fill.** A gap or a vague word. Give the concrete answer you would choose, such as the default value, the screen, the message or the rule. Answer every question the idea file lists as not discussed, or say that only the owner can.
- **Cut.** A feature the first version can drop. Say what dropping it saves.
- **Reorder.** A change to the order of work, so that each step is usable and the distinctive part comes early.
- **Add.** Something missing that the person using the product would notice on the first day. Use this kind least. An addition must pay for itself by replacing something or by closing a gap from the walk-through.

Each proposal needs a concrete reason. Say who is affected, what happens to them, and when. "This may not scale" is not a reason. "The gateway has no accounts, so one misbehaving host can use the whole notification quota" is a reason.

Do not invent proposals to look thorough. When a decision is sound, keep it and say so in one line. State each real problem directly, without softening it.

If the `inspiration` skill is installed beside this one, use its short form when a proposal needs to know how other products solved the same problem. Read `../inspiration/SKILL.md`, relative to this skill's folder.

## 6. Settle the proposals with the owner

Give the user a short summary first: what holds, what you checked, and the most important proposals.

Then ask the owner to decide each proposal. Order them by how much they change the design. Ask in plain language, one decision per question, with your recommended answer first. If your agent has a tool for asking the user multiple-choice questions, use it, and ask as many questions per call as it allows.

- When a proposal depends on the answer to another, ask the other first.
- When the owner rejects a proposal, ask for the reason and keep the original decision.
- When a proposal needs a fact only the owner has, such as who the first user is, ask for the fact.
- When the owner gives a new idea in place of yours, check it against the rest of the design before you accept it.

The owner makes every decision. You do not change the design on your own judgment.

## 7. Write the design

Write `design.md` in the same folder as the idea file, using the layout in [design-template.md](./design-template.md). If a `design.md` is already there, read it and ask the user before you replace it. Leave the idea file unchanged. It is the record of where the design started.

The design is a document to build from, not a review report.

- State each decision as settled, with its reason. Put the options that lost in "Also considered", including the idea file's original decision when a proposal replaced it.
- Use the concrete form everywhere. Write the default, the limit, the wording or the rule. A sentence the builder would have to interpret is not finished.
- Move claims you confirmed into the verified list. Correct or remove claims you found false. Keep what nobody could check under "Not verified", with what would settle each one.
- Record what changed from the idea file and why in "Changes from the idea". Record each rejected proposal there too, with the owner's reason and the consequence they accepted.

Write the file once the first round of answers is in, and update it after each later round. A session can end without warning.

## Finish

1. Read the design once as a builder who has never seen the idea file. Fix anything that needs the idea file or this conversation to understand.
2. Tell the user the path, and list in a few lines what changed from the idea and what is still open.

Do not start building. The design is the only output.
