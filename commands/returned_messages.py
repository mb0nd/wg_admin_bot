from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from modules.user_callback import UserCallbackData
from modules.wg_services import WgServices
from modules.wg_user_new import WgUser
from modules.wg_user_new import get_user
from db.requests import get_blocked_users, get_real_users
from commands.keyboards import block_users_menu, real_users_menu, one_user_menu, back_button

async def return_user_menu(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData):
    user = await get_user(callback_data.id, session)
    text = await WgServices.data_preparation([user.user_object]) # тут проблема с парсингом TypeError: 'User' object is not iterable
    await call.message.edit_text(text, reply_markup=one_user_menu(user.user_object), parse_mode='HTML')

async def messages_for_real_user_menu(call: types.CallbackQuery, session: AsyncSession):
    real_users = await get_real_users(session)
    if real_users:
        await call.message.edit_text('Подтвержденные пользователи:', reply_markup=real_users_menu(real_users))
    else:
        await call.message.edit_text('Список подтвержденных пользователей пуст.', reply_markup=back_button())

async def messages_for_blocked_user_menu(call: types.CallbackQuery, session: AsyncSession):
    blocked_users = await get_blocked_users(session)
    if blocked_users:
        await call.message.edit_text('Заблокированные пользователи:', reply_markup=block_users_menu(blocked_users))
    else:
        await call.message.edit_text('Список заблокированных пользователей пуст.', reply_markup=block_users_menu(blocked_users))