from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from db.models import User
from user_callback import UserCallbackData

def getvpn() -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(
        text='getvpn', 
        callback_data='getvpn'
    ).as_markup(resize_keyboard=True)

def get_accept_buttons(user_id, user_name) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='✅ accept', callback_data=UserCallbackData(action='accept_user', id=user_id, name=user_name).pack()),
        InlineKeyboardButton(text='❌ decline', callback_data=UserCallbackData(action='decline_user', id=user_id, name=user_name).pack()),
        width=2
    ).as_markup(resize_keyboard=True)

def admin_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Отправить оповещение об оплате 💰', callback_data='send_message_to_pay'))
    builder.row(InlineKeyboardButton(text='Потребление трафика 📈', callback_data='traffic_statistics'))
    builder.row(InlineKeyboardButton(text='Список реальных пользователей 📗', callback_data='real_users'))
    builder.row(InlineKeyboardButton(text='Список заблокированных пользователей 📕', callback_data='block_users'))
    builder.row(InlineKeyboardButton(text='Перезапустить WG 🔌', callback_data='restart_wg'))
    builder.row(InlineKeyboardButton(text='Закрыть ❌', callback_data='close'))
    return builder.as_markup(resize_keyboard=True)

def block_users_menu(user_list: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for id, name in user_list:
        builder.row(InlineKeyboardButton(text=f"{name} : удалить ❌", callback_data=UserCallbackData(action='delete_blocked_user', id=id).pack()))
    builder.row(InlineKeyboardButton(text='< Назад', callback_data='admin'))
    return builder.as_markup(resize_keyboard=True)

def real_users_menu(user_list: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in user_list:
        builder.row(InlineKeyboardButton(text=f"{user.user_name}", callback_data=UserCallbackData(action='user_manage', id=user.user_id).pack()))
    builder.row(InlineKeyboardButton(text='< Назад', callback_data='admin'))
    return builder.as_markup(resize_keyboard=True)

def one_user_menu(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if user.is_baned:
        builder.row(InlineKeyboardButton(text="разблокировать ✅", callback_data=UserCallbackData(action='uban_user', id=user.user_id).pack()))
    else:
        builder.row(InlineKeyboardButton(text="заблокировать 🚫", callback_data=UserCallbackData(action='ban_user', id=user.user_id).pack()))
    if user.is_pay:
        builder.row(InlineKeyboardButton(text="Сделать VIP 👍🏻", callback_data=UserCallbackData(action='pay_user', id=user.user_id).pack()))
    else:
        builder.row(InlineKeyboardButton(text="Убрать из VIP 👎🏻", callback_data=UserCallbackData(action='pay_user', id=user.user_id).pack()))
    builder.row(InlineKeyboardButton(text="удалить ❌", callback_data=UserCallbackData(action='delete_user', id=user.user_id).pack()))
    builder.row(InlineKeyboardButton(text='< Назад', callback_data='real_users'))
    return builder.as_markup(resize_keyboard=True)

def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().button(
        text='< Назад', 
        callback_data='admin'
    ).as_markup(resize_keyboard=True)
