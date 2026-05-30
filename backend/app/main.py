from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.sessions import router as sessions_router
from app.api.users import router as users_router
from app.config import settings
from app.llm.generation_service import LangChainGenerationService
from app.services.session_repository import SessionRepository
from app.services.session_service import SessionService
from app.services.user_data_service import StudyPersistenceService

REPAIR_VERSION = 2


def create_app(
    session_service: SessionService | None = None,
) -> FastAPI:
    app = FastAPI(title="AI 闯关学习 API", version="1.0.0")

    origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if origins == ["*"] else origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if session_service is None:
        repository = SessionRepository()
        generation_service = LangChainGenerationService()
        persistence_service = StudyPersistenceService(generation_service)
        session_service = SessionService(repository, generation_service, persistence_service)

    app.state.session_service = session_service
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(sessions_router)

    @app.get("/health")
    def health() -> dict[str, int | str]:
        return {"status": "ok", "repairVersion": REPAIR_VERSION}

    return app


app = create_app()
