import logging
from .models import AddressResolved
from app.db.models import Address
from app.utils.enums import AddressType, AddressTypeEmoji

from geopy.geocoders import Nominatim
from geopy.location import Location

from typing import Any, List, Optional, Union


class AddressUtil:
    def __init__(self) -> None:
        pass

    def get_building(self, query):
        geolocator = Nominatim(user_agent="vbb-app")
        location: list[Location] = geolocator.geocode(
            query,
            exactly_one=False,
            timeout=3)

        if location is None:
            return None

        for loc in location:
            if loc.raw.get("class", "building") in [
                "building",
                "place"
            ]:
                return loc

        return location[0]

    def get_resolved_address(self, address: str) -> Optional[AddressResolved]:
        location: Location = self.get_building(address)

        if location is None:
            return None

        address_parts = location.address.split(',')
        street_name = address_parts[1].strip()
        house_number_test = address_parts[0].strip()

        try:
            house_number = int(house_number_test.split('-')[0])
        except ValueError:
            house_number = 0
            street_name = house_number_test

        city = address_parts[-3].strip()
        plz = address_parts[-2].strip()
        latitude = round(location.latitude, 8)
        longitude = round(location.longitude, 8)

        return AddressResolved(
            street_name=street_name,
            house_number=house_number,
            city=city,
            plz=plz,
            latitude=latitude,
            longitude=longitude,
        )

    async def register_user_resolved_addresses(
            self,
            home_address_resolved: AddressResolved,
            default_destination_address_resolved: AddressResolved,
            user_id: int,
            f
    ) -> None:
        await f.db.register_user(
            addresses={
                "home_address": home_address_resolved,
                "default_destination_address": default_destination_address_resolved,
            },
            user_id=user_id
        )

    async def user_addresses_short(self, user_id: int, f) -> list[list[int | str | Any]]:
        user_addresses: list[Address] = await f.db.get_user_addresses(user_id)

        addresses_data = []

        for address in user_addresses:
            address_usage = await f.db.check_address_usage(user_id, address.id)

            addresses_data.append(
                [address.id,
                 address.street_name + " " + str(address.house_number),
                 address_usage]
            )

        return addresses_data

    def get_address_types(self) -> list[str]:
        ans = []
        for address_type in AddressType:
            match address_type:
                case AddressType.Home:
                    prefix = AddressTypeEmoji.Home.value
                case AddressType.DefaultDestination:
                    prefix = AddressTypeEmoji.DefaultDestination.value

            ans.append(
                "%s %s" % (prefix, address_type.value)
            )

        return ans

    async def update_address(self, address_t: str, address_id: int, user_id: int, f) -> None:
        address_type = self.get_address_type(address_t)
        user = await f.db.get_user(user_id)

        updates = {}
        home_address_id = user.home_address_id
        default_destination_address_id = user.default_destination_address_id

        match address_type:
            case AddressType.Home:
                updates["home_address_id"] = address_id
                if address_id == default_destination_address_id:
                    updates["default_destination_address_id"] = home_address_id
            case AddressType.DefaultDestination:
                updates["default_destination_address_id"] = address_id
                if address_id == home_address_id:
                    updates["home_address_id"] = default_destination_address_id

        await f.db.update_user_data(
            user_id=user_id,
            updates=updates
        )

    def address_usage_add_emoji(self, address_usage: str) -> Optional[str]:
        match address_usage:
            case AddressType.Home:
                prefix = AddressTypeEmoji.Home.value
            case AddressType.DefaultDestination:
                prefix = AddressTypeEmoji.DefaultDestination.value
            case _:
                return None

        return "%s %s" % (prefix, address_usage.value)

    def get_address_type(self, address_t: str):
        for address_type in AddressType:
            if address_type.value in address_t:
                return address_type

    async def add_address(self, address_resolved: AddressResolved, user_id: int, f):
        result = await f.db.add_address(address_resolved, user_id)

        if result is None:
            logging.warning("Address was not added, already exists!")

    def build_address(self, address: Address) -> str:
        return f"{address.street_name} {address.house_number}"
