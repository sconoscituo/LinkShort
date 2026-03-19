import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "LinkShort"


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        reg = await client.post("/api/users/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        })
        assert reg.status_code == 201
        assert reg.json()["email"] == "test@example.com"

        login = await client.post("/api/users/login", data={
            "username": "test@example.com",
            "password": "testpass123",
        })
        assert login.status_code == 200
        assert "access_token" in login.json()


@pytest.mark.asyncio
async def test_short_code_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/nonexistentcode")
    assert response.status_code == 404
