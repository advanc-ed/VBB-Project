import logging

from app.vbb.enums import TransportMode
from app.vbb.models.leg import LegFactory, Leg
from dataclasses import dataclass
from app.vbb.models.others import OthersFactory, OthersType, Cycle


class JourneyFactory:
    @staticmethod
    def create(raw_data):
        if raw_data is None:
            return None

        legs = [
            LegFactory.create(leg)
            for leg in raw_data.get('legs', [])
        ]

        return Journey(
            type=raw_data.get('type'),
            legs=legs,
            refresh_token=raw_data.get("refreshToken"),
            cycle=OthersFactory.create(raw_data.get("cycle"), OthersType.CYCLE)
        )


@dataclass
class Journey:
    type: str
    legs: list[Leg]
    refresh_token: str
    cycle: Cycle

    def __repr__(self):
        return "Journey(type=%s, legs=%s, refresh_token=%s, cycle=%s" % (
            self.type,
            self.legs,
            self.refresh_token[:15] + '...' + self.refresh_token[-15:],
            self.cycle
        )

    def __post_init__(self):
        self.remove_invalid_legs()

    def remove_invalid_legs(self):
        new_legs = []
        for leg in self.legs:
            if not leg.invalid_leg:
                new_legs.append(leg)

        self.legs = new_legs

    def count_transfers(self):
        counter = 0

        for leg in self.legs:
            if leg.transport_mode != TransportMode.WALKING:
                counter += 1

        return max(counter - 1, 0)
