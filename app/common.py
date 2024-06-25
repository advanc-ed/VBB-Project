from dataclasses import dataclass

from app.config import Config
from app.db.functions import DB


@dataclass
class FMT:
    """
    FMT class has DB and Config in it
    """
    db: DB
    config: Config
