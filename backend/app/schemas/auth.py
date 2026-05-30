from datetime import datetime

from pydantic import BaseModel, Field


class WechatLoginRequest(BaseModel):
    code: str = Field(min_length=1)


class UserProfileResponse(BaseModel):
    id: str
    nickname: str
    avatar_url: str | None = Field(default=None, alias="avatarUrl")
    created_at: datetime | None = Field(default=None, alias="createdAt")

    model_config = {"populate_by_name": True}


class LoginUserResponse(UserProfileResponse):
    is_new_user: bool = Field(alias="isNewUser")

    model_config = {"populate_by_name": True}


class WechatLoginResponse(BaseModel):
    token: str
    expires_in: int = Field(alias="expiresIn")
    user: LoginUserResponse

    model_config = {"populate_by_name": True}


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=20)
    avatar_url: str | None = Field(default=None, alias="avatarUrl", max_length=512)

    model_config = {"populate_by_name": True}
