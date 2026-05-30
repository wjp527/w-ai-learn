import pytest

from tests.conftest import auth_headers, complete_session


@pytest.mark.asyncio
async def test_list_question_sets(db_client):
    headers = await auth_headers(db_client, "qb-user")
    await complete_session(db_client, headers)

    response = await db_client.get("/users/me/question-sets", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["practiceStatus"] == "practiced"


@pytest.mark.asyncio
async def test_get_questions_hides_answers(db_client):
    headers = await auth_headers(db_client, "preview-user")
    await complete_session(db_client, headers)

    list_response = await db_client.get("/users/me/question-sets", headers=headers)
    question_set_id = list_response.json()["items"][0]["id"]
    detail_response = await db_client.get(
        f"/users/me/question-sets/{question_set_id}",
        headers=headers,
    )
    assert detail_response.status_code == 200
    question = detail_response.json()["questions"][0]
    assert "correctAnswer" not in question


@pytest.mark.asyncio
async def test_practice_creates_ready_session(db_client):
    headers = await auth_headers(db_client, "practice-user")
    await complete_session(db_client, headers)

    list_response = await db_client.get("/users/me/question-sets", headers=headers)
    question_set_id = list_response.json()["items"][0]["id"]
    practice_response = await db_client.post(
        f"/users/me/question-sets/{question_set_id}/practice",
        headers=headers,
    )
    assert practice_response.status_code == 200
    session_id = practice_response.json()["sessionId"]
    detail_response = await db_client.get(f"/sessions/{session_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_cannot_access_other_users_set(db_client):
    headers_a = await auth_headers(db_client, "owner-user")
    await complete_session(db_client, headers_a)
    list_response = await db_client.get("/users/me/question-sets", headers=headers_a)
    question_set_id = list_response.json()["items"][0]["id"]

    headers_b = await auth_headers(db_client, "other-user")
    detail_response = await db_client.get(
        f"/users/me/question-sets/{question_set_id}",
        headers=headers_b,
    )
    assert detail_response.status_code == 404
