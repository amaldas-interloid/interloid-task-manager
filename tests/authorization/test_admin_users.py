from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_normal_user_cannot_list_users(
    client: AsyncClient,
    test_user,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/users",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 403


async def test_admin_can_list_users(
    client: AsyncClient,
    admin_user,
    test_user,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/users",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True


async def test_admin_can_deactivate_user(
    client: AsyncClient,
    admin_user,
    test_user,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["is_active"] is False


async def test_admin_can_promote_user(
        client: AsyncClient,
        admin_user,
        test_user,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
       f"/api/v1/users/{test_user.id}",
       headers={
           "Authorization": f"Bearer {access_token}",
       },
       json={
           "role": "admin",
       },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["role"] == "admin"

async def test_admin_cannot_deactivate_self(
    client: AsyncClient,
    admin_user,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
        f"/api/v1/users/{admin_user.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 422


async def test_admin_cannot_demote_self(
    client: AsyncClient,
    admin_user,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
        f"/api/v1/users/{admin_user.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "role": "user",
        },
    )

    assert response.status_code == 422


async def test_last_active_admin_cannot_be_deactivated(
    client: AsyncClient,
    admin_user,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
        f"/api/v1/users/{admin_user.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 422


async def test_admin_cannot_deactivate_last_other_active_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    admin_user,
    second_admin,
) -> None:
    admin_user.is_active = False

    await db_session.commit()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin2@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
        f"/api/v1/users/{second_admin.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 422


async def test_admin_can_deactivate_another_admin_when_one_remains(
    client: AsyncClient,
    admin_user,
    second_admin,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
        f"/api/v1/users/{second_admin.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["is_active"] is False
