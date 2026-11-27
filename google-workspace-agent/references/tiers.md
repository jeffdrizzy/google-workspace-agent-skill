# Tiers: Standard vs Scaled

How to pick a usage tier, what each one costs, and how quota
increases work. Read this during step 4 of the skill.

Source: Google's "Understand Google Workspace API and MCP server
pricing and billing tiers" developer page, updated November 24,
2026, and the Google Workspace Updates announcement of the same
date. Prices are in USD. Google can change them — re-check the
pricing page before quoting a cost to a user.

## The two tiers at a glance

| | Standard Tier | Scaled Tier |
| --- | --- | --- |
| Cost | Free, no billing account needed | Billed from April 1, 2027 |
| MCP quota | 5,000 requests/day, per project, per product | Higher quotas on request |
| MCP daily free allowance | 5,000/day (the cap itself) | None — billed from the first successful request |
| Quota increase | Not possible on Standard | Enrol in Scaled, then submit a request |
| Applies to | Each Google Cloud project by default | The whole Google Cloud project |
| REST allowance | Never charged on Standard | Large daily no-charge allowances per bucket |

The tiers start with Gmail, Drive, and Calendar. Scaled-tier MCP
billing applies to the Gmail, Calendar, and Drive MCP servers.

Standard is the default tier for every new Google Cloud project,
and the default for all existing projects unless a developer opts
in to Scaled.

## Standard tier

- Free, no Google Cloud Billing account or credit card required.
- Capped at **5,000 requests per day, per project, per product**
  across the generally available Workspace MCP servers.
- That cap **cannot be raised** on Standard. Submitting a quota
  request is not possible on the Standard tier — requesting higher
  MCP quotas requires enrolling in the Scaled tier with a linked
  billing account.
- Usage on Standard never produces a charge.
- Google reports that more than 99% of active developers sit
  within Standard limits at no added cost.

Use Standard when the agent's estimated daily MCP requests fit
comfortably inside 5,000 a day per product. Most single-user and
small-team agents fit here.

## Scaled tier

- Higher quotas, but you must enrol, link a billing account, and
  submit a quota request if higher limits are required. Enrolment
  alone does not raise the limits.
- It applies to the **whole Google Cloud project**, not per API —
  every product in the project moves to Scaled together.
- **Billing starts April 1, 2027.** Before that date, Scaled
  enrolment does not bill.
- **MCP has no daily free allowance on Scaled.** Switching from
  Standard to Scaled removes the free 5,000 MCP requests a day.
  MCP requests are billed from the first successful (`2xx`)
  request; error (`4xx`) requests are excluded.
- REST APIs keep large daily no-charge allowances on Scaled (for
  example, 70 million light Gmail requests a day). That allowance
  does not apply to MCP traffic.

### Scaled pricing, per 1,000 successful requests

| Bucket | Price | Typical MCP tools |
| --- | --- | --- |
| Light | $0.10 | Gmail `list_labels`, Drive `get_file_metadata` |
| Medium | $0.20 | Gmail `create_draft`, Drive `create_file` |
| Plus | $0.25 | Drive `search_files`, all Calendar MCP tools |
| Premium | $0.50 | Gmail `search_threads`, `get_thread`, Drive `read_file_content` |

Composite MCP tools count as multiple billing units, because one
tool invocation triggers several underlying API calls. Estimate
cost per tool call, not per user message.

## The February 1, 2027 trap

From February 1, 2027, AI agents calling the Workspace REST APIs
directly are limited to Standard-tier quotas **regardless of the
tier selected**. Paying for Scaled does not buy a higher REST
quota for an agent. The only way to use Scaled quotas as an agent
is through the MCP servers (or `gwscli`).

## How to decide

1. Estimate daily MCP requests per product from the audit. Count
   tool calls, and assume each user request triggers several.
2. If the estimate is well under 5,000 a day per product, choose
   Standard. Say so in the migration record, with the estimate.
3. If the estimate exceeds 5,000 a day per product, choose Scaled
   — and show the user the expected monthly cost first, using the
   buckets above. A quiet agent on Scaled still pays from the
   first request, so do not choose Scaled "to be safe".
4. If the agent needs higher quotas, enrol in Scaled and submit
   the quota request. Do not assume enrolment raised anything.
5. After April 1, 2027, check the first Scaled bill and confirm
   the tier is still the right one. Usage changes after a
   migration, and so does the bill.

## Worked example (placeholder numbers)

An agent triages 200 emails a day: 200 thread searches (Premium,
$0.50/1,000) and 200 thread reads (Premium) = 400 Premium
requests a day. On Standard, that fits easily inside 5,000 a day
and costs $0. On Scaled, the same 400 requests a day cost about
$0.20 a day, or about $6 a month — and the free 5,000 a day is
gone. That agent should stay on Standard.

An agent that indexes a shared Drive with 40,000 file reads a day
does not fit on Standard. That agent needs Scaled, a quota
request, and a real cost estimate before anyone enables it.
