# pskills

My collection of agent skills. Each skill is a folder with a `SKILL.md` file in the standard format, so it works in Claude Code, Codex, Cursor, pi and other agents that read skills.

| Skill | What it does |
| --- | --- |
| `brainstorm` | Talks an idea through with you until it is clear. Looks at what already exists, finds the centre of the idea and its edges, offers its own suggestions for you to accept or veto, and keeps a map of the idea as it forms. Writes an idea file that says what to build and why. |
| `inspiration` | Answers a "how should we do this?" question by checking how existing products solved it, then gives options and a recommendation for your project. |
| `refine` | Turns an idea file into a final design by interviewing you. Checks the claims the idea depends on, walks through the product as its user, then asks you every design decision in rounds, as one engineer asks another. A term from outside your field is explained once, and nothing is simplified. Each question comes with a recommended answer and with approaches that existing products took. Writes `design.md`. |
| `writing` | Writes or edits prose so that it is plain, makes its point early, and has none of the patterns that mark text as machine-written. |
| `commit` | Commits the current changes with a `subsystem: summary` message and a prose description, authored by you alone with no co-author or tool attribution. |

`writing` and `commit` also run on their own when a task calls for them, such as editing a README or asking for a commit. The other skills run only when you invoke them. More skills will be added over time.

## Install

For any supported agent, run this in your project.

```
npx skills add pxc0de/pskills
```

The installer asks which agent you use and puts the skills in the folder that agent reads. You can also copy the folders under `skills/` into your agent's skills folder by hand. Install `inspiration` together with `brainstorm` and `refine`, because both read `inspiration` from the neighbouring folder.

In Claude Code you can install the collection as a plugin instead.

```
/plugin marketplace add pxc0de/pskills
/plugin install pskills@pskills
```

## Use

Invoke a skill by name, in whatever way your agent provides. In Claude Code that looks like this.

```
/brainstorm I want to build a personal assistant on top of Claude Code
/inspiration how do self-hosted apps send push notifications to a phone?
/writing tighten the README
/commit
```

When you install the collection as a Claude Code plugin, each command takes the `pskills:` prefix, as in `/pskills:brainstorm`.

`brainstorm` and `refine` work as a pair. `brainstorm` is a conversation about what to build and why, and it writes the result to `docs/idea.md` in the current project. `refine` is an interview about how it should work. Open a new session and run it on the idea file. It writes `docs/design.md` beside it and leaves the idea file unchanged.

```
/refine docs/idea.md
```

## Testing the skills

`evals/` holds test cases for each skill. A case describes a user to simulate, the facts that user holds back, and the checks a good session should pass.

The `stress-test` skill in `.claude/skills/` runs them. It is a tool for working on this repository and is not part of the published collection. Open the repository in Claude Code and invoke it.

```
/stress-test refine
/stress-test
```

It plays each case as a full conversation between separate headless agents, with the skill, without it, and with its last committed version, all on one model. Judges that do not know which is which grade the sessions and compare them. It then edits the skill to fix what the evidence shows, reruns to confirm, and leaves the changes uncommitted. Runs go to `~/.cache/skill-stress-test/`.

## Credits

- `refine` builds on the grilling skills in [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock.
- `commit` takes its message format and rules from the commit message skill in [Ghostty](https://github.com/ghostty-org/ghostty), written by its authors.
- `writing` was inspired by the unslop skill in [pstack](https://github.com/michael-denyer/pstack-claude), by Lauren Tan and ported to Claude Code by Michael Denyer.
