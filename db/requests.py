from re import U
from typing import  Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from db import create_async_engine, get_session_maker
import os



"""async def get_user_by_id(session: AsyncSession, user_id: int):
    user = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    return user"""

async def create_user(user_data: Dict):
    async_engine = create_async_engine(os.getenv('PG_URL'))
    session_maker = get_session_maker(async_engine)
    async with session_maker() as session:
        session: AsyncSession
        async with session.begin():
            user = User(
                user_id = user_data['id'],
                user_name = user_data['name'],
                full_name = user_data['full_name'],
                pub_key = user_data['pub_key'],
                ip = user_data['ip']
            )
        await session.merge(user)
        await session.commit()
         