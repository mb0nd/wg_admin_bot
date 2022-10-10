from aiogram import Bot, Router, types, F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.cb_data import UserCallbackData
from bot.modules.wg_services import check_username
from commands.keyboards import getvpn, get_accept_buttons
from env_reader import Settings
from db.models import User


router = Router()

class GetUsername(StatesGroup):
    get_username = State()

@router.message(commands=["start"])
async def start(message: types.Message, in_verification: set, state: FSMContext) -> types.Message:
    if not message.from_user.id in in_verification:
        if message.from_user.username is None:
            await message.answer('Как к вам обращаться?')
            await state.set_state(GetUsername.get_username)
        else:
            await message.answer(
                f'Привет {message.from_user.username}, для продолжения нажми кнопку ниже.', 
                reply_markup=getvpn(message.from_user.id, message.from_user.username)
            )
@router.message(GetUsername.get_username)
async def set_username(message: types.Message, state: FSMContext):
    if check_username(message.text):
        await message.answer(
                f'Привет {message.text}, для продолжения нажми кнопку ниже.', 
                reply_markup=getvpn(message.from_user.id, message.text)
            )
        await state.clear()
    else:
        await message.answer('Вы не ввели имя, так у нас ни чего не получится, попробуйте еще раз')

@router.callback_query(UserCallbackData.filter(F.action =='get_vpn'))
async def get_vpn(
    call: types.CallbackQuery, 
    bot: Bot, 
    env: Settings, 
    session: AsyncSession, 
    in_verification: set,
    callback_data: UserCallbackData
):
    user = await session.get(User, callback_data.id)
    if user:
        await call.message.edit_text( text='Вы уже зарегистрированы!')
        return
    in_verification.add(callback_data.id)
    
    await bot.send_message(
        chat_id=env.admin_id,
        text= f"@{callback_data.name} ({call.from_user.full_name}) отправил запрос на доступ.",
        reply_markup=get_accept_buttons(callback_data.id, callback_data.name)
    )
    await call.message.delete()
    await call.answer(
        'Ваш запрос отправлен на рассмотрение владельцу сервиса.',
        show_alert=True
    )

@router.message()
async def any_text(message: types.Message):
    await message.answer(text='Не известный запрос, используйте кнопки')