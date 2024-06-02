from enum import Enum
from typing import Optional


class TransportMode(Enum):
    SUBURBAN = "🚈"
    SUBWAY = "🚇"
    TRAM = "🚋"
    BUS = "🚌"
    FERRY = "⛴️"
    # EXPRESS = "🚄"
    REGIONAL = "🚆"
    WALKING = "🚶"

    @classmethod
    def get_emoji(cls, mode: str) -> str:
        try:
            return cls[mode.upper()].value
        except KeyError:
            raise ValueError(f"No emoji found for transport mode: {mode}")

    @classmethod
    def get_mode_from_string(cls, mode: str) -> Optional["TransportMode"]:
        try:
            return cls[mode.upper()]
        except KeyError:
            return None
