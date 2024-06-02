from typing import Optional
from app.vbb.models.others import Color, Operator, OthersFactory, OthersType


class LineFactory:
    @staticmethod
    def get_line(line_data: dict[str, any]) -> Optional["Line"]:
        if line_data is None:
            return None

        return Line(line_data)


class Line:
    def __init__(self, line_data: dict[str, any]):
        self.type: str = line_data.get("type")
        self.id: str = line_data.get("id")
        self.trip_nr: str = line_data.get("fahrtNr")
        self.name: str = line_data.get("name")
        self.public: bool = line_data.get("public")
        self.admin_code: str = line_data.get("adminCode")
        self.product_name: str = line_data.get("productName")
        self.mode: str = line_data.get("mode")
        self.product: str = line_data.get("product")
        self.operator: Operator = OthersFactory.create(line_data.get("operator"), OthersType.OPERATOR)  # noqa
        self.color: Color = OthersFactory.create(line_data.get("color"), OthersType.COLOR)  # noqa
