from aiogram import Bot, Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from user_callback import UserCallbackData
from env_reader import Settings
from sqlalchemy.exc import IntegrityError
from gen_user import addUser
from db.requests import create_user, decline_access_user

router = Router()

@router.callback_query(UserCallbackData.filter(F.action =='accept_user'))
async def accept_event_user(call: types.CallbackQuery, session: AsyncSession, bot: Bot, callback_data: UserCallbackData, env: Settings, in_verification: set) -> None:
    print("Мы сюда зашли")
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
        await decline_access_user(callback_data, session)
        await call.message.edit_text(text=f"Пользователю {callback_data.name} доступ запрещен")
    except IntegrityError:
        await call.answer('Не удалось забанить, что то пошло не так ...')
    in_verification.discard(int(callback_data.id))
