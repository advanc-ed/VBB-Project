import logging

from aiogram import F, Router
from aiogram.filters import Command, ExceptionTypeFilter
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode, setup_dialogs
from aiogram_dialog.api.exceptions import NoContextError, OutdatedIntent, UnknownIntent, UnknownState

from app.dialogs import states
from app.dialogs.add_address import address_add_dialog
from app.dialogs.address_confirmation import confirm_address_dialog
from app.dialogs.addresses import addresses_dialog
from app.dialogs.journeys import journeys_dialog
from app.dialogs.location import location_handler_dialog
from app.dialogs.main import main_dialog
from app.dialogs.register import register_dialog
from app.dialogs.settings import settings_dialog
from app.dialogs.stop import stops_dialog


async def start(message: Message, dialog_manager: DialogManager):
    """Start dialog manager"""
    await dialog_manager.start(states.MainSG.MAIN, mode=StartMode.RESET_STACK)


async def cancel(message: Message, dialog_manager: DialogManager):
    """Disable all dialogs of user"""
    try:
        await dialog_manager.reset_stack()
    except NoContextError as e:
        logging.error("No dialog to cancel.")
        return await message.reply("No dialog to cancel.")

    await message.reply("Dialog cancelled.")


async def geolocation(message: Message, dialog_manager: DialogManager):
    """Start dialog handler for messages with geolocation"""
    await dialog_manager.start(states.Location.MAIN, mode=StartMode.RESET_STACK, data={"location": message.location})


async def on_dialog_fail(event, dialog_manager: DialogManager):
    """Restart dialog on failure."""
    logging.warning("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        states.MainSG.MAIN, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,
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
router.message.register(geolocation, F.location)

router.errors.register(
    on_dialog_fail,
    ExceptionTypeFilter(UnknownIntent, UnknownState, OutdatedIntent),
)

router.include_router(dialog_router)
setup_dialogs(router)
