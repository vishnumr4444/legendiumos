"""Jira Cloud two-way sync.

All calls are no-ops returning {"synced": False} until JIRA_BASE_URL,
JIRA_EMAIL and JIRA_API_TOKEN are configured. Issue-level security note:
Legendium employee visibility is enforced app-side; if employees get direct
Jira logins, mirror the rule with Jira issue security schemes.
"""
import base64
import httpx
from .. import config

TYPE_MAP = {"epic": "Epic", "story": "Story", "task": "Task", "subtask": "Sub-task"}
STATUS_TO_TRANSITION = {"todo": "To Do", "in_progress": "In Progress",
                        "review": "In Review", "blocked": "Blocked", "done": "Done"}


def _enabled() -> bool:
    return bool(config.JIRA_BASE_URL and config.JIRA_EMAIL and config.JIRA_API_TOKEN)


def _headers() -> dict:
    token = base64.b64encode(
        f"{config.JIRA_EMAIL}:{config.JIRA_API_TOKEN}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


async def create_issue(project_key: str, item_type: str, summary: str,
                       description: str = "", parent_key: str | None = None) -> dict:
    if not _enabled():
        return {"synced": False, "reason": "jira-not-configured"}
    fields = {
        "project": {"key": project_key},
        "issuetype": {"name": TYPE_MAP.get(item_type, "Task")},
        "summary": summary[:255],
        "description": {"type": "doc", "version": 1, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": description or summary}]}]},
    }
    if parent_key and item_type in ("subtask", "story", "task"):
        fields["parent"] = {"key": parent_key}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{config.JIRA_BASE_URL}/rest/api/3/issue",
                              headers=_headers(), json={"fields": fields})
        r.raise_for_status()
        return {"synced": True, "key": r.json()["key"]}


async def add_comment(issue_key: str, body: str) -> dict:
    if not _enabled():
        return {"synced": False}
    payload = {"body": {"type": "doc", "version": 1, "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": body}]}]}}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{config.JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment",
                              headers=_headers(), json=payload)
        r.raise_for_status()
        return {"synced": True}


async def transition_issue(issue_key: str, status: str) -> dict:
    if not _enabled():
        return {"synced": False}
    target = STATUS_TO_TRANSITION.get(status, "To Do")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{config.JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions",
                             headers=_headers())
        r.raise_for_status()
        for t in r.json().get("transitions", []):
            if t["name"].lower() == target.lower():
                await client.post(
                    f"{config.JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions",
                    headers=_headers(), json={"transition": {"id": t["id"]}})
                return {"synced": True}
    return {"synced": False, "reason": f"no transition to {target}"}


async def fetch_issue(issue_key: str) -> dict:
    if not _enabled():
        return {"synced": False}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{config.JIRA_BASE_URL}/rest/api/3/issue/{issue_key}",
                             headers=_headers())
        r.raise_for_status()
        return {"synced": True, "issue": r.json()}
