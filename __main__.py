import asyncio
import logging
from aiogram import Dispatcher, Bot, F
from commands.admin_commands.main import router as admin_router
from commands.user_commands import router as user_router
from modules.env_reader import env
from middlewares.is_baned_middleware import IsBanedMiddleware
from middlewares.db_session_middleware import DbSessionMiddleware
from db import Base, create_async_engine, get_session_maker, proceed_schemas


async def main() -> None:
    logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',level=logging.INFO)
    dp = Dispatcher()
    bot = Bot(token=env.api_token.get_secret_value())
    # регистрируем доступные команды в боте в выпадающую менюху
    async_engine = create_async_engine(env.pg_url)
    session_maker = get_session_maker(async_engine)

    # Мидлварь которая прокидывает сессию БД 
    dp.update.outer_middleware.register(DbSessionMiddleware())

    # Мидлварь с проверкой на БАН проверяет все события
    dp.update.outer_middleware.register(IsBanedMiddleware())
    admin_router.message.filter(F.from_user.id == env.admin_id)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    in_verification = set()

    #создает таблицы по классам
    await proceed_schemas(async_engine, Base.metadata)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, session_maker=session_maker, env=env, in_verification=in_verification, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__': 
    try:
        asyncio.get_event_loop().run_until_complete(main()) #на замену asyncio.run() вроде как фиксит ошибку с ssl
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')