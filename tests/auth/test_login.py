from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken


async def test_login_success(
    client: AsyncClient,
    test_user,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["access_token"] is not None
    assert body["data"]["refresh_token"] is not None
    assert body["data"]["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(
    client: AsyncClient,
    test_user,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "wrongpassword123!",
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_unkown_email_returns_401(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_stores_refresh_token_hash(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user,
) -> None:
    response = await client.post(
        "api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    refresh_token = body["data"]["refresh_token"]

    result = await db_session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == test_user.id,
        )
    )

    stored_token = result.scalar_one_or_none()

    assert stored_token is not None

    assert stored_token.token_hash == hash_refresh_token(refresh_token)

    assert stored_token.revoked_at is None
