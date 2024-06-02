import enum
from typing import Optional


class AddressType(enum.Enum):
    Home = "Home Address"
    DefaultDestination = "Destination Address"
    NoUse = "No Use"


class AddressTypeEmoji(enum.Enum):
    Home = "🏚️"
    DefaultDestination = "🏢"
    NoUse = "No Use"


class WalkingSpeed(enum.Enum):
    slow = "slow"
    normal = "normal"
    fast = "fast"


class WalkingSpeedWithEmoji(enum.Enum):
    slow = "🐢 Slow"
    normal = "🚶‍♀️ Normal"
    fast = "🏃‍♂️ Fast"

    @staticmethod
    def get_walking_speed(mode: str) -> Optional["WalkingSpeedWithEmoji"]:
        try:
            return WalkingSpeedWithEmoji[mode]
        except KeyError:
            return None
