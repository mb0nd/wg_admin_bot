__all__ = ['register_user_commands', 'keyboards']

from aiogram import F
from aiogram import Dispatcher, Router
from aiogram.dispatcher.filters import Command
from middlewares.is_baned_middleware import IsBanedMiddleware
from middlewares.db_session_middleware import DbSessionMiddleware 
from middlewares.is_admin_middleware import IsAdminMiddleware
from user_callback import UserCallbackData
from commands.commands import start, admin_command, get_vpn, any_text, accept_event_user, decline_event_user

router_admin = Router()
router_user = Router()

def register_user_commands(dp: Dispatcher, session_maker) -> None:
    # Мидлварь которая прокидывает сессию БД и объект Бота 
    dp.update.outer_middleware.register(DbSessionMiddleware(session_maker))
    # Мидлварь с проверкой на БАН проверяет все события
    dp.update.outer_middleware.register(IsBanedMiddleware())
    
    router_user.message.register(start, Command(commands=['start']))
    router_user.callback_query.register(get_vpn, text='getvpn')
    router_user.message.register(any_text)

    # Мидлварь проверяет приславшего команду на Админа
    router_admin.message.middleware.register(IsAdminMiddleware())
    router_admin.message.register(admin_command, Command(commands=['admin']))
    router_admin.callback_query.register(accept_event_user, UserCallbackData.filter(F.action=='accept_user'))
    router_admin.callback_query.register(decline_event_user, UserCallbackData.filter(F.action=='decline_user'))
    dp.include_router(router_admin)
    dp.include_router(router_user)
    
   
    