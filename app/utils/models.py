from dataclasses import dataclass


@dataclass
class AddressResolved:
    street_name: str
    house_number: int
    city: str
    plz: int
    latitude: float
    longitude: float

    def __str__(self):
        return f"{self.street_name} {self.house_number}, {self.plz} {self.city}"
