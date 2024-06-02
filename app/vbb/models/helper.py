from datetime import datetime, timedelta
from typing import Optional

from aiogram.types import Location

from app.db.models import Address


class Helper:

    @staticmethod
    def get_time_string_from_datetime(dt: str | datetime, delay: int = 0) -> str:
        """
        Makes a string containing hour and minute of a given datetime.
        :param dt: datetime string to calculate string for
        :param delay: a possible delay (in seconds) to add to datetime before making the string
        :return: hh:mm formatted string of datetime time
        """

        if delay is None:
            delay = 0

        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)

        dt_ = dt + timedelta(seconds=delay)
        return dt_.strftime("%H:%M")

    @staticmethod
    def get_datetime_from_string(date_string: str) -> Optional[datetime]:
        if not date_string:
            return None

        dt = datetime.fromisoformat(date_string)

        return dt

    @staticmethod
    def time_difference(earlier: datetime, later: datetime) -> str:
        """Order is not important, cause function uses abs."""
        # Calculate the time difference
        time_diff = abs(later - earlier)

        # Extract the total seconds
        total_seconds = int(time_diff.total_seconds())

        # Calculate hours and minutes
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        # Format the string as HH:MM
        time_diff_str = f"{hours:02}:{minutes:02}"

        return time_diff_str

    @staticmethod
    async def get_address_from_location(location: Location) -> Optional[Address]:
        from app.utils import address_util
        latitude = location.latitude
        longitude = location.longitude

        resolved_address = address_util.get_resolved_address(f"{latitude}, {longitude}")

        return resolved_address
