from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from firebase_functions import https_fn
    from firebase_admin import initialize_app
    HAS_FIREBASE = True
except ImportError:
    HAS_FIREBASE = False

from .database import Base, engine, SessionLocal
from .config import CORS_ORIGINS
from .seed import seed
from .routers import auth_router, workitems, command_center, dashboards, misc

app = FastAPI(title="Legendium OS API", version="1.0.0",
              description="AI-powered project management and operational "
                          "intelligence platform for the Legendium ecosystem.")

if HAS_FIREBASE:
    try:
        initialize_app()
    except ValueError:
        pass # App already initialized

app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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

# Firebase Functions entry point
api = None
if HAS_FIREBASE:
    try:
        from a2wsgi import ASGIMiddleware
        wsgi_app = ASGIMiddleware(app)
        api = https_fn.on_request(wsgi_app)
    except ImportError:
        pass
