from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from db.requests import get_blocked_users, get_real_users
from commands.keyboards import block_users_menu, real_users_menu


async def messages_for_real_user_menu(call: types.CallbackQuery, session: AsyncSession):
    real_users = await get_real_users(session)
    if real_users:
        await call.message.edit_text('Подтвержденные пользователи:', reply_markup=real_users_menu(real_users).as_markup(resize_keyboard=True))
    else:
        await call.message.edit_text('Список подтвержденных пользователей пуст.', reply_markup=real_users_menu(real_users).as_markup(resize_keyboard=True))


async def messages_for_blocked_user_menu(call: types.CallbackQuery, session: AsyncSession):
    blocked_users = await get_blocked_users(session)
    if blocked_users:
        await call.message.edit_text('Заблокированные пользователи:', reply_markup=block_users_menu(blocked_users).as_markup(resize_keyboard=True))
    else:
        await call.message.edit_text('Список заблокированных пользователей пуст.', reply_markup=block_users_menu(blocked_users).as_markup(resize_keyboard=True))