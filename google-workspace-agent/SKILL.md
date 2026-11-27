---
name: google-workspace-agent
description: Migrate an AI agent from Google Workspace REST APIs to Google's official Workspace MCP servers before the February 1, 2027 enforcement deadline, or build a new Workspace agent the compliant way from the start. Covers Gmail, Drive, Docs, Sheets, Slides, Calendar, Chat, and Tasks: audit existing REST calls, map them to MCP tools, set up the OAuth agent client, pick Standard vs Scaled tier, and handle the Gmail send, 30-day retention, and confirmation-prompt gotchas. Use when someone asks to migrate a Gmail agent to MCP, move a Workspace agent off REST APIs, build an agent that uses Gmail, Drive, Docs, Sheets or Calendar, fix a Workspace agent's quotas, or prepare for the February 2027 Workspace MCP deadline.
---

# Google Workspace Agent

Move an AI agent off Google Workspace REST APIs and onto Google's
official Workspace MCP servers — before Google enforces it — or build
a new Workspace agent the compliant way from the start.

## The deadline, in one paragraph

On November 24, 2026, Google made its Workspace MCP servers and the
official Workspace CLI (`gwscli`) generally available, alongside a
Workspace AI Tools Addendum. From **February 1, 2027**, technical
enforcement begins: an AI agent that still calls the Workspace REST
APIs directly is capped at Standard-tier quotas, whatever tier the
project pays for. Scaled-tier billing starts **April 1, 2027**.
The REST APIs do not disappear — but for an agent, staying on them
after February 1 means running slow, in breach of the terms, on the
free tier's limits. This skill migrates the agent properly, and
proves it with a check script.

Sources for the dates and limits in this skill: the Google Workspace
Updates blog post of November 24, 2026, "Simplifying agent access
while keeping organizations in control", and Google's "Understand
Google Workspace API and MCP server pricing and billing tiers"
developer page (updated November 24, 2026). Where a fact comes from a
secondary source rather than Google, this skill says so.

## When to use this skill

Use this skill when the user asks for any of these:

- Migrate an agent from the Gmail, Drive, Docs, Sheets, Slides,
  Calendar, Chat, or Tasks REST API to Workspace MCP servers
- Build a new AI agent that reads or writes Gmail, Drive, Docs,
  Sheets, Slides, Calendar, Chat, or Tasks
- Fix a Workspace agent that is hitting quota limits, or work out
  whether it needs the Standard or Scaled tier
- Set up OAuth for an AI agent that touches Google Workspace
- Work out what a Workspace agent is allowed to do with Gmail
  (read, draft) and what it cannot do (send, reply, forward)
- Prepare an agent for the February 1, 2027 Workspace MCP
  enforcement deadline, or the April 1, 2027 Scaled billing start

Do not use this skill for a human-facing app that calls the Workspace
REST APIs with no AI agent involved — those apps stay on REST, and
the MCP requirement does not apply to them. Do not use it for a
non-Google email or calendar provider. If the user only wants a
plain Gmail or Calendar integration with no agent, say so and do not
migrate anything.

## Scope: which products, which servers

Eight Google-hosted MCP servers are generally available, one per
product, at `https://<product>mcp.googleapis.com/mcp/v1`:

| Product | MCP server host |
| --- | --- |
| Gmail | `gmailmcp.googleapis.com` |
| Drive | `drivemcp.googleapis.com` |
| Docs | `docsmcp.googleapis.com` |
| Sheets | `sheetsmcp.googleapis.com` |
| Slides | `slidesmcp.googleapis.com` |
| Calendar | `calendarmcp.googleapis.com` |
| Chat | `chatmcp.googleapis.com` |
| Tasks | `tasksmcp.googleapis.com` |

Keep (Google Keep) was announced as coming soon at launch; it is not
a generally available MCP server yet. Do not plan a migration around
it — check Google's current server list first.

The Standard and Scaled tiers start with Gmail, Drive, and Calendar.
The other products' MCP servers share the same tier model, but
Scaled-tier MCP billing applies to the Gmail, Calendar, and Drive
MCP servers (Google's pricing page, November 24, 2026).

## Rules that apply to every migration

1. Audit first, then migrate. Find every Workspace REST call in the
   agent's code, config, and prompts before changing anything.
   Do not start with code.
2. Work on a separate branch. Open a pull request for review. Merge
   only when the user explicitly says yes.
3. One agent, one OAuth client. Create a new OAuth 2.0 client for
   the agent and mark it "Use this client for an AI-powered agent"
   (Google Auth Platform > Clients). Never reuse a human app's
   client for an agent, and never mix human and agent flows on one
   client ID. See `references/auth.md`.
4. Never promise what the MCP servers cannot do. The Gmail MCP
   server cannot send, reply to, or forward an email, and cannot
   edit a draft after creating it — those tools are partner-only.
   It can search and read threads, create and list drafts, and
   manage labels. Design the workflow around that, do not claim
   the agent sends mail when it only drafts it. See
   `references/gotchas.md`.
5. No long-term memory from Workspace data. Data derived from
   Workspace — embeddings, memory indexes, user profiles,
   organisational graphs, findings — must not be stored for more
   than 30 days, and must be deleted when the user disconnects or
   revokes access. Never use Workspace data for model training,
   fine-tuning, evaluation datasets, or distillation. See
   `references/gotchas.md`.
6. Only process Workspace data to fulfil active, user-authorised
   tasks. Do not collect, keep, or index it beyond the task in hand.
7. Pick a tier on purpose and write it down. Standard is free and
   capped at 5,000 requests per day, per project, per product, and
   that cap cannot be raised. Scaled lifts the cap but bills from
   the first successful MCP request, with no daily free allowance
   on MCP. Record the choice in the migration record. See
   `references/tiers.md`.
8. Verify with the check script, not by reading code. Run
   `scripts/check-migration.py` against the agent's project. It
   must pass before the migration is called done.
9. Never invent a Google endpoint, tool name, quota, or price.
   If a tool or limit is not in the references or in Google's
   current documentation, check the live MCP server's tool list
   first (`tools/list` answers without an OAuth token) or say you
   do not know. Prices and quotas change; the numbers in this skill
   are as published on November 24, 2026.

## Procedure

Work through the steps in order. Do not skip step 1. Each step ends
with a check; do not move on until the check passes.

### Step 1 — Audit the agent's current Workspace usage

Before changing anything, inventory what the agent actually does:

- List every Workspace product the agent touches: Gmail, Drive,
  Docs, Sheets, Slides, Calendar, Chat, Tasks.
- For each product, list every REST call: endpoint, method, and
  what the agent does with the result. Search the code, config,
  prompts, and any MCP or plugin configuration for the REST
  hostnames: `gmail.googleapis.com`, `drive.googleapis.com`,
  `docs.googleapis.com`, `sheets.googleapis.com`,
  `slides.googleapis.com`, `calendar.googleapis.com`,
  `chat.googleapis.com`, `tasks.googleapis.com`, and
  `www.googleapis.com`.
- List every place the agent stores Workspace-derived data:
  vector stores, memory indexes, caches, logs, embeddings.
  Note how long each one keeps it.
- List every place the agent sends, shares, or publishes
  Workspace data: outbound email, shared files, webhooks, other
  services.
- Write the findings down as a migration record (see step 6).
  One row per REST call: product, endpoint, purpose, MCP
  replacement (or "no MCP equivalent — redesign needed").

Check: the audit lists every REST call and every store of derived
data, or states explicitly that there are none. If the audit is
incomplete, stop here — a migration built on a partial audit will
leave a REST call behind, and that call will be throttled from
February 1, 2027.

### Step 2 — Map REST calls to MCP tools

For each REST call in the audit, find its MCP replacement. Read
`references/migration.md` for the per-product mapping and for what
has no equivalent.

- Most read operations map cleanly: search and read threads,
  read files, read documents, list events.
- Some write operations do not: Gmail send, reply, forward, and
  editing a draft after creation are partner-only on the Gmail MCP
  server. Drive move, rename, share, trash, and comments have no
  MCP equivalent in the current servers. For each of these, decide
  with the user: redesign the workflow (for example, draft instead
  of send, and let a human send), or keep that one step out of the
  agent entirely.
- Docs, Slides, and Tasks are close to REST parity; Gmail and
  Drive are the thinnest. Budget the redesign time there.
- Confirm each mapping against the live server's tool list
  (`tools/list` on `https://<product>mcp.googleapis.com/mcp/v1`)
  before writing code. Tool catalogues change; the mapping in the
  references is as reported in November 2026.

Check: every REST call has a row that says either its MCP tool
name or "no equivalent — redesigned as …". No row may say "to be
decided".

### Step 3 — Set up the OAuth agent client

Read `references/auth.md`, then:

- Create a new OAuth 2.0 client in Google Cloud for this agent
  only, and mark it "Use this client for an AI-powered agent"
  (Google Auth Platform > Clients). Do not reuse an existing
  human-app client.
- Request only the scopes the audit says the agent needs, least
  privilege first. Gmail read-only scopes if the agent never
  writes; add draft-creation scope only if the workflow creates
  drafts. Never ask for full mailbox or full Drive scope "just in
  case".
- If the agent runs inside an organisation, ask the Workspace
  admin to check the Admin console controls (Security > API
  Controls): the agent's client ID may need to be explicitly
  trusted, and DLP, classification, audit-log, and
  human-in-the-loop confirmation settings apply to MCP tool
  responses and external writes.
- Service accounts with domain-wide delegation reach the MCP
  servers under the admin's delegation settings, without the
  agent-client flag (reported by secondary sources, November
  2026 — verify against Google's current docs before relying on
  it).

Check: the agent authenticates against an MCP server with its own
flagged client and can list tools. A request from an unflagged
client is rejected, so this check catches a wrong client early.

### Step 4 — Pick Standard or Scaled tier, on purpose

Read `references/tiers.md`, then decide with the user:

- Estimate the agent's daily MCP requests per product from the
  audit. Count tool calls, not user messages — one user request
  can trigger several MCP calls, and composite tools can count
  as multiple billing units.
- Standard tier: free, no billing account needed, 5,000 requests
  per day, per project, per product. The cap cannot be raised on
  Standard, and quota-increase requests are not possible on it.
  If the estimate fits comfortably inside 5,000 a day per product,
  stay on Standard. Google reports more than 99% of active
  developers sit within Standard limits.
- Scaled tier: higher quotas, but it applies to the whole Google
  Cloud project, needs a linked billing account, and from April 1,
  2027 MCP requests on Gmail, Calendar, and Drive are billed from
  the first successful request — $0.10 Light, $0.20 Medium, $0.25
  Plus, $0.50 Premium per 1,000 requests — with no daily free
  allowance on MCP. Switching to Scaled also removes the free
  5,000 MCP requests a day. Only choose Scaled if the estimate
  genuinely exceeds Standard, and warn the user about the cost
  before enabling it.
- If the agent needs higher quotas, enrol in Scaled and submit a
  quota request. Do not assume enrolment alone raises the limits.

Check: the tier choice, the estimate behind it, and the expected
monthly cost (or $0 on Standard) are written in the migration
record. A tier nobody wrote down is a tier nobody chose.

### Step 5 — Rewrite the agent onto MCP, gotchas first

Rewrite the agent's Workspace access to call the MCP servers,
then fix the three gotchas before testing anything else:

1. **Gmail send.** If the old workflow sent email, redesign it:
   the agent creates a draft, a human reviews and sends it, or
   the workflow stops at the draft. Never present a draft as a
   sent email, and never route around the limit by calling the
   Gmail REST API directly — that is exactly what the February 1
   enforcement throttles.
2. **Retention.** Give every store of Workspace-derived data a
   30-day expiry, and a purge on disconnect or revocation. If the
   agent kept a long-term memory index of the inbox, rebuild the
   workflow so the index is short-lived or dropped. See
   `references/gotchas.md`.
3. **Confirmation prompts.** External writes (creating files,
   sharing, sending anything the agent is allowed to send) may
   require a human-in-the-loop confirmation via MCP Form
   Elicitation, depending on admin settings. Build the workflow
   to expect a confirmation step; do not try to bypass it.
- Keep the REST code out. Delete or disable the old REST calls;
  do not leave them commented out as a fallback. A fallback that
  still fires is still a REST call.
- Use `gwscli`, the official Workspace CLI, for terminal or
  sandboxed agents where an MCP client is not available. Do not
  hard-code its flags in brittle scripts — Google warns its
  command signatures and JSON output may change without backward
  compatibility.

Check: the agent completes its main workflow end to end through
MCP only, with the draft-instead-of-send and confirmation steps
visible in the flow.

### Step 6 — Write the migration record and verify

Write a migration record at the root of the agent's project
(`workspace-migration.json` or `MIGRATION.md`). It must contain:

- The audit summary: products used, REST calls found, MCP
  replacements chosen.
- The OAuth client ID (not the secret) and the scopes granted.
- The tier chosen (Standard or Scaled), the daily estimate, and
  the expected cost.
- The gotcha decisions: how Gmail send is handled, the retention
  policy, and how confirmations are handled.
- The date of the migration and the date the check script last
  passed.

Then run the check script:

```sh
python3 google-workspace-agent/scripts/check-migration.py <agent-project-dir>
```

It verifies three things: no direct Workspace REST calls remain
in the agent's code or config, an MCP configuration is present,
and a tier selection is recorded. It exits 0 on pass and non-zero
with a clear message on fail. Fix every failure; do not ship a
migration the script fails.

Check: the script prints `PASSED: migration verified` and the
record is committed. The migration is not done until both are
true.

### Step 7 — Test in production conditions, then watch the dates

- Test the migrated agent against real Workspace data, not mocks,
  for every product it touches. A mock that passes does not prove
  the MCP tools return what the agent expects.
- Test the failure paths: quota exceeded on Standard, a
  confirmation declined by the human, a draft the agent cannot
  send, access revoked mid-task. Each one must fail clearly, not
  silently.
- Watch the two dates: **February 1, 2027** (enforcement — REST
  calls from agents capped at Standard quotas) and **April 1,
  2027** (Scaled billing starts — check the first bill, and
  confirm the tier is still the right one).
- Re-check the live MCP tool lists after any Google announcement.
  New tools appear and partner-only gates change; a mapping made
  in November 2026 can go stale.

Check: the agent works on real data, the failure paths fail
clearly, and the user knows the two dates and what happens on
each.

## Common mistakes

- Migrating the code but keeping the old OAuth client. The MCP
  servers reject unflagged clients, so the agent fails at login
  with a generic error.
- Reusing one OAuth client for a human app and an agent. Keep
  them separate, or the agent's flag and scopes leak into the
  human flow.
- Assuming Gmail can send. It cannot, without partner access.
  Draft-then-human-send is the honest workflow.
- Keeping a permanent vector index of the inbox. The 30-day cap
  and the delete-on-disconnect rule make that non-compliant.
- Choosing Scaled "to be safe". Scaled removes the free 5,000
  MCP requests a day and bills from the first successful request.
  It costs money from April 1, 2027 even for a quiet agent.
- Leaving a REST fallback in the code. If it can fire, it will
  fire — and from February 1, 2027 it runs at Standard quotas
  in breach of the terms.
- Estimating cost per user message instead of per MCP call. One
  message can trigger many calls, and composite tools count as
  multiple billing units.

## References (load on demand)

- `references/migration.md` — REST → MCP mapping per product,
  what changes and what breaks
- `references/auth.md` — OAuth agent client setup, scopes, admin
  console controls
- `references/tiers.md` — Standard vs Scaled tiers, quota
  increases, pricing as published November 24, 2026
- `references/gotchas.md` — Gmail send, 30-day retention, no
  training or evals, confirmation prompts
- `examples/gmail-triage-calendar.md` — a Gmail triage + Calendar
  agent migrated end to end, with placeholder data only
- `scripts/check-migration.py` — verifies no REST calls remain,
  MCP config is present, and a tier is recorded
