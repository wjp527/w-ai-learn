from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.schemas.session import (
    AnswerRecord,
    KnowledgePoint,
    Question,
    SessionStatus,
    StudyReport,
)


@dataclass
class StudySession:
    id: str
    source_text: str
    question_count: int
    status: SessionStatus = SessionStatus.PROCESSING
    knowledge_points: list[KnowledgePoint] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    answer_records: list[AnswerRecord] = field(default_factory=list)
    report: StudyReport | None = None
    error_message: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    quiz_started_at: datetime | None = None

    def mark_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
