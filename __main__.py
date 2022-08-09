import asyncio
import logging
from aiogram import Dispatcher, Bot
from env_reader import env
from commands import register_user_commands
from db import Base, create_async_engine, get_session_maker, proceed_schemas

async def main() -> None:
    logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',level=logging.INFO)

    dp = Dispatcher()
    bot = Bot(token=env.api_token)
    # регистрируем доступные команды в боте в выпадающую менюху

    async_engine = create_async_engine(env.pg_url)
    session_maker = get_session_maker(async_engine)

    register_user_commands(dp)

    #создает таблицы по классам
    await proceed_schemas(async_engine, Base.metadata)

    await dp.start_polling(bot, session_maker=session_maker, env=env) #Сессию можно брать отсюда

if __name__ == '__main__': 
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')