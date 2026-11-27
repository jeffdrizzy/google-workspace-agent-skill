# Gotchas: the traps that break Workspace agents

The three traps that break most Workspace agent migrations, plus
confirmation prompts. Read this before step 5 of the skill.

Source: the Workspace AI Tools Addendum, published November 24,
2026, as summarised in Google's announcement and in independent
reporting of the addendum's text. The addendum supplements the
Google APIs Terms of Service and wins where the two conflict.

## 1. Gmail cannot send — partner-only

The Gmail MCP server can search and read threads, create and list
drafts, and manage labels. It **cannot** send an email, reply to
one, forward one, or edit a draft after creating it. Those tools
exist on the server but require partner access and are not
generally available. Google has not publicly detailed how a
developer qualifies for partner access — treat it as unavailable.

What to do instead:

- The agent drafts; a human reviews and sends. That is the honest
  workflow, and it is the one to build.
- Never present a draft as a sent email. The user must be able to
  tell the difference between "drafted" and "sent".
- Never route around the limit by calling the Gmail REST API
  directly for sending. That is exactly the call the February 1,
  2027 enforcement throttles to Standard quotas, and it breaches
  the addendum.
- If a workflow cannot work without the agent sending mail, say
  so plainly and stop — do not build a workaround.

Also missing from the Gmail MCP server: filters, settings,
attachment download, and push notifications. Drafts with
attachments are reported as not supported yet. Move those jobs out
of the agent.

## 2. The 30-day retention cap on Workspace-derived data

The addendum caps how long you may keep "Google Technical
Information" at **30 days**. That term covers anything derived
from Workspace data, including:

- Vector embeddings built from emails or documents
- Memory indexes and search indexes over Workspace content
- User profiles and organisational graphs derived from it
- Findings and summaries the agent stored for later use

Rules that follow from the cap:

- Give every store of Workspace-derived data a 30-day expiry, and
  enforce it automatically. A monthly rebuild is not a plan — an
  automatic TTL eviction is.
- Delete Workspace data as soon as the user disconnects the agent
  or revokes access. Wire the revocation webhook or callback to a
  purge; do not leave it as a manual step.
- Only process Workspace data to fulfil active, user-authorised
  tasks. Do not collect, keep, or index it beyond the task in
  hand.
- An agent that built a long-term index of the inbox — for
  example, to answer questions about last year's contracts — has
  to rebuild it monthly or drop it. Say that to the user before
  migrating, not after.

## 3. No training, no evals, no competing products

Workspace data must not be used for:

- Model training or fine-tuning
- Evaluation datasets or distillation
- Systematic probing of Workspace services
- Building a product similar to a Workspace service

This applies even to data the user authorised the agent to read.
Reading an email to answer a question is allowed; feeding that
email into a training set is not.

## 4. Confirmation prompts before external writes

Admin settings can require a human-in-the-loop confirmation
before external writes, enforced through MCP Form Elicitation.
That means:

- Creating files, sharing, or sending anything the agent is
  allowed to send may pause for a human to confirm.
- Build the workflow to expect the confirmation step. Show the
  user what is waiting for confirmation, and what happens if
  they decline.
- Do not try to bypass, auto-approve, or pre-confirm on the
  user's behalf. A confirmation the agent skips is a control
  the agent broke.
- Test the decline path: a declined confirmation must fail
  clearly, with the work left in a safe state — not half done,
  and not silently retried.

## 5. The February 1, 2027 enforcement is a quota cap, not a block

From February 1, 2027, agents calling Workspace REST APIs
directly are limited to Standard-tier quotas, regardless of tier.
Google describes no outright block on that date — the REST calls
keep working, slowly, in breach of the terms, and Google may cut
off access or suspend the account for breaching the addendum.
Do not tell a user "REST stops working on February 1". Tell them
the true version: it gets throttled to the free tier's limits and
puts the account at risk.
