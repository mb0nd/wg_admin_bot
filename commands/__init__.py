__all__ = ['register_user_commands', 'keyboards']

import os
from aiogram import F
from aiogram import Dispatcher, Router
from aiogram.dispatcher.filters import Command
from middlewares.is_baned_middleware import IsBanedMiddleware
from middlewares.db_session_middleware import DbSessionMiddleware 
from user_callback import UserCallbackData
from commands.commands import start, admin_command, get_vpn, any_text, accept_event_user, decline_event_user

router_admin = Router()
router_user = Router()

def register_user_commands(dp: Dispatcher) -> None:
    # Мидлварь которая прокидывает сессию БД 
    dp.update.outer_middleware.register(DbSessionMiddleware())
    # Мидлварь с проверкой на БАН проверяет все события
    dp.update.outer_middleware.register(IsBanedMiddleware())
    
    dp.include_router(router_admin)
    dp.include_router(router_user)

    router_user.message.register(start, Command(commands=['start']))
    router_user.callback_query.register(get_vpn, text='getvpn')
    router_user.message.register(any_text)
    router_user.callback_query.register(any_text)

    router_admin.message.filter(F.from_user.id == int(os.getenv('ADMIN_ID')))
    router_admin.message.register(admin_command, Command(commands=['admin']))
    router_admin.callback_query.filter(F.from_user.id == int(os.getenv('ADMIN_ID')))
    router_admin.callback_query.register(accept_event_user, UserCallbackData.filter(F.action=='accept_user'))
    router_admin.callback_query.register(decline_event_user, UserCallbackData.filter(F.action=='decline_user'))
    

    