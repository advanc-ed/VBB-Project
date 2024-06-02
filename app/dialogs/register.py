import logging

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import (
    Dialog, Window, DialogManager, ShowMode, LaunchMode
)
from aiogram_dialog.widgets.kbd import (
    Button, Row, SwitchTo, Start
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.input import MessageInput

from app.dialogs import states
from app.dialogs.common import MAIN_MENU_BUTTON

from app.utils.enums import AddressType
from app.common import FMT
from app.utils import address_util


async def home_address_input_handler(message: Message, widget: MessageInput, manager: DialogManager):
    logging.info("home_address_input_handler")
    logging.info("state from home handler")
    logging.info(manager.current_context().state)
    address_passed = message.text
    manager.dialog_data["home_address"] = address_passed
    await message.delete()
    await manager.start(
        state=states.AddressConfirmationSG.CONFIRM,
        data={
            "address": address_passed,
            "type": AddressType.Home
        },
        show_mode=ShowMode.EDIT
    )


async def destination_address_input_handler(message: Message, widget: MessageInput, manager: DialogManager):
    logging.info("destination_address_input_handler")
    logging.info("state from dest handler")
    logging.info(manager.current_context().state)
    address_passed = message.text
    manager.dialog_data["destination_address"] = address_passed
    await message.delete()
    await manager.start(
        state=states.AddressConfirmationSG.CONFIRM,
        data={
            "address": address_passed,
            "type": AddressType.DefaultDestination
        },
        show_mode=ShowMode.EDIT
    )


async def on_register_finish(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.answer("Thank you. Writing answers to the database.")
    home_address = manager.dialog_data["home_address_data"]
    destination_address = manager.dialog_data["destination_address_data"]

    await address_util.register_user_resolved_addresses(
        home_address,
        destination_address,
        callback.from_user.id,
        f=manager.middleware_data.get("f")
    )


async def get_data(dialog_manager: DialogManager, **kwargs):
    f: FMT = dialog_manager.middleware_data.get("f")

    is_registered = await f.db.is_registered(dialog_manager.event.from_user.id)

    home_address = dialog_manager.dialog_data.get("home_address_data", "")
    destination_address = dialog_manager.dialog_data.get("destination_address_data", "")  # noqa

    return {
        "home_address": str(home_address),
        "destination_address": str(destination_address),
        "registered": is_registered,
    }


main_window = Window(
    Multi(
        Const("You have already registered!",
              when="registered"),
        Const("You have not registered yet.\nPlease do it in order to use bot.",
              when=~F["registered"]),
    ),
    SwitchTo(
        text=Const("Registration"),
        id="register",
        state=states.RegisterSG.HOME_ADDRESS,
    ),
    MAIN_MENU_BUTTON,
    state=states.RegisterSG.MAIN,
    getter=get_data
)

home_address_window = Window(
    Const("Please, write your home address\nExample: <code>Randomstr. 20, 11111 Berlin</code>:"),
    MessageInput(home_address_input_handler),
    state=states.RegisterSG.HOME_ADDRESS,
)

destination_address_window = Window(
    Const("Please enter your default destination address:"),
    MessageInput(destination_address_input_handler),
    state=states.RegisterSG.DESTINATION_ADDRESS,
)

finish_window_message = Multi(
    Const("Thank you for your answers. <b>Please confirm your answers:</b>\n"),
    Format("🏚️ Home address: <code>{home_address}</code>"),
    Format("🏢 Destination address: <code>{destination_address}</code>")
)

finish_window = Window(
    finish_window_message,
    Row(
        SwitchTo(
            Const("🔁 Restart"),
            id="register_restart",
            state=states.RegisterSG.HOME_ADDRESS
        ),
        Start(
            Const("✅ Confirm"),
            id="register_confirm",
            on_click=on_register_finish,
            state=states.MainSG.MAIN
        )
    ),
    getter=get_data,
    state=states.RegisterSG.FINISH
)


async def on_result(start_data: dict, result: dict, dialog_manager: DialogManager, **kwargs):
    address_type = None
    match start_data.get("type"):
        case AddressType.Home:
            address_type = "home_address_data"
        case AddressType.DefaultDestination:
            address_type = "destination_address_data"

    if address_type is not None:
        dialog_manager.dialog_data[address_type] = result.get("address_data")

    success: bool = result.get("success", False)

    if success:
        await dialog_manager.next()
        logging.info("address was accepted.")
    else:
        # pochemu tak?
        logging.info("address was declined.")
        await dialog_manager.show()
        return


register_dialog = Dialog(
    main_window,
    home_address_window,
    destination_address_window,
    finish_window,
    on_process_result=on_result,
    launch_mode=LaunchMode.SINGLE_TOP
)
