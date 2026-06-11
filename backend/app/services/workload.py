"""Workload Engine: load, overload detection, reassignment suggestions."""
from sqlalchemy.orm import Session
from ..models import User, WorkItem

ACTIVE = ("todo", "in_progress", "review", "blocked")


def team_workload(db: Session, dept_id: int | None = None) -> list[dict]:
    q = db.query(User)
    if dept_id:
        q = q.filter(User.department_id == dept_id)
    out = []
    for u in q.all():
        items = db.query(WorkItem).filter(
            WorkItem.assignee_id == u.id, WorkItem.status.in_(ACTIVE)).all()
        load = sum(max(i.estimate_hours - i.logged_hours, 0) for i in items)
        util = round(load / u.capacity_hours * 100) if u.capacity_hours else 0
        out.append({
            "user_id": u.id, "username": u.username, "full_name": u.full_name,
            "role": u.role, "title": u.title, "skills": u.skills.split(",") if u.skills else [],
            "capacity_hours": u.capacity_hours, "load_hours": round(load, 1),
            "utilization": util, "open_items": len(items),
            "status": "overloaded" if util > 100 else "high" if util > 80
                      else "healthy" if util > 30 else "available",
            "avatar_color": u.avatar_color,
        })
    return sorted(out, key=lambda x: -x["utilization"])


def reassignment_suggestions(db: Session, dept_id: int | None = None) -> list[dict]:
    wl = team_workload(db, dept_id)
    hot = [w for w in wl if w["utilization"] > 90 and w["role"] == "employee"]
    cool = [w for w in wl if w["utilization"] < 60 and w["role"] == "employee"]
    suggestions = []
    for h in hot:
        items = (db.query(WorkItem)
                 .filter(WorkItem.assignee_id == h["user_id"],
                         WorkItem.status == "todo")
                 .order_by(WorkItem.priority).all())
        for item in items[:3]:
            for c in cool:
                if _skill_match(item, c["skills"]):
                    suggestions.append({
                        "work_item_id": item.id, "title": item.title,
                        "from_user": h["full_name"], "to_user": c["full_name"],
                        "to_user_id": c["user_id"],
                        "reason": (f"{h['full_name']} is at {h['utilization']}% load; "
                                   f"{c['full_name']} has matching skills and "
                                   f"{c['utilization']}% utilization."),
                    })
                    break
    return suggestions


def _skill_match(item: WorkItem, skills: list[str]) -> bool:
    hay = (item.title + " " + item.discipline).lower()
    return any(s.strip().lower() in hay for s in skills if s.strip())
