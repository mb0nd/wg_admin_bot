import asyncio
import logging
from aiogram import Dispatcher, Bot, F
from env_reader import env
from middlewares.is_baned_middleware import IsBanedMiddleware
from middlewares.db_session_middleware import DbSessionMiddleware
from commands import user_commands, admin_commands
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
    admin_commands.router.message.filter(F.from_user.id == env.admin_id)
    dp.include_router(admin_commands.router)
    dp.include_router(user_commands.router)

    in_verification = set()

    #создает таблицы по классам
    await proceed_schemas(async_engine, Base.metadata)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, session_maker=session_maker, env=env, in_verification=in_verification)

if __name__ == '__main__': 
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')