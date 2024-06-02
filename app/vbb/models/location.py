from typing import Optional, Union
from .others import Products


class LocationFactory:
    @staticmethod
    def get_location(location_data: dict[str, any]) -> Optional[Union["Location", "Stop"]]:

        type = location_data.get("type")
        if type is None:
            return None

        match type:
            case "location":
                return Location(location_data)
            case "stop":
                return Stop(location_data)
            case _:
                return None

    @staticmethod
    def get_products(products_data: Optional[dict[str, any]]) -> Optional['Products']:
        if not products_data:
            return None

        return Products(products_data)


class LocationBase:
    def __init__(self, raw_data: dict[str, any]):
        self.type: str = raw_data.get("type")
        self.id: Optional[str] = raw_data.get("id")


class Stop(LocationBase):
    def __init__(self, raw_data: dict[str, any]):
        super().__init__(raw_data)
        self.name: str = raw_data.get("name")
        self.location = LocationFactory.get_location(raw_data.get("location"))
        self.products = LocationFactory.get_products(raw_data.get("products"))
        self.station_dhid: str = raw_data.get("stationDHID")

    def __repr__(self):
        return f"Stop(%s), Coordinates=%s" % (self.name, self.location)


class Location(LocationBase):
    def __init__(self, raw_data: dict[str, any]):
        from app.vbb.models.others import GeoLocation
        super().__init__(raw_data)
        self.geo = GeoLocation(data=raw_data)
        self.latitude: Optional[float] = self.geo.latitude
        self.longitude: Optional[float] = self.geo.longitude
        self.address: str = raw_data.get("address")

    def __repr__(self):
        return f"Location(geo=%s)" % self.geo
