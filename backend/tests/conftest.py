import os
from urllib.parse import urlparse

import pymysql
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.config import settings
from app.db.base import async_session_factory
from app.db.models.question_set import QuestionSet
from app.db.models.session_meta import StudySessionMeta
from app.db.models.study_record import StudyRecord
from app.db.models.user import User
from app.main import create_app
from app.schemas.session import (
    KnowledgePoint,
    Question,
    QuestionType,
    SessionStatus,
    StudyReport,
    WrongQuestionSummary,
)
from app.services.session_repository import SessionRepository
from app.services.session_service import SessionService
from app.services.user_data_service import StudyPersistenceService


SOURCE_TEXT = (
    "赤壁之战发生于208年，曹操率军南下。孙刘联军以火攻大破曹军于赤壁，"
    "奠定了三国鼎立的基础。赤壁之战后，三国鼎立的局面初步形成。"
) * 2


class FakeGenerationService:
    async def extract_and_generate(
        self,
        source_text: str,
        question_count: int,
        *,
        retry_hint: str | None = None,
    ) -> tuple[list[KnowledgePoint], list[Question]]:
        knowledge_points = [
            KnowledgePoint(
                id="kp1",
                title="赤壁之战时间",
                description="赤壁之战发生于208年",
                sourceEvidence="赤壁之战发生于208年",
            )
        ]
        questions = []
        for index in range(question_count):
            if index % 2 == 0:
                questions.append(
                    Question(
                        id=f"q{index + 1}",
                        type=QuestionType.SINGLE_CHOICE,
                        stem="赤壁之战发生于哪一年？",
                        options=["208年", "220年", "200年", "189年"],
                        correctAnswer="208年",
                        explanation="原文明确记载发生于208年。",
                        sourceEvidence="赤壁之战发生于208年",
                    )
                )
            else:
                questions.append(
                    Question(
                        id=f"q{index + 1}",
                        type=QuestionType.TRUE_FALSE,
                        stem="赤壁之战后，三国鼎立的局面初步形成。",
                        options=["对", "错"],
                        correctAnswer="对",
                        explanation="原文提到三国鼎立局面初步形成。",
                        sourceEvidence="赤壁之战后，三国鼎立的局面初步形成。",
                    )
                )
        return knowledge_points, questions

    async def generate_report(
        self,
        source_text: str,
        knowledge_points: list[KnowledgePoint],
        questions: list[Question],
        answer_records: list,
    ) -> StudyReport:
        total = len(questions)
        correct_count = sum(1 for item in answer_records if item.is_correct)
        wrong_questions = []
        for record in answer_records:
            if record.is_correct:
                continue
            question = next(item for item in questions if item.id == record.question_id)
            wrong_questions.append(
                WrongQuestionSummary(
                    questionId=question.id,
                    stem=question.stem,
                    selectedAnswer=record.selected_answer,
                    correctAnswer=question.correct_answer,
                )
            )
        return StudyReport(
            accuracy=round((correct_count / total) * 100, 1),
            totalQuestions=total,
            correctCount=correct_count,
            wrongQuestions=wrong_questions,
            weakPoints=["三国时间节点"],
            summary="建议再复习时间线相关知识点。",
            durationSeconds=120,
        )

    async def generate_title(self, source_text: str) -> str:
        return "三国历史 · 赤壁之战"


@pytest.fixture(autouse=True)
def enable_mock_login(monkeypatch):
    monkeypatch.setenv("WECHAT_MOCK_LOGIN", "true")
    settings.wechat_mock_login = True


@pytest.fixture(scope="session")
def db_available():
    parsed = urlparse(settings.database_url.replace("+asyncmy", "").replace("+pymysql", ""))
    database = (parsed.path or "").lstrip("/").split("?")[0] or "w_ai_learn"
    try:
        connection = pymysql.connect(
            host=parsed.hostname or "127.0.0.1",
            port=parsed.port or 3306,
            user=parsed.username or "root",
            password=parsed.password or "",
            database=database,
            charset="utf8mb4",
        )
        connection.close()
        return True
    except Exception:  # noqa: BLE001
        return False


@pytest.fixture
def require_db(db_available):
    if not db_available:
        pytest.skip("MySQL 不可用，请检查 backend/.env 中的 DATABASE_URL")


async def _clear_user_tables() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(StudyRecord))
        await session.execute(delete(StudySessionMeta))
        await session.execute(delete(QuestionSet))
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def cleanup_db(require_db):
    await _clear_user_tables()
    yield
    await _clear_user_tables()


@pytest.fixture
def session_service() -> SessionService:
    generation = FakeGenerationService()
    persistence = StudyPersistenceService(generation)
    return SessionService(SessionRepository(), generation, persistence)


@pytest.fixture
def app(session_service: SessionService):
    return create_app(session_service=session_service)


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.fixture
async def db_client(app, cleanup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


async def login(client: AsyncClient, code: str = "test-code-001") -> dict:
    response = await client.post("/auth/wechat/login", json={"code": code})
    assert response.status_code == 200
    payload = response.json()
    return payload


async def auth_headers(client: AsyncClient, code: str = "test-code-001") -> dict[str, str]:
    payload = await login(client, code)
    return {"Authorization": f"Bearer {payload['token']}"}


async def complete_session(client: AsyncClient, headers: dict[str, str] | None = None) -> str:
    request_kwargs = {"json": {"sourceText": SOURCE_TEXT, "questionCount": 5}}
    if headers:
        request_kwargs["headers"] = headers
    create_response = await client.post("/sessions", **request_kwargs)
    assert create_response.status_code == 200
    session_id = create_response.json()["sessionId"]

    import asyncio

    detail = None
    for _ in range(20):
        detail_response = await client.get(f"/sessions/{session_id}")
        detail = detail_response.json()
        if detail["status"] == SessionStatus.READY.value:
            break
        await asyncio.sleep(0.05)

    assert detail is not None
    assert detail["status"] == SessionStatus.READY.value

    for question in detail["questions"]:
        answer_kwargs = {
            "json": {
                "questionId": question["id"],
                "selectedAnswer": question["correctAnswer"],
            }
        }
        if headers:
            answer_kwargs["headers"] = headers
        answer_response = await client.post(f"/sessions/{session_id}/answers", **answer_kwargs)
        assert answer_response.status_code == 200

    report_kwargs = {}
    if headers:
        report_kwargs["headers"] = headers
    report_response = await client.get(f"/sessions/{session_id}/report", **report_kwargs)
    assert report_response.status_code == 200
    return session_id
