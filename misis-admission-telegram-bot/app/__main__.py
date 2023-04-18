#region third-party imports
from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import asyncio
import os
from typing import Dict, List, Optional
import re
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


@dp.callback_query_handler(lambda c: True)
async def query_handler(call: types.CallbackQuery):
    current_path = call.data
    btn_id = current_path.split(':')[-1]
    keyboard_btn = shit.get_btns(btn_id)
    keyboard = build_markup(current_path, keyboard_btn)
    msg_repl = shit.get_reply(btn_id)

    lat_lon = re.findall(r'\d+\.\d+', msg_repl)
    if lat_lon:
        lat, lon = lat_lon
        msg_repl = msg_repl.split('[')[0].strip()
        await call.message.answer(msg_repl)
        await call.message.answer_location(
            latitude=lat,
            longitude=lon
        )
        return

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