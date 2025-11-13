import enum
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from prism_models.base import BaseModel
from prism_models.chat import Contact, ConversationMessage
from prism_models.content import Chunk, QAPair

# MessageFeedback model removed - using new Feedback model below


class FeedbackType(str, enum.Enum):
    THUMBS_DOWN = "thumbs_down"
    CORRECTION = "correction"
    ENHANCEMENT = "enhancement"
    DELETION = "deletion"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"


class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class FeedbackConfidence(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ABSOLUTE = "absolute"


class AugmentationAction(str, enum.Enum):
    CREATE = "create"
    CORRECT = "correct"
    ENHANCE = "enhance"
    DELETE = "delete"


class AugmentationStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisType(str, enum.Enum):
    CONTENT_ANALYSIS = "content_analysis"
    IMPACT_ASSESSMENT = "impact_assessment"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"


class Feedback(BaseModel):
    message_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("conversation_message.id"),
        nullable=True,
        index=True,
    )
    feedback_type: Mapped[FeedbackType] = mapped_column(String(50), nullable=False)

    correction: Mapped[str | None] = mapped_column(Text)
    status: Mapped[FeedbackStatus] = mapped_column(String(50), default=FeedbackStatus.PENDING, nullable=False, index=True)
    admin_notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    message: Mapped[Optional["ConversationMessage"]] = relationship()

    analysis: Mapped[list["FeedbackAnalysis"]] = relationship(back_populates="feedback", cascade="all, delete-orphan")
    augmentations: Mapped[list["Augmentation"]] = relationship(back_populates="feedback", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Feedback(id={self.id}, type='{self.feedback_type}', status='{self.status}')>"


class FeedbackAnalysis(BaseModel):
    __tablename__ = "feedback_analysis"
    feedback_id: Mapped[int] = mapped_column(Integer, ForeignKey("feedback.id"), nullable=False, index=True)

    llm_response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason_to_reject: Mapped[str | None] = mapped_column(Text)

    # Relationships
    feedback: Mapped["Feedback"] = relationship(back_populates="analysis")

    def __repr__(self):
        return f"<FeedbackAnalysis(id={self.id}, feedback_id={self.feedback_id})>"


class Augmentation(BaseModel):
    feedback_id: Mapped[int] = mapped_column(Integer, ForeignKey("feedback.id"), nullable=False, index=True)
    original_chunk_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("chunk.id"), nullable=True)
    generated_chunk_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("chunk.id"), nullable=True)
    # Relationships
    feedback: Mapped["Feedback"] = relationship(back_populates="augmentations")
    original_chunk: Mapped[Optional["Chunk"]] = relationship(foreign_keys=[original_chunk_id])
    generated_chunk: Mapped[Optional["Chunk"]] = relationship(foreign_keys=[generated_chunk_id])

    def __repr__(self):
        return f"<Augmentation(id={self.id})>"
