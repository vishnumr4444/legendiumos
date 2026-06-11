from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, AuditLog
from ..auth import verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username.lower()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Incorrect username or password")
    db.add(AuditLog(user_id=user.id, action="login")); db.commit()
    return {"access_token": create_token(user), "token_type": "bearer",
            "user": _user_dict(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _user_dict(user)


def _user_dict(u: User) -> dict:
    return {"id": u.id, "username": u.username, "full_name": u.full_name,
            "role": u.role, "title": u.title, "department_id": u.department_id,
            "avatar_color": u.avatar_color}
