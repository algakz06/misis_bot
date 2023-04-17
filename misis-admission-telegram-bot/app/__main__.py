#region third-party imports
from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import asyncio
import os
from typing import Dict, List, Optional
#endregion

#region local imports
from app import config
from app.config import log
from app.keyboards import reply_keyboards
from app.keyboards.reply_keyboards import build_markup
from app.utils.shit import Shit
from app.utils.db import DBManager
#endregion


#region app initialization
bot = Bot(config.tg_token)
dp = Dispatcher(bot)
shit = Shit()
db = DBManager()
#endregion

admin_only = lambda message: db.is_admin(message.from_user.id) if isinstance(message, types.Message) else db.is_admin(message)

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

buttons: Dict[str, str] = shit.get_all_buttons()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    buttons = shit.get_btns('1')
    reply_msg = shit.get_reply('0')
    await message.answer(reply_msg, reply_markup=reply_keyboards.build_markup('', buttons, True))
    db.insert_bot_user(message.from_user.id)

@dp.message_handler(admin_only, commands=['reload'])
async def resend_keyboard():
    buttons = shit.get_btns('1')
    for user_id in db.get_users():
        await bot.send_message(
            chat_id=user_id,
            text='Клавиатура обновилась',
            reply_markup=reply_keyboards.build_markup('', buttons, True)
        )

@dp.message_handler()
async def handler(message: types.Message) -> None:
    if message.text == 'Где? Что?!':
        await message.answer('Узнай точную геолокацию того, что тебя интересует!',
                             reply_markup=reply_keyboards.get_location_markup())
        return
    if message.text not in buttons.values():
        print('ERROR: no message')
        return

    btn_id = [btn_id for btn_id, text in buttons.items() if text == message.text][0]

    if btn_id is None:
        return

    reply_msg: str = shit.get_reply(btn_id)
    keyboard_btn: List[str] = shit.get_btns(btn_id)
    keyboard = build_markup(current_path=btn_id,
                            buttons=keyboard_btn)

    if keyboard is not None:
        await message.answer(reply_msg, reply_markup=keyboard)
    else:
        await message.answer(reply_msg)

@dp.callback_query_handler(lambda c: c.data.startswith('back:'))
async def query_back(call: types.CallbackQuery):
    current_path = call.data.split(':')
    current_path.pop()
    last_btn = current_path[-1]
    current_path = ':'.join(current_path[1:])
    msg_repl: str = shit.get_reply(last_btn)
    keyboard_btn: Dict[str, str] = shit.get_btns(last_btn)
    keyboard = build_markup(current_path, keyboard_btn)

    if keyboard is None:
        await call.message.edit_text(msg_repl)
        return

    if msg_repl is None:
        await call.message.edit_reply_markup(reply_markup=keyboard)
        return

    await call.message.edit_text(msg_repl)
    await call.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('location:'))
async def send_locations(call: types.CallbackQuery):
    loc = call.data.split('location:')[-1]
    lat, lon = locations.get(loc, None)
    loc += '📍'
    await call.message.answer(loc)
    await call.message.answer_location(
        latitude=lat,
        longitude=lon
        )

@dp.callback_query_handler(lambda c: True)
async def query_handler(call: types.CallbackQuery):
    current_path = call.data
    btn_id = current_path.split(':')[-1]
    keyboard_btn = shit.get_btns(btn_id)
    keyboard = build_markup(current_path, keyboard_btn)
    msg_repl = shit.get_reply(btn_id)

    if keyboard is None:
        await call.message.edit_text(msg_repl)
        return

    if msg_repl is None:
        await call.message.edit_reply_markup(reply_markup=keyboard)
        return

    await call.message.edit_text(msg_repl)
    await call.message.edit_reply_markup(reply_markup=keyboard)


if __name__ == '__main__':
    from aiogram import executor
    async def task():
        while True:
            buttons = shit.get_all_buttons()
            await asyncio.sleep(30)

    loop = asyncio.get_event_loop()
    loop.create_task(task())

    executor.start_polling(dp, skip_updates=True)