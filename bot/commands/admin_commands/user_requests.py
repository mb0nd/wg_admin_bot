from aiogram import Bot, Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from cb_data import UserCallbackData
from sqlalchemy.exc import IntegrityError
from db.requests import decline_access_user
from modules.wg_services import get_user, check_first_connection

router = Router()

@router.callback_query(UserCallbackData.filter(F.action =='accept_user'))
async def accept_event_user(call: types.CallbackQuery, session: AsyncSession, bot: Bot, callback_data: UserCallbackData, in_verification: set) -> None:
    user = await get_user(callback_data.id, session, callback_data.name)
    config = await user.create_user()
    await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ разрешен")
    message = await bot.send_document(callback_data.id, config)
    status =  await check_first_connection(user.user_object.pub_key)
    if not status:
        await user.delete_user(session)
        await call.message.edit_text(text=f"Срок действия файла конфигурации для {callback_data.name} истек.")
        await bot.send_message(callback_data.id, 'Срок действия файла конфигурации истек.')
    await bot.delete_message(callback_data.id, message.message_id)
    in_verification.discard(int(callback_data.id))

@router.callback_query(UserCallbackData.filter(F.action =='decline_user'))
async def decline_event_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData, in_verification: set) -> None:
    try:
        await decline_access_user(callback_data, session)
        await session.commit()
        await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ запрещен")
    except IntegrityError:
        await call.answer('Не удалось забанить, что то пошло не так ...')
    in_verification.discard(int(callback_data.id))