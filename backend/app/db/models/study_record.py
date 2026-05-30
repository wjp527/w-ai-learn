from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StudyRecord(Base):
    __tablename__ = "study_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    question_set_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("question_sets.id", ondelete="RESTRICT"), nullable=False
    )
    session_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    accuracy: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    wrong_questions: Mapped[list] = mapped_column(JSON, nullable=False)
    weak_points: Mapped[list] = mapped_column(JSON, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    user: Mapped["User"] = relationship(back_populates="study_records")
    question_set: Mapped["QuestionSet"] = relationship(back_populates="study_records")
