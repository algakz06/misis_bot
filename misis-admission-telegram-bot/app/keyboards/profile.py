#!/usr/bin/env python3

"""Profile keyboards for AIOGram."""

from aiogram.types import InlineKeyboardButton as InlKbBtn, InlineKeyboardMarkup as InlKbMarkup
from app import config

inlEditProfileBtn = InlKbBtn(config.EDIT_PROFILE_BTN,
                             callback_data='profile:edit')
inlProfileMenu = InlKbMarkup(row_width=1).add(inlEditProfileBtn)
