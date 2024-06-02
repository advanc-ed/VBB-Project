import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command, ExceptionTypeFilter

from aiogram_dialog import DialogManager, setup_dialogs, StartMode, ShowMode

from aiogram_dialog.api.exceptions import NoContextError, UnknownIntent, UnknownState, OutdatedIntent

from app import dp

from app.dialogs import states
from app.dialogs.main import main_dialog
from app.dialogs.add_address import address_add_dialog
from app.dialogs.address_confirmation import confirm_address_dialog
from app.dialogs.addresses import addresses_dialog
from app.dialogs.register import register_dialog
from app.dialogs.settings import settings_dialog
from app.dialogs.journeys import journeys_dialog
from app.dialogs.stop import stops_dialog
from app.dialogs.location import location_handler_dialog
from app.filters.user import IsRegistered


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.MainSG.MAIN, mode=StartMode.RESET_STACK)


async def cancel(message: Message, dialog_manager: DialogManager):
    try:
        await dialog_manager.done()
    except NoContextError as e:
        logging.error("No dialog to cancel.")
        return await message.reply("No dialog to cancel.")

    await message.reply("Dialog cancelled.")


async def on_unknown_intent(event, dialog_manager: DialogManager):
    # Example of handling UnknownIntent Error and starting new dialog.
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        states.MainSG.MAIN, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,
    )


async def on_unknown_state(event, dialog_manager: DialogManager):
    # Example of handling UnknownState Error and starting new dialog.
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        states.MainSG.MAIN, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND
    )


dialog_router = Router()
dialog_router.include_routers(
    main_dialog,
    addresses_dialog,
    register_dialog,
    confirm_address_dialog,
    address_add_dialog,
    settings_dialog,
    stops_dialog,
    journeys_dialog,
    location_handler_dialog
)

router = Router()

router.message.register(start, Command("menu"))
router.message.register(cancel, Command("cancel"))
router.errors.register(
    on_unknown_intent,
    ExceptionTypeFilter(UnknownIntent),
)
router.errors.register(
    on_unknown_state,
    ExceptionTypeFilter(UnknownState, OutdatedIntent),
)
router.include_router(dialog_router)
setup_dialogs(router)
