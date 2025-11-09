from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.models.concept import Concept
from app.schemas.concept import ConceptCreate, ConceptUpdate, ConceptResponse
from app.utils.auth import get_current_user
from app.models.users import User

router = APIRouter(prefix="/concepts", tags=["Concepts"])


@router.post("/", response_model=ConceptResponse, status_code=status.HTTP_201_CREATED)
def create_concept(
    concept_in: ConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Create a new concept (admin or roadmap owner context)."""
    concept = Concept(**concept_in.dict())
    db.add(concept)
    db.commit()
    db.refresh(concept)
    return concept


@router.get("/", response_model=List[ConceptResponse])
def list_concepts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """✅ List all active concepts."""
    concepts = db.query(Concept).filter(Concept.is_active == True).offset(skip).limit(limit).all()
    return concepts


@router.get("/{concept_id}", response_model=ConceptResponse)
def get_concept(
    concept_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Retrieve a concept by ID."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    return concept


@router.put("/{concept_id}", response_model=ConceptResponse)
def update_concept(
    concept_id: UUID,
    concept_update: ConceptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Update concept details."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    for field, value in concept_update.dict(exclude_unset=True).items():
        setattr(concept, field, value)

    db.commit()
    db.refresh(concept)
    return concept


@router.delete("/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept(
    concept_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Soft delete concept by marking inactive."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    concept.is_active = False
    db.commit()
    return None
