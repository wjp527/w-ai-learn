import asyncio

import pytest

from app.schemas.session import SessionStatus
from app.services.session_service import SessionIncompleteError, SessionNotFoundError, ValidationError
from tests.conftest import SOURCE_TEXT, FakeGenerationService
from app.services.session_repository import SessionRepository
from app.services.session_service import SessionService


@pytest.mark.asyncio
async def test_create_session_starts_processing(session_service: SessionService):
    result = await session_service.create_session(SOURCE_TEXT, 5)
    assert result.status == SessionStatus.PROCESSING
    assert result.session_id

    await asyncio.sleep(0.05)
    detail = session_service.get_session(result.session_id)
    assert detail.status == SessionStatus.READY
    assert len(detail.questions) == 5


@pytest.mark.asyncio
async def test_create_session_rejects_short_text(session_service: SessionService):
    with pytest.raises(ValidationError):
        await session_service.create_session("太短", 5)


@pytest.mark.asyncio
async def test_submit_answer_and_report_flow(session_service: SessionService):
    created = await session_service.create_session(SOURCE_TEXT, 5)
    await asyncio.sleep(0.05)
    detail = session_service.get_session(created.session_id)
    first = detail.questions[0]

    answer = await session_service.submit_answer(created.session_id, first.id, first.correct_answer)
    assert answer.is_correct is True

    for question in detail.questions[1:]:
        await session_service.submit_answer(created.session_id, question.id, "错误答案")

    report = await session_service.get_report(created.session_id)
    assert report.total_questions == 5
    assert report.correct_count == 1
    assert len(report.wrong_questions) == 4


@pytest.mark.asyncio
async def test_get_report_requires_all_answers(session_service: SessionService):
    created = await session_service.create_session(SOURCE_TEXT, 5)
    await asyncio.sleep(0.05)

    with pytest.raises(SessionIncompleteError):
        await session_service.get_report(created.session_id)


def test_get_session_not_found(session_service: SessionService):
    with pytest.raises(SessionNotFoundError):
        session_service.get_session("missing-id")
