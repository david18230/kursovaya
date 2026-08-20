import random
import pytest

@pytest.mark.asyncio
async def test_register_booking(async_client):
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
    response = await async_client.post("/bookings/",
    json={
        "room_id": 3,
        "date_in": "2026-08-25",
        "date_out": "2026-08-27",
        "guest_count": 2
    },
   headers =  {"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_cancel_booking(async_client):
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
    booking_response = await async_client.post("/bookings/",
    json={
        "room_id": 3,
        "date_in": "2026-08-29",
        "date_out": "2026-08-30",
        "guest_count": 2
    },
   headers =  {"Authorization": f"Bearer {token}"})
    booking_id = booking_response.json()["id"]
    cancel_response = await async_client.patch(f"/bookings/cancel/{booking_id}",
    headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"