from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken


async def test_logout_revokes_refresh_token(
        client: AsyncClient,
        db_session: AsyncSession,
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

    refresh_token  = login_response.json()["data"]["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout_response.status_code == 200

    token_hash = hash_refresh_token(refresh_token)

    result = await db_session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
        )
    )

    stored_token = result.scalar_one_or_none()

    assert stored_token is not None
    assert stored_token.revoked_at is not None


async def test_logout_already_revoked_token_returns_200(
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

    refresh_token = login_response.json()["data"]["refresh_token"]

    first_logout = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert first_logout.status_code == 200

    second_logout = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert second_logout.status_code == 200

async def test_logout_invalid_refresh_token_returns_401(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": "this-token-does-not-exist",
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_REFRESH_TOKEN"


async def test_logged_out_refresh_token_cannot_be_refreshed(
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

    refresh_token = login_response.json()["data"]["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout_response.status_code == 200

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 401