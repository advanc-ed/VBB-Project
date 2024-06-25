from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    CurrentPage,
    NextPage,
    PrevPage, Row,
    StubScroll,
)
from aiogram_dialog.widgets.text import Format
from app.dialogs import states
from app.dialogs.common import MAIN_MENU_BUTTON
from app.vbb.func import get_journeys
from app.utils import message_builder

from app.common import FMT


async def paging_getter(dialog_manager: DialogManager, **_kwargs):
    from app import sessionmanager, config
    current_page = await dialog_manager.find(ID_STUB_SCROLL).get_page()
    user_id = dialog_manager.event.from_user.id
    f: FMT = dialog_manager.middleware_data.get("f")
    if f is None:
        async with sessionmanager() as session:
            user = await session.get_user(user_id)
            home_address = await session.get_address(user.home_address_id)
            destination_address = await session.get_address(user.default_destination_address_id)
    else:
        user = await f.db.get_user(user_id)

    start_data = dialog_manager.start_data
    location_ = start_data.get("location") if start_data else None
    now = start_data.get("now", True) if start_data else True

    if f is None:
        data = await get_journeys(user, home_address=home_address, destination_address=destination_address)
    else:
        data = await get_journeys(user, f.db, now=now) \
            if location_ is None \
            else await get_journeys(user, f.db, location_, now=now)

    journey = data[current_page]

    return {
        "pages": len(data),
        "current_page": current_page + 1,
        "journey_information": await message_builder.build_journey_text(journey)
    }


ID_STUB_SCROLL = "stub_scroll"

main_window = Window(
    Format("{journey_information}"),
    StubScroll(id=ID_STUB_SCROLL, pages="pages"),
    Row(
        PrevPage(
            scroll=ID_STUB_SCROLL,
        ),
        CurrentPage(
            scroll=ID_STUB_SCROLL, text=Format(
                "({current_page1} / {pages})"),
        ),
        NextPage(
            scroll=ID_STUB_SCROLL,
        ),
    ),
    MAIN_MENU_BUTTON,
    state=states.JourneysSG.MAIN,
    getter=paging_getter,
)

journeys_dialog = Dialog(
    main_window,
)
