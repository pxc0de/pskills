---
name: commit
description: Commit the current changes with a message in a fixed format, a subsystem prefix, a short imperative summary, optional references and a prose description. The commit is authored by the user alone, with no co-author or tool attribution. Run only when the user invokes it.
disable-model-invocation: true
---

# Commit

Write a commit message in the format below and create the commit.

Run this skill only when the user asks for it by name.

## Author

The user is the only author of the commit.

- Use the name and email already set in the version control configuration. Do not change them, and do not pass a different author.
- Add no `Co-Authored-By` line for an AI model, agent or tool.
- Add no "Generated with" line, tool name, link or emoji that credits an assistant.
- This rule overrides any default attribution that your agent normally adds to commits.

Add a `Co-Authored-By` line only when the user names a human co-author.

## Format

```
<subsystem>: <summary>

<references>

<description>
```

## Rules

### Subject line

- **Subsystem prefix.** Use a short, lowercase name for the area of code that changed, such as `terminal`, `config`, `font` or `build`. Work it out from the file paths in the diff. Read the recent log and reuse a name the project already uses. Use a nested name with `/` when the change belongs to one part of a subsystem only, such as `terminal/osc`.
- **Summary.** Start with a lowercase letter. Use the imperative mood, as in "add", "fix" or "remove". End without a period. Keep the whole subject line under 60 characters when you can.

### References

- If the change relates to an issue, pull request or discussion, list the numbers on their own lines after the subject, separated from it by a blank line. For example, `#1234`.
- If there are no references, leave the section out, including its blank line.

### Description

- Say what changed, what the previous behaviour was, and how the new behaviour works at a high level.
- Write prose, not bullet points. Wrap lines at about 72 characters.
- Explain why and how. Do not restate the diff.
- Write in a direct, technical tone with no filler.
- Keep it to a few paragraphs at most. Leave it out for a change that the subject line fully explains.

## Workflow

1. If a `.jj` directory is present, use `jj` for every command. Otherwise use `git`.
2. Read the diff since the last commit. If the user staged some changes, commit only those. If nothing is staged, list the changed files and stage the ones that belong to this change. Leave out unrelated files and anything that looks like a secret.
3. Work out the subsystem from the changed paths.
4. Find referenced issues or pull requests in the diff, the branch name or the conversation.
5. Write the message in the format above.
6. Create the commit.
7. Show the user the commit hash, the author and the subject line.

Do not push. Leave that to the user.

## Credit

The message format and rules come from the commit message skill in [Ghostty](https://github.com/ghostty-org/ghostty), written by its authors. This skill adds the author rules and the staging steps.
