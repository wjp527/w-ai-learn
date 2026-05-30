import asyncio

import pytest

from tests.conftest import SOURCE_TEXT

@pytest.mark.asyncio
async def test_create_session_api(client):
    response = await client.post(
        "/sessions",
        json={
            "sourceText": SOURCE_TEXT,
            "questionCount": 5,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "processing"
    assert payload["sessionId"]


@pytest.mark.asyncio
async def test_create_session_rejects_invalid_input(client):
    response = await client.post(
        "/sessions",
        json={"sourceText": "太短", "questionCount": 5},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_full_session_flow(client):
    create_response = await client.post(
        "/sessions",
        json={
            "sourceText": SOURCE_TEXT,
            "questionCount": 5,
        },
    )
    session_id = create_response.json()["sessionId"]

    detail = None
    for _ in range(20):
        detail_response = await client.get(f"/sessions/{session_id}")
        detail = detail_response.json()
        if detail["status"] == "ready":
            break
        await asyncio.sleep(0.05)

    assert detail is not None
    assert detail["status"] == "ready"
    assert len(detail["questions"]) == 5

    for question in detail["questions"]:
        answer_response = await client.post(
            f"/sessions/{session_id}/answers",
            json={
                "questionId": question["id"],
                "selectedAnswer": question["correctAnswer"],
            },
        )
        assert answer_response.status_code == 200
        assert answer_response.json()["isCorrect"] is True

    report_response = await client.get(f"/sessions/{session_id}/report")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["totalQuestions"] == 5
    assert report["correctCount"] == 5
    assert report["accuracy"] == 100.0


@pytest.mark.asyncio
async def test_get_missing_session_returns_404(client):
    response = await client.get("/sessions/not-found")
    assert response.status_code == 404
