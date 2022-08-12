from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from user_callback import UserCallbackData

def getvpn():
    return InlineKeyboardBuilder().button(
        text='getvpn', 
        callback_data='getvpn'
    ).as_markup(resize_keyboard=True)

def get_accept_buttons(user_id, user_name):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='✅ accept', callback_data=UserCallbackData(action='accept_user', id=user_id, name=user_name).pack()),
        InlineKeyboardButton(text='❌ decline', callback_data=UserCallbackData(action='decline_user', id=user_id, name=user_name).pack()),
        width=2
    ).as_markup(resize_keyboard=True)

def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Потребление трафика 📈', callback_data='traffic_statistics'))
    builder.row(InlineKeyboardButton(text='Список реальных пользователей 📗', callback_data='real_users'))
    builder.row(InlineKeyboardButton(text='Список заблокированных пользователей 📕', callback_data='block_users'))
    builder.row(InlineKeyboardButton(text='Закрыть ❌', callback_data='close'))
    return builder.as_markup(resize_keyboard=True)

def block_users_menu(user_list: list):
    builder = InlineKeyboardBuilder()
    for id, name in user_list:
        builder.row(InlineKeyboardButton(text=f"{name} : удалить ❌", callback_data=UserCallbackData(action='delete_user', id=id).pack()))
    builder.row(InlineKeyboardButton(text='< Назад', callback_data='admin'))
    return builder.as_markup(resize_keyboard=True)

def real_users_menu(user_list: list):
    builder = InlineKeyboardBuilder()
    for user in user_list:
        if user.is_baned:
            builder.row(InlineKeyboardButton(text=f"{user.user_name} : разблокировать ✅", callback_data=UserCallbackData(action='uban_user', id=user.user_id).pack()))
        else:
            builder.row(InlineKeyboardButton(text=f"{user.user_name} : заблокировать ❌", callback_data=UserCallbackData(action='ban_user', id=user.user_id).pack()))
    builder.row(InlineKeyboardButton(text='< Назад', callback_data='admin'))
    return builder.as_markup(resize_keyboard=True)