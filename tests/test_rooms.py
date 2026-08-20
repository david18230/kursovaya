import pytest
from main import app
@pytest.mark.asyncio
async def test_get_rooms(async_client):
    response = await async_client.get("/rooms/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["page"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["pages"], int)

    assert isinstance(data["data"], list)


