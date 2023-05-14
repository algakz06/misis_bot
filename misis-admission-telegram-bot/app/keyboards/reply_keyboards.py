from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from app.config import log
import app.config as config

from typing import Optional, Union, Dict


def build_markup(current_path: str,
                 buttons: Optional[Dict[str, str]],
                 is_main: bool = False) -> Union[ReplyKeyboardMarkup,
                                                 InlineKeyboardMarkup]:
    if is_main:
        markup = reply_markup(buttons=buttons)
        markup.add(KeyboardButton(config.PROFILE_BTN))
    else:
        markup = inline_markup(current_path=current_path, buttons=buttons)
    return markup


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
