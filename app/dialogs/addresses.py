import logging
import operator

from typing import Dict

from aiogram import F

from aiogram_dialog import (
    Dialog, DialogManager, SubManager,
    Window
)
from aiogram_dialog.widgets.kbd import (
    Checkbox, ListGroup,
    ManagedCheckbox, Radio, Row,
    ManagedListGroup, Start
)
from aiogram_dialog.widgets.text import Const, Format, Multi

from app.utils import address_util, message_builder
from app.common import FMT
from app.utils.enums import AddressType

from app.dialogs import states
from app.dialogs.common import MAIN_MENU_BUTTON


def when_checked(data: Dict, widget, manager: SubManager) -> bool:
    check: ManagedCheckbox = manager.find("check")

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
    Const("You have no addresses yet. To add an address, click on the button below.",
          when=~F["message_text"]),
    Format("{message_text}")
)

addresses_list_group = ListGroup(
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
)

add_address_button = Start(
    Const("Add address"), id="set", state=states.AddressAddSG.INPUT
)

main_window = Window(
    message_text,
    addresses_list_group,
    add_address_button,
    MAIN_MENU_BUTTON,
    state=states.AddressesSG.MAIN,
    getter=data_getter,
)

addresses_dialog = Dialog(
    main_window,
    on_start=on_start,
)
