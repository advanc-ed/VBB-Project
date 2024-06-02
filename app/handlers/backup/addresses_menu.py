import asyncio
import logging
import operator
import os

from typing import Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ContentType

from aiogram_dialog import (
    Dialog, DialogManager, LaunchMode, ShowMode,
    setup_dialogs, StartMode, SubManager,
    Window
)
from aiogram_dialog.widgets.kbd import (
    Checkbox, ListGroup,
    ManagedCheckbox, Radio, Row,
    ManagedListGroup, ManagedRadio,
    Button, Cancel, Back, Start
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const, Format, Multi

from app import dp
from app.utils import address_util, message_builder
from app.common import FMT
from app.utils.enums import AddressType


class AddressAddSG(StatesGroup):
    input = State()
    confirm = State()


async def address_handler(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
):
    manager.dialog_data["address"] = message.text
    await message.delete()
    await manager.switch_to(
        state=AddressAddSG.confirm,
        show_mode=ShowMode.EDIT
    )


async def get_address_data(dialog_manager: DialogManager, **kwargs):
    address = dialog_manager.dialog_data.get("address")
    address_data = address_util.get_resolved_address(address)

    if address_data is None:
        logging.warning("No address")
        return

    address_message = \
        """Street: %s
House number: %s
City: %s
Postal code: %s

📍 Pin: %s, %s""" % (
            address_data.street_name,
            address_data.house_number,
            address_data.city,
            address_data.plz,
            address_data.latitude,
            address_data.longitude
        )

    dialog_manager.dialog_data["address_data"] = address_data

    return {
        "address": address,
        "address_data": address_data,
        "address_message": address_message
    }


async def on_finish(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await address_util.add_address(manager.dialog_data["address_data"], callback.from_user.id, manager.middleware_data["f"])
    await manager.done()

ask_for_address_window = Window(
    Const("Please write address to add:"),
    Cancel(),
    MessageInput(address_handler, content_types=[ContentType.TEXT]),
    state=AddressAddSG.input,
)

confirm_address_window = Window(
    Format("You have entered: <code>{address}</code>"),
    Format("Is this correct information about your address?\n"),
    Format("{address_message}"),
    Row(
        Back(Const("No")),
        Button(Const("Yes"), id="yes", on_click=on_finish),
    ),
    state=AddressAddSG.confirm,
    getter=get_address_data,
)

address_add_dialog = Dialog(
    ask_for_address_window,
    confirm_address_window,
)


class AddressesSG(StatesGroup):
    greeting = State()


def when_checked(data: Dict, widget, manager: SubManager) -> bool:
    # manager for our case is already adapted for current ListGroup row
    # so `.find` returns widget adapted for current row
    # if you need to find widgets outside the row, use `.find_in_parent`
    check: ManagedCheckbox = manager.find("check")
    radio: ManagedRadio = manager.find("radio")

    return check.is_checked()


async def data_getter(dialog_manager: DialogManager, **kwargs):
    f: FMT = dialog_manager.middleware_data.get("f")
    user_id: int = dialog_manager.event.from_user.id

    message_text = await message_builder.user_addresses_list(user_id, f)
    addresses_data_short = await address_util.user_addresses_short(user_id, f)

    return {
        "message_text": message_text,
        "addresses_data_short": addresses_data_short,
        "addresses_types": [AddressType.Home, AddressType.DefaultDestination, AddressType.NoUse]
    }


async def on_start(_, manager: DialogManager):
    lg: ManagedListGroup = manager.find("lg")

    data = await data_getter(manager)

    await update_buttons(data, lg)


async def update_buttons(data, lg: ManagedListGroup):
    for address in data.get("addresses_data_short"):
        address_id = address[0]
        address_usage = address[2]

        widget: Radio = lg.find_for_item("radio", str(address_id))

        await widget.set_checked(address_usage.value)


async def state_changed(event, source, manager: SubManager, *args, **kwargs):
    logging.info("state_changed")


async def change_state(event, source, manager: SubManager, *args, **kwargs):
    if AddressType.NoUse.value in args[0]:
        return
    logging.info("Change state")

    f: FMT = manager.middleware_data.get("f")

    await address_util.update_address(
        address_t=args[0],
        address_id=int(manager.item_id),
        user_id=event.from_user.id,
        f=f
    )

    data = await data_getter(manager)

    lg = manager.find_in_parent("lg")
    await update_buttons(data, lg)


message_text = Multi(
    Const(
        "Here are your addresses:\n",
    ),
    Format("{message_text}")
)


dialog = Dialog(
    Window(
        message_text,
        ListGroup(
            Checkbox(
                Format("⤵️ {item[1]}"),
                Format("➡️ {item[1]}"),
                id="check",
            ),
            Row(
                Radio(
                    checked_text=Format("🔘 {item.value}"),
                    unchecked_text=Format("⚪️ {item.value}"),
                    id="radio",
                    item_id_getter=lambda item: item.value,
                    items=lambda data: data["data"]["addresses_types"],
                    when=when_checked,
                    on_click=change_state,
                ),
            ),
            id="lg",
            item_id_getter=operator.itemgetter(0),
            items=lambda data: data["addresses_data_short"],
        ),
        Start(Const("Enter address"), id="set", state=AddressAddSG.input),
        state=AddressesSG.greeting,
        getter=data_getter,
    ),
    on_start=on_start,
    launch_mode=LaunchMode.SINGLE_TOP,
)


# async def start(message: Message, dialog_manager: DialogManager):
#     # it is important to reset stack because user wants to restart everything
#     await dialog_manager.start(AddressesSG.greeting, mode=StartMode.RESET_STACK)

# dialog_router = Router()
# dialog_router.include_router(address_add_dialog)
# dialog_router.include_router(dialog)

# dp.include_router(dialog_router)
# dp.message.register(start, Command("addresses"))
# setup_dialogs(dp)
