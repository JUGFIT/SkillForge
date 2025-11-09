# app/routers/projects.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ActivityLog, Project, ProjectMember
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.notifications import create_notification
from app.utils.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


# -----------------------------------------------------------
# 🧩 Utility: Activity Logging
# -----------------------------------------------------------
def log_activity(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    action: str,
    details: str = "",
    metadata: dict | None = None,
):
    """Centralized project activity logger"""
    activity = ActivityLog(
        project_id=project_id,
        user_id=user_id,
        action=action,
        details=details,
        meta_data=metadata or {},
    )
    db.add(activity)
    db.commit()
    return activity


# -----------------------------------------------------------
# 🚀 Create Project
# -----------------------------------------------------------
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = (
        db.query(Project)
        .filter(Project.name == project_in.name, Project.owner_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Project with this name already exists"
        )

    new_project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id,
        status="active",
        visibility=project_in.visibility or "private",
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Automatically add owner as project member
    owner_member = ProjectMember(
        project_id=new_project.id,
        user_id=current_user.id,
        role="owner",
        status="active",
    )
    db.add(owner_member)
    db.commit()

    log_activity(
        db,
        new_project.id,
        current_user.id,
        "project_created",
        f"Project '{new_project.name}' created",
    )

    return new_project


# -----------------------------------------------------------
# 📋 List Projects
# -----------------------------------------------------------
@router.get("/", response_model=List[ProjectResponse])
def get_user_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects


# -----------------------------------------------------------
# 🔍 Get Project
# -----------------------------------------------------------
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Allow access to owner or active member
    is_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    if not (project.owner_id == current_user.id or is_member):
        raise HTTPException(
            status_code=403, detail="Not authorized to view this project"
        )

    return project


# -----------------------------------------------------------
# ✏️ Update Project
# -----------------------------------------------------------
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only project owner can update the project"
        )

    for field, value in project_in.dict(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    log_activity(
        db,
        project.id,
        current_user.id,
        "project_updated",
        f"Updated project '{project.name}'",
    )

    return project


# -----------------------------------------------------------
# 🗑️ Archive/Delete Project
# -----------------------------------------------------------
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only owner can archive/delete the project"
        )

    project.status = "archived"
    project.is_active = False
    db.commit()

    log_activity(
        db,
        project.id,
        current_user.id,
        "project_archived",
        f"Archived project '{project.name}'",
    )
    return None


# ============================================================
# 🔁 Ownership Transfer (Professional Version)
# ============================================================


class OwnershipTransferRequest(BaseModel):
    """Validated schema for ownership transfer"""

    new_owner_id: UUID = Field(
        ..., description="UUID of the user to transfer ownership to"
    )


@router.patch("/{project_id}/transfer", status_code=status.HTTP_200_OK)
def transfer_ownership(
    project_id: UUID,
    request: OwnershipTransferRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Transfer ownership of a project to another active member.
    Only the current owner can perform this action.
    """
    new_owner_id = request.new_owner_id

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the current owner can transfer ownership"
        )

    # Validate the target member
    new_owner_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == new_owner_id,
        )
        .first()
    )
    if not new_owner_member:
        raise HTTPException(
            status_code=404, detail="New owner must be an existing project member"
        )

    try:
        old_owner_id = project.owner_id

        # Update project and member roles atomically
        project.owner_id = new_owner_id
        db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == old_owner_id,
        ).update({"role": "member"})

        new_owner_member.role = "owner"
        db.commit()

        # Log activity
        log_activity(
            db,
            project_id,
            current_user.id,
            "ownership_transferred",
            f"Ownership transferred from {current_user.username} to member {new_owner_id}",
        )

        # Notify both parties
        create_notification(
            db,
            new_owner_id,
            title="You Are Now the Project Owner",
            message=f"You have been made the owner of project '{project.name}'.",
        )
        create_notification(
            db,
            old_owner_id,
            title="Ownership Transferred",
            message=f"You transferred ownership of '{project.name}' to another member.",
        )

        db.refresh(project)
        return {
            "message": "Ownership transferred successfully",
            "project_id": str(project_id),
            "new_owner_id": str(new_owner_id),
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")
