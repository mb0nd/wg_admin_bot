from aiogram import Bot, Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from cb_data import UserCallbackData
from modules.wg_services import data_preparation, restart_wg
from commands.keyboards import back_button
from db.models import DbUser
from db.requests import get_real_users, get_pay_users, delete_user_in_db
from commands.returned_messages import messages_for_real_user_menu, messages_for_blocked_user_menu

router = Router()
@router.callback_query(F.data == 'send_message_to_pay')
async def send_message_to_pay(call: types.CallbackQuery, session: AsyncSession, bot: Bot):
    pay_users = await get_pay_users(session)
    if pay_users:
        for user in pay_users:
            await bot.send_message(chat_id=user, text= f"Срок аренды сервера подходит к концу, пора бы оплатить 🙂")
        await call.answer('Сообщение об оплате разослано.', show_alert=True)
    else:
        await call.answer('Не кому отсылать, все халявщики.', show_alert=True)

@router.callback_query(F.data == 'traffic_statistics')
async def admin_traffic_statistics(call: types.CallbackQuery, session: AsyncSession):
    data_db = await get_real_users(session) 
    text = await data_preparation(data_db)
    if not text:
        text = 'Нет зарегистрированных пользователей.'
    await call.message.edit_text(text, reply_markup=back_button(), parse_mode='HTML')

@router.callback_query(F.data == 'real_users')
async def admin_real_users(call: types.CallbackQuery, session: AsyncSession) -> None:
    await messages_for_real_user_menu(call, session)

@router.callback_query(F.data == 'block_users')
async def admin_blocked_users(call: types.CallbackQuery, session: AsyncSession) -> None:
    await messages_for_blocked_user_menu(call, session)

@router.callback_query(UserCallbackData.filter(F.data == 'delete_blocked_user'))
async def admin_delete_blocked_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    user = await session.get(DbUser, callback_data.id)
    await delete_user_in_db(user, session)
    await session.commit()
    await messages_for_blocked_user_menu(call, session)

@router.callback_query(F.data == 'restart_wg')
async def admin_restart_wg(call: types.CallbackQuery) -> None:
    text, status = await restart_wg()
    if status:
        return await call.answer(text, show_alert=True)
    else:
        await call.message.answer(text, parse_mode='HTML')

@router.callback_query(F.data == 'close')
async def admin_close_menu(call: types.CallbackQuery) -> None:
    await call.message.delete()