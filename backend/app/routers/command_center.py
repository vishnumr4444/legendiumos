"""AI Command Center: natural language -> full Jira-ready work breakdown."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import (User, Project, Department, WorkItem, Dependency,
                      Notification, AuditLog, Document)
from ..auth import get_current_user, require_role
from ..services.ai_engine import decompose
from ..services import jira_client

router = APIRouter(prefix="/api/command", tags=["command-center"])


class Command(BaseModel):
    prompt: str


@router.post("/preview")
async def preview(cmd: Command, user: User = Depends(require_role("admin", "lead")),
                  db: Session = Depends(get_db)):
    """Decompose without committing - the user reviews the plan first."""
    context = _rag_context(db, cmd.prompt)
    plan = await decompose(cmd.prompt, context)
    plan["totals"] = _totals(plan)
    return plan


class ExecutePayload(BaseModel):
    prompt: str
    plan: dict


@router.post("/execute")
async def execute(payload: ExecutePayload,
                  user: User = Depends(require_role("admin", "lead")),
                  db: Session = Depends(get_db)):
    """Commit an approved plan: create items, dependencies, notify, sync Jira."""
    plan = payload.plan
    dept = db.query(Department).filter(Department.slug == plan.get("department", "vrxr")).first()
    project = (db.query(Project)
               .filter(Project.name.ilike(f"%{plan.get('project', '')}%")).first())
    if not project:
        project = Project(name=plan.get("project", "AI Generated Project"),
                          slug=f"ai-{int(datetime.utcnow().timestamp())}",
                          department_id=dept.id if dept else None,
                          description=f"Created by AI Command Center: {payload.prompt}")
        db.add(project); db.flush()

    users = {u.username: u for u in db.query(User).all()}
    title_index: dict[str, WorkItem] = {}
    created = 0

    async def make(node: dict, type_: str, parent: WorkItem | None) -> WorkItem:
        nonlocal created
        owner = users.get(node.get("owner", ""), None)
        item = WorkItem(
            type=type_, title=node["title"],
            description=node.get("description", ""),
            discipline=node.get("discipline", "development"),
            estimate_hours=node.get("estimate_hours", 0),
            project_id=project.id, parent_id=parent.id if parent else None,
            assignee_id=owner.id if owner else None, reporter_id=user.id,
            due_date=datetime.utcnow() + timedelta(days=14))
        db.add(item); db.flush()
        title_index[item.title] = item
        created += 1
        if owner:
            db.add(Notification(user_id=owner.id, kind="assignment",
                                message=f"AI assigned you: {item.title}"))
        if dept and dept.jira_project_key:
            parent_key = parent.jira_key if parent else None
            res = await jira_client.create_issue(dept.jira_project_key, type_,
                                                 item.title, item.description,
                                                 parent_key)
            if res.get("synced"):
                item.jira_key = res["key"]
        return item

    for epic in plan.get("epics", []):
        e = await make(epic, "epic", None)
        for story in epic.get("stories", []):
            s = await make(story, "story", e)
            for task in story.get("tasks", []):
                t = await make(task, "task", s)
                for sub in task.get("subtasks", []):
                    await make(sub, "subtask", t)

    linked = 0
    for dep in plan.get("dependencies", []):
        blocker = title_index.get(dep.get("blocker"))
        blocked = title_index.get(dep.get("blocked"))
        if blocker and blocked:
            db.add(Dependency(blocker_id=blocker.id, blocked_id=blocked.id))
            linked += 1

    db.add(AuditLog(user_id=user.id, action="ai_command_execute",
                    detail=f"{payload.prompt} -> {created} items"))
    db.commit()
    return {"ok": True, "project": project.name, "items_created": created,
            "dependencies_linked": linked,
            "jira_synced": any(i.jira_key for i in title_index.values())}


def _totals(plan: dict) -> dict:
    epics = plan.get("epics", [])
    stories = sum(len(e.get("stories", [])) for e in epics)
    tasks = sum(len(s.get("tasks", [])) for e in epics for s in e.get("stories", []))
    subtasks = sum(len(t.get("subtasks", [])) for e in epics
                   for s in e.get("stories", []) for t in s.get("tasks", []))
    hours = 0.0
    for e in epics:
        for s in e.get("stories", []):
            for t in s.get("tasks", []):
                hours += t.get("estimate_hours", 0)
                for st in t.get("subtasks", []):
                    hours += st.get("estimate_hours", 0)
    return {"epics": len(epics), "stories": stories, "tasks": tasks,
            "subtasks": subtasks, "estimate_hours": hours,
            "dependencies": len(plan.get("dependencies", []))}


def _rag_context(db: Session, prompt: str, limit_chars: int = 2000) -> str:
    """Lightweight retrieval over the knowledge base (keyword scored).
    Swap with Qdrant vector search in production - interface stays the same."""
    words = {w.lower() for w in prompt.split() if len(w) > 3}
    scored = []
    for doc in db.query(Document).all():
        text = (doc.text_content or "")[:8000].lower()
        score = sum(text.count(w) for w in words)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda x: -x[0])
    out = []
    total = 0
    for _, doc in scored[:3]:
        chunk = f"[{doc.filename}] {doc.text_content[:700]}"
        out.append(chunk); total += len(chunk)
        if total > limit_chars:
            break
    return "\n\n".join(out)
