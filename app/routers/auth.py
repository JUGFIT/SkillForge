# app/routers/auth.py
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import requests

from app.core.database import get_db
from app.models.users import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    TokenPair,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserProfile,
)
from app.utils import auth as auth_utils
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# -----------------------------------------------------------
# 🧩 REGISTER USER
# -----------------------------------------------------------
@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=auth_utils.hash_password(payload.password),
        full_name=payload.full_name,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email (optional async)
    token = auth_utils.create_action_token(
        str(user.id), "verify", expires_minutes=60 * 24
    )
    print(f"🔐 EMAIL VERIFICATION TOKEN for {user.email}: {token}")
    auth_utils.send_verification_email(user.email, token)

    return {
        "message": "User registered successfully. Verification email sent.",
        "user": user,
    }


# -----------------------------------------------------------
# 🔑 LOGIN USER (ACCESS + REFRESH TOKEN PAIR)
# -----------------------------------------------------------
@router.post("/login", response_model=TokenPair)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not auth_utils.verify_password(
        payload.password, user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not getattr(user, "is_verified", True):
        raise HTTPException(status_code=401, detail="Email not verified")

    # Generate JWT access + refresh
    access = auth_utils.create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_record = auth_utils.create_and_store_refresh_token(db, user)

    return {
        "access_token": access,
        "refresh_token": refresh_record.token,
        "token_type": "bearer",
    }


# -----------------------------------------------------------
# ♻️ REFRESH TOKEN (ROTATION)
# -----------------------------------------------------------
@router.post("/refresh", response_model=TokenPair)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    rt = auth_utils.get_refresh_token_record(db, payload.refresh_token)
    if not rt or rt.is_expired():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == rt.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Rotate refresh token
    new_rt = auth_utils.rotate_refresh_token(db, payload.refresh_token, user)
    access = auth_utils.create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access,
        "refresh_token": new_rt.token,
        "token_type": "bearer",
    }


# -----------------------------------------------------------
# 🚪 LOGOUT (REVOKE REFRESH TOKEN)
# -----------------------------------------------------------
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    auth_utils.revoke_refresh_token(db, payload.refresh_token)
    return {"message": "Logged out successfully."}


# -----------------------------------------------------------
# 👤 GET CURRENT USER
# -----------------------------------------------------------
@router.get("/me", response_model=UserProfile)
def get_me(user: User = Depends(auth_utils.get_current_user)):
    return user


# -----------------------------------------------------------
# 🔐 FORGOT PASSWORD FLOW
# -----------------------------------------------------------
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        return {"message": "If an account exists, an email has been sent."}

    token = auth_utils.create_action_token(str(user.id), "reset", expires_minutes=60)
    auth_utils.send_reset_email(user.email, token)
    return {"message": "If an account exists, an email has been sent."}


# -----------------------------------------------------------
# 🔄 RESET PASSWORD
# -----------------------------------------------------------
@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user_id = auth_utils.verify_action_token(payload.token, "reset")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = auth_utils.hash_password(payload.new_password)
    db.add(user)
    db.commit()
    return {"message": "Password reset successful."}


# -----------------------------------------------------------
# ✅ VERIFY EMAIL
# -----------------------------------------------------------
@router.get("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(token: str, db: Session = Depends(get_db)):
    user_id = auth_utils.verify_action_token(token, "verify")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.add(user)
    db.commit()
    return {"message": "Email verified successfully."}


# -----------------------------------------------------------
# 🌐 GOOGLE OAUTH 2.0 (SERVER CALLBACK)
# -----------------------------------------------------------
@router.get("/oauth/google/callback")
def google_oauth_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles Google OAuth redirect (the front-end should send ?code=... to this endpoint).
    """
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")

    # Exchange auth code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": "http://127.0.0.1:8000/auth/oauth/google/callback",
        "grant_type": "authorization_code",
    }
    resp = requests.post(token_url, data=data)
    if not resp.ok:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    tokens = resp.json()
    id_token = tokens.get("id_token")

    # Verify the ID token via Google's public API
    user_info = requests.get(
        f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    ).json()
    email = user_info.get("email")
    name = user_info.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    # Create or get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            username=email.split("@")[0],
            email=email,
            full_name=name,
            is_verified=True,
            hashed_password=auth_utils.hash_password("oauth-google"),  # dummy hash
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Issue tokens
    access = auth_utils.create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_record = auth_utils.create_and_store_refresh_token(db, user)

    return JSONResponse(
        {
            "access_token": access,
            "refresh_token": refresh_record.token,
            "token_type": "bearer",
            "message": "Google OAuth login successful",
        }
    )
