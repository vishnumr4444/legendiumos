"""JWT auth + RBAC visibility rules.

Visibility model (per Legendium policy):
  admin    -> everything
  lead     -> own department's items + own subordinates
  employee -> ONLY items assigned to them. No peer visibility, even inside
              shared projects. Cross-task visibility is lead-only.
"""
import hashlib, os, hmac
from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import config
from .database import get_db
from .models import User

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "dept": user.department_id,
        "exp": datetime.utcnow() + timedelta(hours=config.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    cred_err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user = db.get(User, int(payload["sub"]))
        if not user:
            raise cred_err
        return user
    except jwt.PyJWTError:
        raise cred_err


def require_role(*roles):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker


def visible_assignee_ids(user: User, db: Session) -> list[int] | None:
    """Return assignee ids this user may see; None means unrestricted (admin)."""
    if user.role == "admin":
        return None
    if user.role == "lead":
        subs = db.query(User).filter(User.manager_id == user.id).all()
        dept_members = db.query(User).filter(User.department_id == user.department_id).all()
        ids = {user.id} | {s.id for s in subs} | {m.id for m in dept_members}
        return list(ids)
    return [user.id]
