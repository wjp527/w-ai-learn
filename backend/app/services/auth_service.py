import random
import uuid
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token
from app.db.models.user import User


class AuthError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _default_nickname() -> str:
    return f"学渣 No.{random.randint(1000, 9999)}"


async def _fetch_wechat_openid(code: str) -> str:
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.wechat_app_id,
        "secret": settings.wechat_app_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    last_error: Exception | None = None
    for _ in range(2):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)
                payload = response.json()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue

        if payload.get("errcode"):
            raise AuthError("微信登录失败")
        openid = payload.get("openid")
        if not openid:
            raise AuthError("微信登录失败")
        return openid

    raise AuthError("微信登录失败") from last_error


class AuthService:
    async def login_with_wechat_code(
        self,
        db: AsyncSession,
        code: str,
    ) -> tuple[str, int, User, bool]:
        if settings.wechat_mock_login:
            openid = f"mock_{code}"
        else:
            openid = await _fetch_wechat_openid(code)

        result = await db.execute(select(User).where(User.openid == openid))
        user = result.scalar_one_or_none()
        is_new_user = user is None

        now = _utc_now()
        if user is None:
            user = User(
                id=str(uuid.uuid4()),
                openid=openid,
                nickname=_default_nickname(),
                avatar_url=None,
                created_at=now,
                updated_at=now,
            )
            db.add(user)
        else:
            user.updated_at = now

        await db.commit()
        await db.refresh(user)
        token, expires_in = create_access_token(user.id, user.openid)
        return token, expires_in, user, is_new_user

    async def update_profile(
        self,
        db: AsyncSession,
        user: User,
        *,
        nickname: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        if nickname is None and avatar_url is None:
            raise ValidationError("至少提供一个更新字段")

        if nickname is not None:
            cleaned = nickname.strip()
            if not cleaned:
                raise ValidationError("昵称不能为空")
            if len(cleaned) > 20:
                raise ValidationError("昵称不能超过 20 字")
            user.nickname = cleaned

        if avatar_url is not None:
            user.avatar_url = avatar_url.strip() or None

        user.updated_at = _utc_now()
        await db.commit()
        await db.refresh(user)
        return user
