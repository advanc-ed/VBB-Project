from aiogram import types
from aiogram.filters import BaseFilter

from app import owner_id
from app import sessionmanager


class IsOwner(BaseFilter):
    """Checking if user is owner via comparing his id with owner id from config."""

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == owner_id


class IsRegistered(BaseFilter):
    is_registered: bool

    async def __call__(self, message: types.Message) -> bool:
        async with sessionmanager() as session:
            registered = await session.is_registered()
            return bool(registered) == self.is_registered
