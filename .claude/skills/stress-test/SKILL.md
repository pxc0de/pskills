---
name: stress-test
description: Stress-test the skills in this repository and improve them from the results. Independent headless agents with no shared context play out full conversations against simulated users who hold back facts, once with the skill, once without it and once with its previous version, all on one model below the best available. Fresh judges grade every run and compare the arms blind. Then edit the skill to fix what the evidence shows and rerun to confirm. Tests one named skill or all of them. Run only when the user invokes it.
disable-model-invocation: true
---

# Stress test

Find out whether a skill makes an agent better at its job, where it breaks, and what to change. Then make the change and prove it helped.

The testing is done by a script, [scripts/stress.py](./scripts/stress.py), which starts separate `claude -p` processes. You are the engineer who reads the evidence and edits the skill. You do not play any part in the test conversations yourself, and you do not grade them.

Run this skill only when the user asks for it by name. A full run takes real time and money.

## How the test works

Each test case is a situation built to strain the skill: a user who answers in three words, an idea that already exists, a file with a false claim in it. The script plays every case as a full conversation between two processes.

- **The agent under test** runs in an empty sandbox folder with Claude Code's normal tools. It receives the skill the way a user's invocation delivers it.
- **The simulated user** plays a persona from the case file. The persona holds facts it will not volunteer. They come out only if the agent asks the right question or says something that contradicts them. How many of those facts reach the final output is the most objective number in the report.

Each case runs in up to three arms, so the skill is compared with something.

| Arm | What the agent gets |
| --- | --- |
| `skill` | the skill as it is in the working tree |
| `none` | no skill, only a plain request for the same result |
| `previous` | the skill as it was at an earlier git ref, when it differs |

After each conversation, fresh processes grade it. None of them knows which arm it is looking at.

- **Script checks** are regular expressions and shell commands. They cost nothing and cannot be argued with.
- **A judge** reads the transcript and the output and rules on each written assertion, with a quote as evidence. It also reports problems no assertion covers.
- **A reader** gets only the output file and lists the questions it would still have to ask before using it.
- **A comparator** gets two sessions of the same case, unlabelled, and says which output is better and which conversation the user would have preferred.

No process shares context with another, and none sees the user's settings, memory, CLAUDE.md or installed skills. Every process in one run uses the same model.

## 1. Work out what to test

Read the user's request for four things.

- **Which skills.** One or more names, or all of them when none is named.
- **Which model.** Use `sonnet` unless the user names another. See "Choosing the model" below.
- **Whether to improve.** Improve the skill unless the user asks for a report only.
- **How thorough.** The default is two repeats of each case in each arm. Use three when the user asks for a thorough run, and one for a quick look.

Run the script from the repository root to see what exists.

```
python3 <this skill's folder>/scripts/stress.py list
```

If a skill the user asked for has no cases, write them before you go on. Read [references/cases.md](./references/cases.md) first. Write at least two cases, run `stress.py check`, and tell the user what you wrote and what each case strains. Cases live in `evals/<skill>/` and are part of the repository.

## Choosing the model

Run the test on a model below the best one available. Today that means `sonnet` or `opus`, and `sonnet` when the user does not say.

The reason is that a skill is read by whatever model the user happens to run. An instruction that only the strongest model follows is a weak instruction, and the weaker model shows where the wording is unclear. Do not pass the top model unless the user asks for it by name.

One run uses one model for every agent, simulated user and judge. Never mix models inside a run, and never compare numbers from runs on different models. If you rerun to confirm a change, use the model of the first run.

## 2. Run it

Print the plan first, and tell the user in one line how many conversations it is, on which model.

```
python3 <this skill's folder>/scripts/stress.py run <skill>... --model sonnet --dry-run
```

Then run it without `--dry-run`. Start it as a background command with a timeout of two hours, because a conversation with research in it takes several minutes and a full run can take an hour. Do not poll it. You are told when it ends. If your agent cannot run a command in the background, run it in the foreground with the longest timeout you have, one skill at a time.

Useful options:

- `--repeats N` sets the runs per case and arm.
- `--cases a,b` runs only those cases.
- `--arms skill,none` leaves out an arm.
- `--previous <git ref or folder>` chooses the earlier version. The default is `HEAD`, so an uncommitted edit is compared with the last commit.
- `--max-cost 25` stops starting new work once the run has spent that many dollars.
- `--parallel N` sets how many conversations run at once. The default is 4.

The script prints one line as each conversation ends and the path of `report.md` at the end. Run folders go to `~/.cache/skill-stress-test/`, outside the repository, so that no test agent can see the case files.

## 3. Read the evidence

Read `report.md`. It has a scoreboard for each arm, the blind comparison results, every check the skill failed with a quote, the hidden facts the skill missed, and what the judges noticed.

Do not act on the report alone. For every failure you might act on, open the transcript it cites and read the turns around the quote. Judges misread, simulated users drift, and a regular expression can match the wrong thing. Sort each failure into one of five kinds.

- **A fault in the skill.** An instruction is missing, unclear, contradicted by another, or too weak to hold on this model. This is the only kind you fix in the skill.
- **A fault in the case.** The persona made the right behaviour impossible, the assertion tests something the skill never promised, or a pattern matched innocent text. Fix the case file and tell the user.
- **A fault in the judge.** The transcript shows the judge was wrong. Note it and move on. If the same assertion is misjudged twice, its wording is unclear. Rewrite it.
- **A limit of the test.** A tool call the sandbox refused, a turn limit set too low, or behaviour that needs something a headless run lacks. The multiple-choice question tool is the main example. It does not exist in these runs, so the skill's plain-text path is the only one tested.
- **Noise.** It failed in one repeat of one case and passed everywhere else. Leave it unless it comes back.

Then read the four signals that matter more than any single failure.

1. **Skill against no skill.** If the skill does not beat the plain request on outcome checks and blind comparisons, the skill is not earning its length. Say so to the user plainly. Do not tune a skill that loses overall without telling them.
2. **What the other arm did better.** The comparators record this even when the skill wins. It shows what the skill suppresses, such as a question the plain agent asked on its own.
3. **Hidden facts that never came up.** The skill is not leading the agent to ask about that area.
4. **Checks that no skill also passed every time.** The instruction behind such a check may not be needed. A shorter skill is followed better.

## 4. Improve the skill

Skip this step when the user asked for a report only, or when nothing above noise is a fault in the skill.

Choose at most three causes to fix in one round. With more, the confirming run cannot tell which change did what.

- **Fix the cause in general terms.** Never name a test case, a persona or a product from a case in the skill, and do not write an instruction that would help only that case. If you cannot state the fix as something true of every session, it is the wrong fix.
- **Say why.** The reader of a skill is a model, and it follows a reason better than an order. Write the reason next to the instruction. Capital letters and words such as "always" and "never" used for force are a sign that the reason is missing.
- **Change or remove before you add.** Look first for the sentence that caused the behaviour and rewrite it. A skill that gains a paragraph every round gets worse, because each new instruction weakens the rest.
- **Keep the owner's intent.** You are fixing how well the skill does what its owner designed it to do. If the evidence says the design itself is wrong, report that and leave the decision to the user.
- **Match the file.** Keep its voice, its structure and its level of detail. If the repository has a `writing` skill, follow it for the prose.

Edit the files under `skills/`. Do not commit.

## 5. Confirm the change

An edit is a guess until a run confirms it. Rerun the cases whose failures you tried to fix, plus one case you did not touch, to catch a regression. Compare the new version with the version you started from. The first run printed the folder that holds it.

```
python3 <this skill's folder>/scripts/stress.py run <skill> --model <same model> \
  --cases <affected>,<one other> --arms skill,previous \
  --previous <first run folder>/snap/current/skills
```

Keep an edit when the failure it targeted is gone in most repeats and nothing else got worse beyond noise. Otherwise restore the file from that same folder and tell the user the fix did not hold.

Do at most two rounds of improving and confirming unless the user asks for more. Stop earlier when nothing above noise is left.

## 6. Tell the user

Report in this order, briefly.

1. What ran: the skills, the model, the number of conversations and the cost.
2. Whether each skill beats no skill, and its previous version, with the numbers from the scoreboard.
3. What you changed in each skill, and the evidence for each change. Say which changes the confirming run supported and which you reverted.
4. What you found and left alone, and why: noise, a limit of the test, or a decision that belongs to the user.
5. Any case files you wrote or changed.
6. The paths of the reports.

State the limits when they bear on the result. The numbers rest on a few runs. The simulated user is more patient and more articulate than a person. Taste and tone are only partly measurable, so the user's own sessions remain the final check.

All changes are uncommitted, so the user can read the diff before keeping any of it.
