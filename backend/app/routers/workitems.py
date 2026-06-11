from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, WorkItem, Project, Comment, Notification, AuditLog, Dependency
from ..auth import get_current_user, visible_assignee_ids
from ..services.ai_engine import analyze_comment
from ..services import jira_client

router = APIRouter(prefix="/api/work-items", tags=["work-items"])


def _serialize(i: WorkItem) -> dict:
    return {
        "id": i.id, "type": i.type, "title": i.title, "description": i.description,
        "status": i.status, "priority": i.priority, "discipline": i.discipline,
        "estimate_hours": i.estimate_hours, "logged_hours": i.logged_hours,
        "due_date": i.due_date.isoformat() if i.due_date else None,
        "project_id": i.project_id, "project_name": i.project.name if i.project else None,
        "parent_id": i.parent_id, "assignee_id": i.assignee_id,
        "assignee": i.assignee.full_name if i.assignee else None,
        "assignee_color": i.assignee.avatar_color if i.assignee else "#475569",
        "jira_key": i.jira_key,
        "comment_count": len(i.comments),
    }


@router.get("")
def list_items(project_id: int | None = None, status: str | None = None,
               user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(WorkItem)
    allowed = visible_assignee_ids(user, db)
    if allowed is not None:
        if user.role == "employee":
            q = q.filter(WorkItem.assignee_id == user.id)  # own tasks only
        else:
            q = q.filter(WorkItem.assignee_id.in_(allowed))
    if project_id:
        q = q.filter(WorkItem.project_id == project_id)
    if status:
        q = q.filter(WorkItem.status == status)
    return [_serialize(i) for i in q.order_by(WorkItem.updated_at.desc()).all()]


@router.get("/{item_id}")
def get_item(item_id: int, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    item = db.get(WorkItem, item_id)
    if not item:
        raise HTTPException(404, "Work item not found")
    _check_visibility(user, item, db)
    data = _serialize(item)
    data["comments"] = [{
        "id": c.id, "author": c.author.full_name, "author_color": c.author.avatar_color,
        "body": c.body, "created_at": c.created_at.isoformat(),
        "ai_flags": c.ai_flags.split(",") if c.ai_flags else [],
    } for c in sorted(item.comments, key=lambda c: c.created_at)]
    deps = db.query(Dependency).filter(
        (Dependency.blocked_id == item.id) | (Dependency.blocker_id == item.id)).all()
    data["blocked_by"] = [d.blocker_id for d in deps if d.blocked_id == item.id]
    data["blocks"] = [d.blocked_id for d in deps if d.blocker_id == item.id]
    data["children"] = [_serialize(c) for c in item.children]
    return data


class ItemCreate(BaseModel):
    type: str
    title: str
    description: str = ""
    project_id: int
    assignee_id: int | None = None
    parent_id: int | None = None
    priority: str = "medium"
    discipline: str = "development"
    estimate_hours: float = 0
    due_date: datetime | None = None


@router.post("")
async def create_item(payload: ItemCreate, user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user.role == "employee":
        raise HTTPException(403, "Task creation is lead-only. Tasks flow down from your lead.")
    if user.role == "lead" and payload.assignee_id:
        assignee = db.get(User, payload.assignee_id)
        if assignee and assignee.manager_id != user.id and assignee.id != user.id:
            raise HTTPException(403, "Leads can only assign to their own team")
    item = WorkItem(**payload.model_dump(), reporter_id=user.id)
    db.add(item); db.flush()
    if payload.assignee_id:
        db.add(Notification(user_id=payload.assignee_id, kind="assignment",
                            message=f"New {payload.type} assigned: {payload.title}"))
    project = db.get(Project, payload.project_id)
    if project and project.department and project.department.jira_project_key:
        res = await jira_client.create_issue(
            project.department.jira_project_key, item.type, item.title, item.description)
        if res.get("synced"):
            item.jira_key = res["key"]
    db.add(AuditLog(user_id=user.id, action="create_work_item", detail=item.title))
    db.commit()
    return _serialize(item)


class StatusUpdate(BaseModel):
    status: str


@router.patch("/{item_id}/status")
async def update_status(item_id: int, payload: StatusUpdate,
                        user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    item = db.get(WorkItem, item_id)
    if not item:
        raise HTTPException(404, "Work item not found")
    _check_visibility(user, item, db)
    item.status = payload.status
    if item.jira_key:
        await jira_client.transition_issue(item.jira_key, payload.status)
    db.add(AuditLog(user_id=user.id, action="status_change",
                    detail=f"{item.title} -> {payload.status}"))
    db.commit()
    return _serialize(item)


class CommentCreate(BaseModel):
    body: str


@router.post("/{item_id}/comments")
async def add_comment(item_id: int, payload: CommentCreate,
                      user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    item = db.get(WorkItem, item_id)
    if not item:
        raise HTTPException(404, "Work item not found")
    _check_visibility(user, item, db)
    flags = analyze_comment(payload.body)
    c = Comment(work_item_id=item.id, author_id=user.id, body=payload.body,
                ai_flags=",".join(flags))
    db.add(c)
    if flags:  # escalate to lead + admin
        leads = db.query(User).filter(User.role.in_(["lead", "admin"])).all()
        for lead in leads:
            db.add(Notification(user_id=lead.id, kind="risk",
                                message=f"AI flagged [{', '.join(flags)}] on '{item.title}'"))
    if item.jira_key:
        await jira_client.add_comment(item.jira_key, payload.body)
    db.commit()
    return {"ok": True, "ai_flags": flags}


def _check_visibility(user: User, item: WorkItem, db: Session):
    if user.role == "admin":
        return
    if user.role == "employee" and item.assignee_id != user.id:
        raise HTTPException(403, "You can only access tasks assigned to you")
    if user.role == "lead":
        allowed = visible_assignee_ids(user, db)
        if item.assignee_id and item.assignee_id not in allowed:
            raise HTTPException(403, "Outside your team's scope")
