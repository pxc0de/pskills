# Writing test cases

A case is a situation that strains a skill, written so that an independent agent can play the user in it. Cases live in the repository under `evals/`.

```
evals/
  <skill>/
    skill.toml              settings and checks shared by every case of this skill
    cases/
      <case-id>/
        case.toml           the situation, the persona and the case's own checks
        files/              optional. Copied into the sandbox before the session
        setup.sh            optional. Run in the sandbox before the session
```

Run `stress.py check` after you write or change a case.

## What makes a case worth running

- **It strains one or two things.** Name them in `stress`. A case that tests everything explains nothing when it fails.
- **A good agent and a mediocre agent would end up in different places.** If any agent would pass, the case measures nothing.
- **It could happen.** Write the opening message the way a person types it, with the typos and the missing context.
- **It does not describe the skill.** A case written from the skill's own wording only tests whether the agent can read. Write it from the job the skill is for.

Situations that find real faults: a user who answers in three words, a user who agrees with everything, a user who contradicts an earlier answer, a user who does not know and says so, a user outside their field, a user who drags the session off course, a user who leaves early, an input file with a false claim or two parts that disagree, and a request whose honest answer is "this already exists".

## skill.toml

```toml
# What the session is for, in terms of the job. Comparators read it. Do not mention the skill's own rules.
purpose = """..."""

# What the no-skill arm is told. It must ask for the same result at the same path,
# and it must contain {opening}.
baseline_prompt = """
Turn the idea in docs/idea.md into a design I can build from. Write it to docs/design.md.

{opening}
"""

deliverable = "docs/design.md"   # optional. The file the session should write or change
max_user_turns = 14              # the conversation is cut off after this many user messages

# Optional. A fresh agent gets only the deliverable and this task, and lists what it
# would still have to ask. Fewer questions is better.
reader_task = """You are about to build the first step from this design. ..."""

extra_tools = ["Bash"]             # optional. Tools beyond Read, Write, Edit, Glob, Grep, WebSearch, WebFetch
allowed_tools = ["Bash(git *)"]    # optional. Which uses of them run without a prompt
capture = ["git log -1"]           # optional. Commands whose output the judges see as a result

[[checks]]       # run by the script
[[assertions]]   # ruled on by a judge
```

A case can override `deliverable`, `max_user_turns`, `reader_task`, `extra_tools`, `allowed_tools` and `capture`.

## case.toml

```toml
title = "A false claim stated as fact"
stress = "One sentence on what this case strains."

# The user's first message. For a skill, this is what follows the command.
opening = "docs/idea.md"

# Who the simulated user is. Write it to them, as "you".
persona = """
You are a staff backend engineer ...

Behaviours:
- If the agent proposes X, turn it down. Your reason is ...
- When asked about Y, say you don't know.
- When the agent says the file is ready and its summary matches, end the conversation.
"""

# What the user knows and will not volunteer.
hidden_facts = [
  "It has to cover two GitHub hosts at once ...",
]

[[checks]]
[[assertions]]
```

### The persona

- Give a role, the years of experience, what they know well and what they do not. The agent's tone is judged against this person.
- Say how they type: length, case, patience.
- Write behaviours as triggers. "If the agent does X, do Y" is played reliably. "Be difficult" is not.
- Always say when the conversation ends. Without that, sessions run to the turn limit.
- Include the reason behind each rejection. The simulated user is asked for it.

### Hidden facts

A hidden fact is a constraint the user would not think to mention and a good question would uncover. Each one must change what the right output is, or it only tests thoroughness for its own sake. Three or four is enough. Do not hide something a person would say in their first message.

### Planted errors

A false claim in an input file must be false. Check it at its source the day you write the case, and write the true state of things into the assertion so the judge does not have to know it. Place some claims where the skill is told to look and at least one where it is not.

## Checks

The script runs these. Use one whenever a rule can be tested without judgement.

| `type` | Needs | Passes when |
| --- | --- | --- |
| `forbid_in_agent_turns` | `pattern` | no agent message matches the regular expression. Code blocks and quotes are skipped |
| `max_questions_per_turn` | `max`, optional `allowed_share` | at most that share of agent messages (default 0.25) has more than `max` question marks |
| `require_in_deliverable` | `pattern` | the deliverable matches |
| `forbid_in_deliverable` | `pattern` | the deliverable does not match |
| `file_unchanged` | `path` | the session left that file as it was |
| `shell` | `run` | the command exits 0 when run in the sandbox after the session |

Each check also takes an `id`, a `kind`, and a `why` that states the rule as a sentence. Test a pattern on text that should match and text that should not before you rely on it. Write patterns in TOML literal strings, with single quotes, so backslashes need no escaping.

## Assertions

```toml
[[assertions]]
id = "false-webhook-claim-caught"
kind = "outcome"
text = "The agent established that GitHub has no webhook for a user's notification inbox, told the owner, and the design does not rely on one."
```

- **State what must be true, checkably.** The judge needs to be able to quote the place that decides it. "The design is good" cannot be judged. "The design says what the person sees when a step fails" can.
- **One claim per assertion,** or a failure does not say which half failed.
- **Say when it does not apply.** If it depends on something that may not happen, add "Mark this na if ...".
- **Give the judge the facts.** If the assertion depends on something true about the world, state it in the text.

### outcome or behaviour

`kind` decides how the report uses a result.

- `outcome` is something any competent agent doing this job should achieve, whatever its instructions. The idea file names the gap that existing tools leave. The false claim was caught. The user was not talked down to. Outcome results are compared across arms, and they are what shows whether the skill is better than no skill.
- `behaviour` is a rule only the skill states. The agent showed a map. Questions came in rounds. Behaviour results show whether the agent follows the skill. The other arms are expected to fail them, so they prove nothing about whether the skill is better.

When in doubt, ask whether a user would care if they never saw the skill. If yes, it is an outcome. Most of a suite's weight should be on outcomes. A skill can pass every behaviour check and still lose to no skill.
