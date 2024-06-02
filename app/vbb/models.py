from dataclasses import dataclass, make_dataclass, fields
from datetime import datetime
# todo: implement it better


@dataclass
class Location:
    latitude: float
    longitude: float

    def __str__(self):
        return f"📍 {self.latitude} {self.longitude}"
