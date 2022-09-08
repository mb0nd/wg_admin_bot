from aiogram import Bot, Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from modules.user_callback import UserCallbackData
from sqlalchemy.exc import IntegrityError
from db.requests import decline_access_user
# _____________________________________________
from modules.wg_user_new import get_user


router = Router()

"""@router.message(commands=["test"])
async def accept_event_user(message: types.Message, session: AsyncSession) -> None:
    user = await get_user(435654754, 'qqq', session)

"""
@router.callback_query(UserCallbackData.filter(F.action =='accept_user'))
async def accept_event_user(call: types.CallbackQuery, session: AsyncSession, bot: Bot, callback_data: UserCallbackData, in_verification: set) -> None:
    user = await get_user(callback_data.id, callback_data.name, session)
    config = await user.create_user(session)
    await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ разрешен")
    await bot.send_document(callback_data.id, config)
    in_verification.discard(int(callback_data.id))

@router.callback_query(UserCallbackData.filter(F.action =='decline_user'))
async def decline_event_user(call: types.CallbackQuery, session: AsyncSession, callback_data: UserCallbackData, in_verification: set) -> None:
    try:
        await decline_access_user(callback_data, session)
        await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ запрещен")
    except IntegrityError:
        await call.answer('Не удалось забанить, что то пошло не так ...')
    in_verification.discard(int(callback_data.id))


# {'path_to_user': '/etc/wireguard/bondarenko_m_s', 'name': 'bondarenko_m_s', 'publickey': '6ClSRtFuEr4Pim4Bm5VuUp3fBb3y074RUm5sXM6SRx8=', 'ip': '10.0.0.40', 'privatekey': None}
# 
# {'path_to_user': '/etc/wireguard/qqq', 'name': 'qqq', 'publickey': 'hcZx/zozPOBp7Rio5D/pylufK0SQVjw+syOB0wv2bTo=', 'ip': '10.0.0.42', 'privatekey': '2OPyWP65QgRKdAurlUZIeRi4sMFbAx0C4GUEVJByxVo='}