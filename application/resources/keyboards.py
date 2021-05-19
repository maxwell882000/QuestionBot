from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from application.core.models import Option
from typing import List


def from_test_options(options: List[Option]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    for option in options:
        button = InlineKeyboardButton(option.value, callback_data='{}@{}'.format(option.test_id, option.id))
        keyboard.add(button)
    return keyboard
