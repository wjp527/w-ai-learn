import pytest

from tests.conftest import auth_headers, complete_session


@pytest.mark.asyncio
async def test_resume_last_completed(db_client):
    headers = await auth_headers(db_client, "resume-user")
    await complete_session(db_client, headers)

    response = await db_client.get("/users/me/resume", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["hasResume"] is True
    assert payload["type"] == "last_completed"
    assert payload["title"] == "三国历史 · 赤壁之战"


@pytest.mark.asyncio
async def test_resume_none_for_new_user(db_client):
    headers = await auth_headers(db_client, "resume-empty")
    response = await db_client.get("/users/me/resume", headers=headers)
    assert response.status_code == 200
    assert response.json()["hasResume"] is False
