from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, ContentType, Message

from aiogram_dialog import (
    ChatEvent, Dialog, DialogManager,
    setup_dialogs,
    StartMode, Window, ShowMode
)
from aiogram_dialog.api.exceptions import NoContextError
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi

from aiogram.filters import Command
from aiogram.types import Message

from app import dp
from app.utils import address_util

import logging


class RegisterSG(StatesGroup):
    home_address = State()
    destination_address = State()
    finish = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = {
        "home_address": dialog_manager.dialog_data.get("home_address", ""),
        "destination_address": dialog_manager.dialog_data.get("destination_address", ""),
    }

    return data


async def home_address_handler(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
):
    manager.dialog_data["home_address"] = message.text
    await message.delete()
    await manager.switch_to(
        state=RegisterSG.destination_address,
        show_mode=ShowMode.EDIT
    )


async def destination_address_handler(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
):
    manager.dialog_data["destination_address"] = message.text
    await message.delete()
    await manager.switch_to(
        state=RegisterSG.finish,
        show_mode=ShowMode.EDIT
    )


async def other_type_handler(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
):
    await message.answer("Text is expected!")


async def on_finish(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager
):
    if manager.is_preview():
        await manager.done()
        return
    await callback.message.answer("Thank you. Writing answers to the database.")
    await address_util.register_user_resolved_addresses(
        manager.dialog_data["home_address"],
        manager.dialog_data["destination_address"],
        callback.from_user.id,
        f=manager.middleware_data.get("f")
    )
    await manager.done()

ask_for_home_address_window = Window(
    Const("Please, write your home address\nExample: <code>Randomstr. 20, 11111 Berlin</code>:"),
    MessageInput(home_address_handler, content_types=[ContentType.TEXT]),
    MessageInput(other_type_handler),
    state=RegisterSG.home_address,
)

ask_for_destination_address_window = Window(
    Format(
        "Please enter your default destination address:"),
    MessageInput(destination_address_handler,
                 content_types=[ContentType.TEXT]),
    MessageInput(other_type_handler),
    state=RegisterSG.destination_address,
)

confirm_addresses_window = Window(
    Multi(
        Format("Thank you for your answers. <b>Please confirm your answers:</b>"),
        Format(" "),
        Format("🏚️ Home address: <code>{home_address}</code>"),
        Format(
            "🏢 Destination address: <code>{destination_address}</code>"),
        sep="\n"
    ),
    Row(
        SwitchTo(Const("🔁 Restart"), id="restart",
                 state=RegisterSG.home_address),
        Button(Const("✅ Confirm"), on_click=on_finish, id="finish"),
    ),
    getter=get_data,
    state=RegisterSG.finish,
)

dialog = Dialog(
    ask_for_home_address_window,
    ask_for_home_address_window,
    confirm_addresses_window,
)


# async def start(message: Message, dialog_manager: DialogManager):
#     await dialog_manager.start(RegisterSG.home_address, mode=StartMode.RESET_STACK)


# async def cancel(message: Message, dialog_manager: DialogManager):
#     try:
#         await dialog_manager.done()
#     except NoContextError as e:
#         logging.error("No dialog to cancel.")
#         return await message.reply("No dialog to cancel.")

#     await message.reply("Dialog cancelled.")

# dp.message.register(start, Command("register"))
# dp.message.register(cancel, Command("cancel"))

# dp.include_router(dialog)
# setup_dialogs(dp)
