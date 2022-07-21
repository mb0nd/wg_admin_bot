from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from user_callback import UserCallbackData

def getvpn():
    return InlineKeyboardBuilder().button(
        text='getvpn', 
        callback_data='getvpn'
    )

def get_accept_buttons(user_id, user_name, full_name):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='✅ accept', callback_data=UserCallbackData(action='accept_user', id=user_id, name=user_name, full_name=full_name).pack()),
        InlineKeyboardButton(text='❌ decline', callback_data=UserCallbackData(action='decline_user', id=user_id, name=user_name, full_name=full_name).pack()),
        width=2
    )