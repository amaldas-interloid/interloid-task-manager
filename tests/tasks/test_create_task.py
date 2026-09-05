import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.anyio
async def test_create_task_success(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["data"]["access_token"]

    response = await client.post(
        "/api/v1/tasks",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "Learn FastAPI",
            "description": "Complete Task CRUD",
            "status": "Todo",
            "priority": "High",
            "due_date": "2026-09-05",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Task created successfully"

    assert body["data"]["title"] == "Learn FastAPI"
    assert body["data"]["description"] == "Complete Task CRUD"
    assert body["data"]["status"] == "Todo"
    assert body["data"]["priority"] == "High"
    assert body["data"]["due_date"] == "2026-09-05"

    assert body["data"]["owner_id"] == str(test_user.id)
