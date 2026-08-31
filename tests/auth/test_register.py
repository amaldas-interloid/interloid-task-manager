from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def test_register_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["data"]["email"] == "testuser@example.com"
    assert body["data"]["first_name"] == "Test"
    assert body["data"]["last_name"] == "User"
    assert body["data"]["role"] == "user"
    assert body["data"]["is_active"] is True

    result = await db_session.execute(
        select(User).where(
            User.email == "testuser@example.com",
        )
    )

    user = result.scalar_one_or_none()

    assert user is not None
    assert user.email == "testuser@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.role.value == "user"
    assert user.is_active is True


async def test_register_duplicate_email_returns_409(
    client: AsyncClient,
) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }

    first_response = await client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    second_response = await client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

async def test_register_invalid_email_returns_422(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422


async def test_register_missing_email_returns_422(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422


async def test_register_missing_password_returns_422(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422


async def test_register_weak_password_returns_422(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "123",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422


async def test_login_inactive_user_returns_401(
        client: AsyncClient,
        inactive_user,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json = {
            "email": "inactive@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"

    
