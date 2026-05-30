from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_access_token(user_id: str, openid: str) -> tuple[str, int]:
    expires_seconds = settings.jwt_expire_days * 24 * 3600
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "openid": openid,
        "iat": now,
        "exp": now + timedelta(seconds=expires_seconds),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token, expires_seconds


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
