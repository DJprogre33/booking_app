from datetime import date

import pytest

from app.utils.transaction_manager import ITransactionManager


@pytest.mark.parametrize(
    "location,date_from,date_to,total_hotels",
    [
        ("Алтай", date(2023, 9, 10), date(2023, 9, 20), 3),
        ("Коми", date(2023, 9, 10), date(2023, 9, 20), 2),
        ("Ижора", date(2024, 12, 15), date(2024, 12, 25), 0),
        ("Ижора", date(2024, 11, 15), date(2024, 12, 25), 0),
        ("Ижора", date(2024, 11, 20), date(2024, 12, 23), 0),
        ("Ижора", date(2024, 11, 25), date(2024, 12, 30), 0),
    ],
)
async def test_get_hotels_by_location_and_time(
    location: str,
    date_from: date,
    date_to: date,
    total_hotels: int,
    transaction_manager: ITransactionManager,
) -> None:
    async with transaction_manager:
        hotels = await transaction_manager.hotels.get_hotels_by_location_and_time(
            location=location, date_from=date_from, date_to=date_to
        )
        assert len(hotels) == total_hotels
        for hotel in hotels:
            assert location.lower() in hotel["location"].lower()
