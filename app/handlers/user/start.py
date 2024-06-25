from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.common import FMT

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, f: FMT, bot: Bot):
    user_id = message.from_user.id
    bot_information = await bot.get_me()
    if not await f.db.is_registered_in_db(user_id):
        await f.db.register(user_id)

    await message.answer(
        f"Welcome in <b>{bot_information.full_name}</b>! \n" +
        f"<b>️ Press</b> /menu <b>for starting the dialog.</b> \n" +
        f"<b>️ Press</b> /help <b>for more information and usage help.</b>"
    )
