import logging

from aiogram.filters import Command
from aiogram.types import Message

from app import dp, sessionmanager

from app.vbb.func import get_journeys
from app.utils import message_builder


@dp.message(Command("journeys"))
async def journeys_handler(message: Message, session: sessionmanager):
    user = await session.get_user(message.from_user.id)
    journeys = await get_journeys(user, session)
    for journey in journeys:
        message_text = await message_builder.build_journey_text(journey)
        await message.answer(message_text)
