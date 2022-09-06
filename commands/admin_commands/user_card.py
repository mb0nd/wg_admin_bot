from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from user_callback import UserCallbackData
from db.models import User
from wg_user import WgUser
from db.requests import get_user_by_id, delete_user_by_id, switch_user_pay_status, switch_user_ban_status
from commands.returned_messages import messages_for_real_user_menu, return_user_menu


router = Router()

@router.callback_query(UserCallbackData.filter(F.action =='user_manage'))
async def admin_manage_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    await return_user_menu(call, session, callback_data)

@router.callback_query(UserCallbackData.filter(F.action =='set_pay_status'))
async def set_pay_status(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData):
    await switch_user_pay_status(callback_data, session)
    await return_user_menu(call, session, callback_data)

@router.callback_query(UserCallbackData.filter(F.action =='set_ban_status'))
async def admin_set_user_ban_status(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    await switch_user_ban_status(callback_data, session)
    await return_user_menu(call, session, callback_data)

@router.callback_query(UserCallbackData.filter(F.action =='delete_user'))
async def admin_delete_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData) -> None:
    user: User = await get_user_by_id(callback_data.id, session)
    await WgUser.remove_user(*user)
    await delete_user_by_id(callback_data.id, session)
    await messages_for_real_user_menu(call, session)