# API Documentation

Base URL: `http://localhost:8000`. Live interactive reference: `/docs` (Swagger UI).
All endpoints except `/api/auth/login` and `/api/health` require `Authorization: Bearer <JWT>`.

## Auth
| Method | Path | Body | Notes |
|---|---|---|---|
| POST | /api/auth/login | form: username, password | returns token + user |
| GET | /api/auth/me | - | current user |

## Work items
| Method | Path | Notes |
|---|---|---|
| GET | /api/work-items?project_id=&status= | RBAC-scoped list |
| GET | /api/work-items/{id} | full detail: comments, children, dependencies |
| POST | /api/work-items | admin/lead only; leads limited to own team; auto Jira create |
| PATCH | /api/work-items/{id}/status | body `{"status": "..."}`; auto Jira transition |
| POST | /api/work-items/{id}/comments | body `{"body": "..."}`; AI flag scan + lead escalation; mirrors to Jira |

## AI Command Center (admin/lead)
| Method | Path | Notes |
|---|---|---|
| POST | /api/command/preview | `{"prompt": "..."}` -> full plan with totals (no commit) |
| POST | /api/command/execute | `{"prompt", "plan"}` -> creates items, dependencies, notifications, Jira issues |

## Dashboards
| Method | Path | Notes |
|---|---|---|
| GET | /api/dashboard | role-aware payload: executive / lead / employee |
| GET | /api/dashboard/notifications | latest 20 for current user |

## Workload (admin/lead)
| Method | Path | Notes |
|---|---|---|
| GET | /api/workload | team utilization + AI rebalance suggestions |
| POST | /api/workload/reassign/{item_id}/{to_user_id} | apply a suggestion |

## Reports (admin/lead)
| Method | Path | Notes |
|---|---|---|
| GET | /api/reports/{daily\|weekly\|sprint\|executive}?format=json\|csv\|md | role-scoped |

## Knowledge
| Method | Path | Notes |
|---|---|---|
| POST | /api/knowledge/upload | multipart file; text formats indexed for RAG |
| GET | /api/knowledge | library list |

## Misc
GET /api/projects (role-scoped) · GET /api/team · GET /api/health
