import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.anyio
async def test_get_tasks_returns_current_user_tasks(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    create_response = await client.post(
        "/api/v1/tasks",
        headers=headers,
        json={
            "title": "Pytest Task",
            "description": "Test GET tasks endpoint",
            "status": "Todo",
            "priority": "High",
            "due_date": "2026-09-10",
        },
    )

    assert create_response.status_code == 201

    response = await client.get(
        "/api/v1/tasks?limit=20&offset=0",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Tasks fetched successfully"
    assert body["error"] is None

    assert isinstance(body["data"]["items"], list)

    assert body["data"]["pagination"]["total"] >= 1
    assert body["data"]["pagination"]["limit"] == 20
    assert body["data"]["pagination"]["offset"] == 0

    task = next(
        item for item in body["data"]["items"] if item["title"] == "Pytest Task"
    )

    assert task["owner_id"] == str(test_user.id)
    assert task["title"] == "Pytest Task"
    assert task["status"] == "Todo"
    assert task["priority"] == "High"


@pytest.mark.anyio
async def test_get_tasks_with_filters_and_search(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    tasks = [
        {
            "title": "Deploy backend",
            "description": "Production deployment",
            "status": "Todo",
            "priority": "High",
            "due_date": "2026-09-10",
        },
        {
            "title": "Deploy frontend",
            "description": "Frontend deployment",
            "status": "Done",
            "priority": "High",
            "due_date": "2026-09-11",
        },
        {
            "title": "Write tests",
            "description": "Pytest",
            "status": "Todo",
            "priority": "High",
            "due_date": "2026-09-12",
        },
    ]

    for task in tasks:
        response = await client.post(
            "/api/v1/tasks",
            headers=headers,
            json=task,
        )

        assert response.status_code == 201

    response = await client.get(
        ("/api/v1/tasks?status=Todo&priority=High&search=deploy&limit=10&offset=0"),
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["error"] is None

    assert body["data"]["pagination"]["total"] == 1
    assert body["data"]["pagination"]["limit"] == 10
    assert body["data"]["pagination"]["offset"] == 0

    assert len(body["data"]["items"]) == 1

    task = body["data"]["items"][0]

    assert task["title"] == "Deploy backend"
    assert task["status"] == "Todo"
    assert task["priority"] == "High"


@pytest.mark.anyio
async def test_get_tasks_rejects_limit_above_100(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = await client.get(
        "/api/v1/tasks?limit=500",
        headers=headers,
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Validation failed"
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_get_tasks_rejects_inverted_due_date_range(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = await client.get(
        ("/api/v1/tasks?due_from=2026-09-01&due_to=2026-08-01"),
        headers=headers,
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Validation failed"
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_get_tasks_returns_only_current_user_tasks(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Current user task",
            "description": "Belongs to current user",
            "status": "Todo",
            "priority": "Medium",
            "due_date": "2026-09-01",
        },
        headers=headers,
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["error"] is None

    items = body["data"]["items"]

    assert all(task["owner_id"] == str(test_user.id) for task in items)


@pytest.mark.anyio
async def test_admin_can_get_all_tasks(
    client: AsyncClient,
    admin_user: User,
    test_user: User,
) -> None:
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email,
            "password": "StrongPassword123!",
        },
    )

    assert admin_login.status_code == 200

    admin_token = admin_login.json()["data"]["access_token"]

    admin_headers = {
        "Authorization": f"Bearer {admin_token}",
    }

    user_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "StrongPassword123!",
        },
    )

    assert user_login.status_code == 200

    user_token = user_login.json()["data"]["access_token"]

    user_headers = {
        "Authorization": f"Bearer {user_token}",
    }

    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Normal user admin visibility task",
            "description": "Created by normal user",
            "status": "Todo",
            "priority": "Medium",
            "due_date": "2026-09-01",
        },
        headers=user_headers,
    )

    assert create_response.status_code == 201

    created_task = create_response.json()["data"]

    response = await client.get(
        "/api/v1/tasks",
        headers=admin_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["error"] is None

    items = body["data"]["items"]

    assert any(
        task["id"] == created_task["id"] and task["owner_id"] == str(test_user.id)
        for task in items
    )


@pytest.mark.anyio
async def test_admin_can_filter_tasks_by_owner_id(
    client: AsyncClient,
    admin_user: User,
    test_user: User,
) -> None:
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email,
            "password": "StrongPassword123!",
        },
    )

    assert admin_login.status_code == 200

    admin_token = admin_login.json()["data"]["access_token"]

    admin_headers = {
        "Authorization": f"Bearer {admin_token}",
    }

    user_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "StrongPassword123!",
        },
    )

    assert user_login.status_code == 200

    user_token = user_login.json()["data"]["access_token"]

    user_headers = {
        "Authorization": f"Bearer {user_token}",
    }

    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Owner filter task",
            "description": "Task used for owner filter test",
            "status": "Todo",
            "priority": "Medium",
            "due_date": "2026-09-01",
        },
        headers=user_headers,
    )

    assert create_response.status_code == 201

    response = await client.get(
        f"/api/v1/tasks?owner_id={test_user.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["error"] is None

    items = body["data"]["items"]

    assert len(items) >= 1

    assert all(task["owner_id"] == str(test_user.id) for task in items)


@pytest.mark.anyio
async def test_get_tasks_filters_by_inclusive_due_date_range(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    first_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Due range start task",
            "description": "Task exactly on due_from",
            "status": "Todo",
            "priority": "Medium",
            "due_date": "2026-09-01",
        },
        headers=headers,
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Due range end task",
            "description": "Task exactly on due_to",
            "status": "Todo",
            "priority": "Medium",
            "due_date": "2026-09-10",
        },
        headers=headers,
    )

    assert second_response.status_code == 201

    response = await client.get(
        ("/api/v1/tasks?due_from=2026-09-01&due_to=2026-09-10"),
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["error"] is None

    items = body["data"]["items"]

    titles = {task["title"] for task in items}

    assert "Due range start task" in titles
    assert "Due range end task" in titles


@pytest.mark.anyio
async def test_get_tasks_search_is_case_insensitive(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Deploy Production API",
            "description": "Search test",
            "status": "Todo",
            "priority": "Medium",
            "due_date": "2026-09-10",
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    response = await client.get(
        "/api/v1/tasks?search=deploy",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["error"] is None

    items = body["data"]["items"]

    assert any(task["title"] == "Deploy Production API" for task in items)


@pytest.mark.anyio
async def test_get_tasks_pagination_limit_and_offset(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    for number in range(1, 4):
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": f"Pagination Task {number}",
                "description": "Pagination test",
                "status": "Todo",
                "priority": "Medium",
                "due_date": "2026-09-10",
            },
            headers=headers,
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks?search=Pagination%20Task&limit=2&offset=0",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["error"] is None

    data = body["data"]

    assert data["pagination"]["total"] == 3
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["offset"] == 0

    assert len(data["items"]) == 2


@pytest.mark.anyio
async def test_get_tasks_pagination_offset_skips_records(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    created_ids = []

    for number in range(1, 4):
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": f"Offset Task {number}",
                "description": "Offset pagination test",
                "status": "Todo",
                "priority": "Medium",
                "due_date": "2026-09-10",
            },
            headers=headers,
        )

        assert response.status_code == 201

        created_ids.append(response.json()["data"]["id"])

    response = await client.get(
        "/api/v1/tasks?search=Offset%20Task&limit=2&offset=1",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert body["success"] is True
    assert body["error"] is None

    assert data["pagination"]["total"] == 3
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["offset"] == 1

    assert len(data["items"]) == 2


@pytest.mark.anyio
async def test_normal_user_cannot_filter_tasks_by_another_owner(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    second_user_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "secondtaskuser@example.com",
            "password": "Test1234",
            "first_name": "Second",
            "last_name": "User",
        },
    )

    assert second_user_response.status_code == 201

    second_user = second_user_response.json()["data"]
    second_user_id = second_user["id"]

    response = await client.get(
        f"/api/v1/tasks?owner_id={second_user_id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Tasks fetched successfully"
    assert body["error"] is None

    items = body["data"]["items"]

    assert all(task["owner_id"] == str(test_user.id) for task in items)


@pytest.mark.anyio
async def test_tasks_sort_by_created_at_asc(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    for title in [
        "First Task",
        "Second Task",
        "Third Task",
    ]:
        response = await client.post(
            "/api/v1/tasks",
            headers=headers,
            json={
                "title": title,
                "priority": "Medium",
            },
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks",
        params={
            "sort_by": "created_at",
            "order": "asc",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    items = body["data"]["items"]

    created_dates = [item["created_at"] for item in items]

    assert len(created_dates) == 3

    assert created_dates == sorted(
        created_dates,
    )


@pytest.mark.anyio
async def test_tasks_sort_by_created_at_desc(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    for title in [
        "First Task",
        "Second Task",
        "Third Task",
    ]:
        response = await client.post(
            "/api/v1/tasks",
            headers=headers,
            json={
                "title": title,
                "priority": "Medium",
            },
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks",
        params={
            "sort_by": "created_at",
            "order": "desc",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    items = body["data"]["items"]

    created_dates = [item["created_at"] for item in items]

    assert len(created_dates) == 3

    assert created_dates == sorted(
        created_dates,
        reverse=True,
    )


@pytest.mark.anyio
async def test_tasks_sort_by_priority_asc(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    for title, priority in [
        ("High Task", "High"),
        ("Low Task", "Low"),
        ("Medium Task", "Medium"),
    ]:
        response = await client.post(
            "/api/v1/tasks",
            headers=headers,
            json={
                "title": title,
                "priority": priority,
            },
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks",
        params={
            "sort_by": "priority",
            "order": "asc",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    items = body["data"]["items"]

    priorities = [item["priority"] for item in items]

    assert priorities == [
        "Low",
        "Medium",
        "High",
    ]


@pytest.mark.anyio
async def test_tasks_sort_by_priority_desc(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    for title, priority in [
        ("Low Task", "Low"),
        ("Medium Task", "Medium"),
        ("High Task", "High"),
    ]:
        response = await client.post(
            "/api/v1/tasks",
            headers=headers,
            json={
                "title": title,
                "priority": priority,
            },
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks",
        params={
            "sort_by": "priority",
            "order": "desc",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    items = body["data"]["items"]

    priorities = [item["priority"] for item in items]

    assert priorities == [
        "High",
        "Medium",
        "Low",
    ]


@pytest.mark.anyio
async def test_tasks_sort_by_due_date_asc(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_response = await client.post(
        "api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    tasks = [
        {
            "title": "Later Task",
            "priority": "Medium",
            "due_date": "2026-09-15",
        },
        {
            "title": "No Due Date Task",
            "priority": "Medium",
            "due_date": None,
        },
        {
            "title": "Earlier Task",
            "priority": "Medium",
            "due_date": "2026-09-10",
        },
    ]

    for task in tasks:
        response = await client.post(
            "/api/v1/tasks",
            headers=headers,
            json=task,
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks",
        params={
            "sort_by": "due_date",
            "order": "asc",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    items = body["data"]["items"]

    due_dates = [item["due_date"] for item in items]

    assert due_dates == [
        "2026-09-10",
        "2026-09-15",
        None,
    ]


@pytest.mark.anyio
async def test_tasks_sort_by_due_date_desc(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    tasks = [
        {
            "title": "Earlier Task",
            "priority": "Medium",
            "due_date": "2026-09-10",
        },
        {
            "title": "No Due Date Task",
            "priority": "Medium",
            "due_date": None,
        },
        {
            "title": "Later Task",
            "priority": "Medium",
            "due_date": "2026-09-15",
        },
    ]

    for task in tasks:
        response = await client.post(
            "/api/v1/tasks",
            headers=headers,
            json=task,
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/tasks",
        params={
            "sort_by": "due_date",
            "order": "desc",
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    items = body["data"]["items"]

    due_dates = [item["due_date"] for item in items]

    assert due_dates == [
        "2026-09-15",
        "2026-09-10",
        None,
    ]


@pytest.mark.anyio
async def test_invalid_sort_by_returns_422(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = await client.get(
        "/api/v1/tasks",
        params={
            "sort_by": "invalid_field",
        },
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_invalid_sort_order_returns_422(
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

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = await client.get(
        "/api/v1/tasks",
        params={
            "order": "invalid_order",
        },
        headers=headers,
    )

    assert response.status_code == 422
