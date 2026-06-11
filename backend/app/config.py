"""Legendium OS configuration. All values overridable via environment."""
import os

SECRET_KEY = os.getenv("SECRET_KEY", "legendium-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "12"))

# SQLite by default; point to Postgres in production:
# postgresql+psycopg://user:pass@host:5432/legendium
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legendium.db")

# OpenAI (AI Command Center). Without a key the engine falls back to the
# built-in deterministic decomposition templates so the demo works offline.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Jira Cloud
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")          # e.g. https://legendium.atlassian.net
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY_VRXR = os.getenv("JIRA_PROJECT_KEY_VRXR", "VRXR")
JIRA_PROJECT_KEY_ROBOTICS = os.getenv("JIRA_PROJECT_KEY_ROBOTICS", "ROBO")
JIRA_PROJECT_KEY_OPERATIONS = os.getenv("JIRA_PROJECT_KEY_OPERATIONS", "OPS")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
