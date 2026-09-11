import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_refresh_token
from app.main import app
from app.models.refresh_token import RefreshToken
from app.models.user import User


async def test_login_success(
    client: AsyncClient,
    test_user,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
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
            "email": test_user.email,
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
            "email": test_user.email,
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


@pytest.mark.anyio
async def test_login_rate_limit_after_five_failures(
    client: AsyncClient,
    test_user: User,
) -> None:
    for _ in range(5):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 429

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == ("LOGIN_RATE_LIMIT_EXCEEDED")

    assert "Retry-After" in response.headers

    retry_after = int(response.headers["Retry-After"])

    assert retry_after > 0


@pytest.mark.anyio
async def test_login_rate_limit_is_applied_per_email(
    test_user: User,
) -> None:
    for index in range(5):
        transport = ASGITransport(
            app=app,
            client=(f"10.0.0.{index + 1}", 12345),
        )

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "WrongPassword123!",
                },
            )

        assert response.status_code == 401

    transport = ASGITransport(
        app=app,
        client=("10.0.0.100", 12345),
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "StrongPassword123!",
            },
        )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == ("LOGIN_RATE_LIMIT_EXCEEDED")


@pytest.mark.anyio
async def test_login_rate_limit_is_applied_per_ip(
    client: AsyncClient,
) -> None:
    for index in range(5):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": f"unknown{index}@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "another@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 429

    assert response.json()["error"]["code"] == ("LOGIN_RATE_LIMIT_EXCEEDED")

    assert "Retry-After" in response.headers
