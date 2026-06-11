# Jira Integration

Two-way sync against Jira Cloud REST API v3. Idle (safe no-op) until configured.

## Setup
1. Create an API token: https://id.atlassian.com/manage-profile/security/api-tokens
2. In `.env`:
```
JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_EMAIL=joseph@legendium.in
JIRA_API_TOKEN=xxxx
JIRA_PROJECT_KEY_VRXR=VRXR
JIRA_PROJECT_KEY_ROBOTICS=ROBO
JIRA_PROJECT_KEY_OPERATIONS=OPS
```
3. Each Legendium department maps to one Jira project key.

## What syncs
| App event | Jira action |
|---|---|
| Work item created (manually or by AI execute) | Issue created (Epic/Story/Task/Sub-task), key stored on the item |
| Status dragged on the board | Workflow transition (todo->To Do, in_progress->In Progress, review->In Review, blocked->Blocked, done->Done) |
| Comment posted | Comment mirrored to the issue |

Items display their `jira_key` chip on the board once synced.

## Status mapping
Adjust `STATUS_TO_TRANSITION` in `backend/app/services/jira_client.py` if your Jira workflow uses different status names. The client looks up available transitions per issue and matches by name, so renames are one-line changes.

## Security note
Legendium's employee isolation (own-tasks-only) is enforced in this app. If employees are ever given direct Jira logins, replicate the rule with Jira issue security schemes so the boundary holds in both tools.

## Webhooks (inbound sync)
For Jira -> Legendium updates, register a webhook to POST issue events to a future `/api/jira/webhook` endpoint; `fetch_issue()` in the client already supports pull-based reconciliation.
