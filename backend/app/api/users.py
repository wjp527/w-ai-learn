from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_required
from app.db.base import get_db_session
from app.db.models.user import User
from app.schemas.user import (
    PaginatedQuestionSetsResponse,
    PaginatedStudyRecordsResponse,
    PracticeResponse,
    QuestionSetDetailResponse,
    QuestionSetListItem,
    QuestionPreview,
    ResumeResponse,
    StudyRecordDetailResponse,
    StudyRecordListItem,
    UserStatsResponse,
    WrongQuestionDetail,
)
from app.services.session_service import SessionService
from app.services.user_data_service import (
    QuestionSetService,
    StudyRecordService,
    UserResumeService,
)
from app.utils.display import (
    format_created_date,
    format_duration_seconds,
    format_full_datetime,
    format_relative_datetime,
    format_total_duration,
    infer_subject_icon,
)

router = APIRouter(prefix="/users/me", tags=["users"])
study_record_service = StudyRecordService()
question_set_service = QuestionSetService()
resume_service = UserResumeService()


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


@router.get("/stats", response_model=UserStatsResponse, response_model_by_alias=True)
async def get_my_stats(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
) -> UserStatsResponse:
    stats = await study_record_service.get_stats(db, user.id)
    return UserStatsResponse(
        total_sessions=stats["total_sessions"],
        average_accuracy=stats["average_accuracy"],
        total_duration_seconds=stats["total_duration_seconds"],
        total_duration_display=format_total_duration(stats["total_duration_seconds"]),
    )


@router.get("/records", response_model=PaginatedStudyRecordsResponse, response_model_by_alias=True)
async def list_my_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50, alias="pageSize"),
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
) -> PaginatedStudyRecordsResponse:
    rows, total = await study_record_service.list_records(
        db, user.id, page=page, page_size=page_size
    )
    items = [
        StudyRecordListItem(
            id=record.id,
            title=title,
            subject_icon=infer_subject_icon(title),
            finished_at=record.finished_at,
            finished_at_display=format_relative_datetime(record.finished_at),
            duration_seconds=record.duration_seconds,
            duration_display=format_duration_seconds(record.duration_seconds),
            accuracy=float(record.accuracy),
            correct_count=record.correct_count,
            total_questions=record.total_questions,
        )
        for record, title in rows
    ]
    return PaginatedStudyRecordsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/records/{record_id}",
    response_model=StudyRecordDetailResponse,
    response_model_by_alias=True,
)
async def get_my_record(
    record_id: str,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
) -> StudyRecordDetailResponse:
    row = await study_record_service.get_record(db, user.id, record_id)
    if row is None:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    record, title = row
    wrong_questions = [
        WrongQuestionDetail.model_validate(item) for item in record.wrong_questions
    ]
    return StudyRecordDetailResponse(
        id=record.id,
        title=title,
        accuracy=float(record.accuracy),
        correct_count=record.correct_count,
        total_questions=record.total_questions,
        duration_seconds=record.duration_seconds,
        duration_display=format_duration_seconds(record.duration_seconds),
        finished_at=record.finished_at,
        finished_at_display=format_full_datetime(record.finished_at),
        wrong_questions=wrong_questions,
        summary=record.summary,
        question_set_id=record.question_set_id,
    )


@router.get(
    "/question-sets",
    response_model=PaginatedQuestionSetsResponse,
    response_model_by_alias=True,
)
async def list_my_question_sets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50, alias="pageSize"),
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
) -> PaginatedQuestionSetsResponse:
    rows, total = await question_set_service.list_question_sets(
        db, user.id, page=page, page_size=page_size
    )
    items: list[QuestionSetListItem] = []
    for row in rows:
        question_set = row["question_set"]
        practice_status = row["practice_status"]
        last_accuracy = row["last_accuracy"]
        if practice_status == "unpracticed":
            badge = "未练习"
        elif last_accuracy is not None and last_accuracy < 70:
            badge = f"{int(last_accuracy)}%"
        else:
            badge = "已练过"
        items.append(
            QuestionSetListItem(
                id=question_set.id,
                title=question_set.title,
                question_count=question_set.question_count,
                type_label=row["type_label"],
                created_at=question_set.created_at,
                created_at_display=format_created_date(question_set.created_at),
                practice_status=practice_status,
                last_accuracy=last_accuracy,
                badge=badge,
            )
        )
    return PaginatedQuestionSetsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/question-sets/{question_set_id}",
    response_model=QuestionSetDetailResponse,
    response_model_by_alias=True,
)
async def get_my_question_set(
    question_set_id: str,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
) -> QuestionSetDetailResponse:
    question_set = await question_set_service.get_question_set(db, user.id, question_set_id)
    if question_set is None:
        raise HTTPException(status_code=404, detail="题目集不存在")
    preview = question_set_service.get_questions_preview(question_set)
    return QuestionSetDetailResponse(
        id=question_set.id,
        title=question_set.title,
        questions=[QuestionPreview.model_validate(item) for item in preview],
    )


@router.post(
    "/question-sets/{question_set_id}/practice",
    response_model=PracticeResponse,
    response_model_by_alias=True,
)
async def practice_question_set(
    question_set_id: str,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
    session_service: SessionService = Depends(get_session_service),
) -> PracticeResponse:
    question_set = await question_set_service.get_question_set(db, user.id, question_set_id)
    if question_set is None:
        raise HTTPException(status_code=404, detail="题目集不存在")
    result = await session_service.create_session_from_question_set(
        question_set,
        user_id=user.id,
        db=db,
    )
    return PracticeResponse(session_id=result.session_id, status=result.status.value)


@router.get("/resume", response_model=ResumeResponse, response_model_by_alias=True)
async def get_my_resume(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
) -> ResumeResponse:
    payload = await resume_service.get_resume(db, user.id)
    updated_at_display = None
    if payload.get("updated_at") is not None:
        updated_at_display = format_relative_datetime(payload["updated_at"])
    return ResumeResponse(
        has_resume=payload["has_resume"],
        type=payload.get("type", "none"),
        session_id=payload.get("session_id"),
        title=payload.get("title"),
        answered_count=payload.get("answered_count"),
        total_questions=payload.get("total_questions"),
        accuracy=payload.get("accuracy"),
        updated_at_display=updated_at_display,
    )
