import os
from dotenv import load_dotenv
import logging

load_dotenv()

tg_token = os.getenv("TG_TOKEN")
backend_url = 'misis-admission.seizure.icu:80'

POSTGRES_HOST = os.getenv('POSTGRES_HOST', '')
POSTGRES_USER = os.getenv("POSTGRES_USER", '')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', '')
SECRET_KEY = os.getenv('SECRET_KEY', '')

DEFAULT_BASE_URL: str = 'https://misis-admission.seizure.icu'
PROFILE_BTN: str = 'Профиль'
EDIT_PROFILE_BTN: str = 'Редактировать'

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
