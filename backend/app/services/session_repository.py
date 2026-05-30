import json
from pathlib import Path

from app.models.study_session import StudySession
from app.schemas.session import SessionStatus


class SessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, StudySession] = {}

    def save(self, session: StudySession) -> None:
        self._sessions[session.id] = session

    def get(self, session_id: str) -> StudySession | None:
        return self._sessions.get(session_id)

    def clear(self) -> None:
        self._sessions.clear()


class FileSessionRepository(SessionRepository):
    def __init__(self, file_path: str) -> None:
        super().__init__()
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, session: StudySession) -> None:
        super().save(session)
        payload = {
            sid: {
                "id": item.id,
                "source_text": item.source_text,
                "question_count": item.question_count,
                "status": item.status.value,
                "error_message": item.error_message,
            }
            for sid, item in self._sessions.items()
        }
        self._file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
