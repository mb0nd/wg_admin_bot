__all__ = ['register_user_commands', 'bot_commands', 'keyboards']

from aiogram import Router, F
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command
from middlewares.is_baned_middleware import IsBanedMiddleware
from user_callback import UserCallbackData
from middlewares.db_session_middleware import DbSessionMiddleware 
from commands.commands import start, help_command, get_vpn, any_text, accept_event_user, decline_event_user

def register_user_commands(router: Dispatcher, session_maker, bot) -> None:
    router.update.outer_middleware.register(IsBanedMiddleware(session_maker))
    router.message.register(start, Command(commands=['start']))
    router.message.register(help_command, Command(commands=['help']))
    router.callback_query.middleware.register(DbSessionMiddleware(session_maker, bot))
    router.callback_query.register(get_vpn, text='getvpn')
    router.callback_query.register(accept_event_user, UserCallbackData.filter(F.action=='accept_user'))
    router.callback_query.register(decline_event_user, UserCallbackData.filter(F.action=='decline_user'))
    router.message.register(any_text)