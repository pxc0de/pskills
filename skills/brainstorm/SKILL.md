---
name: brainstorm
description: Think an idea through with the user one decision at a time, in plain language. Each question comes with a recommended answer and with approaches that existing products took to the same problem. The session ends with a written brief that an independent reviewer can critique. Run only when the user invokes it.
disable-model-invocation: true
---

# Brainstorm

Interview the user about their idea until you both understand it the same way. Continue until you would not have to guess at any part of it. Then give them a written brief that a reviewer who missed the session can critique.

Run this skill only when the user asks for it by name.

## Work through the decisions in rounds

Every idea contains decisions, and most decisions depend on earlier ones. You cannot ask how login works before you know who the users are.

At any point, you can ask some questions without guessing at an answer you have not heard. Ask all of those together as one round, then wait. The answers settle some decisions and make new questions askable. Work out the next round from them.

If a question depends on another question in the same round, move it to a later round. The user cannot answer it well yet.

Start with the basics. If you do not know what the idea is, who will use it, or why it should exist when similar products already do, ask that first.

Ask every question you have. If your question tool limits how many questions fit in one call, ask the rest in the next call.

## Ask in plain language

The user should be able to answer each question in a few seconds without rereading it.

- **One decision per question.** A question that contains "and" is often two questions.
- **Use everyday words.** Write "the machine your sessions run on", not "the execution host". When a technical term is the right word, use it and say what it means the first time.
- **Say why you are asking** when the reason is not obvious. Users answer better when they know what the answer affects.
- **Give a concrete example.** Show what each choice would look like in use.
- **Word the question so that "yes" accepts your recommendation.**
- **Name the cost of each option.** Say what the team must build, what can break, and what the option prevents later. Plain language still has to be precise.

Compare these two versions of one question.

> Should the persistence layer treat the harness transcript as the system of record, or maintain an independent event log?

> Where should the chat history live? Claude Code already saves its own, so we could read that. Or we keep our own copy. I'd keep our own. It survives a restarted session, and it has the same format whichever tool runs underneath. The cost is one more thing to store.

If your agent has a tool for asking the user multiple-choice questions, use it. Put your recommended option first and label it as recommended. Put each option's cost in its description. If you have no such tool, number the questions in plain text and write your recommendation under each one.

## Bring ideas with each question

Before you ask a round, find out how existing products handled each question in it. The `inspiration` skill describes how. Read `../inspiration/SKILL.md`, relative to this skill's folder, and follow its short form. If that file is missing, do the work directly. Find two or three products that faced the same decision, read what they do in their own code or docs, and note what it cost them.

Use what you found in the question.

- Before the options, say in a line or two what other products do. For example, "T3 Code makes you sign in for this. Orca doesn't. It uses a key stored on your machine."
- Offer the real approaches as the options, and say which product uses each one.
- If every product does it the same way, say so. The user should know when they are choosing to differ.
- If no product does what the user wants, say that too. The user may have found a gap, or a reason nobody built it.

Match the research effort to the question. Read a repository for a decision that shapes the whole design. Take a quick look for a small one. Tell the user which claims you checked and which you recalled from memory, because they will build on them.

## Recommend an answer every time

Give a recommendation for every question, with the reason in one sentence. Without one, the user has to do the analysis themselves.

When the user chooses something else, accept it and continue. Record that they chose against your recommendation, and what you recommended. A later reviewer should examine those decisions first.

## When the reply is not a decision

Users often reply with a question of their own. The decision is still open.

- **"What do you suggest?"** State your recommendation and reason again in simpler words, then ask for a yes.
- **"How does X do it?"** Find out, report it, and ask the question again with the new options.
- **An example instead of a choice.** State the decision you think the example implies, and ask whether you understood it.
- **A reply that contradicts an earlier decision.** Name both decisions and ask which one stands.

## You find facts, the user makes decisions

Do not ask the user for anything you can look up, such as what the repository contains, what a tool supports, or how another product works. Look it up. If a lookup takes time, ask the questions that do not depend on it while you wait.

Ask the user about every decision, including the ones that look obvious to you. Users are surprised later by decisions an agent made without asking.

## Write the brief as you go

After each round, write the settled decisions to the brief file. A session can end without warning, and a decision that exists only in the chat is lost with it.

Write to `docs/brainstorm/<short-topic-name>.md` in the current project unless the user names another location. Use the layout in [brief-template.md](./brief-template.md). Tell the user the path the first time you write the file.

For each decision, record what the user chose, why, which options they turned down, and which products do it the same way. The brief's reader was not in the session and has the job of disagreeing, so they need the rejected options as much as the chosen ones.

## Finish

The session is complete when you have no question left to ask.

1. Fill in the last two sections of the brief. List the claims nobody verified and the questions the session did not reach.
2. Give the user a short summary of the decisions and ask whether it matches their understanding. Correct the brief if it does not.
3. Tell the user the brief is ready for critique. Recommend that they open a new session and run the `critique` skill on the brief. A reviewer who followed the interview has already accepted each answer, so the same session should not review it.

Do not start building. The brief is the only output.

## Credit

This skill builds on the grilling skills in [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock. Asking in rounds, recommending an answer for every question, and leaving decisions to the user all come from there.
