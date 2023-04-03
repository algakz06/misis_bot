import os
from dotenv import load_dotenv

load_dotenv()

tg_token = os.getenv("TG_TOKEN")
backend_url = 'misis-admission.seizure.icu:80'