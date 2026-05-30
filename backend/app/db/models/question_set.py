from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QuestionSet(Base):
    __tablename__ = "question_sets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_points: Mapped[list] = mapped_column(JSON, nullable=False)
    questions: Mapped[list] = mapped_column(JSON, nullable=False)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    user: Mapped["User"] = relationship(back_populates="question_sets")
    study_records: Mapped[list["StudyRecord"]] = relationship(back_populates="question_set")
    session_metas: Mapped[list["StudySessionMeta"]] = relationship(back_populates="question_set")
