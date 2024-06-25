from aiogram import F, Router
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
import logging
from app import dp
from app.dialogs import states

router = Router()


@router.message(F.location)
# async def start(message: Message, dialog_manager: DialogManager):
#     await dialog_manager.start(states.Location.MAIN, mode=StartMode.RESET_STACK, data={"location": message.location})
async def start(message: Message, **kwargs):
    await message.answer('test...')
