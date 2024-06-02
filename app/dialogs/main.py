from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const
from app.dialogs import states
from app.dialogs.common import CLOSE_STATE_BUTTON

main_dialog = Dialog(
    Window(
        Const("Main Window."),
        Const("Select menu option:"),
        Start(
            text=Const("🏚️ Addresses menu"),
            id="addresses",
            state=states.AddressesSG.MAIN,
        ),
        Start(
            text=Const("👋 Registration menu"),
            id="register",
            state=states.RegisterSG.MAIN,
        ),
        Start(
            text=Const("🚌 Get nearby stops"),
            id="nearby_stops",
            state=states.Scrolls.STUB
        ),
        Start(
            text=Const("🗺 Get journeys"),
            id="journeys",
            state=states.JourneysSG.MAIN
        ),
        Start(
            text=Const("⚙️ Settings"),
            id="settings",
            state=states.SettingsSG.MAIN
        ),
        CLOSE_STATE_BUTTON,
        state=states.MainSG.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
