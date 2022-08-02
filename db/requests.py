from typing import  Dict, List
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, BanList


async def create_user(user_data: Dict, session_maker) -> None:
    async with session_maker() as session:
        session: AsyncSession
        async with session.begin():
            user = User(
                user_id = user_data['id'],
                user_name = user_data['name'],
                pub_key = user_data['pub_key'],
                ip = user_data['ip']
            )
        session.add(user)
        await session.commit()

async def get_user_by_id(session_maker: AsyncSession, id: int) -> User:
    async with session_maker() as session:
        session: AsyncSession
        stmt = select(User).where(User.user_id == id)
        result = await session.execute(stmt)
        user = result.scalars().first()
    return user

async def get_all_users(session_maker: AsyncSession) -> List[User]: # Пока не проверял, должен быть кортеж кортежей
    async with session_maker() as session:
        session: AsyncSession
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
    return users
         
async def get_ban_list(session_maker: AsyncSession) -> List:
    async with session_maker() as session:
        session: AsyncSession
        stmt = select(distinct(BanList.user_id))  #stmt = "SELECT DISTINCT user_id FROM banlist"
        result = await session.execute(stmt)
        ban_list = result.scalars().all()
    return ban_list

async def ban_user(session_maker: AsyncSession, id: int):
    async with session_maker() as session:
        session: AsyncSession
        async with session.begin():
            baned_user = BanList(
                user_id = id
            )
        session.add(baned_user)
        await session.commit()

"""
Дублирует вышестоящую функцию из таблицы users по флагу is_baned... 
Возможно оно будет более правильно в дальнейшем, пока юзаем отдельную таблицу
________________________________________________________________________________
async def get_ban_list_from_users_table(session_maker: AsyncSession) -> List:
    async with session_maker() as session:
        session: AsyncSession
        stmt = select(distinct(User.user_id)).where(User.is_baned == True)
        result = await session.execute(stmt)
        ban_list = result.scalars().all()
    return ban_list"""