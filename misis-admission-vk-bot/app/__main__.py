# region third-party imports
from vkbottle.bot import Bot, Message
from vkbottle import Callback, GroupEventType, GroupTypes, Keyboard, ShowSnackbarEvent


from typing import Dict, List, Union
import re
import random
import requests

# endregion

# region local imports
from app import config
from app.utils.bot_buttons import Layout
from app.keyboards.reply_keyboards import build_markup, reply_markup
from app.utils.users import BotUsers
from app.utils.statistics import Statistics
from app.utils.states import User, UserEditProfile, AddAdmin
from app.keyboards.buttons import PROFILE_BTN
from app import replies

# endregion

# Общие
bot = Bot(token=config.vk_token)
layout = Layout()
bot_users = BotUsers()
stat = Statistics()


global counter

counter = 0


# виды callback-кнопок
@bot.on.message(text=["начать", "start", "Start", "Начать", "/start"])
async def start(message: Message):
    """Start handler."""
    user_exists = bot_users.user_exists(message.from_id)
    if user_exists:
        await message.answer(
            "Привет! Кажется, мы уже знакомы. Чем могу помочь?",
            keyboard=build_markup("", layout.get_btns("1"), is_main=True),
        )
        return
    else:
        await message.answer(
            """
Привет!\n
Это телеграмм-бот НИТУ МИСИС,\
здесь ты сможешь получить ответ на все свои вопросы\n
Только перед этим нам надо получить от тебя немного информации
"""
        )
        await message.answer(
            "Для начала отправь мне свое имя",
        )
        await bot.state_dispenser.set(message.peer_id, User.FIRST_NAME)


@bot.on.message(state=User.FIRST_NAME)
async def get_first_name(message: Message):
    if not re.match("^([А-ЯЁ][а-яё]*)$", message.text):
        await message.answer('Неверный формат, напиши свое имя, например "Даниил"')
        return
    await message.answer("Записал!\n\nТеперь отправь свою фамилию")
    bot_users.add_params(message.from_id, "first_name", message.text)
    await bot.state_dispenser.set(message.peer_id, User.LAST_NAME)


@bot.on.message(state=User.LAST_NAME)
async def get_last_name(message: Message):
    if not re.match("^([А-ЯЁ][а-яё]*)$", message.text):
        await message.answer(
            'Неверный формат, напиши свою фамилию, например "Коротков"'
        )
        return
    await message.answer(
        "Окей, двигаемся дальше\n\nОтправь свой город (например, Москва)"
    )
    bot_users.add_params(message.from_id, "last_name", message.text)
    await bot.state_dispenser.set(message.peer_id, User.CITY)


@bot.on.message(state=User.CITY)
async def get_city(message: Message):
    if not re.match("^[А-Яа-яЁё]{2,20}$", message.text):
        await message.answer("Неверный формат!")
        return
    await message.answer("Почти закончили! Напиши свой email")
    bot_users.add_params(message.from_id, "city", message.text)
    await bot.state_dispenser.set(message.peer_id, User.EMAIL)


@bot.on.message(state=User.EMAIL)
async def get_email(message: Message):
    if not requests.get(
        f"{config.DEFAULT_BASE_URL}/check/email?email={message.text}"
    ).json()["is_valid"]:
        await message.answer('Неверный формат! Пример "lll@gmail.com"')
        return
    await message.answer(
        "Последний шаг — твой номер телефона! Отправь его в формате 79999999999"
    )
    bot_users.add_params(message.from_id, "email", message.text)
    await bot.state_dispenser.set(message.peer_id, User.PHONE)


@bot.on.message(state=User.PHONE)
async def get_phone(message: Message):
    if not requests.get(
        f"{config.DEFAULT_BASE_URL}/check/phone_number?phone={message.text}"
    ).json()["is_valid"]:
        await message.answer('Неверный формат! Пример: "79999999999"')
        return
    await message.answer("Спасибо за регистрацию и добро пожаловать!")
    buttons = layout.get_btns("1")
    reply_msg = layout.get_reply("0")
    await message.answer(reply_msg, keyboard=build_markup("", buttons, is_main=True))
    bot_users.add_params(message.from_id, "phone_number", message.text)
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.message(text=PROFILE_BTN)
async def profile(message: Message):
    if not bot_users.user_exists(message.from_id):
        await message.answer("Вы не зарегистрированы!")
        return
    await message.answer(
        replies.profile_info(bot_users.get(message.from_id)),
        keyboard=None,
    )


@bot.on.message(text="/elevate")
async def elevate(message: Message):
    if bot_users.admins.is_admin(message.from_id):
        await message.answer("Вы уже администратор!")
        return
    await message.answer("Введите токен доступа")
    await bot.state_dispenser.set(message.peer_id, AddAdmin.ADD_ADMIN)


@bot.on.message(state=AddAdmin.ADD_ADMIN)
async def add_admin(message: Message):
    if not bot_users.admins.add(message.from_id, message.text):
        await message.answer("Неверный токен доступа")
        return
    await message.answer("Вы администратор!")
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.message(text="/reload")
async def reload(message: Message):
    if not bot_users.admins.is_admin(message.from_id):
        await message.answer("Вы не администратор!")
        return
    users = bot_users.get_ids()
    keyboard = build_markup("", layout.get_btns("1"), is_main=True)
    for user in users:
        await bot.api.messages.send(
            user_id=user,
            random_id=random.randint(-2147483648, 2147483647),
            message="Привет! Клавиатура обновилась",
            keyboard=keyboard,
        )


@bot.on.message()
async def message_handler(message: Message):
    buttons = layout.get_btns("1")

    if buttons is None:
        return

    if message.text not in buttons.values():
        return

    btn_id = [btn_id for btn_id, text in buttons.items() if text == message.text][0]

    stat.store(
        user_id=message.from_id,
        button_id=btn_id,
    )

    reply_msg = layout.get_reply(btn_id)
    if reply_msg is None:
        reply_msg = "Нажмите на интересующую вас кнопку"
    keyboard_btns = layout.get_btns(btn_id)
    keyboard = build_markup(current_path=btn_id, buttons=keyboard_btns)

    if isinstance(keyboard, list):
        await message.answer(reply_msg, keyboard=keyboard[0])
        await message.answer("Продолжение клавиатуры", keyboard=keyboard[1])
    else:
        await message.answer(reply_msg, keyboard=keyboard)


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def callback_handler(event: GroupTypes.MessageEvent):
    current_path: List[str] = event.object.payload["path"].split(":")
    if current_path[0] == "back":
        current_path.pop()
        btn_id = current_path[-1]
        current_path = ":".join(current_path[1:])
    else:
        btn_id = current_path[-1]
        current_path = ":".join(current_path)
    reply_msg: Union[str, None] = layout.get_reply(btn_id)
    keyboard_btn: Union[None, Dict[str, str]] = layout.get_btns(btn_id)
    keyboard = build_markup(current_path, keyboard_btn)

    lat_lon = re.findall(r"\d+\.\d+", reply_msg)
    if len(lat_lon) == 2:
        lat, lon = lat_lon
        reply_msg = reply_msg.split("[")[0].strip()

        await bot.api.messages.send(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            random_id=random.randint(-2147483648, 2147483647),
            lat=float(lat),
            long=float(lon),
            message=reply_msg,
        )
        stat.store(
            user_id=event.object.user_id,
            button_id=btn_id,
        )
        return

    if reply_msg is None:
        if isinstance(keyboard, list):
            await bot.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.object.conversation_message_id,
                keyboard=keyboard[0],
                message="Нажми на интересующую тебя кнопку",
            )
            await bot.api.messages.send(
                peer_id=event.object.peer_id,
                random_id=random.randint(-2147483648, 2147483647),
                message="Продолжение клавиатуры",
                keyboard=keyboard[1],
            )
        else:
            await bot.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.object.conversation_message_id,
                keyboard=keyboard,
                message="Нажми на интересующую тебя кнопку",
            )
    else:
        if isinstance(keyboard, list):
            await bot.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.object.conversation_message_id,
                keyboard=keyboard[0],
                message=reply_msg,
            )
            await bot.api.messages.send(
                peer_id=event.object.peer_id,
                random_id=random.randint(-2147483648, 2147483647),
                message="Продолжение клавиатуры",
                keyboard=keyboard[1],
            )
        else:
            await bot.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.object.conversation_message_id,
                keyboard=keyboard,
                message=reply_msg,
            )
    stat.store(
        user_id=event.object.user_id,
        button_id=btn_id,
    )


bot.run_forever()
