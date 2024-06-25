import uuid
from datetime import datetime, timedelta

import pytz
from sqlalchemy import (BigInteger, Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, Sequence,
                        String, Time, UUID)
from sqlalchemy.orm import relationship

from app.db.base import Base


def get_now():
    berlin_timezone = pytz.timezone("Europe/Berlin")
    return berlin_timezone.localize(datetime.now())


def get_current_datetime():
    return get_now()


def get_current_time():
    return get_now().time()


def get_check_time():
    return get_now() - timedelta(hours=4)


class Address(Base):
    __tablename__ = "addresses"
    __allow_unmapped__ = True

    id = Column(Integer,
                Sequence('addresses_id_seq'),
                primary_key=True,
                unique=True,
                autoincrement=True)
    street_name = Column(String(100))
    house_number = Column(Integer)
    city = Column(String(50))
    plz = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    created_by_id = Column(BigInteger)


class User(Base):
    __tablename__ = "users"
    __allow_unmapped__ = True

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    home_address_id = Column(
        Integer,
        ForeignKey('addresses.id'),
        default=None)
    default_destination_address_id = Column(
        Integer,
        ForeignKey('addresses.id'),
        default=None)
    walking_speed = Column(String(10), nullable=False, default="normal")
    max_transfers = Column(Integer, nullable=False, default=4)
    max_journeys = Column(Integer, nullable=False, default=10)
    min_transfer_time = Column(Integer, nullable=False, default=0)
    arrival_time = Column(Time, nullable=False, default=get_current_time)
    check_time = Column(Time, nullable=False, default=get_check_time)
    regional = Column(Boolean, nullable=False, default=True)
    suburban = Column(Boolean, nullable=False, default=True)
    bus = Column(Boolean, nullable=False, default=True)
    ferry = Column(Boolean, nullable=False, default=True)
    subway = Column(Boolean, nullable=False, default=True)
    tram = Column(Boolean, nullable=False, default=True)
    is_notified = Column(Boolean, nullable=False, default=False)

    home_address: Address = relationship(
        "Address", foreign_keys=[home_address_id])
    default_destination_address: Address = relationship(
        "Address", foreign_keys=[default_destination_address_id]
    )

    __table_args__ = (
        CheckConstraint(
            "walking_speed IN ('slow', 'normal', 'fast')", name='chk_walking_speed'),
    )

    def __repr__(self) -> str:
        return f"{self.id} - {self.home_address_id} - {self.default_destination_address_id}"


class JourneyDB(Base):
    __tablename__ = "journeys"
    __allow_unmapped__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refresh_token = Column(String(1000))
    created_by_id = Column(BigInteger)
    created_at = Column(DateTime, default=get_current_datetime)
