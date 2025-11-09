# app/routers/members.py
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.database import get_db
from app.services.notifications import create_notification
from app.utils.auth import get_current_user

router = APIRouter(prefix="/members", tags=["Project Members"])


# Utility: create an activity log entry
def log_activity(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    action: str,
    details: str = "",
    metadata: dict | None = None,
):
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


@router.post(
    "/",
    response_model=schemas.ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    member_in: schemas.ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.query(models.Project).filter_by(id=member_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Only owner can directly add members
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to manage members for this project"
        )

    existing = (
        db.query(models.ProjectMember)
        .filter_by(project_id=member_in.project_id, user_id=member_in.user_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    new_member = models.ProjectMember(
        project_id=member_in.project_id,
        user_id=member_in.user_id,
        role=member_in.role or "member",
        status="active",
        invited_by=current_user.id,
        joined_at=datetime.utcnow(),
        meta={"added_via": "direct_add"},
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    # Activity + Notification
    log_activity(
        db,
        project.id,
        current_user.id,
        "member_added",
        f"Added member {member_in.user_id} to project '{project.name}'",
    )
    if member_in.user_id:
        create_notification(
            db,
            member_in.user_id,
            title="Added to Project",
            message=f"You were added to project '{project.name}' by {current_user.username}",
        )

    return new_member


@router.get("/{project_id}", response_model=List[schemas.ProjectMemberResponse])
def list_members(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.query(models.Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_member = (
        db.query(models.ProjectMember)
        .filter_by(project_id=project_id, user_id=current_user.id)
        .first()
    )
    if not (project.owner_id == current_user.id or is_member):
        raise HTTPException(status_code=403, detail="You are not part of this project")

    members = db.query(models.ProjectMember).filter_by(project_id=project_id).all()
    return members


@router.patch("/{member_id}", response_model=schemas.ProjectMemberResponse)
def update_member(
    member_id: UUID,
    data: schemas.ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    member = (
        db.query(models.ProjectMember)
        .join(models.Project)
        .filter(
            models.ProjectMember.id == member_id,
            models.Project.owner_id == current_user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found or unauthorized")

    old_role = member.role
    for key, value in data.dict(exclude_unset=True).items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)

    # Activity + Notification
    log_activity(
        db,
        member.project_id,
        current_user.id,
        "member_updated",
        f"Updated member {member.user_id or ''} (role {old_role} → {member.role})",
    )
    if member.user_id:
        create_notification(
            db,
            member.user_id,
            title="Membership Updated",
            message=f"Your project role was updated in '{member.project.name}'",
        )

    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    member = (
        db.query(models.ProjectMember)
        .join(models.Project)
        .filter(
            models.ProjectMember.id == member_id,
            models.Project.owner_id == current_user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found or unauthorized")

    project_name = member.project.name
    target_user_id = member.user_id

    db.delete(member)
    db.commit()

    # Activity + Notification
    log_activity(
        db,
        member.project_id,
        current_user.id,
        "member_removed",
        f"Removed member {target_user_id} from project '{project_name}'",
    )
    if target_user_id:
        create_notification(
            db,
            target_user_id,
            title="Removed from Project",
            message=f"You were removed from project '{project_name}' by {current_user.username}",
        )
    return None
