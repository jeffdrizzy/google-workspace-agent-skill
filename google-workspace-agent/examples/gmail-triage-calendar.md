# Example: Gmail triage + Calendar agent, migrated end to end

A worked migration of a small agent that triages an inbox every
morning and books focus time on the owner's calendar. All data
below is placeholder data — names, addresses, and counts are
invented to show the shape of the work, not real mail.

## Before: what the agent did on REST

Every morning at 08:00, the agent:

1. Listed unread Gmail threads with `users.threads.list`
   (`gmail.googleapis.com/gmail/v1/users/me/threads?q=is:unread`).
2. Read each thread with `users.threads.get`.
3. Sorted threads into three labels: `Needs reply`, `FYI`, and
   `Newsletters`.
4. Replied to short, routine threads with a canned answer using
   `users.messages.send`.
5. Booked a 90-minute focus block on the owner's Calendar with
   `calendar.events.insert` if the inbox had more than 20 unread
   threads.

The agent also kept a permanent vector index of every email it
had ever read, so it could answer "what did we agree with the
supplier last year?".

## The audit (step 1)

| REST call | Product | Purpose |
| --- | --- | --- |
| `users.threads.list` | Gmail | Find unread threads |
| `users.threads.get` | Gmail | Read each thread |
| `users.messages.send` | Gmail | Reply to routine threads |
| `calendar.events.insert` | Calendar | Book focus time |
| Permanent vector index | Gmail | Long-term memory over mail |

## The mapping (step 2)

| Old REST call | MCP replacement | Notes |
| --- | --- | --- |
| `users.threads.list` | Gmail MCP search threads tool | Same query, same result shape to check |
| `users.threads.get` | Gmail MCP read thread tool | Verify against live `tools/list` |
| `users.messages.send` | **No equivalent** | Redesign: see below |
| `calendar.events.insert` | Calendar MCP create event tool | All Calendar tools are in the Plus billing bucket |
| Permanent vector index | **Not allowed** | Replaced with a 30-day rolling index, see below |

## The redesign (steps 3–5)

**Gmail send.** The agent no longer replies. Instead it creates a
draft reply with the Gmail MCP create-draft tool, applies the
`Needs reply` label, and shows the owner a morning list: "3 drafts
waiting for you". The owner reviews and sends them. The morning
summary says "3 drafts ready", never "3 replies sent".

**Retention.** The permanent vector index is deleted. It is replaced
with a rolling 30-day index: every entry carries an expiry date 30
days after it was created, and a nightly job deletes expired
entries. When the owner disconnects the agent, a purge deletes the
whole index. The agent can no longer answer "what did we agree
last year?" — that is stated in the morning summary, not hidden.

**Auth.** A new OAuth client is created for the agent only, marked
"Use this client for an AI-powered agent", with Gmail read-only +
draft-creation scopes and Calendar event scopes. The old REST
client is not reused.

**Tier.** The agent makes about 120 Gmail MCP requests and 1
Calendar request a day — well inside the Standard tier's 5,000 a
day per product. Tier chosen: Standard, $0. Recorded in the
migration record.

## The migration record

`workspace-migration.json` in the agent's project root:

```json
{
  "agent": "gmail-triage-calendar",
  "migrated": "2026-12-15",
  "tier": "standard",
  "daily_estimate": {
    "gmail": 120,
    "calendar": 1
  },
  "expected_monthly_cost_usd": 0,
  "oauth_client_id": "123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com",
  "scopes": [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.events"
  ],
  "gmail_send": "draft-only, human sends",
  "retention_days": 30,
  "purge_on_disconnect": true,
  "check_script_last_passed": "2026-12-15"
}
```

Note: the client ID and scopes above are placeholders. A real
record holds the real client ID, never the client secret.

## The check (step 6)

```sh
python3 google-workspace-agent/scripts/check-migration.py /path/to/gmail-triage-calendar
```

Expected output:

```
PASSED: migration verified
```

The script found no direct Workspace REST calls in the agent's
code or config, found the MCP configuration, and found the tier
recorded as Standard.

## After: what the owner sees

Morning summary, after migration:

> Good morning. 14 unread threads. 3 drafts waiting for your
> review — 2 supplier replies, 1 meeting reschedule. I booked a
> 90-minute focus block at 10:00. I can search the last 30 days of
> mail; anything older than that, I will need you to forward it to
> me.

That summary is honest about what the agent can and cannot do —
and that honesty is the point of the migration.
