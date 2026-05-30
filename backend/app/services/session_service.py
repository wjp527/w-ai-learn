import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.question_set import QuestionSet
from app.models.study_session import StudySession
from app.schemas.session import (
    AnswerRecord,
    CreateSessionResponse,
    KnowledgePoint,
    Question,
    ReportResponse,
    SessionDetailResponse,
    SessionStatus,
    SubmitAnswerResponse,
    WrongQuestionSummary,
)
from app.config import settings
from app.services.generation_protocol import GenerationService
from app.services.session_repository import SessionRepository
from app.services.user_data_service import StudyPersistenceService
from app.utils.question_validator import repair_questions, validate_questions
from app.utils.validators import clean_source_text, validate_question_count, validate_source_text


class SessionNotFoundError(Exception):
    pass


class SessionNotReadyError(Exception):
    pass


class QuestionNotFoundError(Exception):
    pass


class SessionIncompleteError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def _friendly_error_message(exc: Exception) -> str:
    message = str(exc)
    if "response_format" in message or "json_schema" in message:
        return "AI 接口格式不兼容，请确认后端已更新并重启服务"
    if "OutputParserException" in type(exc).__name__ or "validation error" in message.lower():
        return "AI 返回格式异常，请重试或减少题目数量"
    if "api_key" in message.lower() or "authentication" in message.lower():
        return "DeepSeek API Key 无效或未配置，请检查 backend/.env"
    if len(message) > 200:
        return message[:200] + "..."
    return message or "AI 生成失败，请稍后重试"


class SessionService:
    def __init__(
        self,
        repository: SessionRepository,
        generation_service: GenerationService,
        persistence_service: StudyPersistenceService | None = None,
    ) -> None:
        self._repository = repository
        self._generation_service = generation_service
        self._persistence_service = persistence_service or StudyPersistenceService(
            generation_service
        )

    async def create_session(
        self,
        source_text: str,
        question_count: int,
        *,
        user_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> CreateSessionResponse:
        text_error = validate_source_text(source_text)
        if text_error:
            raise ValidationError(text_error)

        count_error = validate_question_count(question_count)
        if count_error:
            raise ValidationError(count_error)

        session_id = str(uuid.uuid4())
        cleaned_text = clean_source_text(source_text)
        session = StudySession(
            id=session_id,
            source_text=cleaned_text,
            question_count=question_count,
        )
        self._repository.save(session)
        if user_id and db is not None:
            await self._persistence_service.create_session_meta(
                db, user_id=user_id, session=session
            )
        asyncio.create_task(self._process_session(session_id, user_id=user_id))
        return CreateSessionResponse(session_id=session_id, status=SessionStatus.PROCESSING)

    async def create_session_from_question_set(
        self,
        question_set: QuestionSet,
        *,
        user_id: str,
        db: AsyncSession,
    ) -> CreateSessionResponse:
        session_id = str(uuid.uuid4())
        knowledge_points = [
            KnowledgePoint.model_validate(item) for item in question_set.knowledge_points
        ]
        questions = [Question.model_validate(item) for item in question_set.questions]
        session = StudySession(
            id=session_id,
            source_text=question_set.source_text,
            question_count=question_set.question_count,
            status=SessionStatus.READY,
            knowledge_points=knowledge_points,
            questions=questions,
        )
        self._repository.save(session)
        await self._persistence_service.create_session_meta(
            db,
            user_id=user_id,
            session=session,
            question_set_id=question_set.id,
        )
        return CreateSessionResponse(session_id=session_id, status=SessionStatus.READY)

    async def _process_session(self, session_id: str, *, user_id: str | None = None) -> None:
        session = self._repository.get(session_id)
        if session is None:
            return

        max_attempts = settings.llm_max_retries + 1
        last_error: str | None = None
        try:
            for attempt in range(max_attempts):
                try:
                    knowledge_points, questions = await self._generation_service.extract_and_generate(
                        session.source_text,
                        session.question_count,
                        retry_hint=last_error,
                    )
                    questions = repair_questions(questions)
                    validation_error = validate_questions(questions, session.question_count)
                    if validation_error:
                        questions = repair_questions(questions)
                        validation_error = validate_questions(questions, session.question_count)
                    if validation_error:
                        last_error = validation_error
                        raise ValueError(validation_error)

                    session.knowledge_points = knowledge_points
                    session.questions = questions
                    session.status = SessionStatus.READY
                    session.error_message = None
                    break
                except Exception as exc:  # noqa: BLE001
                    if attempt >= max_attempts - 1:
                        raise exc
            else:
                session.status = SessionStatus.FAILED
                session.error_message = "AI 生成失败，请稍后重试"
        except Exception as exc:  # noqa: BLE001
            session.status = SessionStatus.FAILED
            session.error_message = _friendly_error_message(exc)
        finally:
            session.mark_updated()
            self._repository.save(session)
            if user_id and session.status == SessionStatus.READY:
                from app.db.base import async_session_factory

                async with async_session_factory() as db:
                    await self._persistence_service.create_session_meta(
                        db, user_id=user_id, session=session
                    )

    def get_session(self, session_id: str) -> SessionDetailResponse:
        session = self._require_session(session_id)
        return SessionDetailResponse(
            session_id=session.id,
            status=session.status,
            knowledge_points=session.knowledge_points,
            questions=session.questions,
            error_message=session.error_message,
        )

    async def submit_answer(
        self,
        session_id: str,
        question_id: str,
        selected_answer: str,
        *,
        user_id: str | None = None,
    ) -> SubmitAnswerResponse:
        session = self._require_session(session_id)
        if session.status != SessionStatus.READY:
            raise SessionNotReadyError("会话尚未准备好，请稍后再试")

        if session.quiz_started_at is None:
            session.quiz_started_at = datetime.now(timezone.utc)

        question = next((item for item in session.questions if item.id == question_id), None)
        if question is None:
            raise QuestionNotFoundError("题目不存在")

        existing = next((item for item in session.answer_records if item.question_id == question_id), None)
        if existing is not None:
            session.answer_records = [
                item for item in session.answer_records if item.question_id != question_id
            ]

        is_correct = selected_answer == question.correct_answer
        session.answer_records.append(
            AnswerRecord(
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                answered_at=datetime.now(timezone.utc),
            )
        )
        session.mark_updated()
        self._repository.save(session)

        if user_id:
            await self._sync_answer_progress(session_id, user_id)

        return SubmitAnswerResponse(
            is_correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            source_evidence=question.source_evidence,
        )

    async def _sync_answer_progress(self, session_id: str, user_id: str) -> None:
        session = self._repository.get(session_id)
        if session is None:
            return
        from app.db.base import async_session_factory

        async with async_session_factory() as db:
            await self._persistence_service.update_session_meta_progress(
                db, user_id=user_id, session=session
            )

    async def get_report(
        self,
        session_id: str,
        *,
        user_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> ReportResponse:
        session = self._require_session(session_id)
        if session.status != SessionStatus.READY:
            raise SessionNotReadyError("会话尚未准备好，无法生成报告")

        if len(session.answer_records) < len(session.questions):
            raise SessionIncompleteError("请先完成全部题目")

        if session.report is None:
            session.finished_at = datetime.now(timezone.utc)
            session.report = await self._generation_service.generate_report(
                session.source_text,
                session.knowledge_points,
                session.questions,
                session.answer_records,
            )
            if session.quiz_started_at and session.finished_at:
                duration = int((session.finished_at - session.quiz_started_at).total_seconds())
                session.report.duration_seconds = duration
            session.mark_updated()
            self._repository.save(session)

        if user_id and db is not None and session.report is not None:
            await self._persistence_service.persist_completed_session(
                db,
                user_id=user_id,
                session=session,
                report=session.report,
            )

        return ReportResponse.model_validate(session.report.model_dump())

    def build_fallback_report(self, session: StudySession) -> ReportResponse:
        total = len(session.questions)
        correct_count = sum(1 for item in session.answer_records if item.is_correct)
        accuracy = round((correct_count / total) * 100, 1) if total else 0.0
        wrong_questions: list[WrongQuestionSummary] = []

        for record in session.answer_records:
            if record.is_correct:
                continue
            question = next(item for item in session.questions if item.id == record.question_id)
            wrong_questions.append(
                WrongQuestionSummary(
                    question_id=question.id,
                    stem=question.stem,
                    selected_answer=record.selected_answer,
                    correct_answer=question.correct_answer,
                )
            )

        duration_seconds = 0
        if session.quiz_started_at and session.finished_at:
            duration_seconds = int((session.finished_at - session.quiz_started_at).total_seconds())

        from app.schemas.session import StudyReport

        report = StudyReport(
            accuracy=accuracy,
            total_questions=total,
            correct_count=correct_count,
            wrong_questions=wrong_questions,
            weak_points=[item.title for item in session.knowledge_points[:2]],
            summary="本次学习已完成，建议回顾错题涉及的知识点。",
            duration_seconds=duration_seconds,
        )
        return ReportResponse.model_validate(report.model_dump())

    def _require_session(self, session_id: str) -> StudySession:
        session = self._repository.get(session_id)
        if session is None:
            raise SessionNotFoundError("会话不存在")
        return session
