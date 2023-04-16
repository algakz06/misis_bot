# region third-party imports
import json

from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from typing import Dict, List, Union
# endregion

# region local imports
from app import config
from app.utils.shit import Shit
from app.keyboards import reply_keyboards

# endregion

# Общие
GROUP_ID = config.vk_group_id
GROUP_TOKEN = config.vk_token
API_VERSION = "5.120"

# виды callback-кнопок
CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app")

locations = {
    'Вход в английский корпус':	(55.726497, 37.606416),
    'Вход в корпус А': (55.726962, 37.607838),
    'Вход в корпус АВ':	(55.728068, 37.606949),
    'Вход в корпус Б':	(55.728472, 37.609033),
    'Вход в корпус В':	(55.728614, 37.610716),
    'Вход в корпус Г':	(55.726975, 37.607154),
    'Вход в корпус Д':	(55.727383, 37.606469),
    'Вход в корпус Е':	(55.728484, 37.607646),
    'Вход в корпус К':	(55.729822, 37.610312),
    'Вход в корпус Л':	(55.728068, 37.606949),
    'Вход в корпус Т':	(55.727286, 37.605205),
    'Горняк-1':	(55.697194, 37.578429),
    'Горняк-2':	(55.698054, 37.579476),
    'ДСГ-5':	(55.739215, 37.542639),
    'ДСГ-6':	(55.739590, 37.542354),
    'Металлург-1':	(55.645949, 37.529914),
    'Металлург-2':	(55.645528, 37.530213),
    'Металлург-3':	(55.645197, 37.529068),
    'Металлург-4':	(55.654467, 37.520895),
    'Спорт зал Беляево':	(55.644699, 37.529732),
    'Спорт зал Горного':	(55.726964, 37.605577)
}


def main():
    shit = Shit()
    vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

    buttons: Dict[str, str] = shit.get_all_buttons()

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj['message']['text'].lower() == 'start':
                buttons = shit.get_btns('1')
                reply_msg = shit.get_reply('0')
                vk.messages.send(
                    user_id=event.obj.message["from_id"],
                    random_id=get_random_id(),
                    peer_id=event.obj.message["from_id"],
                    keyboard=reply_keyboards.build_markup('', buttons, True),
                    message=reply_msg
                )
            elif event.obj['message']['text'].startswith('back:'):
                pass
            elif event.obj['message']['text'] in buttons.values():
                if event.obj['message']['text'] == 'Где? Что?!':
                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        random_id=get_random_id(),
                        peer_id=event.obj.message["from_id"],
                        keyboard=reply_keyboards.get_location_markup(),
                        message='Узнай точную геолокацию того, что тебя интересует!'
                    )
                else:
                    btn_id = [btn_id for btn_id, text in buttons.items() if text == event.obj['message']['text']][0]

                    if btn_id is None:
                        return

                    reply_msg: str = shit.get_reply(btn_id)
                    keyboard_btn: Dict[str, str] = shit.get_btns(btn_id)
                    keyboard = reply_keyboards.build_markup(
                        current_path=btn_id,
                        buttons=keyboard_btn
                    )
                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        random_id=get_random_id(),
                        peer_id=event.obj.message["from_id"],
                        keyboard=keyboard,
                        message=reply_msg
                    )

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            # if event.object.payload.get('type') in CALLBACK_TYPES:
            if 'location' in event.object.payload:
                pass
            current_path: Union[str, List[str]] = event.object.payload['path'].split(':')
            if current_path[0] == 'back':
                current_path.pop()
                btn_id = current_path[-1]
                current_path = ':'.join(current_path[1:])
            else:
                btn_id = current_path[-1]
                current_path = ':'.join(current_path)
            reply_msg: str = shit.get_reply(btn_id)
            keyboard_btn: Dict[str, str] = shit.get_btns(btn_id)
            keyboard = reply_keyboards.build_markup(current_path, keyboard_btn)

            if reply_msg is None:
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    conversation_message_id=event.obj.conversation_message_id,
                    random_id=get_random_id(),
                    keyboard=keyboard,
                    message='Нажми на интересующую тебя кнопку'
                )
            else:
                vk.messages.edit(
                    peer_id=event.obj.peer_id,
                    conversation_message_id=event.obj.conversation_message_id,
                    random_id=get_random_id(),
                    keyboard=keyboard,
                    message=reply_msg
                )


if __name__ == '__main__':
    main()