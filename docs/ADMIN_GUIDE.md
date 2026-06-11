# Admin Guide (Joseph)

## Accounts and roles
Seeded crew (password `legendium`, change in production):
| User | Role | Scope |
|---|---|---|
| joseph | admin | everything: all departments, AI Command, workload, reports, knowledge |
| amal | lead | VR/XR team: noel, vishnu, krishnaprasad |
| anson | lead | Robotics team: vysakh |
| noel, vishnu, krishnaprasad, vysakh | employee | own tasks only |

Rules enforced server-side:
- Employees see and touch only their own assignments. No peer visibility anywhere.
- Employees cannot create tasks; work flows down from leads.
- Leads create/assign only within their own team and see only their department.

## Daily operation
1. **Dashboard** is mission control: KPIs, department rings, project health, AI risk feed, crew load, upcoming deadlines.
2. **AI Command** for any new initiative: type the goal, review the generated plan (owners, hours, dependencies, milestones), then Approve & push.
3. **Workload** weekly: apply or dismiss AI rebalance suggestions.
4. **Reports** before reviews: executive brief in MD pastes cleanly into email/Teams.
5. **Knowledge**: keep SOPs and roadmaps uploaded; the AI plans better with context.

## Adding people / departments
Insert via DB or extend `backend/app/seed.py` (users, departments, projects sections), then restart with a fresh DB. A future admin UI can sit on the same endpoints.

## Audit
Sensitive actions (logins, item creation, status changes, AI executes) land in `audit_logs`.
