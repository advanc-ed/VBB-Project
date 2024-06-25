import aiohttp
import asyncio
import logging
import random

from aiogram.types import Location

from datetime import datetime
from urllib.parse import urlencode, urljoin

from app.db.models import Address, User
from app.vbb.models import Helper

base_url = "https://v6.vbb.transport.rest"


def minutes_left(target_time: datetime) -> int:
    target_time = target_time.replace(tzinfo=None)

    # Get the current time
    now = datetime.now()

    # Calculate the difference
    time_difference = target_time - now

    # Convert the difference to minutes
    minutes_left = time_difference.total_seconds() // 60

    return int(minutes_left)


async def fetch_data(base_url, path, params):
    # Use urljoin to safely join the base URL and the path
    full_url = urljoin(base_url, path)
    params = {k: str(v) if isinstance(v, bool)
    else v for k, v in params.items()}

    async with aiohttp.ClientSession() as session:
        logging.debug(f"Fetching data from {full_url}?{urlencode(params)}")
        async with session.get(full_url, params=params) as response:
            response.raise_for_status()
            return await response.json()


async def update_stops_data(user_id: int, f):
    return {
        "some_data": "some_data",
        "information": f"some_information + {random.randint(0, 100)}"
    }


async def get_reachable_stops(user_id: int, f, distance=500, **kwargs):
    """Args:
        distance (int, optional): Distance in meters to stop. Defaults to 500.
    """
    user = await f.db.get_user(user_id)
    address = await f.db.get_address(user.home_address_id)

    latitude = address.latitude
    longitude = address.longitude

    path = "/locations/nearby"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance,
        "linesOfStops": True
    }

    params.update(kwargs)

    stops_information = await fetch_data(base_url, path, params)

    await asyncio.gather(
        *[
            fetch_departures(stop) for stop in stops_information
        ]
    )

    return stops_information


async def fetch_departures(stop):
    stop["departures"] = await get_stop_departures(stop["id"])


async def get_stop_departures(stop_id: str, **kwargs):
    path = f"/stops/{stop_id}/departures"

    params = {
        "duration": 30,
        "results": 50,
    }

    params.update(kwargs)

    departures: dict = await fetch_data(base_url, path, params)

    return departures.get("departures", [])


async def update_stop_information(stop_id: str, **kwargs):
    departures = await get_stop_departures(stop_id, linesOfStops=True, **kwargs)

    if not departures:
        return None

    stop = departures[0].get("stop")

    stop["departures"] = departures

    return stop


async def get_journeys(user: User = None,
                       session=None,
                       location: Location = None,
                       now: bool = False,
                       home_address: Address = None,
                       destination_address: Address = None,
                       **kwargs):
    from app.utils import address_util
    from app.vbb.utils import time_to_iso
    from app.vbb.models import JourneyFactory

    if home_address is None and destination_address is None:
        home_address: Address = await session.get_address(user.home_address_id)
        if location is None:
            destination_address: Address = await session.get_address(user.default_destination_address_id)  # noqa
        else:
            destination_address: Address = await Helper.get_address_from_location(location)

    path = "/journeys"

    params = {  # addresses
        "from.latitude": home_address.latitude,
        "from.longitude": home_address.longitude,
        "from.address": address_util.build_address(home_address),
        "to.latitude": destination_address.latitude,
        "to.longitude": destination_address.longitude,
        "to.address": address_util.build_address(destination_address),
    }

    params.update({
        "walkingSpeed": user.walking_speed,
        "transfers": user.max_transfers,
        "results": user.max_journeys,
        "transferTime": user.min_transfer_time,
        "regional": user.regional,
        "suburban": user.suburban,
        "bus": user.bus,
        "ferry": user.ferry,
        "subway": user.subway,
        "tram": user.tram
    })

    params.update(kwargs)

    if not now:
        params.update(
            {"arrival": time_to_iso(user.arrival_time)}
        )

    journeys_ans: dict = await fetch_data(base_url, path, params)

    journeys = [
        JourneyFactory.create(journey)
        for journey in journeys_ans.get("journeys")
    ]

    return journeys
