from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from app.config import log

from typing import Optional, Union, Dict

def build_markup(current_path: str,
                 buttons: Optional[Dict[str, str]],
                 is_main: bool = False) -> Union[ReplyKeyboardMarkup,
                                        InlineKeyboardMarkup]:
    if is_main:
        return reply_markup(buttons=buttons)
    else:
        return inline_markup(current_path=current_path, buttons=buttons)

def reply_markup(buttons: Optional[Dict[str, str]] = None) -> ReplyKeyboardMarkup:
    if buttons is None:
        return None

    buttons = list(buttons.values())
    keyboard = []
    temp = []

    for button in buttons:
        if len(temp) < 2:
            temp.append(KeyboardButton(button))
        else:
            t = temp.copy()
            keyboard.append(t)
            temp.clear()
            temp.append(KeyboardButton(button))
    else:
        if len(temp) > 0:
            keyboard.append(temp)
    keyboard.append([KeyboardButton('Где? Что?!')])
    return ReplyKeyboardMarkup(keyboard=keyboard)

def inline_markup(current_path: str, buttons: Optional[Dict[str, str]] = None) -> InlineKeyboardMarkup:
    if buttons is None:
        return None

    keyboard = []
    log.info(f'current_path={current_path}, buttons={buttons}')

    for button_id, button in buttons.items():
        path = current_path.split(':')
        path.append(button_id)
        path = ':'.join(path)
        keyboard.append([InlineKeyboardButton(button, callback_data=path)])

    if len(current_path.split(':')) > 1:
        keyboard.append([InlineKeyboardButton('Назад', callback_data=f'back:{current_path}')])


    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_location_markup() -> InlineKeyboardMarkup:
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

    keyboard = []

    for loc, _ in locations.items():
        keyboard.append([InlineKeyboardButton(loc, callback_data=f'location:{loc}')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)