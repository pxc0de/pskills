---
name: refine
description: Turn an idea file into a final design by interviewing its owner. Check the claims the idea depends on, walk through the product as its user, then put every design decision to the owner in rounds, as one engineer asks another. Each question comes with a recommended answer and with approaches that existing products took. Writes design.md. Works on an idea file written by the brainstorm skill or on any draft plan. Run only when the user invokes it.
disable-model-invocation: true
---

# Refine

The user has an idea file that says what they want to build and why. It does not say how. Find every decision the design needs, settle each one with the owner, and write a design someone could build from.

The owner is most likely an engineer. Talk to them as a peer throughout, in the way "Ask as one engineer asks another" describes.

The design has to be sound, and it has to have taste. A sound design rests on facts somebody checked, leaves nothing for the builder to guess, and says what happens when a step fails. A design with taste does few things and does each of them well, so the person using it never has to wonder what happens next.

Run this skill only when the user asks for it by name.

## Before you start

Ask for the idea file's path if the user did not give one. The `brainstorm` skill writes it to `docs/idea.md`.

Work from the file and not from memory of a conversation. A new session is the better place to run this skill, because reading the file cold shows what it fails to say. If you took part in the brainstorm behind it, tell the user that once and continue if they want to stay.

You may read the project's files and outside sources at any point to check facts.

If the file cannot tell you what the product is, who it is for, or why it should exist, the idea is not ready for a design. Tell the user and recommend the `brainstorm` skill. If they want to continue anyway, ask those questions first.

## 1. Say what you understood

Write two or three sentences that describe the idea, using only the idea file. Ask the owner whether that is right before you go further. Then list anything you could not work out from the file. Each gap is something the design must answer.

## 2. Check the claims

A design fails when a fact it depends on is false. Find those facts and test them before you ask anything.

- Check every item under "Not verified".
- Check every finding about another product that the idea file labels as secondary or from memory.
- Find claims the idea file states as fact without a label, and check the ones a decision will depend on.

Check each claim at its source. Read the code, the official docs or the tool's own output. Run the tool when running it is cheap. Record each result as confirmed, false or could not check, with where you looked.

## 3. Use the product in your head

Read the idea again as the person who will use the product. Walk through these moments and write down what that person sees and does at each one.

- **The first ten minutes.** Installing it, setting it up, and the first time it does something useful.
- **An ordinary day.** The thing they do most often, from start to finish.
- **The moment it goes wrong.** The network is down, a step fails, or they made a mistake. Say what they see and what they can do next.

Every point where you had to guess what happens is a decision the design has not made. Every word such as "simple" or "fast" that names a wish without a behaviour is one too.

Also note which parts of the idea the walk-through never touched. They are candidates to cut.

## 4. Lay out the decisions

Collect the decisions from four places: the gaps from step 1, the claims that turned out false, the points where the walk-through stopped, and the questions the idea file lists under "For the design".

Most decisions depend on earlier ones. You cannot ask how login works before you know whether there are accounts. Arrange the decisions by what each one depends on, and sort them into three kinds.

- **Decisions that shape the design.** Where the data lives, what it runs on, how the main action works. These are expensive to change later. Ask them early and research them properly.
- **Ordinary decisions.** Each has real options with different costs.
- **Defaults.** The answer follows from the idea file or from an earlier decision, or only one answer is sensible.

The order of work is a decision too, and it comes last because it depends on the rest. Recommend an order in which each step is usable when it is finished and the part only this product does comes early. A distinctive part that arrives last is tested last.

## 5. Ask in rounds

At any point, you can ask some questions without guessing at an answer you have not heard. Ask all of those together as one round, then wait. The answers settle some decisions and make new questions askable. Work out the next round from them.

If a question depends on another question in the same round, move it to a later round. The owner cannot answer it well yet.

Put the decisions that shape the design first in a round. End the round with the defaults as a short list headed "Unless you object, I will also take these", one line each. The owner still sees every decision, and their attention goes to the ones that need it.

If your agent has a tool for asking the user multiple-choice questions, use it. Put your recommended option first and label it as recommended. Put each option's cost in its description. If the tool limits how many questions fit in one call, ask the rest in the next call. If you have no such tool, number the questions in plain text and write your recommendation under each one.

## Ask as one engineer asks another

Assume the owner is an engineer, and often a senior one. Write each question the way you would put it to a colleague you respect. Be direct and precise, and leave out the padding. Clear language is not simplified language.

An engineer is expert in some fields and new to others. A machine learning engineer may be deciding how login works, and a backend engineer may be deciding how a screen manages its state. Unfamiliar terms must not stop them from reaching the best answer, so give them what they need to judge it for themselves.

- **Use the correct technical term.** It is the word the owner will meet in the docs and search for later. Do not swap it for a vaguer description.
- **Explain a term that belongs to a specialty.** The first time you use it, add a clause that says what it is and why it matters for this decision. Do this once per term. Do not explain what every engineer knows, such as a cache, a queue or an API.
- **Adjust to what the owner shows.** When their answers show they know a field, stop explaining its terms. When they ask what something means, explain more in that field and nowhere else.
- **Give the whole trade-off.** Include the technical consequences, such as what breaks under load or what a later migration would involve. Do not leave out a complication to keep the question short. The owner needs enough to disagree with you.
- **One decision per question.** A question that contains "and" is often two questions.
- **Say why you are asking** when the reason is not obvious. The owner answers better when they know what the answer affects.
- **Give a concrete example.** Show what each choice would look like in use.
- **Name the cost of each option.** Say what the team must build, what can break, and what the option prevents later.
- **Ask each question once.** Word it so that agreeing with your recommendation is a "yes", and stop there. Do not end sentences with "OK?", "right?" or "does that make sense?" Do not check whether the owner followed you. If they did not, they will ask.
- **Leave out praise and reassurance.** No "great question", and no "don't worry, this part is simple".

Compare three versions of one question, put to an owner who does not work on web security.

The first assumes a specialist, and the owner cannot weigh the options.

> Opaque session IDs in HttpOnly cookies, or stateless JWTs with refresh rotation?

The second talks down. It hides the terms, drops the trade-off and asks for agreement the owner cannot give honestly.

> When you log in, the app has to remember it's you. We can keep a note on our side, or give your browser a pass to show. Let's keep the note on our side, OK?

The third gives the owner the terms and the consequences.

> How should the browser prove who is logged in? The two usual answers are a session cookie and a JWT. A session cookie holds a random ID that the server looks up on every request. A JWT is a signed token that carries the user's identity, so the server verifies the signature and needs no lookup. I'd use the session cookie. Logging someone out takes effect at once because we delete the row. A JWT stays valid until it expires unless we keep a revocation list, and that list brings the lookup back. The cost is one database read per request, which is negligible at our size.

## Bring what exists with each question

Before you ask a round, find out how existing products handled each question in it. The `inspiration` skill describes how. Read `../inspiration/SKILL.md`, relative to this skill's folder, and follow its short form. If that file is missing, do the work directly. Find two or three products that faced the same decision, read what they do in their own code or docs, and note what it cost them. Start with the products the idea file lists under "What exists".

Use what you found in the question.

- Before the options, say in a line or two what other products do. For example, "T3 Code makes you sign in for this. Orca doesn't. It uses a key stored on your machine."
- Offer the real approaches as the options, and say which product uses each one.
- If every product does it the same way, say so. The owner should know when they are choosing to differ.
- If no product does what the owner wants, say that too. They may have found a gap, or a reason nobody built it.

Match the research effort to the decision. Read a repository for a decision that shapes the design. Take a quick look for an ordinary one. Tell the owner which claims you checked and which you recalled from memory, because they will build on them.

## Recommend an answer, and choose it with taste

Give a recommendation for every question, with the reason in one sentence. Without one, the owner has to do the analysis themselves. Choose the recommendation by these rules, in this order.

1. **Serve the centre.** The idea file names the one thing the product must do well. Prefer the option that makes that part better, even when it costs something elsewhere.
2. **Keep what the owner called good.** The idea file says what good means for this product. When an option works against it, say so in the question.
3. **Do less.** Prefer the option with fewer features, fewer settings and fewer steps. Recommend a good default over a setting. When a feature does not serve the centre, recommend cutting it from the first version and say what the cut saves.
4. **Design the failure.** An option is not complete until it says what the person sees when the step fails and what they can do next.
5. **Do the familiar thing** unless being different is the point of the product. People already know how the familiar thing works.
6. **Stay consistent.** Use one word for each thing, and make the same action work the same way everywhere. If a new decision breaks a pattern set by an earlier one, name both.
7. **Be concrete.** Recommend the default value, the limit, the wording or the rule. "A short timeout" is not a recommendation. "30 seconds, then the message 'Still waiting for the server' with a retry button" is one.

Do not bring back what the idea file lists under "Turned down" unless you found a fact the brainstorm did not have.

When the owner chooses something else, accept it and continue. Record that they chose against your recommendation, and what you recommended.

## Show it when words cannot settle it

Some questions cannot be answered in the abstract. How a screen is laid out, how an error message reads and what a command prints are examples. Put the thing itself in the question as a text sketch of the screen, the exact message or a sample of the output. When the choice is between two versions, show both.

If a question needs a working version to try before anyone can answer it, say so. Record it as an open question that needs a prototype, name what the prototype must show, and continue with the rest.

## When the idea file is wrong

The idea is the owner's, and this skill does not redesign it. But the idea file can contain a claim you found false, two parts that conflict, or a centre the walk-through could not reach. Raise each of these in the first round as a question, with the change you propose and a concrete reason. Say who is affected, what happens to them, and when. "This may not scale" is not a reason. "The gateway has no accounts, so one misbehaving host can use the whole notification quota" is a reason.

Do not invent problems to look thorough. When a part of the idea is sound, keep it.

## When the reply is not a decision

Owners often reply with a question of their own. The decision is still open.

- **"What do you suggest?"** State your recommendation again and add the reasoning you left out the first time. The decision is still the owner's.
- **"How does X do it?"** Find out, report it, and ask the question again with the new options.
- **"I don't know."** Take it as a real answer. Offer your recommendation as a provisional decision, and record it as provisional with what would settle it.
- **An example instead of a choice.** State the decision you think the example implies, and ask whether you understood it.
- **A new idea in place of your options.** Check it against the decisions already made before you accept it, and say what it conflicts with.
- **A reply that contradicts an earlier decision.** Name both decisions and ask which one stands.

## You find facts, the owner makes decisions

Do not ask the owner for anything you can look up, such as what the repository contains, what a tool supports, or how another product works. Look it up. If a lookup takes time, ask the questions that do not depend on it while you wait.

Put every decision in front of the owner, as a question or in the list of defaults. You do not settle a decision on your own judgment, including the ones that look obvious to you. Owners are surprised later by decisions an agent made without asking.

## Write the design as you go

Write `design.md` in the same folder as the idea file, using the layout in [design-template.md](./design-template.md). Write it once the first round of answers is in, and update it after each later round. A session can end without warning. Tell the user the path the first time you write the file.

If a `design.md` is already there, read it and ask the user before you replace it. Leave the idea file unchanged. It is the record of where the design started.

The design is a document to build from, not a record of the interview.

- State each decision as settled, with its reason. Put the options that lost in "Also considered".
- Use the concrete form everywhere. Write the default, the limit, the wording or the rule. A sentence the builder would have to interpret is not finished.
- Move claims you confirmed into the verified list. Correct or remove claims you found false. Keep what nobody could check under "Not verified", with what would settle each one.
- Record each place where the design departs from the idea file in "Changes from the idea", with the reason.

## Finish

The interview is complete when you have no question left to ask. Then check the whole design before you call it finished.

1. Read the design as a builder who has never seen the idea file. Fix anything that needs the idea file or this conversation to understand.
2. Walk through the three moments from step 3 again, this time using only the design. Each point where you still have to guess is one more question for the owner.
3. Name what the first version could drop and still be worth using, and ask the owner whether to drop it.
4. Give the owner a short summary. List the decisions that are expensive to change, the decisions made against your recommendation, and what is still open. Ask whether it matches their understanding, and correct the design if it does not.
5. Tell the user the path.

Do not start building. The design is the only output.

## Credit

This skill builds on the grilling skills in [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock. Asking in rounds, recommending an answer for every question, and leaving decisions to the owner all come from there.
