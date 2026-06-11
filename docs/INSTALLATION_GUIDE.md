# Installation Guide

## Requirements
- Python 3.11+ and Node 18+ (dev), or Docker
- Optional: PostgreSQL 15+, OpenAI API key, Jira Cloud account

## Development
```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend (second terminal)
cd frontend
npm install
npm run dev
```
Open http://localhost:3000. First backend start creates and seeds the database automatically (7 demo users, password `legendium`).

## Production (Docker)
```bash
cp .env.example .env   # fill SECRET_KEY at minimum
docker compose up --build -d
```
Frontend on :3000, API on :8000.

## Production hardening checklist
- Set a strong `SECRET_KEY`; rotate Jira/OpenAI tokens via your secret manager.
- Move to Postgres: `DATABASE_URL=postgresql+psycopg://...` and add `psycopg[binary]` to requirements.
- Change all seeded passwords (or replace `seed.py` with your own bootstrap).
- Put both services behind HTTPS (nginx/Caddy) and set `CORS_ORIGINS` to your domain.
- Set `NEXT_PUBLIC_API_URL` on the frontend to the public API URL.

## Troubleshooting
- "API unreachable" on the dashboard -> backend isn't running on :8000 or CORS_ORIGINS doesn't include the frontend origin.
- Jira chips never appear -> JIRA_* env vars unset, or the token lacks project access.
- Fonts look plain offline -> Google Fonts unreachable; system fallbacks load automatically.
