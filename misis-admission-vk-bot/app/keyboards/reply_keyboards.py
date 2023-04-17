from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from app.config import log

from typing import Optional, Union, Dict, List, Tuple


def build_markup(current_path: str,
                 buttons: Optional[Dict[str, str]],
                 is_main: bool = False) -> Union[VkKeyboard, None]:
    if is_main:
        return reply_markup(buttons=buttons)
    else:
        return inline_markup(current_path=current_path, buttons=buttons)


def reply_markup(buttons: Optional[Dict[str, str]] = None) -> Union[VkKeyboard, None]:
    if buttons is None:
        return None

    buttons = list(buttons.values())
    keyboard = VkKeyboard(one_time=False, inline=False)
    counter = 0

    for button in buttons:
        if counter < 2:
            keyboard.add_button(button, color=VkKeyboardColor.POSITIVE)
            counter += 1
        else:
            keyboard.add_line()
            keyboard.add_button(button, color=VkKeyboardColor.POSITIVE)
            counter = 1

    return keyboard.get_keyboard()


def inline_markup(current_path: str, buttons: Optional[Dict[str, str]] = None) -> Union[VkKeyboard, None]:
    if buttons is None or len(buttons) == 0:
        keyboard = VkKeyboard(one_time=False, inline=True)
        if len(current_path.split(':')) > 1:
            keyboard.add_callback_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={'path': f'back:{current_path}'}
            )
        return keyboard.get_keyboard()

    keyboard = VkKeyboard(one_time=False, inline=True)
    log.info(f'current_path={current_path}, buttons={buttons}')

    buttons: List[Tuple[str, str]] = sorted(buttons.items(), key=lambda x: len(x[1]), reverse=True)
    counter = 0

    for button_id, button in buttons:
        path = current_path.split(':')
        path.append(button_id)
        path = ':'.join(path)
        keyboard.add_callback_button(
            label=button,
            color=VkKeyboardColor.POSITIVE,
            payload={'path': path}
        )

        counter += 1

        if 6 > counter != len(buttons):
            keyboard.add_line()

    if len(current_path.split(':')) > 1:
        keyboard.add_line()
        keyboard.add_callback_button(
            label='Назад',
            color=VkKeyboardColor.NEGATIVE,
            payload={'path': f'back:{current_path}'}
        )

    log.info(f'keyboard={keyboard.get_keyboard()}')

    return keyboard.get_keyboard()


# def get_location_markup() -> VkKeyboard:
#     keyboard = VkKeyboard(one_time=False, inline=True)
#     locations = {
#         'Вход в английский корпус':	(55.726497, 37.606416),
#         'Вход в корпус А': (55.726962, 37.607838),
#         'Вход в корпус АВ':	(55.728068, 37.606949),
#         'Вход в корпус Б':	(55.728472, 37.609033),
#         'Вход в корпус В':	(55.728614, 37.610716),
#         'Вход в корпус Г':	(55.726975, 37.607154),
#         'Вход в корпус Д':	(55.727383, 37.606469),
#         'Вход в корпус Е':	(55.728484, 37.607646),
#         'Вход в корпус К':	(55.729822, 37.610312),
#         'Вход в корпус Л':	(55.728068, 37.606949),
#         'Вход в корпус Т':	(55.727286, 37.605205),
#         'Горняк-1':	(55.697194, 37.578429),
#         'Горняк-2':	(55.698054, 37.579476),
#         'ДСГ-5':	(55.739215, 37.542639),
#         'ДСГ-6':	(55.739590, 37.542354),
#         'Металлург-1':	(55.645949, 37.529914),
#         'Металлург-2':	(55.645528, 37.530213),
#         'Металлург-3':	(55.645197, 37.529068),
#         'Металлург-4':	(55.654467, 37.520895),
#         'Спорт зал Беляево':	(55.644699, 37.529732),
#         'Спорт зал Горного':	(55.726964, 37.605577)
#     }
#
#     for loc, _ in locations.items():
#         keyboard.add_callback_button(
#             label=loc,
#             payload={'location': f'location:{loc}'}
#         )
#
#     return keyboard.get_keyboard()
