import random
import pytest

@pytest.mark.asyncio
async def test_register_success(async_client):
    response = await async_client.post("/auth/register", json={
        "full_name": "Тест Тестов",
        "phone": "+79991234567",
        "email": "test@mail.ru",
        "password": "123456" })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_wrong_email(async_client):
    response = await async_client.post("/auth/login", json={
        "username": "bag@mail.ru",
        "password": "abc456" })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_rate_limiting(async_client):
    email = f"test{random.randint(1000, 9999)}@mail.ru"
    for i in range(5):
        await async_client.post("/auth/login", json = {
            "username": email,
            "password": "wrong" })
    response = await async_client.post("/auth/login", json = {
        "username": email,
        "password": "wrong"})
    assert response.status_code == 429

@pytest.mark.asyncio
async def test_check_phone(async_client):
    response = await async_client.post("/auth/register", json = {
        "full_name": "Тест Тестов",
        "phone": "12345",
        "email": "test@mail.ru",
        "password": "123456"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_check_password(async_client):
    email = f"test{random.randint(1000, 9999)}@mail.ru"
    response = await async_client.post("/auth/register", json = {
        "full_name": "Тест Тестов",
        "phone": "+79991234567",
        "email": email,
        "password": "A123456"
    })
    response = await async_client.post("/auth/login", json = {
        "username": email,
        "password": "A12345"
    })
    assert response.status_code == 401
@pytest.mark.asyncio
async def test_without_token(async_client):
    response = await async_client.get("/users/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_user_access_admin_forbidden(async_client):
    email = f"test{random.randint(1000, 9999)}@mail.ru"
    response = await async_client.post("/auth/register", json={
        "full_name": "Тест Тестов",
        "phone": "+79991234567",
        "email": email,
        "password": "abc456"
    })
    response = await async_client.post("/auth/login", json = {
        "username": email,
        "password": "abc456"
    })
    token = response.json()["access_token"]
    response = await async_client.get("/admin/users",
   headers =  {"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

