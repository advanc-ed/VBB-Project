from dataclasses import dataclass

from app.config import Config
from app.db.functions import DB
from app.utils import AddressUtil, MessageBuilder


@dataclass
class FMT:
    db: DB
    config: Config


@dataclass
class Basic:
    address_util: AddressUtil
    message_builder: MessageBuilder
