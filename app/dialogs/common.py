from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Start, Button, Cancel
from aiogram_dialog.widgets.text import Const
from app.dialogs import states

MAIN_MENU_BUTTON = Start(
    text=Const("☰ Main menu"),
    id="__main__",
    state=states.MainSG.MAIN,
)


async def delete_message(callback_query: CallbackQuery, *args):
    await callback_query.message.delete()


DELETE_MESSAGE_BUTTON = Button(
    text=Const("🚮 Delete"),
    id="delete",
    on_click=delete_message
)


async def close_dialog(callback_query: CallbackQuery, *args):
    await callback_query.answer("Dialog was closed.")


CLOSE_STATE_BUTTON = Cancel(
    text=Const("🏁 Close dialog"),
    id="close",
    on_click=close_dialog
)
