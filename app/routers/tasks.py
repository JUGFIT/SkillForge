from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app import models, schemas
from app.core.database import get_db
from app.utils.auth import get_current_user
from app.utils.crud_helpers import (
    detect_possible_duplicates,
    generate_task_key,
    clear_user_cache,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# -----------------------------------------------------------
# 🧩 CREATE TASK
# -----------------------------------------------------------
@router.post(
    "/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED
)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = (
        db.query(models.Project)
        .filter(
            models.Project.id == task.project_id,
            models.Project.owner_id == current_user.id,
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    # Detect duplicates
    duplicates = detect_possible_duplicates(db, task.project_id, task.title)

    new_task = models.Task(**task.dict(), task_key=generate_task_key(db, project))
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    clear_user_cache(current_user.id)

    return {
        "id": new_task.id,
        "task_key": new_task.task_key,
        "title": new_task.title,
        "description": new_task.description,
        "status": new_task.status,
        "priority": new_task.priority,
        "project_id": new_task.project_id,
        "assignee_id": new_task.assignee_id,
        "created_at": new_task.created_at,
        "updated_at": new_task.updated_at,
        "possible_duplicates": duplicates,
    }


# -----------------------------------------------------------
# 📋 LIST TASKS
# -----------------------------------------------------------
@router.get("/", response_model=List[schemas.TaskResponse])
def list_tasks(
    project_id: UUID,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = (
        db.query(models.Project)
        .filter(
            models.Project.id == project_id, models.Project.owner_id == current_user.id
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    query = db.query(models.Task).filter(models.Task.project_id == project.id)
    if status:
        query = query.filter(models.Task.status == status)

    return query.order_by(models.Task.created_at.desc()).all()


# -----------------------------------------------------------
# 🔍 GET SINGLE TASK
# -----------------------------------------------------------
@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = (
        db.query(models.Task)
        .join(models.Project)
        .filter(models.Task.id == task_id, models.Project.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    return task


# -----------------------------------------------------------
# ✏️ UPDATE TASK
# -----------------------------------------------------------
@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: UUID,
    data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = (
        db.query(models.Task)
        .join(models.Project)
        .filter(models.Task.id == task_id, models.Project.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    clear_user_cache(current_user.id)

    return task


# -----------------------------------------------------------
# ❌ DELETE TASK
# -----------------------------------------------------------
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = (
        db.query(models.Task)
        .join(models.Project)
        .filter(models.Task.id == task_id, models.Project.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")

    db.delete(task)
    db.commit()
    clear_user_cache(current_user.id)
    return None
