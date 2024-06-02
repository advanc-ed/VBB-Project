from aiogram import F, Router
from aiogram.types import CallbackQuery

from app import dp

router = Router()


@router.callback_query(F.data == "delete_this_message")
async def delete_message(callback: CallbackQuery):
    try:
        await callback.message.delete()
        await callback.answer("Deleted.")
    except Exception as e:
        await callback.answer("Error deleting this message. Probably it is too old.")
