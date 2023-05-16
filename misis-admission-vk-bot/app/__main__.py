# region third-party imports
from vkbottle.bot import Bot, Message
from vkbottle import Callback, GroupEventType, GroupTypes, Keyboard, ShowSnackbarEvent


from typing import Dict, List, Union
import re
import requests
from vkbottle.dispatch.views.bot import message

# endregion

# region local imports
from app import config
from app.utils.bot_buttons import Layout
from app.keyboards.reply_keyboards import build_markup, reply_markup
from app.utils.users import BotUsers
from app.utils.statistics import Statistics
from app.utils.states import User, UserEditProfile

# endregion

# Общие
bot = Bot(token=config.vk_token)
layout = Layout()
users = BotUsers()
stat = Statistics()


global counter

counter = 0


# виды callback-кнопок
@bot.on.message(text=["начать", "start", "Start", "Начать"])
async def start(message: Message):
    """Start handler."""
    if users.user_exists(message.from_id):
        await message.answer(
            "Привет! Кажется, мы уже знакомы. Чем могу помочь?",
            keyboard=build_markup("", layout.get_btns("1"), is_main=True),
        )
        return
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
    if not re.match("^[А-Яа-яЁё]{2,20}$", message.text):
        await message.answer('Неверный формат, напиши свое имя, например "Даниил"')
        return
    await message.answer("Записал!\n\nТеперь отправь свою фамилию")
    await bot.state_dispenser.set(message.peer_id, User.LAST_NAME)


@bot.on.message(state=User.LAST_NAME)
async def get_last_name(message: Message):
    if not re.match("^[А-Яа-яЁё]{2,20}$", message.text):
        await message.answer(
            'Неверный формат, напиши свою фамилию, например "Коротков"'
        )
        return
    await message.answer(
        "Окей, двигаемся дальше\n\nОтправь свой город (например, Москва)"
    )
    await bot.state_dispenser.set(message.peer_id, User.CITY)


@bot.on.message(state=User.CITY)
async def get_city(message: Message):
    if not re.match("^[А-Яа-яЁё]{2,20}$", message.text):
        await message.answer("Неверный формат!")
        return
    await message.answer("Почти закончили! Напиши свой email")
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
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.message(text="/elevate")
async def elevate(message: Message):
    pass


@bot.on.message(text="/reload")
async def reload(message: Message):
    pass


@bot.on.message()
async def message_handler(message: Message):
    buttons = layout.get_btns("1")

    if buttons is None:
        return

    if message.text not in buttons.values():
        return

    btn_id = [btn_id for btn_id, text in buttons.items() if text == message.text][0]

    reply_msg = layout.get_reply(btn_id)
    keyboard_btns = layout.get_btns(btn_id)
    keyboard = build_markup(current_path=btn_id, buttons=keyboard_btns)

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
    if lat_lon:
        lat, lon = lat_lon
        reply_msg = reply_msg.split("[")[0].strip()

        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            lat=lat,
            lon=lon,
        )
        return

    if reply_msg is None:
        await bot.api.messages.edit(
            peer_id=event.object.peer_id,
            conversation_message_id=event.object.conversation_message_id,
            keyboard=keyboard,
            message="Нажми на интересующую тебя кнопку",
        )
    else:
        await bot.api.messages.edit(
            peer_id=event.object.peer_id,
            conversation_message_id=event.object.conversation_message_id,
            keyboard=keyboard,
            message=reply_msg,
        )


bot.run_forever()
# async def main():
#     vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
#     vk = vk_session.get_api()
#     longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

#     for event in longpoll.listen():
#         if event.type == VkBotEventType.MESSAGE_NEW:
#             if event.obj["message"]["text"].lower() in ["start", "начать"]:
#                 buttons = shit.get_btns("1")
#                 reply_msg = shit.get_reply("0")
#                 vk.messages.send(
#                     user_id=event.obj.message["from_id"],
#                     random_id=get_random_id(),
#                     peer_id=event.obj.message["from_id"],
#                     keyboard=reply_keyboards.build_markup("", buttons, True),
#                     message=reply_msg,
#                 )
#                 db.insert_bot_user(event.obj.message["from_id"])
#             elif event.obj["message"]["text"] in shit.get_btns("1"):
#                 buttons: Dict[str, str] = shit.get_btns("1")

#                 btn_id = [
#                     btn_id
#                     for btn_id, text in buttons.items()
#                     if text == event.obj["message"]["text"]
#                 ][0]

#                 if btn_id is None:
#                     return

#                 reply_msg: str = shit.get_reply(btn_id)
#                 keyboard_btn: Dict[str, str] = shit.get_btns(btn_id)
#                 keyboard = reply_keyboards.build_markup(
#                     current_path=btn_id, buttons=keyboard_btn
#                 )
#                 vk.messages.send(
#                     user_id=event.obj.message["from_id"],
#                     random_id=get_random_id(),
#                     peer_id=event.obj.message["from_id"],
#                     keyboard=keyboard,
#                     message=reply_msg,
#                 )

#                 db.insert_button_press(event.obj.message["from_id"], btn_id)
#                 counter += 1
#                 if counter == 10:
#                     data = db.get_statistics()
#                     shit.send_stats(data)
#                     counter = 0

#         elif event.type == VkBotEventType.MESSAGE_EVENT:
# current_path: Union[str, List[str]] = event.object.payload["path"].split(
#     ":"
# )
# if current_path[0] == "back":
#     current_path.pop()
#     btn_id = current_path[-1]
#     current_path = ":".join(current_path[1:])
# else:
#     btn_id = current_path[-1]
#     current_path = ":".join(current_path)
# reply_msg: str = shit.get_reply(btn_id)
# keyboard_btn: Dict[str, str] = shit.get_btns(btn_id)
# keyboard = reply_keyboards.build_markup(current_path, keyboard_btn)

# db.insert_button_press(event.obj.message["from_id"], btn_id)
# counter += 1

# if counter == 10:
#     data = db.get_statistics()
#     shit.send_stats(data)
#     counter = 0

# lat_lon = re.findall(r"\d+\.\d+", reply_msg)
# if lat_lon:
#     lat, lon = lat_lon
#     reply_msg = reply_msg.split("[")[0].strip()

#     vk.messages.send(
#         user_id=event.obj.message["from_id"],
#         random_id=get_random_id(),
#         peer_id=event.obj.message["from_id"],
#         lat=lat,
#         long=lon,
#         message=reply_msg,
#     )
#     continue

# if reply_msg is None:
#     vk.messages.edit(
#         peer_id=event.obj.peer_id,
#         conversation_message_id=event.obj.conversation_message_id,
#         random_id=get_random_id(),
#         keyboard=keyboard,
#         message="Нажми на интересующую тебя кнопку",
#     )
# else:
#     vk.messages.edit(
#         peer_id=event.obj.peer_id,
#         conversation_message_id=event.obj.conversation_message_id,
#         random_id=get_random_id(),
#         keyboard=keyboard,
#         message=reply_msg,
#     )


# if __name__ == "__main__":
#     main()
