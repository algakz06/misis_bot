#region third-party imports
from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import logging
import asyncio
import os
from typing import Dict, List
#endregion

#region local imports
from app import config
from app.keyboards import reply_keyboards
from app.keyboards.reply_keyboards import build_markup
from app.utils.shit import Shit
#endregion

# region Logging
# Create a logger instance
log = logging.getLogger('main.py-aiogram')

# AIOGram logging
# logging.basicConfig(level=logging.DEBUG)

# Create log formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Сreate console logging handler and set its level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

# Create file logging handler and set its level
fh = logging.FileHandler(r'logs/telegram_bot.log')
fh.setFormatter(formatter)
log.addHandler(fh)

# region Set logging level
logging_level_lower = os.getenv('LOGGING_LEVEL').lower()
if logging_level_lower == 'debug':
    log.setLevel(logging.DEBUG)
    log.critical("Log level set to debug")
elif logging_level_lower == 'info':
    log.setLevel(logging.INFO)
    log.critical("Log level set to info")
elif logging_level_lower == 'warning':
    log.setLevel(logging.WARNING)
    log.critical("Log level set to warning")
elif logging_level_lower == 'error':
    log.setLevel(logging.ERROR)
    log.critical("Log level set to error")
elif logging_level_lower == 'critical':
    log.setLevel(logging.CRITICAL)
    log.critical("Log level set to critical")
# endregion
#endregion

#region app initialization
bot = Bot(config.tg_token)
dp = Dispatcher(bot, storage=MemoryStorage())
shit = Shit()
#endregion

class Storage(StatesGroup):
    user = State()

buttons: Dict[str, str] = shit.get_all_buttons()

@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    buttons = shit.get_btns('1')
    reply_msg = shit.get_reply('0')
    await state.set_state(Storage.user)
    await state.update_data(queue=['1'])
    await message.answer(reply_msg, reply_markup=reply_keyboards.build_markup(buttons, main_keyboard=True))

@dp.message_handler(Text('Назад'), state='*')
async def get_back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    queue: List[str] = data.get('queue')
    btn_id = queue.pop()
    btn_id = queue.pop()    #get last btn_id
    try:
        reply_msg: str = shit.get_reply(btn_id)
    except IndexError:
        reply_msg: str = 'Главное меню'
    keyboard_btn: List[str] = shit.get_btns(btn_id)
    keyboard = build_markup(keyboard_btn)
    await message.answer(reply_msg, reply_markup=keyboard)

@dp.message_handler(state='*')
async def handler(message: types.Message, state: FSMContext) -> None:
    if message.text not in buttons.keys():
        print('ERROR: no message')
        return
    btn_id = buttons.get(message.text, None)

    if btn_id is None:
        return

    data = await state.get_data()
    queue = data.get('queue')
    queue.append(btn_id)
    await state.update_data(queue=queue)

    reply_msg: str = shit.get_reply(btn_id)
    keyboard_btn: List[str] = shit.get_btns(btn_id)
    keyboard = build_markup(keyboard_btn)

    if keyboard is not None:
        await message.answer(reply_msg, reply_markup=keyboard)
    else:
        await message.answer(reply_msg)

if __name__ == '__main__':
    from aiogram import executor
    async def task():
        while True:
            buttons = shit.get_all_buttons()
            await asyncio.sleep(30)

    loop = asyncio.get_event_loop()
    loop.create_task(task())

    executor.start_polling(dp, skip_updates=True)