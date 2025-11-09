# app/routers/invites.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app import models, schemas
from app.core.database import get_db
from app.utils.auth import get_current_user, hash_password, verify_password
from app.services.notifications import create_notification

router = APIRouter(prefix="/invites", tags=["Invites"])


def log_activity(db: Session, project_id, user_id, action, details="", metadata=None):
    activity = models.ActivityLog(
        project_id=project_id,
        user_id=user_id,
        action=action,
        details=details,
        meta_data=metadata or {},
    )
    db.add(activity)
    db.commit()
    return activity


@router.post("/generate", response_model=schemas.InviteResponse)
def generate_invite(
    invite_in: schemas.InviteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.query(models.Project).filter_by(id=invite_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to generate invites for this project",
        )

    token = secrets.token_urlsafe(24)
    token_hash = hash_password(token)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    invite = models.ProjectMember(
        project_id=invite_in.project_id,
        role=invite_in.role or "member",
        status="pending",
        invited_by=current_user.id,
        invite_token_hash=token_hash,
        invite_token_expires_at=expires_at,
        meta={"method": "invite_token"},
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    # Activity + Notification
    log_activity(
        db,
        project.id,
        current_user.id,
        "invite_generated",
        f"Generated invite for project '{project.name}' (role={invite.role})",
    )
    create_notification(
        db,
        current_user.id,
        title="Invite Created",
        message=f"You generated an invite for project '{project.name}'",
    )

    return {
        "invite_token": token,
        "expires_at": expires_at,
        "project_id": invite_in.project_id,
        "role": invite.role,
    }


@router.post("/accept/{token}", response_model=schemas.ProjectMemberResponse)
def accept_invite(
    token: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    pending_invites = (
        db.query(models.ProjectMember)
        .filter(models.ProjectMember.status == "pending")
        .all()
    )

    matched = None
    for invite in pending_invites:
        if invite.invite_token_hash and verify_password(
            token, invite.invite_token_hash
        ):
            matched = invite
            break

    if not matched:
        raise HTTPException(status_code=400, detail="Invalid invite token")

    if (
        matched.invite_token_expires_at
        and matched.invite_token_expires_at < datetime.utcnow()
    ):
        raise HTTPException(status_code=400, detail="Invite token has expired")

    matched.user_id = current_user.id
    matched.status = "active"
    matched.joined_at = datetime.utcnow()
    matched.invite_token_hash = None
    matched.invite_token_expires_at = None

    db.commit()
    db.refresh(matched)

    # Activity + Notification
    log_activity(
        db,
        matched.project_id,
        current_user.id,
        "invite_accepted",
        f"{current_user.username} accepted invite for project '{matched.project.name}'",
    )
    create_notification(
        db,
        matched.invited_by,
        title="Invite Accepted",
        message=f"{current_user.username} accepted your invite for project '{matched.project.name}'",
    )
    create_notification(
        db,
        current_user.id,
        title="Joined Project",
        message=f"You successfully joined project '{matched.project.name}'",
    )

    return matched
