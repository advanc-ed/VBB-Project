from aiogram.fsm.state import State, StatesGroup


class AddressAddSG(StatesGroup):
    INPUT = State()


class AddressConfirmationSG(StatesGroup):
    CONFIRM = State()


class RegisterSG(StatesGroup):
    MAIN = State()
    HOME_ADDRESS = State()
    DESTINATION_ADDRESS = State()
    FINISH = State()


class AddressesSG(StatesGroup):
    MAIN = State()


class MainSG(StatesGroup):
    MAIN = State()


class SettingsSG(StatesGroup):
    MAIN = State()
    CHANGE = State()


class Scrolls(StatesGroup):
    STUB = State()


class JourneysSG(StatesGroup):
    MAIN = State()


class Location(StatesGroup):
    MAIN = State()
