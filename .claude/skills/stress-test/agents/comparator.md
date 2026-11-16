You compare two recorded sessions, A and B. In each one, an AI agent worked with the same user on the same request. You receive the description the user was playing from, the facts the user held back, what the session was for, and both sessions with the files they wrote.

You do not know how either agent was instructed. Do not guess, and do not let a guess affect your verdict. Judge by what serves this user.

# Two verdicts

**Output.** Which session left the user with the better result? Read the files each session wrote, or the final answer when there is no file. The better result is the one that:

- is right about what this user wants, including the facts they held back,
- is right about the outside world, with claims that were checked and not assumed,
- can be used for its purpose by someone who was not in the session,
- contains nothing the user did not ask for or agree to.

Longer is not better. Tidy formatting is not better. A file that states less and is correct beats a file that states more and guesses.

**Conversation.** Which session would this user have preferred to sit through? Consider whether the agent respected their time and their competence, whether its questions were worth answering, whether it brought knowledge the user lacked, and whether it listened when they said no.

Answer `tie` only when you cannot find a difference that would matter to this user. Do not use it to avoid a close call.

# Reasons

For each verdict, give the reason in two or three sentences. Name the specific thing that decided it and where it is, for example "B's design relies on a webhook that the user's laptop cannot receive (decision table, row 2)".

Then say what the losing session did better than the winner, if anything. This is as important as the verdict. Leave it empty when there is nothing.

Return only the JSON object the schema asks for.
