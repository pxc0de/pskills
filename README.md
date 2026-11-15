# pskills

My collection of agent skills. Each skill is a folder with a `SKILL.md` file in the standard format, so it works in Claude Code, Codex, Cursor, pi and other agents that read skills.

| Skill | What it does |
| --- | --- |
| `brainstorm` | Interviews you about an idea one decision at a time, in plain language. Each question comes with a recommended answer and with approaches that existing products took. Writes a brief that an independent reviewer can critique. |
| `inspiration` | Answers a "how should we do this?" question by checking how existing products solved it, then gives options and a recommendation for your project. |
| `critique` | Reviews a brief in a new session as an independent reviewer. Checks the claims it depends on, finds the decisions most likely to be wrong, and corrects the brief with you. |
| `writing` | Writes or edits prose so that it is plain, makes its point early, and has none of the patterns that mark text as machine-written. |
| `commit` | Commits the current changes with a `subsystem: summary` message and a prose description, authored by you alone with no co-author or tool attribution. |

Every skill runs only when you invoke it. More skills will be added over time.

## Install

For any supported agent, run this in your project.

```
npx skills add pxc0de/pskills
```

The installer asks which agent you use and puts the skills in the folder that agent reads. You can also copy the folders under `skills/` into your agent's skills folder by hand. Install `brainstorm` and `inspiration` together, because `brainstorm` reads `inspiration` from the neighbouring folder.

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

`brainstorm` writes its brief to `docs/brainstorm/<topic>.md` in the current project. For an independent critique, open a new session and run `critique` on that file.

```
/critique docs/brainstorm/personal-assistant.md
```

## Credits

- `brainstorm` builds on the grilling skills in [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock.
- `commit` takes its message format and rules from the commit message skill in [Ghostty](https://github.com/ghostty-org/ghostty), written by its authors.
- `writing` was inspired by the unslop skill in [pstack](https://github.com/michael-denyer/pstack-claude), by Lauren Tan and ported to Claude Code by Michael Denyer.
