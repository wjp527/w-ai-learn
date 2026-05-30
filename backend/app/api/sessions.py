from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user_optional
from app.db.base import async_session_factory
from app.db.models.user import User
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    ReportResponse,
    SessionDetailResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.session_service import (
    QuestionNotFoundError,
    SessionIncompleteError,
    SessionNotFoundError,
    SessionNotReadyError,
    SessionService,
    ValidationError,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


@router.post("", response_model=CreateSessionResponse, response_model_by_alias=True)
async def create_session(
    payload: CreateSessionRequest,
    service: SessionService = Depends(get_session_service),
    user: User | None = Depends(get_current_user_optional),
) -> CreateSessionResponse:
    try:
        if user is not None:
            async with async_session_factory() as db:
                return await service.create_session(
                    payload.source_text,
                    payload.question_count,
                    user_id=user.id,
                    db=db,
                )
        return await service.create_session(payload.source_text, payload.question_count)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc


@router.get("/{session_id}", response_model=SessionDetailResponse, response_model_by_alias=True)
def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
) -> SessionDetailResponse:
    try:
        return service.get_session(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{session_id}/answers",
    response_model=SubmitAnswerResponse,
    response_model_by_alias=True,
)
async def submit_answer(
    session_id: str,
    payload: SubmitAnswerRequest,
    service: SessionService = Depends(get_session_service),
    user: User | None = Depends(get_current_user_optional),
) -> SubmitAnswerResponse:
    try:
        return await service.submit_answer(
            session_id,
            payload.question_id,
            payload.selected_answer,
            user_id=user.id if user else None,
        )
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionNotReadyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except QuestionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{session_id}/report", response_model=ReportResponse, response_model_by_alias=True)
async def get_report(
    session_id: str,
    service: SessionService = Depends(get_session_service),
    user: User | None = Depends(get_current_user_optional),
) -> ReportResponse:
    try:
        if user is not None:
            async with async_session_factory() as db:
                return await service.get_report(session_id, user_id=user.id, db=db)
        return await service.get_report(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionNotReadyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SessionIncompleteError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc