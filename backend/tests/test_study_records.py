import pytest

from tests.conftest import auth_headers, complete_session


@pytest.mark.asyncio
async def test_report_persists_record_for_logged_in_user(db_client):
    headers = await auth_headers(db_client, "persist-user")
    await complete_session(db_client, headers)

    stats_response = await db_client.get("/users/me/stats", headers=headers)
    assert stats_response.status_code == 200
    assert stats_response.json()["totalSessions"] == 1

    records_response = await db_client.get("/users/me/records", headers=headers)
    assert records_response.status_code == 200
    records = records_response.json()
    assert records["total"] == 1
    assert records["items"][0]["title"] == "三国历史 · 赤壁之战"


@pytest.mark.asyncio
async def test_report_does_not_persist_for_anonymous(db_client):
    await complete_session(db_client)

    login_response = await db_client.post("/auth/wechat/login", json={"code": "anon-check"})
    headers = {"Authorization": f"Bearer {login_response.json()['token']}"}
    stats_response = await db_client.get("/users/me/stats", headers=headers)
    assert stats_response.json()["totalSessions"] == 0


@pytest.mark.asyncio
async def test_report_idempotent_no_duplicate_records(db_client):
    headers = await auth_headers(db_client, "idempotent-user")
    session_id = await complete_session(db_client, headers)

    second_report = await db_client.get(f"/sessions/{session_id}/report", headers=headers)
    assert second_report.status_code == 200

    records_response = await db_client.get("/users/me/records", headers=headers)
    assert records_response.json()["total"] == 1


@pytest.mark.asyncio
async def test_list_records_pagination(db_client):
    headers = await auth_headers(db_client, "pagination-user")
    await complete_session(db_client, headers)

    response = await db_client.get("/users/me/records?page=1&pageSize=1", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1


@pytest.mark.asyncio
async def test_stats_aggregation(db_client):
    headers = await auth_headers(db_client, "stats-user")
    await complete_session(db_client, headers)

    stats_response = await db_client.get("/users/me/stats", headers=headers)
    stats = stats_response.json()
    assert stats["averageAccuracy"] == 100
    assert stats["totalDurationSeconds"] >= 0


@pytest.mark.asyncio
async def test_get_record_detail(db_client):
    headers = await auth_headers(db_client, "detail-user")
    await complete_session(db_client, headers)

    records_response = await db_client.get("/users/me/records", headers=headers)
    record_id = records_response.json()["items"][0]["id"]
    detail_response = await db_client.get(f"/users/me/records/{record_id}", headers=headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["accuracy"] == 100.0
    assert detail["summary"]
