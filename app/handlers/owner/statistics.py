from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app import dp
from app.common import FMT
from app.filters.user import IsOwner

router = Router()


@router.message(Command("stats"), IsOwner())
async def stats_handler(message: Message, f: FMT):
    user_count: int = await f.db.get_users_count()
    addresses_count: int = await f.db.get_addresses_count()
    await message.answer(
        f"📊 <b>Users count -</b> <code>{user_count}</code>\n" +
        f"🏚️ <b>Addresses count -</b> <code>{addresses_count}</code>"
    )
