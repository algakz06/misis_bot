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
            elif event.obj['message']['text'] in buttons.values():

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