from typing import Optional

from aiogram.types import CallbackQuery, Location
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs import states
from app.dialogs.common import MAIN_MENU_BUTTON
from app.utils import message_builder
from app.utils.models import AddressResolved
from app.vbb.models import Helper


async def get_data(dialog_manager: DialogManager, **_kwargs):
    location: Optional[Location] = dialog_manager.start_data.get("location", None)
    location: Optional[AddressResolved] = await Helper.get_address_from_location(location)
    address_information_text = message_builder.resolved_address_to_text(location)
    return {
        "address_information_text": address_information_text,
    }


main_text = Format(
    """\
Received location:

{address_information_text}

Please select action:"""
)


async def find_journeys(callback_query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback_query.answer("Getting journeys...")

    await dialog_manager.start(
        state=states.JourneysSG.MAIN,
        data=dialog_manager.start_data,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT
    )


find_journeys_to_location_button = Button(
    text=Const("🗺 Get journeys to this location"),
    id="get_journeys_to_location",
    on_click=find_journeys
)

main_window = Window(
    main_text,
    find_journeys_to_location_button,
    MAIN_MENU_BUTTON,
    state=states.Location.MAIN,
    getter=get_data,
)

location_handler_dialog = Dialog(
    main_window,
)
