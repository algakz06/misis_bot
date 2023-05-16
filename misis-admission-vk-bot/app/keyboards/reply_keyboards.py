from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback

from app.config import log

from typing import Optional, Union, Dict, List, Tuple


def build_markup(
    current_path: str, buttons: Optional[Dict[str, str]], is_main: bool = False
) -> Union[Keyboard, None]:
    if is_main:
        return reply_markup(buttons=buttons)
    else:
        return inline_markup(current_path=current_path, buttons=buttons)


def reply_markup(buttons: Optional[Dict[str, str]] = None) -> Union[Keyboard, None]:
    if buttons is None:
        return None

    buttons = list(buttons.values())
    keyboard = Keyboard(one_time=False, inline=False)
    counter = 0

    for button in buttons:
        if counter < 2:
            keyboard.add(Text(button), color=KeyboardButtonColor.POSITIVE)
            counter += 1
        else:
            keyboard.row()
            keyboard.add(Text(button), color=KeyboardButtonColor.POSITIVE)
            counter = 1

    return keyboard.get_json()


def inline_markup(
    current_path: str, buttons: Optional[Dict[str, str]] = None
) -> Union[Keyboard, None]:
    if buttons is None or len(buttons) == 0:
        keyboard = Keyboard(one_time=False, inline=True)
        if len(current_path.split(":")) > 1:
            keyboard.add(Callback("Назад", payload={"path": f"back:{current_path}"}))
        return keyboard.get_json()

    keyboard = Keyboard(one_time=False, inline=True)
    log.info(f"current_path={current_path}, buttons={buttons}")

    buttons: List[Tuple[str, str]] = sorted(
        buttons.items(), key=lambda x: len(x[1]), reverse=True
    )
    counter = 0

    for button_id, button in buttons:
        path = current_path.split(":")
        path.append(button_id)
        path = ":".join(path)
        keyboard.add(Callback(button, payload={"path": path}))

        counter += 1

        if 6 > counter != len(buttons):
            keyboard.row()

    if len(current_path.split(":")) > 1:
        keyboard.row()
        keyboard.add(Callback("Назад", payload={"path": f"back:{current_path}"}))

    log.info(f"keyboard={keyboard.get_json()}")

    return keyboard.get_json()
