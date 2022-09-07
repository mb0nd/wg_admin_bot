from aiogram import Bot, Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from modules.user_callback import UserCallbackData
from modules.wg_services import WgServices
from commands.keyboards import back_button
from db.requests import delete_user_by_id, get_real_users, get_pay_users
from commands.returned_messages import messages_for_real_user_menu, messages_for_blocked_user_menu

router = Router()

@router.callback_query(text='send_message_to_pay')
async def send_message_to_pay(call: types.CallbackQuery, session: AsyncSession, bot: Bot):
    pay_users = await get_pay_users(session)
    if pay_users:
        for user in pay_users:
            await bot.send_message(chat_id=user, text= f"Срок аренды сервера подходит к концу, пора бы оплатить 🙂")
        await call.answer('Сообщение об оплате разослано.', show_alert=True)
    else:
        await call.answer('Не кому отсылать, все халявщики.', show_alert=True)

@router.callback_query(text='traffic_statistics')
async def admin_traffic_statistics(call: types.CallbackQuery, session: AsyncSession):
    data_db = await get_real_users(session) 
    text = await WgServices.data_preparation(data_db)
    await call.message.edit_text(text, reply_markup=back_button(), parse_mode='HTML')

@router.callback_query(text='real_users')
async def admin_real_users(call: types.CallbackQuery, session: AsyncSession) -> None:
    await messages_for_real_user_menu(call, session)

@router.callback_query(text='block_users')
async def admin_blocked_users(call: types.CallbackQuery, session: AsyncSession) -> None:
    await messages_for_blocked_user_menu(call, session)

@router.callback_query(UserCallbackData.filter(F.action =='delete_blocked_user'))
async def admin_delete_blocked_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    await delete_user_by_id(callback_data.id, session)
    await messages_for_blocked_user_menu(call, session)

@router.callback_query(text='restart_wg')
async def admin_restart_wg(call: types.CallbackQuery) -> None:
    text, status = await WgServices.restart_wg()
    if status:
        return await call.answer(text, show_alert=True)
    else:
        await call.message.answer(text, parse_mode='HTML')

@router.callback_query(text='close')
async def admin_close_menu(call: types.CallbackQuery) -> None:
    await call.message.delete()