import re

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'location_pin_(\d+)'))
))
async def location_cmd(message: Message, command: CommandObject):
    """Returns message with geolocation via deeplink.
    Latitude and longitude are being passed via deep_link and magic filter"""
    args = command.args.split("_")
    *_, latitude, longitude = args
    latitude = float(latitude.replace("-", "."))
    longitude = float(longitude.replace("-", "."))

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🚮 Delete",
            callback_data="delete_this_message"
        )
    )

    await message.answer_location(latitude, longitude, reply_markup=builder.as_markup())
    await message.delete()
