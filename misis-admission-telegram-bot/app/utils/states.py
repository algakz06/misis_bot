from aiogram.dispatcher.filters.state import State, StatesGroup


class User(StatesGroup):
    first_name = State()
    last_name = State()
    city = State()
    email = State()
    phone = State()


class UserEditProfile(StatesGroup):
    first_name = State()
    last_name = State()
    city = State()
    email = State()
    phone = State()
