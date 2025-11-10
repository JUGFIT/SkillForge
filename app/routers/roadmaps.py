from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.roadmap import Roadmap
from app.models.users import User
from app.schemas.roadmap import RoadmapCreate, RoadmapResponse, RoadmapUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


@router.post("/", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
def create_roadmap(
    roadmap: RoadmapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """✅ Create a new roadmap for the current user."""
    new_roadmap = Roadmap(
        title=roadmap.title.strip(),
        description=roadmap.description,
        is_public=roadmap.is_public,
        owner_id=current_user.id,
    )
    db.add(new_roadmap)
    db.commit()
    db.refresh(new_roadmap)
    return new_roadmap


@router.get("/", response_model=List[RoadmapResponse])
def list_roadmaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """✅ List all roadmaps (owned or public)."""
    roadmaps = (
        db.query(Roadmap)
        .filter(
            (Roadmap.is_public.is_(True)) | (Roadmap.owner_id == current_user.id)
        )  # ✅ FIXED: Use .is_(True) instead of == True
        .offset(skip)
        .limit(limit)
        .all()
    )
    return roadmaps


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """✅ Retrieve a specific roadmap by ID."""
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if not roadmap.is_public and roadmap.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return roadmap


@router.put("/{roadmap_id}", response_model=RoadmapResponse)
def update_roadmap(
    roadmap_id: UUID,
    roadmap_update: RoadmapUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """✅ Update a roadmap (only by owner)."""
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if roadmap.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the owner can update this roadmap"
        )

    for field, value in roadmap_update.dict(exclude_unset=True).items():
        setattr(roadmap, field, value)

    db.commit()
    db.refresh(roadmap)
    return roadmap


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_roadmap(
    roadmap_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """✅ Delete a roadmap (only by owner)."""
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if roadmap.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the owner can delete this roadmap"
        )

    db.delete(roadmap)
    db.commit()
    return None
