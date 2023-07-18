from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "location,date_from,date_to,status_code",
    [
        ("Алтай", "2023-09-15", "2023-09-12", 400),
        ("Коми", "2023-09-15", "2023-09-15", 400),
        ("Алтай", "2023-09-15", "2023-09-25", 200),
        ("Коми", "2023-09-15", "2024-02-15", 400)
    ]
)
async def test_get_hotels_by_location_and_time(
        location: str,
        date_from: str,
        date_to: str,
        status_code: int,
        async_client: AsyncClient
):
    responce = await async_client.get(
        f"/hotels/{location}",
        params={
            "date_from": date_from,
            "date_to": date_to
        }
    )

    assert responce.status_code == status_code

