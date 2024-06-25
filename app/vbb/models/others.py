import logging
from dataclasses import MISSING, dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union


class GeoLocation:
    def __init__(self, latitude=None, longitude=None, data: dict = None):
        if latitude is None and longitude is None and data is None:
            raise ValueError("Invalid data.")

        if data is not None:
            latitude = data.get('latitude')
            longitude = data.get('longitude')

        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def __repr__(self):
        return 'GeoLocation(%s, %s)' % (self.latitude, self.longitude)


class OthersType(Enum):
    REMARK = "remark",
    CYCLE = "cycle",
    OPERATOR = "operator"
    COLOR = "color"


class OthersFactory:
    @staticmethod
    def create(raw_data: dict[str, any],
               type: OthersType) -> Optional[
        Union[
            "Remark",
            "Cycle",
            "Operator",
            "Color",
        ]
    ]:

        if raw_data is None:
            raw_data = {}

        def fill_defaults(cls, data: dict[str, any]) -> dict[str, any]:
            pre = {}
            for field in fields(cls):
                if field.name in data:
                    pre[field.name] = data[field.name]
                elif field.default is not MISSING:
                    pre[field.name] = field.default
                elif field.default_factory is not MISSING:
                    pre[field.name] = field.default_factory()
                else:
                    logging.error("Unknown field")
            return pre

        cls = None
        match type:
            case type.REMARK:
                cls = Remark
            case type.CYCLE:
                cls = Cycle
            case type.OPERATOR:
                cls = Operator
            case type.COLOR:
                cls = Color
            case _:
                return None

        if cls:
            filled_data = fill_defaults(cls, raw_data)
            return cls(**filled_data)
        return None


class Products:
    def __init__(self, raw_data: dict[str, any]):
        self.suburban: bool = raw_data.get("suburban", False)
        self.subway: bool = raw_data.get("subway", False)
        self.tram: bool = raw_data.get("tram", False)
        self.bus: bool = raw_data.get("bus", False)
        self.ferry: bool = raw_data.get("ferry", False)
        self.express: bool = raw_data.get("express", False)
        self.regional: bool = raw_data.get("regional", False)


@dataclass
class Remark:
    type: Optional[str] = None
    code: Optional[str] = None
    text: Optional[str] = None
    id: Optional[str] = None
    summary: Optional[str] = None
    icon: Optional[Any] = None
    priority: Optional[int] = None
    products: Optional[dict[str, bool] | Products] = None
    company: Optional[str] = None
    categories: Optional[list[int]] = None
    valid_from: Optional[str | datetime] = None
    valid_until: Optional[str | datetime] = None
    modified: Optional[str | datetime] = None
    extended: bool = False

    def __post_init__(self):
        from .helper import Helper

        def convert_and_set(attribute_name, conversion_function):
            value = getattr(self, attribute_name)
            if value is not None:
                self.extended = True
                setattr(self, attribute_name, conversion_function(value))

        if self.products is not None:
            self.extended = True
            self.products = Products(self.products)

        convert_and_set('valid_from', Helper.get_datetime_from_string)
        convert_and_set('valid_until', Helper.get_datetime_from_string)
        convert_and_set('modified', Helper.get_datetime_from_string)


@dataclass
class Cycle:
    min: Optional[int] = None
    max: Optional[int] = None
    nr: Optional[int] = None


@dataclass
class Operator:
    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class Color:
    fg: Optional[str] = None
    bg: Optional[str] = None
