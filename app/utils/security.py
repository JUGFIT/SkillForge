# pyright: reportMissingImports=false
from datetime import datetime, timedelta
from jose import JWTError, jwt  # type: ignore[import-not-found]
from passlib.context import CryptContext  # type: ignore[import-not-found]
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app import models

# ============================================================
# 🧩 PASSWORD HASHING — ARGON2id (OWASP Recommended)
# ============================================================

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB memory
    argon2__time_cost=3,  # 3 iterations
    argon2__parallelism=4,  # 4 threads
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its Argon2id hash."""
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """Check if an existing hash needs re-hashing (when parameters change)."""
    return pwd_context.needs_update(hashed_password)


# ============================================================
# 🔑 JWT TOKEN HANDLING
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ============================================================
# 👤 CURRENT USER DEPENDENCY
# ============================================================


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Decode JWT and return the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Optional: rehash if parameters changed
    if user.hashed_password and needs_rehash(user.hashed_password):
        user.hashed_password = hash_password("temporary")
        db.commit()

    return user
