import logging

from aiogram.types import CallbackQuery

from aiogram_dialog import (
    Dialog,
    DialogManager,
    Window
)

from aiogram_dialog.widgets.kbd import (
    Row,
    Button,
    Back
)
from aiogram_dialog.widgets.text import Const, Format, Multi

from app.dialogs import states
from app.utils import address_util, message_builder


async def get_address_data(dialog_manager: DialogManager, **kwargs):
    location = dialog_manager.start_data.get("location")
    if location is None:
        address = dialog_manager.start_data.get("address")
    else:
        address = f"{location.latitude}, {location.longitude}"
        
    address_data = address_util.get_resolved_address(address)

    if address_data is None:
        logging.warning("No address")

    address_information_text = message_builder.resolved_address_to_text(
        address_data
    )

    dialog_manager.dialog_data["address"] = address
    dialog_manager.dialog_data["address_data"] = address_data
    dialog_manager.dialog_data["address_information_text"] = address_information_text

    return dialog_manager.dialog_data


async def on_address_confirmed(callback: CallbackQuery, button: Button, manager: DialogManager):
    logging.info("address was confirmed")
    manager.dialog_data["success"] = True
    await manager.done(result=manager.dialog_data)


async def on_address_declined(callback: CallbackQuery, button: Button, manager: DialogManager):
    logging.info("address was not confirmed")
    await manager.done(result={"success": False})


confirm_address_window_message = Multi(
    Format("You have entered: <code>{address}</code>"),
    Const("Is this correct information about your address?\n"),
    Format("{address_information_text}")
)

confirm_address_window = Window(
    confirm_address_window_message,
    Row(
        Back(
            Const("No"),
            id="address_not_confirmed",
            on_click=on_address_declined,
        ),
        Button(
            Const("Yes"),
            id="address_confirmed",
            on_click=on_address_confirmed,
        )
    ),
    state=states.AddressConfirmationSG.CONFIRM,
    getter=get_address_data
)

confirm_address_dialog = Dialog(
    confirm_address_window,
)
