import logging
import asyncio
from datetime import datetime, time

from aiogram.fsm.state import State

from app import sessionmanager
from app.db.models import User
from app.dialogs import states


def is_time_matching(check_time: time):
    now = datetime.now().time()
    return all([now.hour == check_time.hour,
                now.minute == check_time.minute])


async def check_journeys():
    while True:
        async with sessionmanager() as session:
            users: list[User] = await session.get_registered_users()

            for user in users:
                logging.debug("checking user: %s" % user)
                if user.is_notified:
                    continue

                if not is_time_matching(user.check_time):
                    continue

                # todo: build message
                await start_dialog(states.JourneysSG.MAIN, user.id, now=False)

                # await update_notified(user, True)
                await session.update_notified(user, True)

        await asyncio.sleep(15)


async def start_dialog(state: State, user_id, **kwargs):
    from aiogram_dialog.manager.bg_manager import BgManager
    from aiogram.types import Chat, User as TgUser
    from aiogram_dialog import StartMode, ShowMode
    from app import bot, dp
    user = TgUser(id=user_id, is_bot=False, first_name="test")
    chat = Chat(id=user_id, type="private")
    manager = BgManager(user=user, chat=chat, bot=bot, router=dp, intent_id=None, stack_id="")
    await manager.start(state, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND, data=kwargs)


async def remove_is_notified():
    async with sessionmanager() as session:
        users: list[User] = await session.get_registered_users()
        for user in users:
            await session.update_notified(user, False)
