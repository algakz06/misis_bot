from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.keyboards import buttons
from typing import Optional, List


def build_markup(buttons: Optional[List[str]] = None, main_keyboard: bool = False) -> list:
    if buttons is None:
        return None

    keyboard = []
    temp = []
    print(buttons)
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
    if main_keyboard:
        return ReplyKeyboardMarkup(keyboard=keyboard)
    keyboard.append([KeyboardButton('Назад')])
    return ReplyKeyboardMarkup(keyboard=keyboard)

def get_startKb() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(buttons.admission),
            KeyboardButton(buttons.dormitory)
        ],
        [
            KeyboardButton(buttons.extra_life),
            KeyboardButton(buttons.scholarships)
        ]
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard)