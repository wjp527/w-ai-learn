import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_login_creates_new_user(db_client):
    payload = await db_client.post("/auth/wechat/login", json={"code": "new-user-001"})
    assert payload.status_code == 200
    data = payload.json()
    assert data["token"]
    assert data["user"]["isNewUser"] is True
    assert data["user"]["nickname"].startswith("学渣 No.")


@pytest.mark.asyncio
async def test_login_returns_existing_user(db_client):
    first = await db_client.post("/auth/wechat/login", json={"code": "existing-user"})
    second = await db_client.post("/auth/wechat/login", json={"code": "existing-user"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["user"]["isNewUser"] is True
    assert second.json()["user"]["isNewUser"] is False
    assert first.json()["user"]["id"] == second.json()["user"]["id"]


@pytest.mark.asyncio
async def test_get_me_requires_token(db_client):
    response = await db_client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_and_patch_nickname(db_client):
    headers = await auth_headers(db_client, "profile-user")
    me_response = await db_client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200

    patch_response = await db_client.patch(
        "/auth/me",
        headers=headers,
        json={"nickname": "怕踢学渣 No.9527"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["nickname"] == "怕踢学渣 No.9527"
