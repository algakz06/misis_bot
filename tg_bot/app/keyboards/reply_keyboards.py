from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from typing import Optional, List, Union, Dict

def build_markup(buttons: Optional[Dict[str, str]] = None, btn_id: Optional[str] = None) -> Union[ReplyKeyboardMarkup,
                                                                                             InlineKeyboardMarkup]:
    if btn_id == '1':
        return reply_markup(buttons=buttons)
    else:
        return inline_markup(buttons=buttons, btn_id=btn_id)

def reply_markup(buttons: Optional[Dict[str, str]] = None) -> ReplyKeyboardMarkup:
    if buttons is None:
        return None

    buttons = list(buttons.keys())
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

def inline_markup(buttons: Optional[Dict[str, str]] = None, btn_id: str = '') -> InlineKeyboardMarkup:
    if buttons is None:
        return None

    keyboard = []

    for button, button_id in buttons.items():
        keyboard.append([InlineKeyboardButton(button, callback_data=button_id)])

    if len(btn_id.split('.')) != 2:
        keyboard.append([InlineKeyboardButton('Назад', callback_data='Назад')])


    return InlineKeyboardMarkup(inline_keyboard=keyboard)