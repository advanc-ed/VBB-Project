import asyncio
import logging

import coloredlogs
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import app
from app import config
from app import db
from app.ui.commands import remove_bot_commands, set_bot_commands


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    """
    Register bot handlers (commands and dialogs),
             bot commands

    Also drop pending updates

    Args:
        dispatcher: Comes from **kwargs, given by Dispatcher.
        bot: Comes from **kwargs, given by Dispatcher.

    Returns:

    """
    from app import handlers, middlewares

    middlewares.register_middlewares(dp=app.dp, config=config)
    app.dp.include_router(handlers.get_handlers_router())

    await set_bot_commands(app.bot)
    await bot.delete_webhook(
        drop_pending_updates=config.settings.drop_pending_updates,
    )

    logging.info("Bot started!")


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    """
    Close bot instance, FSM Storage and bot session on shutdown.
    Args:
        dispatcher: Comes from **kwargs, given by Dispatcher.
        bot: Comes from **kwargs, given by Dispatcher.

    Returns:

    """
    logging.warning("Stopping bot...")
    await remove_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=config.settings.drop_pending_updates)
    await dispatcher.fsm.storage.close()
    await app.bot.session.close()


async def main():
    """
    Main entry point for the bot.
    Returns:

    """
    logging_level = logging.DEBUG if app.arguments.test else logging.INFO
    coloredlogs.install(level=logging_level, milliseconds=True)
    logging.warning("Starting bot...")

    app.owner_id = app.config.settings.owner_id

    db_url = config.db.database_url
    app.sessionmanager = await db.init(db_url)

    session = AiohttpSession(
        api=TelegramAPIServer.from_base(config.api.bot_api_url))
    token = config.bot.token
    bot_settings = {"session": session}
    app.bot = Bot(token,
                  default=DefaultBotProperties(
                      parse_mode=ParseMode.HTML),
                  **bot_settings)

    storage = MemoryStorage()

    app.dp = Dispatcher(storage=storage)
    app.dp.startup.register(on_startup)
    app.dp.shutdown.register(on_shutdown)

    # - background vbb jobs:
    from app.vbb.service.checker import check_journeys
    asyncio.create_task(check_journeys())  # noqa

    from app.utils import add_scheduler_jobs
    await add_scheduler_jobs()

    await app.dp.start_polling(app.bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
