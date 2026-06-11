# System Architecture

```
┌──────────────────────────┐        ┌───────────────────────────────┐
│  Frontend · Next.js 14   │  REST  │  Backend · FastAPI            │
│  React 18 + TS + Tailwind├───────►│  ├ Auth (JWT, RBAC)           │
│  Day/Night identity      │  JWT   │  ├ AI Engine (OpenAI/local)   │
│  SVG viz, drag-drop board│        │  ├ Workload Engine            │
└──────────────────────────┘        │  ├ Comment Intelligence       │
                                    │  ├ Reports (CSV/MD/JSON)      │
                                    │  └ Knowledge (RAG retrieval)  │
                                    └───────┬───────────┬───────────┘
                                            │           │
                                   ┌────────▼───┐  ┌────▼─────────┐
                                   │ SQLAlchemy │  │ Integrations │
                                   │ SQLite /   │  │ Jira Cloud   │
                                   │ PostgreSQL │  │ OpenAI API   │
                                   └────────────┘  └──────────────┘
```

## Layers
- **Frontend**: stateless SPA pages; token in localStorage; every request bears the JWT. Theme tokens implement the dual brand identity.
- **API**: routers per domain (`auth`, `work-items`, `command`, `dashboard`, `workload`, `reports`, `knowledge`). All RBAC checks server-side.
- **Services**: `ai_engine` (LLM with strict JSON contract + offline fallback), `jira_client` (REST v3, no-op until configured), `workload` (utilization + suggestions).
- **Data**: single WorkItem table with type discriminator mirrors Jira's hierarchy; Dependency edges; audit log on sensitive actions.

## RBAC model
| Role | Sees | Creates |
|---|---|---|
| admin (Joseph) | everything | anything |
| lead (Amal, Anson) | own dept + own team's items | items for own team |
| employee | own assigned items only | nothing (tasks flow down) |

Employee isolation is absolute: no peer visibility even inside a shared project. If employees later get direct Jira accounts, mirror this with Jira issue security schemes (see JIRA_INTEGRATION.md).

## Scaling path
- Swap SQLite -> Postgres via `DATABASE_URL` (no code change).
- Swap keyword retrieval -> Qdrant in `command_center._rag_context` (interface unchanged).
- Backend is stateless: run N replicas behind a load balancer.
