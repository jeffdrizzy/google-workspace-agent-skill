# Migration: REST → MCP mapping

How to move each product's REST calls onto the Workspace MCP
servers. Read this during step 2 of the skill.

## The servers

Each product has its own Google-hosted MCP server, speaking standard
Model Context Protocol JSON-RPC over HTTPS:

```
https://<product>mcp.googleapis.com/mcp/v1
```

For example: `https://gmailmcp.googleapis.com/mcp/v1`,
`https://drivemcp.googleapis.com/mcp/v1`,
`https://calendarmcp.googleapis.com/mcp/v1`.

You can list a server's tools without an OAuth token — send a
`tools/list` request to the endpoint. Do that before writing code:
tool catalogues change, and the mapping below is as reported in
November 2026.

Keep (Google Keep) was announced as coming soon at launch. It is not
a generally available MCP server yet — do not plan a migration
around it.

## What changes, in general

- The agent stops calling `*.googleapis.com` REST endpoints
  directly and instead calls tools on the MCP server for that
  product, authenticated with its flagged OAuth agent client.
- MCP tools return relevant context inside Workspace's security
  boundary, instead of the agent downloading emails and files line
  by line over REST.
- Admin controls apply to MCP tool responses: DLP and
  classification rules, audit logging, and human-in-the-loop
  confirmation before external writes.
- Composite MCP tools can trigger several underlying API calls, so
  one tool invocation can count as multiple billing units on the
  Scaled tier. Count tool calls, not user messages, when you
  estimate usage.

## Per-product mapping

### Gmail — the thinnest server, plan the redesign here first

What the Gmail MCP server can do (as reported November 2026):

- Search threads and messages, read threads and messages
- Create, list, and get drafts
- Manage labels (list, and apply labels to messages)
- Trash and spam handling

What it cannot do — partner-only, or missing entirely:

- **Send, reply, forward** — the tools exist on the server but
  require partner access and are not generally available.
- **Edit a draft after creating it** — partner-only.
- Filters, settings, attachment download, push notifications —
  not available through the MCP server.
- Drafts with attachments are reported as not supported yet.

REST calls to redesign, not translate:

| Old REST call | MCP replacement |
| --- | --- |
| `users.messages.list` / `users.threads.list` | Search threads / messages tool |
| `users.messages.get` / `users.threads.get` | Read thread / message tool |
| `users.drafts.create` | Create draft tool |
| `users.drafts.list` / `users.drafts.get` | List / get drafts tool |
| `users.labels.list` | List labels tool |
| `users.messages.send` | **No equivalent.** Redesign: agent creates a draft, a human reviews and sends it. |
| `users.messages.send` (reply / forward) | **No equivalent.** Same redesign as send. |
| `users.drafts.update` | **No equivalent (partner-only).** Redesign: delete the draft and create a new one, or let a human edit it. |
| `users.settings.filters.*` | **No equivalent.** Move filter management out of the agent. |

### Drive — search and read map well, management does not

What the Drive MCP server can do:

- Search files, list recent files
- Read file content and file metadata, download file content
- Create files and folders, copy files, upload a new revision
- Get file permissions

What it cannot do:

- Move, rename, share, or trash files
- Comments
- Shared-drive management

REST calls to redesign, not translate:

| Old REST call | MCP replacement |
| --- | --- |
| `files.list` / search | Search files tool |
| `files.get` (metadata / content) | Get file metadata / read file content tool |
| `files.create` | Create file tool |
| `files.copy` | Copy file tool |
| `files.update` (new revision) | Upload new revision tool |
| `files.update` (move / rename) | **No equivalent.** Redesign: leave the file where it is, or let a human move it. |
| `permissions.create` (share) | **No equivalent.** Redesign: keep sharing out of the agent. |
| `comments.*` | **No equivalent.** |

### Docs — close to parity

- Read a document, and edit it through any `batchUpdate` request,
  including suggestion mode.
- Map REST `documents.get` to the read tool and
  `documents.batchUpdate` to the edit tool, and verify the exact
  tool names against the live `tools/list`.

### Sheets — read and edit map across

- Read ranges and values, update values, and manage sheets through
  the Sheets MCP tools. Verify tool names against the live server;
  the mapping is close to the REST API, but tool names are the
  server's, not the REST method names.

### Slides — close to parity

- Read a presentation and edit it through `batchUpdate`, as with
  Docs. Verify tool names against the live server.

### Calendar — full coverage, all tools in one billing bucket

- List, create, update, and delete events; list calendars.
- On the Scaled tier, all Calendar MCP tools fall in the Plus
  billing bucket ($0.25 per 1,000 requests, as published
  November 24, 2026). See `tiers.md`.

### Chat — spaces and messages

- Read spaces and messages, and post messages where the server
  allows. Verify against the live tool list; Chat's MCP coverage
  is thinner than Docs or Calendar, so check each operation the
  agent actually uses.

### Tasks — close to parity

- List task lists and tasks, create, update, complete, and delete
  tasks. Map the REST `tasklists` and `tasks` calls across and
  verify against the live tool list.

## What breaks, and how to handle it

1. **A REST call with no MCP equivalent.** Do not work around it
   by keeping the REST call — that is the call the February 1,
   2027 enforcement throttles. Redesign the workflow, or take
   that step out of the agent.
2. **A tool that exists but is partner-only.** Same as above. The
   Gmail send tools are the main case. Treat "partner-only" as
   "not available to this agent".
3. **A workflow that assumed REST quotas.** Standard-tier MCP is
   capped at 5,000 requests a day per project per product, and
   that cap cannot be raised. An agent that made 50,000 Gmail
   REST calls a day will not fit on Standard. See `tiers.md`.
4. **A workflow that assumed long-term memory.** The 30-day cap
   on Workspace-derived data applies to anything the agent
   builds from Workspace content. See `gotchas.md`.
5. **A workflow that assumed silent writes.** Admin settings can
   require human confirmation before external writes. Build the
   confirmation step in; do not bypass it.

## How to confirm a mapping

1. List the server's tools (`tools/list` on the product's MCP
   endpoint — no token needed).
2. Find the tool that does the job, or confirm there is none.
3. Call it once with test data and check the result shape.
4. Only then write the migration row as final.
