#!/usr/bin/env python3

"""Main module."""

# region third-party imports
import requests
from aiogram import Dispatcher, Bot, types
import asyncio
from typing import Dict, Union
import re
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, BotBlocked
# endregion

# region local imports
from app import config
from app.config import log
# from app.keyboards import reply_keyboards
from app.keyboards.reply_keyboards import build_markup, reply_markup
from app.utils.bot_buttons import Layout
from app.utils.users import BotUsers
from app.utils.statistics import Statistics
# from app.utils.db import DBManager
from app.utils.states import User, UserEditProfile
from app.keyboards import profile as profile_kbs
from app.utils import replies
# endregion


# region app initialization
bot = Bot(config.tg_token)
dp = Dispatcher(bot, storage=MemoryStorage())
users = BotUsers()  # Connection check here
layout = Layout()
stats = Statistics()
# db = DBManager()
# endregion

is_admin = (
    lambda message: users.admins.is_admin(message.from_user.id)
    if isinstance(message, types.Message)
    else users.admins.is_admin(message)
)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    """Start handler."""
    if users.user_exists(message.from_user.id):
        await message.answer("Привет! Кажется, мы уже знакомы. Чем могу помочь?",
                             reply_markup=build_markup("", layout.get_btns("1"), is_main=True))
        return
    await message.answer("""
Привет!\n
Это телеграмм-бот НИТУ МИСИС,\
здесь ты сможешь получить ответ на все свои вопросы\n
Только перед этим нам надо получить от тебя немного информации
""")
    await message.answer("Для начала отправь мне свое имя",
                         reply_markup=ReplyKeyboardRemove())
    await User.first_name.set()


@dp.message_handler(state=User.first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    if not re.match("^[А-Яа-яЁё]{2,20}$", message.text):
        await message.answer('Неверный формат, напиши свое имя, например "Даниил"')
        return
    async with state.proxy() as data:
        data["first_name"] = message.text
    await message.answer("Записал!\n\nТеперь отправь свою фамилию",
                         reply_markup=ReplyKeyboardRemove())
    await User.last_name.set()


@dp.message_handler(state=User.last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    if not re.match("^[А-Яа-яЁё]{2,20}$", message.text):
        await message.answer('Неверный формат, напиши свою фамилию, например "Коротков"',
                             reply_markup=ReplyKeyboardRemove())
        return
    async with state.proxy() as data:
        data["last_name"] = message.text
    await message.answer("И последний шаг!\n\nОтправь свою электронную почту",
                         reply_markup=ReplyKeyboardRemove())
    await User.email.set()


@dp.message_handler(state=User.email)
async def get_email(message: types.Message, state: FSMContext):
    if not requests.get(f"{config.DEFAULT_BASE_URL}/check/email?email={message.text}").json()["is_valid"]:
        await message.answer('Неверный формат! Пример: example@ya.ru',
                             reply_markup=ReplyKeyboardRemove())
        return
    async with state.proxy() as data:
        data["email"] = message.text
    await message.answer("Спасибо за регистрацию и добро пожаловать!\n\nВы можете оставить дополнительную информацию о \
себе в пункте меню \"Профиль\"",
                         reply_markup=ReplyKeyboardRemove())
    buttons = layout.get_btns("1")
    reply_msg = layout.get_reply("0")
    await message.answer(
        reply_msg, reply_markup=build_markup("", buttons, is_main=True)
    )
    async with state.proxy() as data:
        users.add(
            message.from_user.id,
            username=message.from_user.username,
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"]
        )
    await state.finish()


@dp.message_handler(commands=["elevate"])
async def elevate_to_admin(message: types.Message):
    # Get token as the message argument
    token = message.get_args().split()[0]
    is_elevated = users.admins.add(message.from_user.id, token)
    if is_elevated:
        await message.answer("Вы теперь администратор!")
        return
    await message.answer("Неверный токен")


@dp.message_handler(commands=["reload"])
async def resend_keyboard(message: types.Message):
    if not is_admin(message):
        await message.answer("Вы не администратор!")
        return

    args = message.get_args().split()
    log.debug(f"Arguments for /reload: {args}")

    if "kb" in args:
        log.debug("Resending keyboard to all users")
        buttons = layout.get_btns("1")
        for user_id in users.get_ids():
            try:
                log.debug(f"Resending keyboard to {user_id}")
                await bot.send_message(
                    chat_id=user_id,
                    text="Клавиатура обновилась",
                    reply_markup=build_markup("", buttons, True)
                )
            except BotBlocked:
                log.debug(f"User {user_id} blocked the bot")
    if "replies" in args:
        log.debug("Asking the backend to reload all replies")
        requests.get(f"{config.DEFAULT_BASE_URL}/reload/replies")
        await bot.send_message(message.from_user.id,
                               "Ответы перезагружены")
    if "users" in args:
        log.debug("Asking the backend to reload all users")
        requests.get(f"{config.DEFAULT_BASE_URL}/reload/users")
        users.fetch()
        users.admins.fetch()
        await bot.send_message(message.from_user.id,
                               "Пользователи перезагружены")


@dp.message_handler(lambda message: message.text == config.PROFILE_BTN)
async def profile_info(message: types.Message):
    """Send user profile info and edit buttons."""
    if not users.user_exists(message.from_user.id):
        await message.answer(replies.not_registered(message.from_user.first_name))
        return
    await bot.send_message(message.from_user.id,
                           replies.profile_info(users.get(message.from_user.id)),
                           reply_markup=profile_kbs.inlProfileMenu)


def get_profile_edit_fields_kb() -> InlineKeyboardMarkup:
    """Get inline keyboard with profile fields for editing."""
    kb = InlineKeyboardMarkup()
    fields = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'city': 'Город',
        'email': 'Email',
        'phone_number': 'Телефон',
    }
    for key in fields:
        kb.add(InlineKeyboardButton(fields[key], callback_data=f'profile:edit:{key}'))
    kb.add(InlineKeyboardButton('Готово', callback_data='profile:edit:done'))
    return kb


@dp.callback_query_handler(lambda c: c.data == 'profile:edit')
async def edit_profile(call: types.CallbackQuery, secondary_run: bool = False) -> None:
    """Edit user profile."""
    keyboard = get_profile_edit_fields_kb()
    if not secondary_run:
        await call.answer()
        await call.message.edit_text(replies.profile_info(users.get(call.from_user.id)),
                                     reply_markup=keyboard)
    else:
        await bot.send_message(call.from_user.id,
                               replies.profile_info(users.get(call.from_user.id)),
                               reply_markup=keyboard)
    mkb_remove = await call.message.answer("Убираю основную клавиатуру...", reply_markup=ReplyKeyboardRemove())
    await mkb_remove.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('profile:edit:') and
                           not c.data == 'profile:edit:done')
async def edit_profile_action(call: types.CallbackQuery, state: FSMContext) -> None:
    """Edit user profile - select action."""
    await call.answer()
    user_data = users.get(call.from_user.id)
    await state.update_data(profile_call=call)
    fn = lambda x: f'profile:edit:{x}'
    if call.data == fn('first_name'):
        await call.message.edit_text(replies.profile_edit_first_name(user_data['first_name'],
                                                                     user_data['last_name']))
        await state.set_state(UserEditProfile.first_name)
    elif call.data == fn('last_name'):
        await call.message.edit_text(replies.profile_edit_last_name(user_data['first_name'],
                                                                    user_data['last_name']))
        await state.set_state(UserEditProfile.last_name)
    elif call.data == fn('city'):
        await call.message.edit_text(replies.profile_edit_city(user_data['city']))
        await state.set_state(UserEditProfile.city)
    elif call.data == fn('email'):
        await call.message.edit_text(replies.profile_edit_email(user_data['email']))
        await state.set_state(UserEditProfile.email)
    elif call.data == fn('phone_number'):
        await call.message.edit_text(replies.profile_edit_phone(user_data['phone_number']))
        await state.set_state(UserEditProfile.phone)
    else:
        await bot.send_message(call.from_user.id, f"Field is not editable yet: {call.data}")


@dp.callback_query_handler(lambda c: c.data == 'profile:edit:done')
async def edit_profile_done(call: types.CallbackQuery, state: FSMContext) -> None:
    """Edit user profile (Original state)."""
    await state.finish()
    await call.answer()
    await call.message.edit_text(replies.profile_info(users.get(call.from_user.id)),
                                 reply_markup=profile_kbs.inlProfileMenu)
    await call.message.answer("Восстанавливаю основную клавиатуру...",
                              reply_markup=build_markup("", layout.get_btns("1"), is_main=True))


@dp.message_handler(state=UserEditProfile.first_name)
async def edit_profile_first_name(message: types.Message, state: FSMContext):
    """Edit user profile first name."""
    profile_call = (await state.get_data())['profile_call']
    await state.update_data(first_name=message.text)
    users.update(profile_call.from_user.id, first_name=message.text)
    await profile_call.message.edit_text(replies.profile_info(users.get(profile_call.from_user.id)),
                                         reply_markup=get_profile_edit_fields_kb())
    await message.delete()
    await state.finish()


@dp.message_handler(state=UserEditProfile.last_name)
async def edit_profile_last_name(message: types.Message, state: FSMContext):
    """Edit user profile last name."""
    profile_call = (await state.get_data())['profile_call']
    await state.update_data(last_name=message.text)
    users.update(profile_call.from_user.id, last_name=message.text)
    await profile_call.message.edit_text(replies.profile_info(users.get(profile_call.from_user.id)),
                                         reply_markup=get_profile_edit_fields_kb())
    await message.delete()
    await state.finish()


@dp.message_handler(state=UserEditProfile.city)
async def edit_profile_city(message: types.Message, state: FSMContext):
    """Edit user profile city."""
    profile_call = (await state.get_data())['profile_call']
    is_updated = users.update(profile_call.from_user.id, city=message.text)
    if not is_updated:
        await message.delete()
        try:
            await profile_call.message.edit_text(replies.invalid_city_try_again())
        except MessageNotModified:
            pass
        return
    await profile_call.message.edit_text(replies.profile_info(users.get(profile_call.from_user.id)),
                                         reply_markup=get_profile_edit_fields_kb())
    await message.delete()
    await state.finish()


@dp.message_handler(state=UserEditProfile.email)
async def edit_profile_email(message: types.Message, state: FSMContext):
    """Edit user profile email."""
    profile_call = (await state.get_data())['profile_call']
    is_updated = users.update(profile_call.from_user.id, email=message.text)
    if not is_updated:
        await message.delete()
        try:
            await profile_call.message.edit_text(replies.invalid_email_try_again())
        except MessageNotModified:
            pass
        return
    await profile_call.message.edit_text(replies.profile_info(users.get(profile_call.from_user.id)),
                                         reply_markup=get_profile_edit_fields_kb())
    await message.delete()
    await state.finish()


@dp.message_handler(state=UserEditProfile.phone)
async def edit_profile_phone(message: types.Message, state: FSMContext):
    """Edit user profile phone."""
    profile_call = (await state.get_data())['profile_call']
    is_updated = users.update(profile_call.from_user.id, phone=message.text)
    if not is_updated:
        await message.delete()
        try:
            await profile_call.message.edit_text(replies.invalid_phone_try_again())
        except MessageNotModified:
            pass
        return
    await profile_call.message.edit_text(replies.profile_info(users.get(profile_call.from_user.id)),
                                         reply_markup=get_profile_edit_fields_kb())
    await message.delete()
    await state.finish()


@dp.message_handler()
async def handler(message: types.Message) -> None:
    if not users.user_exists(message.from_user.id):
        await message.answer(replies.not_registered(message.from_user.first_name))
        return
    buttons: Union[Dict[str, str], None] = layout.get_btns("1")

    if not buttons:
        return

    if message.text not in buttons.values():
        print("ERROR: no message")
        return

    btn_id = [btn_id for btn_id, text in buttons.items() if text == message.text][0]

    if btn_id is None:
        return

    reply_msg: Union[str, None] = layout.get_reply(btn_id)
    keyboard_btn: Union[Dict[str, str], None] = layout.get_btns(btn_id)
    keyboard = build_markup(current_path=btn_id, buttons=keyboard_btn)

    if keyboard is not None:
        await message.answer(reply_msg, reply_markup=keyboard)
    else:
        await message.answer(reply_msg)

    stats.store(message.from_user.id, btn_id)


@dp.callback_query_handler(lambda c: c.data.startswith("back:"))
async def query_back(call: types.CallbackQuery):
    current_path = call.data.split(":")
    current_path.pop()
    last_btn = current_path[-1]
    current_path = ":".join(current_path[1:])
    msg_repl: Union[str, None] = layout.get_reply(last_btn)
    keyboard_btn: Union[Dict[str, str], None] = layout.get_btns(last_btn)
    keyboard = build_markup(current_path, keyboard_btn)

    if keyboard is None:
        await call.message.edit_text(msg_repl)
        return

    if msg_repl is None:
        await call.message.edit_reply_markup(reply_markup=keyboard)
        return

    await call.message.edit_text(msg_repl)
    await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler()
async def query_handler(call: types.CallbackQuery):
    await call.answer()
    if not users.user_exists(call.from_user.id):
        await call.message.answer("Кажется, ты не зарегистрирован! Чтобы начать, нажми сюда: /start")
        return
    current_path = call.data
    btn_id = current_path.split(":")[-1]
    keyboard_btn = layout.get_btns(btn_id)
    keyboard = build_markup(current_path, keyboard_btn)
    msg_repl = layout.get_reply(btn_id) or ""

    stats.store(call.from_user.id, btn_id)

    lat_lon = re.findall(r"\d+\.\d+", msg_repl)
    if lat_lon and len(lat_lon) == 2 and "lat" in msg_repl:
        lat, lon = lat_lon
        msg_repl = msg_repl.split("[")[0].strip()
        await call.message.answer(msg_repl)
        await call.message.answer_location(latitude=lat, longitude=lon)
        return

    if keyboard is None:
        await call.message.edit_text(msg_repl)
        return

    if msg_repl is None:
        await call.message.edit_reply_markup(reply_markup=keyboard)
        return

    await call.message.edit_text(msg_repl)
    await call.message.edit_reply_markup(reply_markup=keyboard)


async def send_stat():
    while True:
        stats.send()
        await asyncio.sleep(30)  # TODO: Increase after testing


async def on_startup(_):
    asyncio.create_task(send_stat())


if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
