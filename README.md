# Google Workspace Agent Skill

An agent skill for moving an AI agent off Google Workspace REST APIs
and onto Google's official Workspace MCP servers — or building a new
Workspace agent the compliant way from the start.

It covers Gmail, Drive, Docs, Sheets, Slides, Calendar, Chat, and
Tasks. It is global: it works for any Workspace user, in any country,
with any currency. Prices in this skill are in USD, as Google
publishes them, and the skill never assumes a country, a currency,
or a region.

## Why this exists

On November 24, 2026, Google made its Workspace MCP servers and the
official Workspace CLI generally available, and published a Workspace
AI Tools Addendum. From **February 1, 2027**, technical enforcement
begins: an AI agent that still calls the Workspace REST APIs
directly is capped at Standard-tier quotas, whatever tier the project
pays for. Scaled-tier billing starts **April 1, 2027**.

That gives every team with a Gmail, Drive, or Calendar agent about
ten weeks from the announcement to find the agent, register its
OAuth client as an agent, map its REST calls to MCP tools, and
decide on a tier. This skill is the checklist for doing that, with
the traps called out: the Gmail MCP server cannot send email, data
derived from Workspace must not be kept for more than 30 days, and
choosing the Scaled tier removes the free allowance.

## Who it is for

- Developers whose AI agent reads or writes Gmail, Drive, Docs,
  Sheets, Slides, Calendar, Chat, or Tasks
- Developers building a new agent on top of Google Workspace
- Anyone responsible for a Workspace agent's quotas, costs, or
  compliance before February 1, 2027

## What is inside

- `google-workspace-agent/SKILL.md` — the skill itself: audit,
  map, set up OAuth, pick a tier, rewrite onto MCP, verify
- `google-workspace-agent/references/` — short files loaded on
  demand: migration mapping, auth, tiers, gotchas
- `google-workspace-agent/examples/gmail-triage-calendar.md` — a
  Gmail triage + Calendar agent migrated end to end, with
  placeholder data only
- `google-workspace-agent/scripts/check-migration.py` — verifies
  no direct REST calls remain, MCP config is present, and a tier
  is recorded

## Install

### Claude Code

Personal, available in every project:

```sh
mkdir -p ~/.claude/skills
cp -r google-workspace-agent ~/.claude/skills/
```

Project only, shared with the team:

```sh
mkdir -p .claude/skills
cp -r google-workspace-agent .claude/skills/
```

Restart Claude Code, then ask it to migrate your Workspace agent.
It will load the skill when the request matches the description.

### Codex

Codex supports the same Agent Skills open standard. Copy the
`google-workspace-agent` folder into the skills directory Codex
reads for your setup, then restart Codex.

### Copilot

Copilot supports Agent Skills in the same format. Copy the
`google-workspace-agent` folder into the skills directory for your
Copilot setup, then restart Copilot.

### Verify the install

```sh
python3 google-workspace-agent/scripts/check-migration.py --help
```

To verify a migrated agent, point the script at the agent's
project directory:

```sh
python3 google-workspace-agent/scripts/check-migration.py <agent-project-dir>
```

It should print `PASSED: migration verified`.

## Example prompts

Try these after installing:

- "Audit my Gmail agent and migrate it from the REST API to the Workspace MCP servers."
- "Build a new agent that triages my Gmail inbox and books time on my Calendar, using MCP."
- "Work out whether my Workspace agent needs the Standard or Scaled tier."
- "What can my Gmail agent do through MCP, and what can't it do?"
- "Check my agent's migration: are there any direct REST calls left?"

## The two dates to remember

- **February 1, 2027** — technical enforcement begins. Agents
  calling Workspace REST APIs directly are capped at Standard-tier
  quotas, regardless of tier.
- **April 1, 2027** — Scaled-tier billing starts. MCP requests on
  Gmail, Calendar, and Drive are billed from the first successful
  request, with no daily free allowance on the Scaled tier.

## Rules the skill enforces

- Audit first, migrate second — find every REST call before
  changing anything
- One OAuth client per agent, marked "Use this client for an
  AI-powered agent"
- Never promise Gmail send — the Gmail MCP server drafts, it does
  not send (send, reply, and forward are partner-only)
- No Workspace-derived data stored for more than 30 days; delete
  it on disconnect or revocation; never use it for training or
  evals
- Pick a tier on purpose and write it down — Standard is free and
  capped at 5,000 requests a day per product; Scaled bills from
  the first request
- Verify with the check script, not by reading code

## Sponsor

If this skill saves you time, you can sponsor the maintainer:

https://github.com/sponsors/jeffdrizzy

## License

MIT. See `LICENSE`.
