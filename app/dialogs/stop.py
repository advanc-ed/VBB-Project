import calendar
from operator import itemgetter

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.common import sync_scroll
from aiogram_dialog.widgets.kbd import (
    CurrentPage, FirstPage, LastPage,
    Multiselect, NextPage, NumberedPager,
    PrevPage, Row, ScrollingGroup,
    StubScroll, SwitchTo,
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, List, ScrollingText
from app.dialogs import states
from app.dialogs.common import MAIN_MENU_BUTTON
from app.vbb.func import get_reachable_stops
from app.utils import message_builder

from app.common import FMT


async def paging_getter(dialog_manager: DialogManager, **_kwargs):
    current_page = await dialog_manager.find(ID_STUB_SCROLL).get_page()
    user_id = dialog_manager.event.from_user.id
    f: FMT = dialog_manager.middleware_data.get("f")
    data: dict = await get_reachable_stops(user_id, f)

    current_stop = data[current_page]

    return {
        "pages": len(data),
        "current_page": current_page + 1,
        "stop_information": await message_builder.stop_to_text(current_stop),
        "stop_name": current_stop.get("name")
    }


ID_STUB_SCROLL = "stub_scroll"

stub_scroll_window = Window(
    Format("{stop_information}"),
    StubScroll(id=ID_STUB_SCROLL, pages="pages"),
    Row(
        PrevPage(
            scroll=ID_STUB_SCROLL,
        ),
        CurrentPage(
            scroll=ID_STUB_SCROLL, text=Format(
                "({current_page1} / {pages}) {data[stop_name]}"),
        ),
        NextPage(
            scroll=ID_STUB_SCROLL,
        ),
    ),
    MAIN_MENU_BUTTON,
    state=states.Scrolls.STUB,
    getter=paging_getter,
)


stops_dialog = Dialog(
    stub_scroll_window,
)
