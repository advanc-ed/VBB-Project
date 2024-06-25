from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app import owner_id
from app.ui.commands import owner_commands, users_commands

router = Router()


@router.message(Command("help"))
async def help_handler(message: Message):
    """Command list"""
    text = "ℹ️ <b>Command list:</b> \n\n"
    commands = (
        owner_commands.items()
        if message.from_user.id == owner_id
        else users_commands.items()
    )
    for command, description in commands:
        text += f"/{command} - <b>{description}</b> \n"
    await message.answer(text)
