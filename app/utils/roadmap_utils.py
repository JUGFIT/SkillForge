# app/utils/roadmap_utils.py
from sqlalchemy.orm import Session

from app.models.roadmap_step import RoadmapStep


def normalize_positions(db: Session, roadmap_id):
    """
    Ensure roadmap steps for a roadmap are sequentially numbered starting at 1.
    Called automatically after create, update, delete, or reorder operations.
    """
    steps = (
        db.query(RoadmapStep)
        .filter(RoadmapStep.roadmap_id == roadmap_id)
        .order_by(RoadmapStep.position.asc())
        .all()
    )

    changed = False
    for idx, step in enumerate(steps, start=1):
        if step.position != idx:
            step.position = idx
            changed = True

    if changed:
        db.commit()

    # Return updated list for optional logging or testing
    return steps
