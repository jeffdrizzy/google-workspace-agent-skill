# Scripts

## `check-migration.py`

Verifies a Google Workspace agent migration from the REST APIs to
the Workspace MCP servers. Run it against the agent's project
directory — not against this skill's folder:

```sh
python3 google-workspace-agent/scripts/check-migration.py <agent-project-dir>
```

It checks three things:

1. **No direct REST calls remain** — no Workspace REST hostnames
   (`gmail.googleapis.com`, `drive.googleapis.com`, and the rest)
   and no REST paths (`/gmail/v1`, `/drive/v3`, `/calendar/v3`,
   and the rest) in the agent's code or config. MCP server
   hostnames (`*mcp.googleapis.com`) are the correct destination
   and do not fail this check.
2. **An MCP configuration is present** — some file references a
   Workspace MCP server (`*mcp.googleapis.com/mcp/v1`) or `gwscli`.
3. **A tier is recorded** — `workspace-migration.json` or
   `MIGRATION.md` in the project root names the tier, Standard or
   Scaled.

Exit code 0 and `PASSED: migration verified` on pass; exit code 1
and a list of problems on fail. The script never modifies the
project it checks.

### Self-test

```sh
python3 google-workspace-agent/scripts/check-migration.py --self-test
```

Builds a passing fixture and a failing fixture in a temporary
directory, checks both, and prints `SELF-TEST PASSED` if the good
one passes and the bad one fails. Use it to confirm the script
itself works before trusting it on a real migration.

### What the script does not check

- Whether the MCP tools the agent calls actually exist — confirm
  each one against the live server's `tools/list`.
- Whether the OAuth client is flagged as an agent client — check
  that in Google Auth Platform > Clients.
- Whether the tier is the right one for the agent's usage —
  that is a judgement call from the audit, in
  `references/tiers.md`.
- Whether Workspace-derived data is deleted within 30 days —
  that is a data-handling rule, not something a code scan can
  prove.
