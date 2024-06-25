from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import Message

from app import bot, config, sessionmanager
from app.common import FMT


class MainMiddleware(BaseMiddleware):
    """
    Main Middleware adds additional information to all handlers:

    sessionmanager - DB Session
    f - FMT
    bot - Bot itself
    """

    def __init__(self) -> None:
        self.config = config
        self.sessionmanager = sessionmanager
        self.bot = bot

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        async with self.sessionmanager() as session:
            data["session"] = session
            data["f"] = FMT(db=session, config=self.config)
            data["bot"] = self.bot
            await handler(event, data)


def register_middleware(dp: Dispatcher):
    main_middleware = MainMiddleware()
    dp.message.middleware(main_middleware)
    dp.callback_query.middleware(main_middleware)
