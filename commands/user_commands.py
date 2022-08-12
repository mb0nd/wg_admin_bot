from cgitb import text
from aiogram import Bot, Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from commands.keyboards import getvpn, get_accept_buttons
from env_reader import Settings
from db.requests import check_user_by_id

router = Router()


@router.message(commands=["start"])
async def start(message: types.Message, in_verification: set) -> types.Message:
    if not message.from_user.id in in_verification:
        await message.answer(
            'Если ты здесь, значит ты знаешь зачем...', 
            reply_markup=getvpn()
        )

@router.callback_query(text='getvpn')
async def get_vpn(
    call: types.CallbackQuery, 
    bot: Bot, 
    env: Settings, 
    session: AsyncSession, 
    in_verification: set
):
    user = await check_user_by_id(call.from_user.id, session)
    print(user)
    if user:
        await call.message.edit_text( text='Вы уже зарегистрированы!')
        return

    in_verification.add(call.from_user.id)
    await bot.send_message(
        chat_id=env.admin_id,
        text= f"@{call.from_user.username} ({call.from_user.full_name}) отправил запрос на доступ.",
        reply_markup=get_accept_buttons(call.from_user.id, call.from_user.username)
    )
    await call.message.delete()
    return await call.answer(
        'Ваш запрос отправлен на рассмотрение владельцу сервиса.',
        show_alert=True
    )

@router.message()
async def any_text(message: types.Message):
    await message.answer(text='Не известный запрос, используйте кнопки')