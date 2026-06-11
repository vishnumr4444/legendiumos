from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from .config import CORS_ORIGINS
from .seed import seed
from .routers import auth_router, workitems, command_center, dashboards, misc

app = FastAPI(title="Legendium OS API", version="1.0.0",
              description="AI-powered project management and operational "
                          "intelligence platform for the Legendium ecosystem.")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

for r in (auth_router.router, workitems.router, command_center.router,
          dashboards.router, misc.router):
    app.include_router(r)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "online", "platform": "Legendium OS"}

