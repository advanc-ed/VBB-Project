import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.filters.user import IsOwner

router = Router()


@router.message(Command("ping"), IsOwner())
async def ping_handler(message: Message):
    """
    Ping checker (bot -> telegram server -> bot)
    via the /ping command (only owner)
    """
    start = time.perf_counter_ns()
    reply_message = await message.answer("<code>⏱ Checking ping...</code>")
    end = time.perf_counter_ns()
    ping = (end - start) * 0.000001
    await reply_message.edit_text(
        f"<b>⏱ Ping -</b> <code>{round(ping, 3)}</code> <b>ms</b>"
    )
