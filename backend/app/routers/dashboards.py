from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, WorkItem, Project, Department, Notification, Comment, Sprint
from ..auth import get_current_user, visible_assignee_ids
from ..services.workload import team_workload

router = APIRouter(prefix="/api/dashboard", tags=["dashboards"])
ACTIVE = ("todo", "in_progress", "review", "blocked")


@router.get("")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "admin":
        return _executive(db)
    if user.role == "lead":
        return _lead(db, user)
    return _employee(db, user)


def _executive(db: Session) -> dict:
    departments = []
    for d in db.query(Department).all():
        items = (db.query(WorkItem).join(Project)
                 .filter(Project.department_id == d.id).all())
        done = [i for i in items if i.status == "done"]
        blocked = [i for i in items if i.status == "blocked"]
        velocity = sum(i.estimate_hours for i in done
                       if i.updated_at and i.updated_at > datetime.utcnow() - timedelta(days=14))
        departments.append({
            "id": d.id, "name": d.name, "slug": d.slug,
            "open": len(items) - len(done), "done": len(done),
            "blocked": len(blocked),
            "velocity_14d": round(velocity, 1),
            "completion": round(len(done) / len(items) * 100) if items else 0,
            "headcount": len(d.members),
        })
    projects = [{
        "id": p.id, "name": p.name, "department": p.department.name if p.department else "",
        "health": p.health, "status": p.status,
        "target_date": p.target_date.isoformat() if p.target_date else None,
        "open_items": sum(1 for i in p.work_items if i.status != "done"),
        "progress": round(sum(1 for i in p.work_items if i.status == "done")
                          / len(p.work_items) * 100) if p.work_items else 0,
    } for p in db.query(Project).all()]
    risks = (db.query(Comment).filter(Comment.ai_flags != "")
             .order_by(Comment.created_at.desc()).limit(8).all())
    all_items = db.query(WorkItem).all()
    burn = sum(i.logged_hours for i in all_items)
    scope = sum(i.estimate_hours for i in all_items)
    return {
        "view": "executive",
        "kpis": {
            "open_items": sum(1 for i in all_items if i.status in ACTIVE),
            "blocked": sum(1 for i in all_items if i.status == "blocked"),
            "done_this_sprint": sum(1 for i in all_items if i.status == "done"),
            "burn_rate": round(burn / scope * 100) if scope else 0,
            "scope_hours": round(scope), "logged_hours": round(burn),
        },
        "departments": departments,
        "projects": projects,
        "workload": team_workload(db),
        "risk_feed": [{
            "id": c.id, "item": c.work_item.title, "author": c.author.full_name,
            "flags": c.ai_flags.split(","), "body": c.body[:160],
            "created_at": c.created_at.isoformat(),
        } for c in risks],
        "upcoming": _upcoming(db),
    }


def _lead(db: Session, user: User) -> dict:
    allowed = visible_assignee_ids(user, db)
    items = db.query(WorkItem).filter(WorkItem.assignee_id.in_(allowed)).all()
    pending_review = [i for i in items if i.status == "review"]
    sprint = (db.query(Sprint)
              .filter(Sprint.department_id == user.department_id,
                      Sprint.state == "active").first())
    sprint_items = [i for i in items if sprint and i.sprint_id == sprint.id]
    done = sum(1 for i in sprint_items if i.status == "done")
    return {
        "view": "lead",
        "kpis": {
            "team_open": sum(1 for i in items if i.status in ACTIVE),
            "blocked": sum(1 for i in items if i.status == "blocked"),
            "pending_approvals": len(pending_review),
            "sprint_progress": round(done / len(sprint_items) * 100) if sprint_items else 0,
        },
        "sprint": {"name": sprint.name,
                   "end_date": sprint.end_date.isoformat()} if sprint else None,
        "workload": team_workload(db, user.department_id),
        "approvals": [_mini(i) for i in pending_review],
        "blocked_items": [_mini(i) for i in items if i.status == "blocked"],
        "upcoming": _upcoming(db, allowed),
    }


def _employee(db: Session, user: User) -> dict:
    items = db.query(WorkItem).filter(WorkItem.assignee_id == user.id).all()
    week_ahead = datetime.utcnow() + timedelta(days=7)
    done_items = [i for i in items if i.status == "done"]
    kpi_completion = round(len(done_items) / len(items) * 100) if items else 0
    return {
        "view": "employee",
        "kpis": {
            "my_open": sum(1 for i in items if i.status in ACTIVE),
            "due_this_week": sum(1 for i in items if i.status in ACTIVE
                                 and i.due_date and i.due_date < week_ahead),
            "in_review": sum(1 for i in items if i.status == "review"),
            "completion_rate": kpi_completion,
        },
        "my_items": [_mini(i) for i in items if i.status != "done"],
        "completed": [_mini(i) for i in done_items[:10]],
        "logged_hours": round(sum(i.logged_hours for i in items), 1),
    }


def _mini(i: WorkItem) -> dict:
    return {"id": i.id, "type": i.type, "title": i.title, "status": i.status,
            "priority": i.priority, "project": i.project.name if i.project else "",
            "assignee": i.assignee.full_name if i.assignee else None,
            "assignee_color": i.assignee.avatar_color if i.assignee else "#475569",
            "due_date": i.due_date.isoformat() if i.due_date else None,
            "estimate_hours": i.estimate_hours, "discipline": i.discipline}


def _upcoming(db: Session, allowed: list[int] | None = None) -> list[dict]:
    q = db.query(WorkItem).filter(WorkItem.status.in_(ACTIVE),
                                  WorkItem.due_date != None)
    if allowed:
        q = q.filter(WorkItem.assignee_id.in_(allowed))
    return [_mini(i) for i in q.order_by(WorkItem.due_date).limit(8).all()]


@router.get("/notifications")
def notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notes = (db.query(Notification).filter(Notification.user_id == user.id)
             .order_by(Notification.created_at.desc()).limit(20).all())
    return [{"id": n.id, "message": n.message, "kind": n.kind, "read": n.read,
             "created_at": n.created_at.isoformat()} for n in notes]
