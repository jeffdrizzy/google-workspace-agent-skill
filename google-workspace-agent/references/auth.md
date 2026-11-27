# Auth: OAuth agent client, scopes, admin controls

How to authenticate an AI agent against the Workspace MCP servers.
Read this during step 3 of the skill.

## The one rule

The MCP servers only accept calls from an OAuth 2.0 client that is
marked **"Use this client for an AI-powered agent"** (Google Auth
Platform > Clients). A request from an unflagged client is rejected
with a generic invalid-token error — it does not tell you the flag
is the problem, so check the flag first when login fails.

## Create the agent's client

1. In Google Cloud Console, open Google Auth Platform > Clients.
2. Create a new OAuth 2.0 client for this agent only.
3. Mark it "Use this client for an AI-powered agent".
4. Do not reuse an existing client that a human-facing app uses.
   A tool that mixes human features with agent workflows must keep
   separate client IDs for each — one for the human flow, one for
   the agent.
5. Store the client secret like a secret: never commit it, never
   paste it into a chat, never log it. The migration record holds
   the client ID, not the secret.

## Scopes: least privilege

Request only the scopes the audit says the agent needs:

- Read-only work: read-only scopes for that product only
  (for example, Gmail read-only if the agent only reads mail).
- Draft creation: add the scope that allows creating drafts —
  and only that, if the agent never modifies anything else.
- Never ask for full mailbox, full Drive, or full Calendar scope
  "just in case". A scope the agent does not need is a scope an
  attacker can use if the agent is compromised.
- Re-check scopes after the mapping step: if a workflow was
  redesigned (for example, draft instead of send), the scopes
  change with it.

## Admin console controls

If the agent runs inside an organisation, the Workspace admin
controls agent access from the Admin console (Security > API
Controls), and the controls apply to MCP tool responses:

- **Block or trust per OAuth client ID.** The admin can block or
  explicitly trust an agent by its client ID. If the agent's
  client is not trusted, ask the admin to trust it — do not work
  around the block.
- **DLP and classification rules.** Existing data-loss-prevention
  and classification rules apply to every MCP tool response.
  An agent cannot read through a DLP rule by switching to MCP.
- **Audit logs.** Agent activity through the MCP servers is
  logged and inspectable by the admin. The migration is not
  invisible, and it should not be.
- **Human-in-the-loop confirmations.** Admins can enforce MCP
  Form Elicitation confirmations before external writes. Build
  the workflow to expect a confirmation step.

Individual users connecting a vendor's agent are also bound by the
Workspace AI Tools Addendum, not just the vendor — so a user
should check with their admin before connecting an agent to a
work account.

## Service accounts

Service accounts with domain-wide delegation reach the MCP servers
under the admin's delegation settings, without the agent-client
flag. This is reported by secondary sources (November 2026), not
confirmed in Google's own announcement — verify it against
Google's current documentation before relying on it, and prefer
the flagged user-delegated client unless the admin explicitly
chooses delegation.

## Troubleshooting sign-in

| Symptom | Check first |
| --- | --- |
| Generic invalid-token error on an MCP call | The OAuth client flag — is "Use this client for an AI-powered agent" actually on? |
| Agent works on REST but fails on MCP | Wrong client — the REST client is probably the unflagged human client. Use the agent's own client. |
| Works for one user, fails for another | Scopes and admin trust are per user and per client — check both for the failing user. |
| Admin blocked the agent | Ask the admin to trust the client ID in Security > API Controls. Do not bypass it. |
| Token works, then stops | Access revoked, or the user disconnected. The agent must delete Workspace-derived data on disconnect — see `gotchas.md`. |
