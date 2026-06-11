# Legendium OS

AI-powered project management and operational intelligence for the Legendium ecosystem (VR/XR, Robotics, Operations).

## What it does
- **AI Command Center**: natural language -> epics, stories, tasks, subtasks with owners, estimates, disciplines, dependencies and milestones. Review the plan, approve, push to Jira.
- **Role dashboards**: Executive (Joseph), Lead (Amal, Anson), Employee (own tasks only). Hard RBAC: employees never see peer tasks.
- **Mission Board**: drag-and-drop kanban, synced to Jira when configured.
- **Workload Engine**: utilization vs capacity, skill-matched AI rebalance suggestions with one-click apply.
- **Comment Intelligence**: every comment scanned for blocker / risk / dependency / urgency; leads auto-notified.
- **Reports**: daily, weekly, sprint, executive in CSV / Markdown / JSON, scoped by role.
- **Knowledge Base**: uploads indexed and fed to the AI as planning context (RAG).
- **Dual identity**: Day (clean cyan/teal) and Night (Legendium Universe) themes.

## Quick start (dev)
Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Frontend:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000. Demo logins: joseph / amal / anson / noel / vishnu / krishnaprasad / vysakh, password `legendium`.

## Quick start (Docker)
```bash
cp .env.example .env
docker compose up --build
```

## Configuration
Everything optional degrades gracefully:
- No `OPENAI_API_KEY` -> deterministic offline planning engine.
- No `JIRA_*` -> sync idles, app fully functional standalone.
- Default DB is SQLite; set `DATABASE_URL` for Postgres.

## Docs
See `/docs`: installation, architecture, API, database schema + ER diagram, Jira integration, AI workflows, admin and user guides, user flows.

API reference is also live at http://localhost:8000/docs (Swagger).
