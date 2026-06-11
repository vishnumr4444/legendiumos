"""Workload, projects, reports, knowledge base."""
import csv, io, json
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Project, WorkItem, Document, Department
from ..auth import get_current_user, require_role
from ..services.workload import team_workload, reassignment_suggestions

router = APIRouter(prefix="/api", tags=["platform"])


@router.get("/projects")
def projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Project)
    if user.role == "lead":
        q = q.filter(Project.department_id == user.department_id)
    elif user.role == "employee":
        ids = {i.project_id for i in db.query(WorkItem)
               .filter(WorkItem.assignee_id == user.id).all()}
        q = q.filter(Project.id.in_(ids or {-1}))
    return [{"id": p.id, "name": p.name, "slug": p.slug, "health": p.health,
             "department": p.department.name if p.department else "",
             "department_slug": p.department.slug if p.department else "",
             "open_items": sum(1 for i in p.work_items if i.status != "done"),
             "progress": round(sum(1 for i in p.work_items if i.status == "done")
                               / len(p.work_items) * 100) if p.work_items else 0}
            for p in q.all()]


@router.get("/workload")
def workload(user: User = Depends(require_role("admin", "lead")),
             db: Session = Depends(get_db)):
    dept = None if user.role == "admin" else user.department_id
    return {"team": team_workload(db, dept),
            "suggestions": reassignment_suggestions(db, dept)}


@router.post("/workload/reassign/{item_id}/{to_user_id}")
def reassign(item_id: int, to_user_id: int,
             user: User = Depends(require_role("admin", "lead")),
             db: Session = Depends(get_db)):
    item = db.get(WorkItem, item_id)
    if not item:
        raise HTTPException(404, "Work item not found")
    item.assignee_id = to_user_id
    db.commit()
    return {"ok": True}


@router.get("/reports/{kind}")
def report(kind: str, format: str = "json",
           user: User = Depends(require_role("admin", "lead")),
           db: Session = Depends(get_db)):
    """kind: daily | weekly | sprint | executive. format: json | csv | md"""
    items = db.query(WorkItem).all()
    if user.role == "lead":
        from ..auth import visible_assignee_ids
        allowed = visible_assignee_ids(user, db)
        items = [i for i in items if i.assignee_id in allowed]
    rows = [{
        "id": i.id, "type": i.type, "title": i.title, "project": i.project.name,
        "assignee": i.assignee.full_name if i.assignee else "",
        "status": i.status, "priority": i.priority, "discipline": i.discipline,
        "estimate_hours": i.estimate_hours, "logged_hours": i.logged_hours,
        "due_date": i.due_date.isoformat() if i.due_date else "",
    } for i in items]
    meta = {"report": kind, "generated_at": datetime.utcnow().isoformat(),
            "generated_by": user.full_name, "item_count": len(rows)}
    if format == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=rows[0].keys() if rows else ["id"])
        writer.writeheader(); writer.writerows(rows)
        return StreamingResponse(io.BytesIO(buf.getvalue().encode()),
                                 media_type="text/csv",
                                 headers={"Content-Disposition":
                                          f"attachment; filename=legendium-{kind}.csv"})
    if format == "md":
        lines = [f"# Legendium {kind.title()} Report",
                 f"Generated {meta['generated_at']} by {meta['generated_by']}", "",
                 "| Item | Project | Assignee | Status | Est | Logged |",
                 "|---|---|---|---|---|---|"]
        lines += [f"| {r['title']} | {r['project']} | {r['assignee']} | "
                  f"{r['status']} | {r['estimate_hours']} | {r['logged_hours']} |"
                  for r in rows]
        text = "\n".join(lines)
        return StreamingResponse(io.BytesIO(text.encode()), media_type="text/markdown",
                                 headers={"Content-Disposition":
                                          f"attachment; filename=legendium-{kind}.md"})
    return {"meta": meta, "rows": rows}


@router.post("/knowledge/upload")
async def upload(file: UploadFile = File(...),
                 user: User = Depends(require_role("admin", "lead")),
                 db: Session = Depends(get_db)):
    raw = await file.read()
    text = ""
    if file.filename.lower().endswith((".txt", ".md", ".csv", ".json")):
        text = raw.decode(errors="ignore")[:200_000]
    doc = Document(filename=file.filename, uploaded_by=user.id,
                   size_bytes=len(raw), text_content=text,
                   kind="sop" if "sop" in file.filename.lower() else "other")
    db.add(doc); db.commit()
    return {"ok": True, "id": doc.id, "indexed_chars": len(text),
            "note": ("Text indexed for retrieval." if text else
                     "Stored. Binary parsing (PDF/DOCX/PPT) plugs in via the "
                     "extraction pipeline - see docs/AI_WORKFLOWS.md.")}


@router.get("/knowledge")
def knowledge(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": d.id, "filename": d.filename, "kind": d.kind,
             "size_bytes": d.size_bytes,
             "uploaded_at": d.uploaded_at.isoformat()} for d in
            db.query(Document).order_by(Document.uploaded_at.desc()).all()]


@router.get("/team")
def team(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    if user.role == "employee":
        users = [u for u in users if u.id == user.id or u.id == user.manager_id]
    return [{"id": u.id, "username": u.username, "full_name": u.full_name,
             "role": u.role, "title": u.title,
             "department": u.department.name if u.department else "",
             "avatar_color": u.avatar_color} for u in users]
