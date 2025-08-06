import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User as UserModel
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "is_active" in data


@pytest.mark.asyncio
async def test_create_existing_user(client: AsyncClient):
    # Create user first
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "existing@example.com",
            "password": "securepassword",
            "full_name": "Existing User"
        }
    )
    
    # Try to create again
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "existing@example.com",
            "password": "anotherpassword",
            "full_name": "Another User"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user with this email already exists in the system."}


@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient, test_session: AsyncSession):
    # Create a user directly in the database for login test
    hashed_password = get_password_hash("testpassword")
    user = UserModel(email="login@example.com", hashed_password=hashed_password, full_name="Login User")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_incorrect_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, test_session: AsyncSession):
    # Create an inactive user directly in the database
    hashed_password = get_password_hash("inactivepassword")
    user = UserModel(email="inactive@example.com", hashed_password=hashed_password, full_name="Inactive User", is_active=False)
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "inactive@example.com",
            "password": "inactivepassword"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Inactive user"}
