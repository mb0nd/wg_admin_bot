from aiogram import Bot, Router, types
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from user_callback import UserCallbackData
from env_reader import Settings
from commands.keyboards import admin_menu, block_users_menu
from gen_user import addUser
from db.requests import create_user, ban_user, get_blocked_users, delete_user_by_id


router = Router()

@router.callback_query(UserCallbackData.filter(F.action =='accept_user'))
async def accept_event_user(call: types.CallbackQuery, session: AsyncSession, bot: Bot, callback_data: UserCallbackData, env: Settings, in_verification: set):
    pub_key, ip, config = await addUser(callback_data.name, env.listen_port, env.path_to_wg) 
    user_data = {
        'id': callback_data.id,
        'name': callback_data.name,
        'pub_key': pub_key,
        'ip': ip
    }
    await create_user(user_data, session)
    await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ разрешен")
    await bot.send_document(callback_data.id, config, protect_content=True)
    in_verification.discard(int(callback_data.id))

@router.callback_query(UserCallbackData.filter(F.action =='decline_user'))
async def decline_event_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData, env: Settings, in_verification: set):
    try:
        await ban_user(callback_data, session, env.path_to_wg)
        await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ запрещен")
    except IntegrityError:
        await call.answer('Не удалось забанить, что то пошло не так ...')
    in_verification.discard(int(callback_data.id))

@router.message(commands=['admin'])
async def admin_command(message: types.Message) -> None:
    await message.answer("You're an admin!", reply_markup=admin_menu().as_markup(resize_keyboard=True))

@router.callback_query(text='admin')
async def back_admin_menu(call: types.CallbackQuery) -> None:
    await call.message.edit_text("You're an admin!", reply_markup=admin_menu().as_markup(resize_keyboard=True))

@router.callback_query(text='block_users')
async def admin_ban_users(call: types.CallbackQuery, session: AsyncSession) -> None:
    blocked_users = await get_blocked_users(session)
    if blocked_users:
        await call.message.edit_text('Заблокированные пользователи:', reply_markup=block_users_menu(blocked_users).as_markup(resize_keyboard=True))
    else:
        await call.message.edit_text('Список заблокированных пользователей пуст.', reply_markup=block_users_menu(blocked_users).as_markup(resize_keyboard=True))

@router.callback_query(UserCallbackData.filter(F.action =='delete_user'))
async def delete_blocked_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    await delete_user_by_id(callback_data.id, session)
    blocked_users = await get_blocked_users(session)
    if blocked_users:
        await call.message.edit_text('Заблокированные пользователи:', reply_markup=block_users_menu(blocked_users).as_markup(resize_keyboard=True))
    else:
        await call.message.edit_text('Список заблокированных пользователей пуст.', reply_markup=block_users_menu(blocked_users).as_markup(resize_keyboard=True))

@router.callback_query(text='close')
async def admin_close_menu(call: types.CallbackQuery) -> None:
    return await call.message.delete()
