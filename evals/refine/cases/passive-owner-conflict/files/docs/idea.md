# Clientboard idea

Status: outcome of a brainstorm on 2026-11-12. It says what to build and why, and leaves how to the design. Nothing is built. The `refine` skill turns this file into `design.md`.

## The idea

Clientboard gives each client of an ML consultancy a web page with the evaluation results of the models built for them. It replaces the PDF reports the team exports and emails today.

## Who it is for

Two groups at each client. Managers who are not technical want to know whether the model is good enough to ship. One technical reviewer per client wants to open individual failure examples. Today both get a PDF by email, and the reviewer writes back to ask for examples.

The team that publishes results is twelve ML engineers. They run evaluations as Python jobs and look at them in Streamlit apps on their own machines.

## Why it should exist

Hosted experiment trackers such as Weights & Biases and MLflow show results well, but they are built for the team that trains the model. Sharing one with a client means giving the client an account in the team's own workspace. A PDF is safe to send and cannot be explored.

## The map

- **Centre:** a client opens one link and sees the current results for their model, and nothing that belongs to another client
- **Does**
  - shows headline metrics for the latest evaluation run
  - lets the reviewer open individual failure examples
  - clients always see live results as soon as an evaluation run finishes
  - every result a client sees has been signed off by an engineer first
  - keeps earlier runs, so a client can compare with last month
- **Not**
  - a tool for training or tracking experiments
  - a place where clients upload data
- **Good means:** it is fast, it is secure, and it is simple to operate

## In the owner's words

"Right now I export PDFs and email them, which is embarrassing."

"I don't want to become a web company. It has to more or less run itself."

## What exists

**Weights & Biases reports** (wandb.ai)

- Reports can be shared by link. Viewers outside the team see a read-only page.
- Source: from memory, not checked.

**Streamlit Community Cloud** (streamlit.io/cloud)

- Hosts a Streamlit app from a repository and can restrict viewers by email address.
- Source: from memory, not checked.

## For the design

- How does a client prove who they are?
- Where does it run, and who keeps it running?
- How do results get from an evaluation job onto the page?
- What does the reviewer see when they open a failure example?

## Not verified

- Streamlit Community Cloud can restrict a private app to a list of viewer email addresses. Its docs would settle it.
