from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_required
from app.db.base import get_db_session
from app.db.models.user import User
from app.schemas.auth import (
    UpdateProfileRequest,
    UserProfileResponse,
    WechatLoginRequest,
    WechatLoginResponse,
)
from app.services.auth_service import AuthError, AuthService, ValidationError

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


def _to_profile(user: User, *, is_new_user: bool | None = None) -> dict:
    payload = {
        "id": user.id,
        "nickname": user.nickname,
        "avatarUrl": user.avatar_url,
        "createdAt": user.created_at,
    }
    if is_new_user is not None:
        payload["isNewUser"] = is_new_user
    return payload


@router.post("/wechat/login", response_model=WechatLoginResponse, response_model_by_alias=True)
async def wechat_login(
    payload: WechatLoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> WechatLoginResponse:
    try:
        token, expires_in, user, is_new_user = await auth_service.login_with_wechat_code(
            db, payload.code
        )
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return WechatLoginResponse(
        token=token,
        expires_in=expires_in,
        user=_to_profile(user, is_new_user=is_new_user),
    )


@router.get("/me", response_model=UserProfileResponse, response_model_by_alias=True)
async def get_me(user: User = Depends(get_current_user_required)) -> UserProfileResponse:
    return UserProfileResponse.model_validate(_to_profile(user))


@router.patch("/me", response_model=UserProfileResponse, response_model_by_alias=True)
async def update_me(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session),
) -> UserProfileResponse:
    try:
        updated = await auth_service.update_profile(
            db,
            user,
            nickname=payload.nickname,
            avatar_url=payload.avatar_url,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    return UserProfileResponse.model_validate(_to_profile(updated))
