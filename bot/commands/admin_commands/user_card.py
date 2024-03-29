from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from cb_data import UserCallbackData
from modules.wg_services import get_user
from commands.returned_messages import messages_for_real_user_menu, return_user_menu

router = Router()

@router.callback_query(UserCallbackData.filter(F.action =='user_manage'))
async def admin_manage_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    user = await get_user(callback_data.id, session)
    await return_user_menu(call, user)

@router.callback_query(UserCallbackData.filter(F.action =='set_pay_status'))
async def set_pay_status(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData):
    user = await get_user(callback_data.id, session)
    await user.switch_pay_status(session)
    await return_user_menu(call, user)

@router.callback_query(UserCallbackData.filter(F.action =='set_ban_status'))
async def admin_set_user_ban_status(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    user = await get_user(callback_data.id, session)
    await user.switch_ban_status(session)
    await return_user_menu(call, user)

@router.callback_query(UserCallbackData.filter(F.action =='delete_user'))
async def admin_delete_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    user = await get_user(callback_data.id, session)
    await user.delete_user(session)
    await messages_for_real_user_menu(call, session)