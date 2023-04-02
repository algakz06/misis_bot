import os
from dotenv import load_dotenv

load_dotenv()

vk_token = os.getenv('VK_TOKEN')
backend_url = 'misis-admission.seizure.icu:80'