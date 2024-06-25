import logging
from typing import Any, Optional

from geopy.geocoders import Nominatim
from geopy.location import Location

from app.db.models import Address
from app.utils.enums import AddressType, AddressTypeEmoji
from .models import AddressResolved


class AddressUtil:
    """
    Class to handle address related operations.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_building(query):
        """
        Get a building object from the given query, via Nominatim.
        Args:
            query: any string, that somehow could be related to a building

        Returns:
            location: Nominatim Location object
        """
        geolocator = Nominatim(user_agent="vbb-app")
        locations: list[Location] = geolocator.geocode(
            query,
            exactly_one=False,
            addressdetails=True,
            namedetails=True,
            timeout=3)

        if locations is None:
            return None

        for location in locations:
            if location.raw.get("class", "building") in [
                "building",
                "place"
            ]:
                return location

        return locations[0]

    @staticmethod
    def parse_building_data(location: Location):
        """
        Parse a building object from Nominatim
        Args:
            location: Nominatim Location object

        Returns:
            (street_name, street_number, city, state, postal_code, country)

        """
        location_data: Optional[dict] = location.raw.get("address", None)
        if location_data is None:
            return None

        street_name = location_data.get("road")
        house_number = location_data.get("house_number")
        house_number = int(house_number.split('-')[0])
        city = location_data.get("city").strip()
        plz = location_data.get("postcode").strip()
        latitude = round(location.latitude, 8)
        longitude = round(location.longitude, 8)

        return street_name, house_number, city, plz, latitude, longitude

    def get_resolved_address(self, address: str) -> Optional[AddressResolved]:
        """
        Get a resolved address object from the given address, via Nominatim.
        Args:
            address: any string, that somehow could be related to a building

        Returns:
            AddressResolved object
        """
        location: Location = self.get_building(address)

        if location is None:
            return None

        street_name, house_number, city, plz, latitude, longitude = self.parse_building_data(location)

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
        """
        Register addresses for a user
        Args:
            home_address_resolved: Home AddressResolved object
            default_destination_address_resolved: Destination AddressResolved object
            user_id: user_id from Telegram
            f: FMT Object for connection to DB
        """
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
