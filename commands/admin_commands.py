from aiogram import Bot, Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from user_callback import UserCallbackData
from env_reader import Settings
from commands.keyboards import admin_menu, back_button
from gen_user import addUser, check_statistics, data_preparation
from db.requests import create_user, ban_user, uban_user, delete_user_by_id, get_real_users
from commands.returned_messages import messages_for_real_user_menu, messages_for_blocked_user_menu, return_user_menu


router = Router()

@router.callback_query(UserCallbackData.filter(F.action =='accept_user'))
async def accept_event_user(call: types.CallbackQuery, session: AsyncSession, bot: Bot, callback_data: UserCallbackData, env: Settings, in_verification: set) -> None:
    pub_key, ip, config = await addUser(callback_data.name, env.listen_port, env.path_to_wg) 
    user_data = {
        'id': callback_data.id,
        'name': callback_data.name,
        'pub_key': pub_key,
        'ip': ip
    }
    await create_user(user_data, session)
    await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ разрешен")
    await bot.send_document(callback_data.id, config, )
    in_verification.discard(int(callback_data.id))

@router.callback_query(UserCallbackData.filter(F.action =='decline_user'))
async def decline_event_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData, env: Settings, in_verification: set) -> None:
    try:
        await ban_user(callback_data, session, env.path_to_wg)
        await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ запрещен")
    except IntegrityError:
        await call.answer('Не удалось забанить, что то пошло не так ...')
    in_verification.discard(int(callback_data.id))

@router.message(commands=['admin'])
async def admin_command(message: types.Message) -> None:
    await message.answer("You're an admin!", reply_markup=admin_menu())

@router.callback_query(text='admin')
async def back_admin_menu(call: types.CallbackQuery) -> None:
    await call.message.edit_text("You're an admin!", reply_markup=admin_menu())

@router.callback_query(text='traffic_statistics')
async def admin_traffic_statistics(call: types.CallbackQuery, session: AsyncSession):
    data_db = await get_real_users(session)
    data_cmd = await check_statistics() 
    text = await data_preparation(data_db, data_cmd)
    await call.message.edit_text(text, reply_markup=back_button(), parse_mode='HTML')

@router.callback_query(text='real_users')
async def admin_real_users(call: types.CallbackQuery, session: AsyncSession) -> None:
    await messages_for_real_user_menu(call, session)

@router.callback_query(UserCallbackData.filter(F.action =='user_manage'))
async def admin_manage_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    await return_user_menu(call, session, callback_data)
    
@router.callback_query(UserCallbackData.filter(F.action =='ban_user'))
async def admin_ban_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData, env: Settings) -> None:
    await ban_user(callback_data, session, env.path_to_wg)
    await return_user_menu(call, session, callback_data)
    
@router.callback_query(UserCallbackData.filter(F.action =='uban_user'))
async def admin_uban_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData, env: Settings) -> None:
    await uban_user(callback_data, session, env.path_to_wg)
    await return_user_menu(call, session, callback_data)

@router.callback_query(text='block_users')
async def admin_blocked_users(call: types.CallbackQuery, session: AsyncSession) -> None:
    await messages_for_blocked_user_menu(call, session)

@router.callback_query(UserCallbackData.filter(F.action =='delete_user'))
async def admin_delete_blocked_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    await delete_user_by_id(callback_data.id, session)
    await messages_for_blocked_user_menu(call, session)

@router.callback_query(text='close')
async def admin_close_menu(call: types.CallbackQuery) -> None:
    return await call.message.delete()