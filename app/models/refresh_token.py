# app/models/refresh_token.py
import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    # Relationship with User model
    user = relationship("User", back_populates="refresh_tokens")

    def is_expired(self, now=None) -> bool:
        """Check if this refresh token is expired or revoked."""
        from datetime import datetime, timezone
        now = now or datetime.now(timezone.utc)
        return self.revoked or self.expires_at <= now

    def __repr__(self):
        return f"<RefreshToken user={self.user_id} revoked={self.revoked}>"
