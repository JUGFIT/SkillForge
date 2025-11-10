from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.refresh_token import RefreshToken
from app.utils import email_utils

# -----------------------------------------------------------
# 🧩 Password Hashing — Argon2id (secure + consistent)
# -----------------------------------------------------------
pwd_ctx = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB memory
    argon2__time_cost=3,  # 3 iterations
    argon2__parallelism=4,  # 4 threads
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# -----------------------------------------------------------
# 🔒 Password Utilities
# -----------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_ctx.verify(plain_password, hashed_password)
    except Exception:
        return False


def needs_rehash(hashed_password: str) -> bool:
    return pwd_ctx.needs_update(hashed_password)


# -----------------------------------------------------------
# ⏰ Timestamp Helper
# -----------------------------------------------------------
def _now() -> datetime:
    return datetime.now(timezone.utc)


# -----------------------------------------------------------
# 🔑 JWT Access Tokens
# -----------------------------------------------------------
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = _now() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": str(subject), "exp": int(expire.timestamp()), "type": "access"}
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc


# -----------------------------------------------------------
# 🔄 Refresh Token Helpers (Persistent / Rotatable)
# -----------------------------------------------------------
def _generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def create_and_store_refresh_token(db: Session, user) -> RefreshToken:
    """
    Create and persist a refresh token tied to the given user.
    Ensures that only the UUID is stored, not the full User object.
    """
    raw_token = _generate_refresh_token()
    expires_at = _now() + timedelta(
        days=getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 30)
    )

    new_rt = RefreshToken(
        user_id=str(user.id),  # ✅ FIXED: store only the UUID, not User instance
        token=raw_token,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(new_rt)
    db.commit()
    db.refresh(new_rt)
    return new_rt


def revoke_refresh_token(db: Session, token_str: str):
    rt = db.query(RefreshToken).filter(RefreshToken.token == token_str).first()
    if rt:
        rt.revoked = True
        db.add(rt)
        db.commit()


def rotate_refresh_token(
    db: Session, old_token_str: str, user
) -> Optional[RefreshToken]:
    old = db.query(RefreshToken).filter(RefreshToken.token == old_token_str).first()
    if old:
        old.revoked = True
        db.add(old)
        db.commit()

    return create_and_store_refresh_token(db, user)


def get_refresh_token_record(db: Session, token_str: str):
    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == token_str,
            RefreshToken.revoked.is_(
                False
            ),  # ✅ FIXED: Use .is_(False) instead of == False
        )
        .first()
    )


# -----------------------------------------------------------
# 👤 Current User (Bearer Dependency)
# -----------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_jwt(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

    from app.models.users import User

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    return user


# -----------------------------------------------------------
# 🧱 Project Role Validation (for RBAC)
# -----------------------------------------------------------
def require_project_role(project_id_param: str, allowed_roles: list[str]):
    """
    Dependency factory for project-scoped role validation.
    Example:
        dependencies=[Depends(require_project_role("project_id", ["owner","admin"]))]
    """

    def _dep(
        project_id: str = project_id_param,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        from app.models.project_member import ProjectMember

        member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
            )
            .first()
        )
        if not member or member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return member

    return _dep


# -----------------------------------------------------------
# 📧 Email Action Tokens (Verification / Reset)
# -----------------------------------------------------------
def create_action_token(user_id: str, action: str, expires_minutes: int = 60) -> str:
    expire = _now() + timedelta(minutes=expires_minutes)
    payload = {"sub": str(user_id), "exp": int(expire.timestamp()), "type": action}
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_action_token(token: str, expected_action: str):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != expected_action:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type"
            )
        return payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )


def send_verification_email(user_email: str, token: str):
    verify_url = f"{getattr(settings, 'APP_URL', 'http://127.0.0.1:8000')}/auth/verify-email?token={token}"
    subject = "Verify your SkillStack account"
    body = f"Click the link to verify your email: {verify_url}"
    try:
        email_utils.send_email_background(user_email, subject, body)
    except Exception:
        # Non-blocking; registration should still succeed even if email fails
        pass
