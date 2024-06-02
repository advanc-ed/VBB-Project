from abc import ABC
from typing import Optional

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func
from sqlalchemy import text

from asyncpg.exceptions import UniqueViolationError

from .models import User, Address, JourneyDB

from app.utils import AddressResolved
from app.utils.enums import AddressType


class DB(AsyncSession, ABC):
    async def is_registered(self, user_id: int) -> bool:
        user = await self.get_user(user_id)

        if user is None:
            return False
        if user.default_destination_address_id is None and user.home_address_id is None:
            return False

        return True

    async def is_registered_in_db(self, user_id: int) -> bool:
        user = await self.get_user(user_id)

        if user is None:
            return False

        return True

    async def get_registered_users(self) -> list[User]:
        q = select(User).where(
            User.home_address_id.isnot(None),
            User.default_destination_address_id.isnot(None)
        )

        return (await self.scalars(q)).all()

    async def register(self, user_id) -> User:
        user = User(id=user_id)
        self.add(user)
        await self.commit()
        return user

    async def get_user(self, user_id) -> User:
        q = select(User).where(User.id == user_id)
        return await self.scalar(q)

    async def get_users_count(self):
        q = func.count(User.id)
        return await self.scalar(q)

    async def update_notified(self, user: User, is_notified: bool) -> None:
        user.is_notified = is_notified
        await self.commit()

    async def get_addresses_count(self):
        q = func.count(Address.id)
        return await self.scalar(q)

    async def update_user_data(self, user_id, updates: dict) -> None:
        q = update(User).where(User.id == user_id).values(**updates)
        await self.execute(q)
        await self.commit()

    async def get_address(self, address_id) -> Address:
        q = select(Address).where(Address.id == address_id)
        return await self.scalar(q)

    async def change_address(self, address_id, updates) -> None:
        q = update(Address).where(Address.id == address_id).values(**updates)
        await self.execute(q)
        await self.commit()

    async def add_address(self, address: AddressResolved, user_id: int) -> Optional[Address]:
        address = Address(
            street_name=address.street_name,
            house_number=address.house_number,
            city=address.city,
            plz=address.plz,
            latitude=address.latitude,
            longitude=address.longitude,
            created_by_id=user_id
        )

        q = select(Address).where(
            Address.street_name == address.street_name,
            Address.house_number == address.house_number,
            Address.city == address.city,
            Address.plz == address.plz,
            Address.created_by_id == address.created_by_id
        )

        if await self.scalar(q) is not None:
            return None

        self.add(address)
        await self.commit()
        return address

    async def register_user(self, addresses: dict[str, AddressResolved], user_id: int) -> User:
        for address_type, address in addresses.items():
            address = await self.add_address(address, user_id)
            await self.update_user_data(
                user_id=user_id,
                updates={
                    f"{address_type}_id": address.id
                }
            )

    async def get_user_addresses(self, user_id: int) -> list[Address]:
        q = select(Address).where(Address.created_by_id == user_id)
        return (await self.scalars(q)).all()

    async def check_address_usage(self, user_id, address_id) -> Optional[AddressType]:
        address = await self.get_address(address_id)
        if address is None:
            raise Exception("Address was not found.")

        user = await self.get_user(user_id)
        if user is None:
            raise Exception("User was not found.")

        if user.home_address_id == address_id:
            return AddressType.Home
        elif user.default_destination_address_id == address_id:
            return AddressType.DefaultDestination
        else:
            return AddressType.NoUse

    async def get_user_journeys(self, user_id) -> list[JourneyDB]:
        q = select(JourneyDB).where(JourneyDB.created_by_id == user_id)
        return (await self.scalars(q)).all()

    async def get_journeys(self) -> list[JourneyDB]:
        q = select(JourneyDB)
        return (await self.scalars(q)).all()

    async def add_journey(self, refresh_token: str, user_id: int) -> JourneyDB:
        journey = JourneyDB(
            refresh_token=refresh_token,
            created_by_id=user_id
        )
        self.add(journey)
        await self.commit()
        return journey
