# app/routers/roadmap_steps.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
# ✅ Use the background task system instead of direct normalization
from app.core.task_executor import enqueue
from app.models.roadmap import Roadmap
from app.models.roadmap_step import RoadmapStep
from app.models.users import User
from app.schemas.roadmap_step import (RoadmapStepCreate, RoadmapStepResponse,
                                      RoadmapStepUpdate)
from app.tasks.normalize_tasks import normalize_roadmap_task
from app.utils.auth import get_current_user

router = APIRouter(prefix="/roadmap-steps", tags=["Roadmap Steps"])


# --- Helpers ---
def _ensure_owner(db: Session, roadmap: Roadmap, user: User):
    if roadmap.owner_id != user.id:
        raise HTTPException(
            status_code=403, detail="Only roadmap owner may modify steps"
        )


# --- Create step ---
@router.post(
    "/", response_model=RoadmapStepResponse, status_code=status.HTTP_201_CREATED
)
def create_step(
    step_in: RoadmapStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == step_in.roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    _ensure_owner(db, roadmap, current_user)

    # Determine default position
    if getattr(step_in, "position", None) is None or step_in.position == 0:
        max_pos = (
            db.query(RoadmapStep.position)
            .filter(RoadmapStep.roadmap_id == step_in.roadmap_id)
            .order_by(RoadmapStep.position.desc())
            .limit(1)
            .first()
        )
        next_pos = (max_pos[0] if max_pos and max_pos[0] else 0) + 1
    else:
        next_pos = step_in.position

    new_step = RoadmapStep(
        roadmap_id=step_in.roadmap_id,
        concept_id=getattr(step_in, "concept_id", None),
        title=step_in.title,
        description=getattr(step_in, "description", None),
        position=next_pos,
        estimated_hours=getattr(step_in, "estimated_hours", None),
        resources=getattr(step_in, "resources", None),
    )

    db.add(new_step)
    db.commit()
    db.refresh(new_step)

    # 🔄 Defer normalization to background for performance & transaction safety
    enqueue(normalize_roadmap_task, step_in.roadmap_id)

    db.refresh(new_step)
    return new_step


# --- List steps for roadmap ---
@router.get("/roadmap/{roadmap_id}", response_model=List[RoadmapStepResponse])
def list_steps_for_roadmap(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 200,
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    if not roadmap.is_public and roadmap.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this roadmap"
        )

    steps = (
        db.query(RoadmapStep)
        .filter(RoadmapStep.roadmap_id == roadmap_id)
        .order_by(RoadmapStep.position.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return steps


# --- Get single step ---
@router.get("/{step_id}", response_model=RoadmapStepResponse)
def get_step(
    step_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    step = db.query(RoadmapStep).filter(RoadmapStep.id == step_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    roadmap = db.query(Roadmap).filter(Roadmap.id == step.roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Parent roadmap not found")
    if not roadmap.is_public and roadmap.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this step")

    return step


# --- Update step ---
@router.put("/{step_id}", response_model=RoadmapStepResponse)
def update_step(
    step_id: UUID,
    step_in: RoadmapStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    step = db.query(RoadmapStep).filter(RoadmapStep.id == step_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    roadmap = db.query(Roadmap).filter(Roadmap.id == step.roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Parent roadmap not found")

    _ensure_owner(db, roadmap, current_user)

    payload = step_in.dict(exclude_unset=True)
    position_changed = "position" in payload and payload["position"] != step.position

    for k, v in payload.items():
        setattr(step, k, v)

    db.add(step)
    db.commit()
    db.refresh(step)

    # 🔄 Normalize if position changed
    if position_changed:
        enqueue(normalize_roadmap_task, roadmap.id)

    return step


# --- Delete step ---
@router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_step(
    step_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    step = db.query(RoadmapStep).filter(RoadmapStep.id == step_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    roadmap = db.query(Roadmap).filter(Roadmap.id == step.roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Parent roadmap not found")

    _ensure_owner(db, roadmap, current_user)

    roadmap_id = step.roadmap_id
    db.delete(step)
    db.commit()

    # 🔄 Schedule background normalization
    enqueue(normalize_roadmap_task, roadmap_id)
    return None


# --- Reorder steps ---
class ReorderRequest(BaseModel):
    roadmap_id: UUID
    order: List[UUID]


@router.patch("/reorder", status_code=status.HTTP_200_OK)
def reorder_steps(
    payload: ReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == payload.roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    _ensure_owner(db, roadmap, current_user)

    steps = (
        db.query(RoadmapStep)
        .filter(RoadmapStep.roadmap_id == payload.roadmap_id)
        .order_by(RoadmapStep.position.asc())
        .all()
    )
    step_map = {s.id: s for s in steps}

    invalid_ids = [sid for sid in payload.order if sid not in step_map]
    if invalid_ids:
        raise HTTPException(status_code=400, detail={"invalid_step_ids": invalid_ids})

    # Reassign positions
    for idx, step_id in enumerate(payload.order, start=1):
        step_map[step_id].position = idx

    # Add missing steps at the end
    remaining = [s for s in steps if s.id not in payload.order]
    next_pos = len(payload.order) + 1
    for s in remaining:
        s.position = next_pos
        next_pos += 1

    db.commit()

    # 🔄 Normalize asynchronously
    enqueue(normalize_roadmap_task, payload.roadmap_id)

    reordered = (
        db.query(RoadmapStep.id)
        .filter(RoadmapStep.roadmap_id == payload.roadmap_id)
        .order_by(RoadmapStep.position.asc())
        .all()
    )
    reordered_ids = [r[0] for r in reordered]
    return {"detail": "Steps reordered successfully", "new_order": reordered_ids}
