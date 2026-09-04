from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


async def test_change_password_success(
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

    response = await client.patch(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "current_password": "StrongPassword123!",
            "new_password": "NewStrongPassword123!",
        },
    )

    assert response.status_code == 200


async def test_old_password_fails_after_password_change(
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

    access_token = login_response.json()["data"]["access_token"]

    change_response = await client.patch(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "current_password": "StrongPassword123!",
            "new_password": "NewStrongPassword123!",
        },
    )

    assert change_response.status_code == 200

    old_password_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert old_password_login.status_code == 401

async def test_new_password_works_after_password_change(
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

    access_token = login_response.json()["data"]["access_token"]

    change_response = await client.patch(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "current_password": "StrongPassword123!",
            "new_password": "NewStrongPassword123!",
        },
    )

    assert change_response.status_code == 200

    new_password_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "NewStrongPassword123!",
        },
    )

    assert new_password_login.status_code == 200

async def test_change_password_wrong_current_password_returns_401(
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

    access_token = login_response.json()["data"]["access_token"]

    response = await client.patch(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewStrongPassword123!",
        },
    )

    assert response.status_code == 401

async def test_change_password_revokes_all_refresh_tokens(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user,
) -> None:
    first_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    second_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert first_login.status_code == 200
    assert second_login.status_code == 200

    access_token = first_login.json()["data"]["access_token"]

    result = await db_session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == test_user.id,
        )
    )

    tokens_before = result.scalars().all()

    assert len(tokens_before) == 2

    response = await client.patch(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "current_password": "StrongPassword123!",
            "new_password": "NewStrongPassword123!",
        },
    )

    assert response.status_code == 200

    result = await db_session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == test_user.id,
        )
        .execution_options(
            populate_existing=True,
        )
    )

    tokens_after = result.scalars().all()

    assert len(tokens_after) == 2

    for token in tokens_after:
        assert token.revoked_at is not None

