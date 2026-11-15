---
name: writing
description: Write or edit prose so that it reads as written by a careful person. Covers docs, READMEs, commit messages, pull request descriptions, skills, emails and chat replies. Decide the point first, then remove the patterns that mark text as machine-written, then check that the meaning survived. Run only when the user invokes it.
disable-model-invocation: true
---

# Writing

Use this skill to draft new text or to edit existing text. The reader should get the point on one read and should not be able to tell that an agent wrote it.

Run this skill only when the user asks for it by name, or when another skill the user invoked calls it.

## 1. Decide what the text says

Most weak prose comes from writing before the point is clear. Answer three questions before you write or edit.

- Who reads this, and what do they already know?
- What should they know or do after reading it?
- What is the main point, in one sentence?

If you cannot write the main point in one sentence, you do not yet know what to say. Find out, or ask the user. Editing cannot fix a text that has no point.

When you edit, also note the kind of text and its tone. A commit message, a tutorial and an apology email follow different conventions. Keep the conventions of the kind you are editing.

## 2. Write it plainly

- Put the main point first. Follow it with what the reader needs to act on it.
- Write one idea per sentence. If a reader would have to go back to parse a sentence, split it.
- Name who does what. "The compiler validates queries" tells the reader more than "queries are validated".
- Choose the common word. Write "use", "help", "many" and "if" in place of "utilize", "facilitate", "numerous" and "in the event that".
- Give the number, the name or the example. "Cuts build time from 90 seconds to 40" tells the reader more than "significantly faster".
- Pick one term for each thing and repeat it. A reader takes a new word to mean a new thing.
- Stop when the content ends. Do not add a closing summary or an offer of more help.

## 3. Remove the patterns

Read the draft as its reader would, and look for the patterns below. Each one costs the reader attention and gives nothing back.

### Sentences that say nothing

- **Feeling in place of fact.** "A database that stays out of your way" describes a mood. Say what the thing does, such as "The library generates no SQL of its own." If the sentence could appear unchanged in another project's docs, cut it.
- **Trailing "-ing" phrases** that claim significance, such as "highlighting the need for", "ensuring a smooth experience" or "reflecting a broader shift". Delete the phrase, or replace it with the evidence.
- **Unnamed sources.** "Experts say" and "it is widely believed" need a name and a link. Without them, delete the claim.
- **Empty endings.** "The future looks promising" and "this is just the beginning" tell the reader nothing. End on the last fact or the next step.
- **Stacked hedges.** "It could potentially be argued that this might" means "this may". Hedge once, where the doubt is, and say what you are unsure about.
- **Filler openings.** Delete "It is worth noting that" and "It is important to remember that". Shorten "in order to" to "to" and "due to the fact that" to "because".

### Inflated wording

- **Words chosen to sound impressive.** Common ones are additionally, crucial, delve, enhance, foster, garner, intricate, landscape, pivotal, robust, seamless, showcase, tapestry, testament, underscore and vibrant. Use the ordinary word.
- **Substitutes for "is" and "has".** "Serves as", "stands as", "boasts" and "features" add nothing. Write "is" or "has".
- **"Not just X, but Y"** and "it's not about X, it's about Y". State Y.
- **Adverbs that support a weak verb.** "Greatly improves" needs the measurement. "Runs quickly" needs the time.
- **Abstract nouns borrowed from engineering.** Substrate, vector, primitive, paradigm, north star, flywheel, bedrock and "surface" as in "API surface" sound technical and usually have a concrete replacement. Use the replacement.

### Mannered style

- **Metaphor where a literal phrase exists.** "A dial worth turning" is "a parameter worth changing". Code does not "ride along" or "hold" anything. Write what it does.
- **Slogans and one-line fragments written for effect.** Rewrite them as ordinary sentences.
- **Groups of three by habit.** List as many items as there are, whether that is two or five.
- **False ranges.** "From onboarding to billing" suggests a scale that does not exist. List the topics.
- **A new synonym each time.** "The parser", "the tool" and "the utility" in one paragraph read as three things.

### Compression

- **Dropped words and symbols.** "Parser rejects bad date → exit 2, no write" makes the reader decode. Write "The parser rejects a bad date, exits with code 2, and writes nothing."
- **Undefined abbreviations and private labels.** A name you invented while working means nothing to the reader. Say the longer thing it stands for.

### Punctuation and formatting

- **Dashes that join clauses.** Replace an em dash with a period or a comma.
- **Colons as connectors.** Use a colon before a list or an example. Do not use one to join two halves of a sentence.
- **Bold everywhere.** Bold the few terms a reader scanning the page must find, and nothing else.
- **Bold labels that repeat the line.** "**Performance:** Performance improved by 20%" says it twice. Write the sentence.
- **Title Case Headings.** Use sentence case.
- **Decorative emoji** in headings and bullets. Remove them.
- **Curly quotes** in technical text. Use straight quotes.
- **Bullets that break up reasoning.** An argument needs sentences that connect. Keep lists for items a reader can scan.

### Chat residue

- **Openers and closers.** Remove "Great question!", "Certainly!", "I hope this helps" and "Let me know if you need anything else".
- **Praise for the reader.** Answer the question.
- **Announcing what you are about to say.** "Here's the thing" and "Let me explain" delay the content. Start with the content.

## 4. Check the result

Removing a pattern often produces its nearest substitute. A deleted dash comes back as a semicolon, and a deleted "crucial" comes back as "essential". Read the text once more after editing, and restructure any sentence where that happened.

Then compare the result with the original.

- Every fact, number, name and instruction in the original is still there and still correct.
- Code, commands, quotations and file paths are unchanged.
- The tone still suits the kind of text and its reader.
- You added no claim that the original did not make.

If the original was vague because the author lacked a fact, do not invent one. Mark the gap and tell the user what is missing.

## What to return

Return the finished text. When you edited an existing text, add one or two lines after it that name the main changes and any gap you could not fill. Do not list every edit.

## Credit

The unslop skill in [pstack](https://github.com/michael-denyer/pstack-claude), by Lauren Tan and ported to Claude Code by Michael Denyer, inspired this skill. Unslop is a catalogue of patterns to detect and fix. This skill adds the steps before and after the catalogue.
