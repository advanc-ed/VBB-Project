from datetime import datetime
from typing import Optional, Union
from app.vbb.models.location import LocationFactory, Stop, Location
from app.vbb.models.line import LineFactory, Line
from app.vbb.models.helper import Helper
from app.vbb.models.others import OthersFactory, OthersType, Remark, Cycle, GeoLocation
from app.vbb.enums import TransportMode


class LegFactory:
    @staticmethod
    def create(raw_data):
        if raw_data is None:
            return None

        return Leg(raw_data)


class Leg:
    def __init__(self, leg_info: dict):
        self.origin: Union[Stop, Location]
        self.destination: Union[Stop, Location]
        self.departure: Optional[datetime]
        self.planned_departure: Optional[datetime]
        self.departure_delay: Optional[int]
        self.arrival: Optional[datetime]
        self.planned_arrival: Optional[datetime]
        self.arrival_delay: Optional[int]
        self.public: Optional[bool]
        self.walking: Optional[bool]
        self.distance: int
        self.reachable: Optional[bool]
        self.trip_id: str
        self.line: Optional[Line]
        self.direction: Optional[str]
        self.current_location: Optional[GeoLocation]
        self.arrival_platform: str
        self.arrival_platform_planned: str
        self.arrival_prognosis_type: str
        self.departure_platform: str
        self.departure_platform_planned: str
        self.departure_prognosis_type: str
        self.remarks: list[Remark]
        self.cycle: Cycle
        self.invalid_leg: bool
        self.raw_data: dict = leg_info
        self.transport_mode: TransportMode
        self.cancelled: bool

        self.__post__init__()

    def __post__init__(self):
        # parse data from dict
        self.parse_data()

        # check if leg is invalid (transfer IN station)
        self.check_invalid_leg()

        # get type
        self.get_transport_mode()

    def parse_data(self):
        self.origin = LocationFactory.get_location(self.raw_data.get("origin"))  # noqa
        self.destination = LocationFactory.get_location(self.raw_data.get("destination"))  # noqa
        self.departure = Helper.get_datetime_from_string(self.raw_data.get("departure"))
        self.planned_departure = Helper.get_datetime_from_string(self.raw_data.get("plannedDeparture"))
        self.departure_delay = self.raw_data.get("departureDelay", 0)
        self.arrival = Helper.get_datetime_from_string(self.raw_data.get("arrival"))
        self.planned_arrival = Helper.get_datetime_from_string(self.raw_data.get("plannedArrival"))
        self.arrival_delay = self.raw_data.get("arrivalDelay", 0)
        self.public = self.raw_data.get("public")
        self.walking = self.raw_data.get("walking", False)
        self.distance = self.raw_data.get("distance")
        self.reachable = self.raw_data.get("reachable")
        self.trip_id = self.raw_data.get("tripId")
        self.line = LineFactory.get_line(self.raw_data.get("line"))
        self.direction = self.raw_data.get("direction")
        self.current_location = LocationFactory.get_location(self.raw_data.get("currentLocation", {}))  # noqa
        self.arrival_platform = self.raw_data.get("arrivalPlatform")
        self.arrival_platform_planned = self.raw_data.get("plannedArrivalPlatform")  # noqa
        self.arrival_prognosis_type = self.raw_data.get("arrivalPrognosisType")  # noqa
        self.departure_platform = self.raw_data.get("departurePlatform")  # noqa
        self.departure_platform_planned = self.raw_data.get("plannedDeparturePlatform")  # noqa
        self.departure_prognosis_type = self.raw_data.get("departurePrognosisType")  # noqa
        self.remarks = [OthersFactory.create(remark, OthersType.REMARK)
                        for remark in self.raw_data.get("remarks", [])]  # noqa
        self.cycle = OthersFactory.create(self.raw_data.get("cycle"), OthersType.CYCLE)  # noqa
        self.cancelled = self.raw_data.get("cancelled", False)

    def check_invalid_leg(self):
        if self.walking:
            if self.origin.id == self.destination.id:
                self.invalid_leg = True
                return

        self.invalid_leg = False

    def get_transport_mode(self):
        type = None
        if self.walking:
            type = "walking"
        else:
            type = self.line.mode

        mode = TransportMode.get_mode_from_string(type)
        if mode is None:
            mode = TransportMode.get_mode_from_string(self.line.product)

        self.transport_mode = mode

    def __repr__(self):
        return "Leg(%s, %s)" % (self.origin, self.destination)
