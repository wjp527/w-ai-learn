import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.question_set import QuestionSet
from app.db.models.session_meta import StudySessionMeta
from app.db.models.study_record import StudyRecord
from app.models.study_session import StudySession
from app.schemas.session import StudyReport
from app.services.generation_protocol import GenerationService
from app.utils.display import infer_type_label, truncate_title


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class StudyPersistenceService:
    def __init__(self, generation_service: GenerationService | None = None) -> None:
        self._generation_service = generation_service

    async def create_session_meta(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        session: StudySession,
        question_set_id: str | None = None,
    ) -> None:
        title = truncate_title(session.source_text)
        total_questions = len(session.questions) or session.question_count
        existing = await db.get(StudySessionMeta, session.id)
        now = _utc_now()
        if existing is None:
            db.add(
                StudySessionMeta(
                    id=session.id,
                    user_id=user_id,
                    question_set_id=question_set_id,
                    status="in_progress",
                    answered_count=0,
                    total_questions=total_questions,
                    title=title,
                    updated_at=now,
                )
            )
        else:
            existing.answered_count = len(session.answer_records)
            existing.total_questions = total_questions
            existing.title = title
            existing.updated_at = now
        await db.commit()

    async def update_session_meta_progress(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        session: StudySession,
    ) -> None:
        meta = await db.get(StudySessionMeta, session.id)
        if meta is None or meta.user_id != user_id:
            return
        meta.answered_count = len(session.answer_records)
        meta.total_questions = len(session.questions) or session.question_count
        meta.updated_at = _utc_now()
        await db.commit()

    async def persist_completed_session(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        session: StudySession,
        report: StudyReport,
    ) -> None:
        existing = await db.execute(
            select(StudyRecord).where(StudyRecord.session_id == session.id)
        )
        if existing.scalar_one_or_none() is not None:
            return

        title = await self._resolve_title(session)
        now = _utc_now()
        question_set = QuestionSet(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            source_text=session.source_text,
            knowledge_points=[item.model_dump(by_alias=True) for item in session.knowledge_points],
            questions=[item.model_dump(by_alias=True) for item in session.questions],
            question_count=len(session.questions),
            created_at=now,
        )
        db.add(question_set)
        await db.flush()

        study_record = StudyRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            question_set_id=question_set.id,
            session_id=session.id,
            accuracy=Decimal(str(report.accuracy)),
            correct_count=report.correct_count,
            total_questions=report.total_questions,
            duration_seconds=report.duration_seconds,
            wrong_questions=[item.model_dump(by_alias=True) for item in report.wrong_questions],
            weak_points=report.weak_points,
            summary=report.summary,
            finished_at=session.finished_at or now,
            created_at=now,
        )
        db.add(study_record)

        meta = await db.get(StudySessionMeta, session.id)
        if meta is None:
            db.add(
                StudySessionMeta(
                    id=session.id,
                    user_id=user_id,
                    question_set_id=question_set.id,
                    status="completed",
                    answered_count=report.total_questions,
                    total_questions=report.total_questions,
                    title=title,
                    updated_at=now,
                )
            )
        else:
            meta.status = "completed"
            meta.question_set_id = question_set.id
            meta.answered_count = report.total_questions
            meta.total_questions = report.total_questions
            meta.title = title
            meta.updated_at = now

        await db.commit()

    async def _resolve_title(self, session: StudySession) -> str:
        if self._generation_service is not None:
            try:
                title = await self._generation_service.generate_title(session.source_text)
                cleaned = title.strip()
                if cleaned:
                    return cleaned[:128]
            except Exception:  # noqa: BLE001
                pass
        return truncate_title(session.source_text)


class QuestionSetService:
    async def list_question_sets(
        self,
        db: AsyncSession,
        user_id: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        total_result = await db.execute(
            select(func.count()).select_from(QuestionSet).where(QuestionSet.user_id == user_id)
        )
        total = int(total_result.scalar_one())

        offset = (page - 1) * page_size
        result = await db.execute(
            select(QuestionSet)
            .where(QuestionSet.user_id == user_id)
            .order_by(QuestionSet.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        question_sets = result.scalars().all()
        items: list[dict] = []

        for question_set in question_sets:
            record_result = await db.execute(
                select(StudyRecord)
                .where(StudyRecord.question_set_id == question_set.id)
                .order_by(StudyRecord.finished_at.desc())
                .limit(1)
            )
            latest_record = record_result.scalar_one_or_none()
            practiced = latest_record is not None
            items.append(
                {
                    "question_set": question_set,
                    "practice_status": "practiced" if practiced else "unpracticed",
                    "last_accuracy": float(latest_record.accuracy) if latest_record else None,
                    "type_label": infer_type_label(question_set.questions),
                }
            )

        return items, total

    async def get_question_set(
        self,
        db: AsyncSession,
        user_id: str,
        question_set_id: str,
    ) -> QuestionSet | None:
        question_set = await db.get(QuestionSet, question_set_id)
        if question_set is None or question_set.user_id != user_id:
            return None
        return question_set

    def get_questions_preview(self, question_set: QuestionSet) -> list[dict]:
        preview: list[dict] = []
        for item in question_set.questions:
            preview.append(
                {
                    "id": item["id"],
                    "type": item["type"],
                    "stem": item["stem"],
                    "options": item.get("options", []),
                }
            )
        return preview


class StudyRecordService:
    async def list_records(
        self,
        db: AsyncSession,
        user_id: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[tuple[StudyRecord, str]], int]:
        total_result = await db.execute(
            select(func.count()).select_from(StudyRecord).where(StudyRecord.user_id == user_id)
        )
        total = int(total_result.scalar_one())
        offset = (page - 1) * page_size

        result = await db.execute(
            select(StudyRecord, QuestionSet.title)
            .join(QuestionSet, StudyRecord.question_set_id == QuestionSet.id)
            .where(StudyRecord.user_id == user_id)
            .order_by(StudyRecord.finished_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.all()), total

    async def get_record(
        self,
        db: AsyncSession,
        user_id: str,
        record_id: str,
    ) -> tuple[StudyRecord, str] | None:
        result = await db.execute(
            select(StudyRecord, QuestionSet.title)
            .join(QuestionSet, StudyRecord.question_set_id == QuestionSet.id)
            .where(StudyRecord.id == record_id, StudyRecord.user_id == user_id)
        )
        row = result.first()
        if row is None:
            return None
        return row[0], row[1]

    async def get_stats(self, db: AsyncSession, user_id: str) -> dict:
        result = await db.execute(
            select(
                func.count(StudyRecord.id),
                func.avg(StudyRecord.accuracy),
                func.coalesce(func.sum(StudyRecord.duration_seconds), 0),
            ).where(StudyRecord.user_id == user_id)
        )
        total_sessions, average_accuracy, total_duration_seconds = result.one()
        return {
            "total_sessions": int(total_sessions or 0),
            "average_accuracy": int(round(float(average_accuracy or 0))),
            "total_duration_seconds": int(total_duration_seconds or 0),
        }


class UserResumeService:
    async def get_resume(self, db: AsyncSession, user_id: str) -> dict:
        in_progress_result = await db.execute(
            select(StudySessionMeta)
            .where(
                StudySessionMeta.user_id == user_id,
                StudySessionMeta.status == "in_progress",
            )
            .order_by(StudySessionMeta.updated_at.desc())
            .limit(1)
        )
        in_progress = in_progress_result.scalar_one_or_none()
        if in_progress is not None and 0 < in_progress.answered_count < in_progress.total_questions:
            accuracy = round(
                (in_progress.answered_count / in_progress.total_questions) * 100, 1
            )
            return {
                "has_resume": True,
                "type": "in_progress",
                "session_id": in_progress.id,
                "title": in_progress.title,
                "answered_count": in_progress.answered_count,
                "total_questions": in_progress.total_questions,
                "accuracy": accuracy,
                "updated_at": in_progress.updated_at,
            }

        completed_result = await db.execute(
            select(StudySessionMeta)
            .where(
                StudySessionMeta.user_id == user_id,
                StudySessionMeta.status == "completed",
            )
            .order_by(StudySessionMeta.updated_at.desc())
            .limit(1)
        )
        completed = completed_result.scalar_one_or_none()
        if completed is not None:
            record_result = await db.execute(
                select(StudyRecord).where(StudyRecord.session_id == completed.id).limit(1)
            )
            record = record_result.scalar_one_or_none()
            accuracy = float(record.accuracy) if record else None
            return {
                "has_resume": True,
                "type": "last_completed",
                "session_id": completed.id,
                "title": completed.title,
                "answered_count": completed.answered_count,
                "total_questions": completed.total_questions,
                "accuracy": accuracy,
                "updated_at": completed.updated_at,
            }

        return {"has_resume": False, "type": "none"}
