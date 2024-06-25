import logging
from datetime import datetime

from aiogram import F
from aiogram import html
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import ChatEvent, Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Checkbox, Group, ManagedCheckbox, SwitchTo, Toggle
from aiogram_dialog.widgets.text import Const, Multi, Format

from app.common import FMT
from app.dialogs import states
from app.dialogs.common import MAIN_MENU_BUTTON
from app.utils import address_util
from app.utils.enums import AddressType, WalkingSpeedWithEmoji
from app.vbb.enums import TransportMode


async def change_walking_speed(callback: CallbackQuery, toggle: Toggle, manager: DialogManager, *args, **kwargs):
    new_walking_speed = args[0].split(' ')[1].lower()

    user_id = callback.from_user.id
    f = manager.middleware_data.get("f")
    await f.db.update_user_data(user_id, {
        "walking_speed": new_walking_speed
    })


async def start_settings(_, manager: DialogManager):
    walking_speed_toggle: Toggle = manager.find('walking_speed_toggle')
    user_ = (await data_getter(manager)).get("user_")
    walking_speed = get_user_walking_speed(user_)
    await walking_speed_toggle.set_checked(walking_speed)

    for transport_mode in TransportMode:
        if transport_mode is TransportMode.WALKING:
            continue

        checkbox: ManagedCheckbox = manager.find(transport_mode.name)

        await checkbox.set_checked(
            getattr(user_, transport_mode.name.lower())
        )


def get_user_walking_speed(user_):
    walking_speed = WalkingSpeedWithEmoji.get_walking_speed(user_.walking_speed)
    if walking_speed is not None:
        walking_speed = walking_speed.value

    return walking_speed


async def data_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    user = dialog_manager.event.from_user
    f: FMT = dialog_manager.middleware_data.get("f")
    addresses = await address_util.user_addresses_short(user.id, f)
    home_address = [address
                    for address in addresses
                    if address[2] == AddressType.Home][0][1] or None
    destination_address = [address
                           for address in addresses
                           if address[2] == AddressType.DefaultDestination][0][1] or None

    walking_speed_toggle_items = [WalkingSpeedWithEmoji.slow,
                                  WalkingSpeedWithEmoji.normal,
                                  WalkingSpeedWithEmoji.fast]

    user_ = await f.db.get_user(user.id)
    arrival_time = user_.arrival_time.strftime("%H:%M")
    check_time = user_.check_time.strftime("%H:%M")

    return {
        "user": user,
        "user_": user_,
        "addresses_count": len(addresses),
        "home_address": home_address,
        "destination_address": destination_address,
        "arrival_time": arrival_time,
        "check_time": check_time,
        "walking_speed_toggle_items": walking_speed_toggle_items,
        "walking_speed": get_user_walking_speed(user_),
    }


message_text = Multi(
    Const("⚙️ Settings window:\n"),
    Format("Name: <b>{user.first_name}</b>"),
    Format("ID: <code>{user.id}</code>\n"),
    Format("Addresses count: {addresses_count}"),
    Format("🏚️ Home address: {home_address}"),
    Format("🏢 Destination address: {destination_address}\n"),
    Format("🕚 Arrival time: {arrival_time}"),
    Format("⏰ Check time: {check_time}\n"),
    Const(html.code(html.quote(">-------------------------<"))),
    Format("Walking speed: {walking_speed}"),
    Format("Minimum transfer time: {user_.min_transfer_time} min."),
    Format("Maximum transfer amount: {user_.max_transfers}."),
    Format("Maximum journeys amount: {user_.max_journeys}."),
)

walking_speed_toggle = Toggle(
    text=Format("Walking speed: {item.value}"),
    id="walking_speed_toggle",
    item_id_getter=lambda item: item.value,
    items=lambda data: data["walking_speed_toggle_items"],
    on_click=change_walking_speed
)


async def go_to_change_window(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data["change_type"] = button.widget_id
    await manager.switch_to(
        state=states.SettingsSG.CHANGE,
        show_mode=ShowMode.EDIT
    )


change_min_transfer_time = Button(
    text=Const("Change min. transfer time"),
    id="min_transfer_time",
    on_click=go_to_change_window,
)

change_max_transfers_amount = Button(
    text=Const("Change max. transfers amount"),
    id="max_transfers",
    on_click=go_to_change_window,
)

change_max_journeys_amount = Button(
    text=Const("Change max. journeys amount"),
    id="max_journeys",
    on_click=go_to_change_window,
)

change_check_time = Button(
    text=Const("Change check time"),
    id="check_time",
    on_click=go_to_change_window,
)

change_arrival_time = Button(
    text=Const("Change arrival time"),
    id="arrival_time",
    on_click=go_to_change_window,
)


async def change_handler(
        message: Message,
        widget: MessageInput,
        manager: DialogManager,
):
    await message.delete()
    change_type = manager.dialog_data["change_type"]
    new_data = message.text
    f = manager.middleware_data.get("f")
    if change_type in ["min_transfer_time", "max_transfers", "max_journeys"]:
        new_data = int(new_data)

    if change_type in ["check_time", "arrival_time"]:
        new_data = datetime.strptime(new_data, "%H:%M")

    await f.db.update_user_data(message.from_user.id, {
        change_type: new_data
    })

    await manager.switch_to(
        state=states.SettingsSG.MAIN,
        show_mode=ShowMode.EDIT
    )


async def check_transport_type(event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager, *args, **kwargs):
    transport_mode = TransportMode[checkbox.widget.widget_id]
    f = manager.middleware_data.get("f")
    await f.db.update_user_data(event.from_user.id, {
        transport_mode.name.lower(): checkbox.is_checked()
    })


transport_types = Group(
    *[Checkbox(
        Const(f"✅ {transport_mode.value} {transport_mode.name.lower().capitalize()}"),
        Const(f"❌ {transport_mode.value} {transport_mode.name.lower().capitalize()}"),
        id=transport_mode.name,
        on_state_changed=check_transport_type,
    ) for transport_mode in TransportMode if transport_mode is not TransportMode.WALKING],
    width=2
)

changes_window = Window(
    Const("Please provide new amount:"),
    Back(),
    MessageInput(change_handler, content_types=[ContentType.TEXT]),
    state=states.SettingsSG.CHANGE,
)

main_menu = Window(
    message_text,
    walking_speed_toggle,
    change_min_transfer_time,
    change_max_transfers_amount,
    change_max_journeys_amount,
    transport_types,
    change_check_time,
    change_arrival_time,
    MAIN_MENU_BUTTON,
    state=states.SettingsSG.MAIN,
    getter=data_getter,
)

settings_dialog = Dialog(
    main_menu,
    changes_window,
    on_start=start_settings
)
