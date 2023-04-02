#region third-party imports
from vkbottle import API
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
import asyncio
import logging
import os
#endregion

#region local imports
from app import config
#endregion

# region Logging
# Create a logger instance
log = logging.getLogger('main.py-vk')

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
fh = logging.FileHandler(r'logs/vk_bot.log')
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
bot = Bot(token=config.vk_token)
#endregion

keyboard = Keyboard(one_time=True, inline=False)
keyboard.add(Text("Button 1"), color=KeyboardButtonColor.POSITIVE)
keyboard.add(Text("Button 2"))
keyboard.row()
keyboard.add(Text("Button 3"))
keyboard = keyboard.get_json()

@bot.on.message(text="Привет")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer("Привет, {}".format(users_info[0].first_name), keyboard=keyboard)

if __name__ == '__main__':
    bot.run_forever()