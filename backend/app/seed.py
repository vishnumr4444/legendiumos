"""Seed the current Legendium team structure with realistic demo data."""
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from .models import (User, Department, Project, WorkItem, Comment, Sprint,
                     Notification, Dependency)
from .auth import hash_password

DEFAULT_PASSWORD = "legendium"  # change on first login in production


def seed(db: Session):
    if db.query(User).first():
        return

    vrxr = Department(name="VR/XR", slug="vrxr", jira_project_key="VRXR")
    robo = Department(name="Robotics", slug="robotics", jira_project_key="ROBO")
    ops = Department(name="Operations", slug="operations", jira_project_key="OPS")
    db.add_all([vrxr, robo, ops]); db.flush()

    def user(username, full_name, role, dept, manager=None, title="", skills="",
             color="#06b6d4", capacity=40):
        u = User(username=username, full_name=full_name,
                 email=f"{username}@legendium.in",
                 password_hash=hash_password(DEFAULT_PASSWORD), role=role,
                 department_id=dept.id if dept else None,
                 manager_id=manager.id if manager else None, title=title,
                 skills=skills, capacity_hours=capacity, avatar_color=color)
        db.add(u); db.flush(); return u

    joseph = user("joseph", "Joseph", "admin", ops,
                  title="Product Manager · Master Admin",
                  skills="product,procurement,packaging,ecommerce,marketing",
                  color="#0ea5e9")
    amal = user("amal", "Amal", "lead", vrxr, joseph, "VR/XR Team Lead",
                "unity,unreal,level design,3d", "#22d3ee")
    anson = user("anson", "Anson", "lead", robo, joseph, "Robotics Team Lead",
                 "pcb,firmware,cad,manufacturing", "#2dd4bf")
    noel = user("noel", "Noel", "employee", vrxr, amal, "3D Artist",
                "3d,blender,texture,animation,render", "#67e8f9")
    vishnu = user("vishnu", "Vishnu", "employee", vrxr, amal, "Web & UI/UX",
                  "website,ui,ux,react,design", "#38bdf8")
    kp = user("krishnaprasad", "Krishnaprasad", "employee", vrxr, amal,
              "Backend & Integrations", "backend,api,integration,ai,python", "#818cf8")
    vysakh = user("vysakh", "Vysakh", "employee", robo, anson,
                  "Testing · Assembly · QC", "testing,qc,assembly,manufacturing", "#34d399")

    projects = {}
    for name, dept in [("Legendium Game", vrxr), ("Website", vrxr),
                       ("Chapter Development", vrxr), ("Asset Pipeline", vrxr),
                       ("Animations", vrxr),
                       ("NanoSpark", robo), ("Otto", robo), ("Ninja", robo),
                       ("Megapath", robo), ("Project K", robo),
                       ("Amazon", ops), ("Flipkart", ops), ("Logistics", ops),
                       ("Procurement", ops), ("Packaging", ops)]:
        slug = name.lower().replace(" ", "-")
        p = Project(name=name, slug=slug, department_id=dept.id,
                    health=random.choice(["green", "green", "green", "amber"]),
                    target_date=datetime.utcnow() + timedelta(days=random.randint(20, 90)),
                    description=f"{name} workstream under {dept.name}.")
        db.add(p); db.flush(); projects[name] = p

    now = datetime.utcnow()
    sprint_v = Sprint(name="VR/XR Sprint 12", department_id=vrxr.id,
                      start_date=now - timedelta(days=6), end_date=now + timedelta(days=8))
    sprint_r = Sprint(name="Robotics Sprint 9", department_id=robo.id,
                      start_date=now - timedelta(days=6), end_date=now + timedelta(days=8))
    db.add_all([sprint_v, sprint_r]); db.flush()

    def wi(type_, title, project, assignee, status="todo", priority="medium",
           discipline="development", est=8, logged=0, parent=None, due=None,
           sprint=None):
        item = WorkItem(type=type_, title=title, project_id=project.id,
                        assignee_id=assignee.id if assignee else None,
                        reporter_id=joseph.id, status=status, priority=priority,
                        discipline=discipline, estimate_hours=est,
                        logged_hours=logged,
                        parent_id=parent.id if parent else None,
                        due_date=due or now + timedelta(days=random.randint(2, 21)),
                        sprint_id=sprint.id if sprint else None)
        db.add(item); db.flush(); return item

    # Chapter 3 epic tree (VR/XR)
    e1 = wi("epic", "Chapter 3 production", projects["Chapter Development"], amal,
            "in_progress", "high", "design", 120, 64, sprint=sprint_v)
    s1 = wi("story", "Chapter 3 asset pipeline", projects["Chapter Development"], noel,
            "in_progress", "high", "design", 40, 22, e1, sprint=sprint_v)
    t1 = wi("task", "Model temple environment kit", projects["Chapter Development"], noel,
            "in_progress", "high", "design", 16, 9, s1, sprint=sprint_v)
    wi("subtask", "Sculpt hero statues", projects["Chapter Development"], noel,
       "done", "medium", "design", 6, 6, t1, sprint=sprint_v)
    wi("subtask", "Bake lighting and LODs", projects["Chapter Development"], noel,
       "in_progress", "medium", "design", 5, 2, t1, sprint=sprint_v)
    wi("task", "Texture pass on environment kit", projects["Chapter Development"], noel,
       "todo", "medium", "design", 12, 0, s1, sprint=sprint_v)
    s2 = wi("story", "Chapter 3 gameplay systems", projects["Chapter Development"], kp,
            "in_progress", "high", "development", 36, 18, e1, sprint=sprint_v)
    t2 = wi("task", "Puzzle trigger framework", projects["Chapter Development"], kp,
            "review", "high", "development", 14, 12, s2, sprint=sprint_v)
    wi("task", "Save-state integration", projects["Chapter Development"], kp,
       "blocked", "critical", "development", 10, 4, s2, sprint=sprint_v)
    wi("task", "Chapter 3 regression test plan", projects["Chapter Development"], amal,
       "todo", "medium", "qa", 6, 0, e1, sprint=sprint_v)

    # Website
    e2 = wi("epic", "Website refresh Q2", projects["Website"], amal,
            "in_progress", "medium", "design", 60, 25, sprint=sprint_v)
    wi("task", "Chapter 3 landing page design", projects["Website"], vishnu,
       "in_progress", "high", "design", 12, 7, e2, sprint=sprint_v)
    wi("task", "Build interactive robot showcase", projects["Website"], vishnu,
       "todo", "medium", "development", 16, 0, e2, sprint=sprint_v)
    wi("task", "SEO and analytics overhaul", projects["Website"], vishnu,
       "todo", "low", "marketing", 8, 0, e2, sprint=sprint_v)

    # NanoSpark robotics
    e3 = wi("epic", "NanoSpark production batch 2", projects["NanoSpark"], anson,
            "in_progress", "critical", "manufacturing", 100, 55, sprint=sprint_r)
    t3 = wi("task", "PCB rev C DFM check", projects["NanoSpark"], anson,
            "review", "critical", "development", 12, 10, e3, sprint=sprint_r)
    wi("task", "Pilot batch incoming QC (50 units)", projects["NanoSpark"], vysakh,
       "in_progress", "high", "qa", 14, 6, e3, sprint=sprint_r)
    wi("task", "Assembly SOP v2", projects["NanoSpark"], vysakh,
       "todo", "medium", "documentation", 8, 0, e3, sprint=sprint_r)
    wi("task", "Enclosure vendor PO", projects["NanoSpark"], anson,
       "blocked", "high", "business", 6, 2, e3, sprint=sprint_r)

    # Otto
    e4 = wi("epic", "Otto prototype validation", projects["Otto"], anson,
            "in_progress", "high", "development", 80, 30, sprint=sprint_r)
    wi("task", "Servo torque benchmarking", projects["Otto"], vysakh,
       "in_progress", "medium", "qa", 10, 4, e4, sprint=sprint_r)
    wi("task", "Gait firmware tuning", projects["Otto"], anson,
       "todo", "medium", "development", 12, 0, e4, sprint=sprint_r)

    # Operations
    e5 = wi("epic", "Flipkart NanoSpark relaunch", projects["Flipkart"], joseph,
            "in_progress", "high", "sales", 40, 12)
    wi("task", "A+ listing content refresh", projects["Flipkart"], joseph,
       "in_progress", "high", "marketing", 8, 3, e5)
    wi("task", "Festive pricing strategy", projects["Flipkart"], joseph,
       "todo", "medium", "business", 6, 0, e5)
    wi("task", "Packaging dieline v3", projects["Packaging"], joseph,
       "review", "medium", "design", 8, 6)

    # Dependencies
    items = {i.title: i for i in db.query(WorkItem).all()}
    for blocker, blocked in [
        ("Model temple environment kit", "Texture pass on environment kit"),
        ("Puzzle trigger framework", "Chapter 3 regression test plan"),
        ("PCB rev C DFM check", "Pilot batch incoming QC (50 units)"),
        ("Chapter 3 landing page design", "Build interactive robot showcase"),
    ]:
        db.add(Dependency(blocker_id=items[blocker].id, blocked_id=items[blocked].id))

    # Comments (some trigger AI flags)
    def comment(item_title, author, body, flags=""):
        db.add(Comment(work_item_id=items[item_title].id, author_id=author.id,
                       body=body, ai_flags=flags,
                       created_at=now - timedelta(hours=random.randint(1, 70))))
    comment("Save-state integration", kp,
            "Blocked: waiting on cloud save API keys from the platform vendor. Can't proceed until access is granted.",
            "blocker,dependency")
    comment("Enclosure vendor PO", anson,
            "Vendor quote came in 18% above budget. Risk of delay if we re-quote. Need a decision urgently.",
            "risk,urgent")
    comment("Pilot batch incoming QC (50 units)", vysakh,
            "12 of 50 boards tested. 1 failure so far - cold joint on U7. Logging photos to the task.")
    comment("Chapter 3 landing page design", vishnu,
            "First draft in Figma. Depends on final chapter key art from Noel before I can lock the hero section.",
            "dependency")
    comment("Puzzle trigger framework", kp,
            "Framework ready for review. All 14 trigger types covered with unit tests.")

    for u, msg, kind in [
        (joseph, "2 blockers and 1 urgent risk detected across departments", "risk"),
        (amal, "Puzzle trigger framework is waiting for your review", "approval"),
        (anson, "Enclosure vendor PO flagged urgent by AI comment scan", "risk"),
        (noel, "New subtask assigned: Bake lighting and LODs", "assignment"),
        (vysakh, "QC pilot batch due in 4 days", "info"),
    ]:
        db.add(Notification(user_id=u.id, message=msg, kind=kind))

    db.commit()
