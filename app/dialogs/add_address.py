import logging

from aiogram.types import Message, CallbackQuery, ContentType

from aiogram_dialog import (
    Dialog, DialogManager, ShowMode,
    Window
)
from aiogram_dialog.widgets.kbd import (
    Button, Cancel
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const

from app.dialogs import states
from app.utils import address_util


async def address_handler(
        message: Message,
        widget: MessageInput,
        manager: DialogManager,
):
    if message.location is not None:
        address_passed = f"{message.location.latitude}, {message.location.longitude}"
    else:
        address_passed = message.text
    manager.dialog_data["address"] = address_passed
    await message.delete()
    await manager.start(
        state=states.AddressConfirmationSG.CONFIRM,
        data={
            "address": address_passed
        },
        show_mode=ShowMode.EDIT
    )


async def on_result(start_data: dict, result: dict, dialog_manager: DialogManager, **kwargs):
    address_data = result.get("address_data")

    success: bool = result.get("success", False)

    if success:
        await address_util.add_address(address_data, dialog_manager.event.from_user.id,
                                       f=dialog_manager.middleware_data.get("f"))
        await dialog_manager.done()


ask_for_address_window = Window(
    Const("Please write address (or send geolocation) to add:"),
    Cancel(),
    MessageInput(address_handler, content_types=[ContentType.TEXT, ContentType.LOCATION]),
    state=states.AddressAddSG.INPUT,
)

address_add_dialog = Dialog(
    ask_for_address_window,
    on_process_result=on_result
)
