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
from app.keyboards import reply_keyboards
from app.keyboards.reply_keyboards import build_markup
from app.utils.shit import Shit
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
    await state.update_data(queue=dict())
    await message.answer(reply_msg, reply_markup=reply_keyboards.build_markup(buttons, '1'))

# @dp.message_handler(Text('Назад'), state='*')
# async def get_back(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     queue: List[str] = data.get('queue')
#     queue.pop()
#     btn_id = queue[-1]    #get last btn_id
#     await state.update_data(queue=queue)
#     try:
#         reply_msg: str = shit.get_reply(btn_id)
#     except IndexError:
#         reply_msg: str = 'Главное меню'
#     keyboard_btn: Dict[str, str] = shit.get_btns(btn_id)
#     keyboard = build_markup(keyboard_btn, btn_id)
#     await message.answer(reply_msg, reply_markup=keyboard)

@dp.message_handler(state='*')
async def handler(message: types.Message, state: FSMContext) -> None:
    if message.text not in buttons.keys():
        print('ERROR: no message')
        return

    btn_id = buttons.get(message.text, None)

    if btn_id is None:
        return

    # data = await state.get_data()
    # queue = data.get('queue')
    # queue.append(btn_id)
    # await state.update_data(queue=queue)

    reply_msg: str = shit.get_reply(btn_id)
    keyboard_btn: List[str] = shit.get_btns(btn_id)
    keyboard = build_markup(keyboard_btn, btn_id)

    if keyboard is not None:
        await message.answer(reply_msg, reply_markup=keyboard)
    else:
        await message.answer(reply_msg)

@dp.callback_query_handler(lambda c: c.data == 'Назад', state='*')
async def query_back(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_id = call.message.message_id
    queue = data.get('queue')
    current_queue: List[str] = queue.get(msg_id)
    if len(current_queue) == 1:
        current_queue.insert(0, current_queue[0][:3])
    current_queue.pop()
    btn_id = current_queue[-1] #get last btn_id
    queue[msg_id] = current_queue
    await state.update_data(queue=queue)
    msg_repl: str = shit.get_reply(btn_id)
    keyboard_btn: Dict[str, str] = shit.get_btns(btn_id)
    keyboard = build_markup(keyboard_btn, btn_id)

    if keyboard is None:
        await call.message.edit_text(msg_repl)
        return

    if msg_repl is None:
        await call.message.edit_reply_markup(reply_markup=keyboard)
        return

    await call.message.edit_text(msg_repl)
    await call.message.edit_reply_markup(reply_markup=keyboard)

@dp.callback_query_handler(lambda c: True, state='*')
async def query_handler(call: types.CallbackQuery, state: FSMContext):
    btn_id = call.data
    msg_id = call.message.message_id

    if btn_id == '0':
        btn_id == '1'

    data = await state.get_data()
    queue: Dict[str, str] = data.get('queue')
    current_queue: List[str] = queue.get(msg_id, None)

    if current_queue is None:
        current_queue = list()
        current_queue.append(btn_id)
    else:
        current_queue.append(btn_id)

    queue[msg_id] = current_queue

    await state.update_data(queue=queue)

    keyboard_btn = shit.get_btns(btn_id)
    keyboard = build_markup(keyboard_btn, btn_id)
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